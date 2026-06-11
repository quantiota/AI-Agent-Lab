# SKA Knowledge Flow Explorer - Gradio App
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
import gradio as gr
import os

# Load MNIST from local data
transform = transforms.Compose([transforms.ToTensor()])
mnist_dataset = datasets.MNIST(root='./data', train=True, download=False, transform=transform)


class SKAModel(nn.Module):
    def __init__(self, input_size=784, layer_sizes=[256, 128, 64, 10], K=50):
        super(SKAModel, self).__init__()
        self.input_size = input_size
        self.layer_sizes = layer_sizes
        self.K = K

        self.weights = nn.ParameterList()
        self.biases = nn.ParameterList()
        prev_size = input_size
        for size in layer_sizes:
            self.weights.append(nn.Parameter(torch.randn(prev_size, size) * 0.01))
            self.biases.append(nn.Parameter(torch.zeros(size)))
            prev_size = size

        self.Z = [None] * len(layer_sizes)
        self.Z_prev = [None] * len(layer_sizes)
        self.D = [None] * len(layer_sizes)
        self.D_prev = [None] * len(layer_sizes)
        self.delta_D = [None] * len(layer_sizes)

        self.frobenius_history = [[] for _ in range(len(layer_sizes))]
        self.knowledge_flow_history = [[] for _ in range(len(layer_sizes))]
        self.entropy_history = [[] for _ in range(len(layer_sizes))]

    def forward(self, x):
        batch_size = x.shape[0]
        x = x.view(batch_size, -1)
        for l in range(len(self.layer_sizes)):
            z = torch.mm(x, self.weights[l]) + self.biases[l]
            self.frobenius_history[l].append(torch.norm(z, p='fro').item())
            d = torch.sigmoid(z)
            self.Z[l] = z
            self.D[l] = d
            x = d
        return x

    def calculate_flows(self, learning_rate):
        for l in range(len(self.layer_sizes)):
            if self.Z[l] is not None and self.Z_prev[l] is not None and self.D_prev[l] is not None:
                delta_Z = self.Z[l] - self.Z_prev[l]
                phi = torch.norm(delta_Z, p='fro') / learning_rate
                self.knowledge_flow_history[l].append(phi.item())
                delta_D = self.D[l] - self.D_prev[l]
                H_lk = (-1 / np.log(2)) * (self.Z[l] * delta_D)
                self.entropy_history[l].append(torch.sum(H_lk).item())

    def ska_update(self, inputs, learning_rate=0.01):
        for l in range(len(self.layer_sizes)):
            if self.D_prev[l] is not None:
                self.delta_D[l] = self.D[l] - self.D_prev[l]
                prev_output = inputs.view(inputs.shape[0], -1) if l == 0 else self.D_prev[l-1]
                d_prime = self.D[l] * (1 - self.D[l])
                gradient = -1 / np.log(2) * (self.Z[l] * d_prime + self.delta_D[l])
                dW = torch.matmul(prev_output.t(), gradient) / prev_output.shape[0]
                self.weights[l] = self.weights[l] - learning_rate * dW
                self.biases[l] = self.biases[l] - learning_rate * gradient.mean(dim=0)

    def initialize_tensors(self):
        for l in range(len(self.layer_sizes)):
            self.Z[l] = None
            self.Z_prev[l] = None
            self.D[l] = None
            self.D_prev[l] = None
            self.delta_D[l] = None
            self.frobenius_history[l] = []
            self.knowledge_flow_history[l] = []
            self.entropy_history[l] = []


def get_mnist_subset(samples_per_class, data_seed=0):
    targets = mnist_dataset.targets.numpy()
    rng = np.random.RandomState(data_seed)
    images_list = []
    for digit in range(10):
        all_indices = np.where(targets == digit)[0]
        rng.shuffle(all_indices)
        for idx in all_indices[:samples_per_class]:
            img, _ = mnist_dataset[idx]
            images_list.append(img)
    return torch.stack(images_list)


