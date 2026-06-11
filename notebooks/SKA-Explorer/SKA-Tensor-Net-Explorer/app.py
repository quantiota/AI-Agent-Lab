# SKA Tensor Net Explorer - Gradio App
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
        self.tensor_net_history = [[] for _ in range(len(layer_sizes))]

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

    def calculate_tensor_net(self):
        for l in range(len(self.layer_sizes)):
            if self.Z[l] is not None and self.Z_prev[l] is not None:
                delta_Z = self.Z[l] - self.Z_prev[l]
                # Tensor Net: Σ (D − ∇_z H) · ΔZ
                D_prime = self.D[l] * (1 - self.D[l])
                nabla_z_H = (1 / np.log(2)) * self.Z[l] * D_prime
                tensor_net_step = torch.sum(delta_Z * (self.D[l] - nabla_z_H))
                self.tensor_net_history[l].append(tensor_net_step.item())

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
            self.tensor_net_history[l] = []


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


def run_tensor_net(n1, n2, n3, n4, K, tau, samples_per_class, data_seed):
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
            model.calculate_tensor_net()
            model.ska_update(inputs, learning_rate)
        model.D_prev = [d.clone().detach() if d is not None else None for d in model.D]
        model.Z_prev = [z.clone().detach() if z is not None else None for z in model.Z]

    num_layers = len(layer_sizes)

    # Plot: Tensor Net per layer with zero-crossing markers
    fig, ax = plt.subplots(figsize=(8, 5))
    for l in range(num_layers):
        data = model.tensor_net_history[l]
        line, = ax.plot(data, label=f"Layer {l+1}")
        if len(data) > 1:
            arr = np.array(data)
            crossings = np.where(np.diff(np.sign(arr)))[0]
            for c in crossings:
                x_cross = c + arr[c] / (arr[c] - arr[c + 1])
                ax.axvline(x=x_cross, color=line.get_color(), linestyle=':', linewidth=1.2, alpha=0.8)
    ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title("Tensor Net Evolution Across Layers")
    ax.set_xlabel("Step Index K")
    ax.set_ylabel("Tensor Net")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    # Plot 2: Tensor Net vs ||Z||_F scatter per layer
    fig2, axes2 = plt.subplots(2, (num_layers + 1) // 2, figsize=(12, 8))
    axes2_flat = axes2.flatten() if num_layers > 1 else [axes2]
    for l in range(num_layers):
        ax = axes2_flat[l]
        tn = model.tensor_net_history[l]
        frob = model.frobenius_history[l][1:len(tn) + 1]
        min_len = min(len(tn), len(frob))
        if min_len < 2:
            ax.set_title(f"Layer {l+1}: Not enough data")
            continue
        tn_plot = tn[:min_len]
        frob_plot = frob[:min_len]
        sc = ax.scatter(frob_plot, tn_plot, c=range(min_len), cmap='Blues_r', s=50, alpha=0.8)
        ax.plot(frob_plot, tn_plot, 'k-', alpha=0.3)
        plt.colorbar(sc, ax=ax, label='Step')
        ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--')
        ax.set_xlabel('Frobenius Norm of Knowledge Tensor Z')
        ax.set_ylabel('Tensor Net')
        ax.set_title(f'Layer {l+1}: Tensor Net vs. Knowledge Magnitude')
        ax.grid(True, alpha=0.3)
    for l in range(num_layers, len(axes2_flat)):
        axes2_flat[l].set_visible(False)
    fig2.tight_layout()

    return fig, fig2


with gr.Blocks(title="SKA Tensor Net Explorer") as demo:
    gr.Image("logo.png", show_label=False, height=100, container=False)
    gr.Markdown("# SKA Tensor Net Explorer")
    gr.Markdown("Visualize the Tensor Net per layer. The zero-crossing marks the transition from unstructured to structured knowledge accumulation.")

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
            run_btn = gr.Button("Run Tensor Net", variant="primary")

            gr.Markdown("---")
            gr.Markdown("### Definitions")
            gr.Markdown(
                "| Quantity | Definition |\n|---|---|\n"
                "| **Tensor Net** | \u03a3 (D \u2212 \u2207z H) \u00b7 \u0394Z |\n"
                "| **\u2207z H** | \u2212(1/ln2) \u00b7 z \u00b7 D(1\u2212D) |\n"
                "| **Zero-crossing** | phase transition |"
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
            gr.Markdown("The Tensor Net captures the balance between decision probabilities D and entropy gradients \u2207z H, weighted by the knowledge change \u0394Z at each step. When positive, the network is accumulating knowledge in the direction of the entropy gradient. The zero-crossing — marked by dotted vertical lines — signals the onset of structured knowledge accumulation.")

            gr.Markdown("---")
            gr.Markdown("### Important Note")
            gr.Markdown(
                "The layered SKA Neural Network presented here is a discrete approximation (a \u201cshadow\u201d) of the underlying continuous "
                "[Riemannian Neural Field (RNF)](https://doi.org/10.13140/RG.2.2.35650.24001).\n\n"
                "It is provided for educational purposes only to illustrate the core mechanism of local entropy reduction through decision shifts \u0394D.\n\n"
                "The true SKA dynamics and all its deeper properties live in the continuous RNF. "
                "The layered discretization is useful for teaching and rapid experimentation, but it is not the complete theory."
            )

        with gr.Column(scale=2):
            plot_tensor = gr.Plot(label="Tensor Net per Layer")
            plot_scatter = gr.Plot(label="Tensor Net vs Frobenius Norm")

    run_btn.click(
        fn=run_tensor_net,
        inputs=[n1_input, n2_input, n3_input, n4_input, k_slider, tau_slider, samples_slider, seed_slider],
        outputs=[plot_tensor, plot_scatter],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860)