def run_knowledge_flow(n1, n2, n3, n4, K, tau, samples_per_class, data_seed):
    layer_sizes = [int(n1), int(n2), int(n3), int(n4)]

    K = int(K)
    samples_per_class = int(samples_per_class)
    data_seed = int(data_seed)
    learning_rate = tau / K

    inputs = get_mnist_subset(samples_per_class, data_seed)

    torch.manual_seed(42)
    np.random.seed(42)
    model = SKAModel(input_size=784, layer_sizes=layer_sizes, K=K)
    model.initialize_tensors()

    for k in range(K):
        model.forward(inputs)
        if k > 0:
            model.calculate_flows(learning_rate)
            model.ska_update(inputs, learning_rate)
        model.D_prev = [d.clone().detach() if d is not None else None for d in model.D]
        model.Z_prev = [z.clone().detach() if z is not None else None for z in model.Z]

    num_layers = len(layer_sizes)
    layer_colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728']
    layer_labels = [f'Layer {l+1}' for l in range(num_layers)]

    # Plot 1: Knowledge Flow per layer — temporal (Fig 4)
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    for l in range(num_layers):
        data = model.knowledge_flow_history[l]
        line, = ax1.plot(data, label=f"Layer {l+1}")
        if len(data) > 1:
            peak_idx = int(np.argmax(data))
            ax1.axvline(x=peak_idx, color=line.get_color(), linestyle=':', linewidth=1.2, alpha=0.8)
    ax1.set_title("Knowledge Flow Evolution Across Layers")
    ax1.set_xlabel("Step Index K")
    ax1.set_ylabel("Knowledge Flow")
    ax1.legend()
    ax1.grid(True)
    fig1.tight_layout()

    # Plot 2: Knowledge Flow vs ||Z||_F scatter per layer (Fig 3)
    fig2, axes2 = plt.subplots(2, (num_layers + 1) // 2, figsize=(12, 8))
    axes2_flat = axes2.flatten() if num_layers > 1 else [axes2]
    for l in range(num_layers):
        ax = axes2_flat[l]
        kf = model.knowledge_flow_history[l]
        frob = model.frobenius_history[l][1:len(kf) + 1]
        min_len = min(len(kf), len(frob))
        if min_len < 2:
            ax.set_title(f"Layer {l+1}: Not enough data")
            continue
        kf_plot = kf[:min_len]
        frob_plot = frob[:min_len]
        sc = ax.scatter(frob_plot, kf_plot, c=range(min_len), cmap='Blues_r', s=50, alpha=0.8)
        ax.plot(frob_plot, kf_plot, 'k-', alpha=0.3)
        plt.colorbar(sc, ax=ax, label='Step')
        # Red dot at entropy minimum
        if model.entropy_history[l]:
            min_idx = int(np.argmin(model.entropy_history[l]))
            if min_idx < min_len:
                ax.scatter(frob_plot[min_idx], kf_plot[min_idx], color='red', s=80, zorder=5)
        ax.set_xlabel('Frobenius Norm of Knowledge Tensor Z')
        ax.set_ylabel('Frobenius Norm of Knowledge Flow')
        ax.set_title(f'Layer {l+1} Knowledge Flow vs Knowledge Magnitude')
        ax.grid(True, alpha=0.3)
    for l in range(num_layers, len(axes2_flat)):
        axes2_flat[l].set_visible(False)
    fig2.tight_layout()

    return fig1, fig2


with gr.Blocks(title="SKA Knowledge Flow Explorer") as demo:
    gr.Image("logo.png", show_label=False, height=100, container=False)
    gr.Markdown("# SKA Knowledge Flow Explorer")
    gr.Markdown("Visualize the knowledge flow per layer across the forward learning steps, and its trajectory in knowledge space.")

    with gr.Row():
        with gr.Column(scale=1):
            n1_input = gr.Slider(8, 512, value=256, step=8, label="Layer 1 \u2014 neurons")
            n2_input = gr.Slider(8, 512, value=128, step=8, label="Layer 2 \u2014 neurons")
            n3_input = gr.Slider(8, 256, value=64,  step=8, label="Layer 3 \u2014 neurons")
            n4_input = gr.Slider(2, 64,  value=10,  step=1, label="Layer 4 \u2014 neurons")
            k_slider = gr.Slider(1, 200, value=50, step=1, label="K (forward steps)")
            tau_slider = gr.Slider(0.1, 0.75, value=0.5, step=0.01, label="Learning budget \u03c4 (\u03c4 = \u03b7\u00b7K)")
            samples_slider = gr.Slider(1, 100, value=100, step=1, label="Samples per class")
            seed_slider = gr.Slider(0, 99, value=0, step=1, label="Data seed (shuffle samples)")
            run_btn = gr.Button("Run Knowledge Flow", variant="primary")

            gr.Markdown("---")
            gr.Markdown("### Definitions")
            gr.Markdown(
                "| Quantity | Definition |\n|---|---|\n"
                "| **Knowledge Flow** | \u03a6 = \u2016\u0394Z\u2016 / \u03b7 |\n"
                "| **\u0394Z** | Z\u2096 \u2212 Z\u2096\u208b\u2081 (pre-activation change) |\n"
                "| **\u03b7** | learning rate = \u03c4 / K |"
            )

            gr.Markdown("---")
            gr.Markdown("### Reference Paper")
            gr.HTML('<a href="https://arxiv.org/abs/2504.03214v1" target="_blank">arXiv:2504.03214v1</a>')

            gr.Markdown("""
**Abstract**

This paper aims to extend the Structured Knowledge Accumulation (SKA) framework recently proposed by mahi. We introduce two core concepts: the Tensor Net function and the characteristic time property of neural learning. First, we reinterpret the learning rate as a time step in a continuous system. This transforms neural learning from discrete optimization into continuous-time evolution. We show that learning dynamics remain consistent when the product of learning rate and iteration steps stays constant. This reveals a time-invariant behavior and identifies an intrinsic timescale of the network. Second, we define the Tensor Net function as a measure that captures the relationship between decision probabilities, entropy gradients, and knowledge change. Additionally, we define its zero-crossing as the equilibrium state between decision probabilities and entropy gradients. We show that the convergence of entropy and knowledge flow provides a natural stopping condition, replacing arbitrary thresholds with an information-theoretic criterion. We also establish that SKA dynamics satisfy a variational principle based on the Euler-Lagrange equation. These findings extend SKA into a continuous and self-organizing learning model. The framework links computational learning with physical systems that evolve by natural laws. By understanding learning as a time-based process, we open new directions for building efficient, robust, and biologically-inspired AI systems.
            """)

            gr.Markdown("---")
            gr.Markdown("### SKA Explorer Suite")
            gr.HTML('<a href="https://huggingface.co/quant-iota" target="_blank">\u2b05 All Apps</a>')
            gr.Markdown("---")
            gr.Markdown("### About this App")
            gr.Markdown("Knowledge flow \u03a6 measures how fast the pre-activations Z change per layer, normalized by \u03b7. The dotted vertical lines on the temporal plot mark the peak of each layer — each layer reaches its maximum knowledge flow at a different step K, revealing a hierarchical learning cascade. The scatter plot traces the trajectory of each layer in knowledge space — darker points are earlier steps. The red dot marks the entropy minimum for each layer, which aligns with the knowledge flow peak: the point where structured knowledge accumulation is optimal. Layer 4 follows a slower, lower trajectory with no distinct peak, reflecting its classification role.")

        with gr.Column(scale=2):
            plot_flow = gr.Plot(label="Knowledge Flow per Layer")
            plot_scatter = gr.Plot(label="Knowledge Flow vs Frobenius Norm")

    run_btn.click(
        fn=run_knowledge_flow,
        inputs=[n1_input, n2_input, n3_input, n4_input, k_slider, tau_slider, samples_slider, seed_slider],
        outputs=[plot_flow, plot_scatter],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860)
