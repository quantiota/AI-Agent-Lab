# SKA Entropy Gradient Explorer - Gradio App
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
import gradio as gr
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        self.entropy = [None] * len(layer_sizes)

        self.entropy_history = [[] for _ in range(len(layer_sizes))]
        self.cosine_history = [[] for _ in range(len(layer_sizes))]

    def forward(self, x):
        batch_size = x.shape[0]
        x = x.view(batch_size, -1)
        for l in range(len(self.layer_sizes)):
            z = torch.mm(x, self.weights[l]) + self.biases[l]
            d = torch.sigmoid(z)
            self.Z[l] = z
            self.D[l] = d
            x = d
        return x

    def calculate_entropy(self):
        for l in range(len(self.layer_sizes)):
            if self.Z[l] is not None and self.D_prev[l] is not None and self.D[l] is not None and self.Z_prev[l] is not None:
                self.delta_D[l] = self.D[l] - self.D_prev[l]
                H_lk = (-1 / np.log(2)) * (self.Z[l] * self.delta_D[l])
                layer_entropy = torch.sum(H_lk)
                self.entropy[l] = layer_entropy.item()
                self.entropy_history[l].append(layer_entropy.item())

                dot_product = torch.sum(self.Z[l] * self.delta_D[l])
                z_norm = torch.norm(self.Z[l])
                delta_d_norm = torch.norm(self.delta_D[l])
                if z_norm > 0 and delta_d_norm > 0:
                    cos_theta = dot_product / (z_norm * delta_d_norm)
                    self.cosine_history[l].append(cos_theta.item())
                else:
                    self.cosine_history[l].append(0.0)

    def ska_update(self, inputs, learning_rate=0.01, use_delta_d=True):
        for l in range(len(self.layer_sizes)):
            if self.delta_D[l] is not None:
                prev_output = inputs.view(inputs.shape[0], -1) if l == 0 else self.D_prev[l-1]
                d_prime = self.D[l] * (1 - self.D[l])
                if use_delta_d:
                    gradient = -1 / np.log(2) * (self.Z[l] * d_prime + self.delta_D[l])
                else:
                    gradient = -1 / np.log(2) * (self.Z[l] * d_prime)
                dW = torch.matmul(prev_output.t(), gradient) / prev_output.shape[0]
                self.weights[l] = self.weights[l] - learning_rate * dW
                self.biases[l] = self.biases[l] - learning_rate * gradient.mean(dim=0)

    def initialize_tensors(self, batch_size):
        for l in range(len(self.layer_sizes)):
            self.Z[l] = None
            self.Z_prev[l] = None
            self.D[l] = None
            self.D_prev[l] = None
            self.delta_D[l] = None
            self.entropy[l] = None
            self.entropy_history[l] = []
            self.cosine_history[l] = []


def get_mnist_subset(samples_per_class, data_seed=0):
    """Select N samples per class from MNIST."""
    images_list = []
    targets = mnist_dataset.targets.numpy()
    rng = np.random.RandomState(data_seed)
    for digit in range(10):
        all_indices = np.where(targets == digit)[0]
        rng.shuffle(all_indices)
        indices = all_indices[:samples_per_class]
        for idx in indices:
            img, label = mnist_dataset[idx]
            images_list.append(img)
    images = torch.stack(images_list)
    return images


def run_delta_d_comparison(neurons_str, K, tau, samples_per_class, data_seed):
    try:
        layer_sizes = [int(x.strip()) for x in neurons_str.split(",")]
    except ValueError:
        return None, None, None, None

    K = int(K)
    samples_per_class = int(samples_per_class)
    data_seed = int(data_seed)
    learning_rate = tau / K

    inputs = get_mnist_subset(samples_per_class, data_seed)

    layer_colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728']
    layer_labels = [f'Layer {l+1}' for l in range(len(layer_sizes))]

    results = {}
    for use_delta_d in [True, False]:
        torch.manual_seed(42)
        np.random.seed(42)
        model = SKAModel(input_size=784, layer_sizes=layer_sizes, K=K)
        model.initialize_tensors(inputs.size(0))

        for k in range(K):
            model.forward(inputs)
            if k > 0:
                model.calculate_entropy()
                model.ska_update(inputs, learning_rate, use_delta_d=use_delta_d)
            model.D_prev = [d.clone().detach() if d is not None else None for d in model.D]
            model.Z_prev = [z.clone().detach() if z is not None else None for z in model.Z]

        results[use_delta_d] = (model.entropy_history, model.cosine_history)

    figs = []
    for use_delta_d in [True, False]:
        entropy_history, cosine_history = results[use_delta_d]
        label = "With ΔD" if use_delta_d else "Without ΔD"

        fig1, ax1 = plt.subplots(figsize=(7, 4))
        for l in range(len(layer_sizes)):
            ax1.plot(entropy_history[l], color=layer_colors[l % len(layer_colors)],
                     label=layer_labels[l], linewidth=1.5)
        ax1.set_title(f"Entropy Evolution — {label}")
        ax1.set_xlabel("Step Index K")
        ax1.set_ylabel("Entropy")
        ax1.legend(fontsize=8)
        ax1.grid(True)
        fig1.tight_layout()

        fig2, ax2 = plt.subplots(figsize=(7, 4))
        for l in range(len(layer_sizes)):
            ax2.plot(cosine_history[l], color=layer_colors[l % len(layer_colors)],
                     label=layer_labels[l], linewidth=1.5)
        ax2.set_title(f"Cosine Alignment — {label}")
        ax2.set_xlabel("Step Index K")
        ax2.set_ylabel("Cos(θ)")
        ax2.legend(fontsize=8)
        ax2.grid(True)
        fig2.tight_layout()

        figs.extend([fig1, fig2])

    # entropy_with, cosine_with, entropy_without, cosine_without
    return figs[0], figs[1], figs[2], figs[3]


with gr.Blocks(title="SKA Entropy Gradient Explorer") as demo:
    gr.Image(os.path.join(BASE_DIR, "logo.png"), show_label=False, height=100, container=False)
    gr.Markdown("# SKA Entropy Gradient Explorer")
    gr.Markdown("Compare the entropy and cosine alignment trajectories with and without the ΔD term in the SKA gradient. Same architecture, same data, same weights — only the gradient formulation differs.")

    with gr.Row():
        with gr.Column(scale=1):
            neurons_input = gr.Textbox(label="Layer sizes (comma-separated)", value="256, 128, 64, 10")
            k_slider = gr.Slider(1, 200, value=50, step=1, label="K (forward steps)")
            tau_slider = gr.Slider(0.1, 0.75, value=0.5, step=0.01, label="Learning budget τ (τ = η·K)")
            samples_slider = gr.Slider(1, 100, value=100, step=1, label="Samples per class")
            seed_slider = gr.Slider(0, 99, value=0, step=1, label="Data seed (shuffle samples)")
            run_btn = gr.Button("Run Comparison", variant="primary")

            gr.Markdown("---")
            gr.Markdown("### The Two Entropy Gradient Variants")
            gr.Markdown(
                "| Variant | Entropy Gradient ∂H/∂z |\n|---|---|\n"
                "| **With ΔD** | -(1/ln2) [ z·D(1-D) + ΔD ] |\n"
                "| **Without ΔD** | -(1/ln2) [ z·D(1-D) ] |"
            )

            gr.Markdown("---")
            gr.Markdown("### Reference Paper")
            gr.HTML('<a href="https://arxiv.org/abs/2503.13942v1" target="_blank">arXiv:2503.13942v1</a>')

            gr.Markdown("""
**Abstract**

We introduce the Structured Knowledge Accumulation (SKA) framework, which reinterprets entropy as a dynamic, layer-wise measure of knowledge alignment in neural networks. Instead of relying on traditional gradient-based optimization, SKA defines entropy in terms of knowledge vectors and their influence on decision probabilities across multiple layers. This formulation naturally leads to the emergence of activation functions such as the sigmoid as a consequence of entropy minimization. Unlike conventional backpropagation, SKA allows each layer to optimize independently by aligning its knowledge representation with changes in decision probabilities. As a result, total network entropy decreases in a hierarchical manner, allowing knowledge structures to evolve progressively. This approach provides a scalable, biologically plausible alternative to gradient-based learning, bridging information theory and artificial intelligence while offering promising applications in resource-constrained and parallel computing environments.
            """)

            gr.Markdown("---")
            gr.Markdown("### SKA Explorer Suite")
            gr.HTML('<a href="https://huggingface.co/quant-iota" target="_blank">⬅ All Apps</a>')
            gr.Markdown("---")
            gr.Markdown("### About this App")
            gr.Markdown("The ΔD term captures the discrete change in decision probability between two consecutive forward passes. Removing it reduces the gradient to a continuous-like form. This app runs both variants side by side — same weights, same data, same architecture — so the role of ΔD is immediately visible in the entropy and cosine trajectories.")

        with gr.Column(scale=2):
            gr.Markdown("### With ΔD")
            plot_entropy_with = gr.Plot(label="Entropy — With ΔD")
            plot_cosine_with = gr.Plot(label="Cosine Alignment — With ΔD")

        with gr.Column(scale=2):
            gr.Markdown("### Without ΔD")
            plot_entropy_without = gr.Plot(label="Entropy — Without ΔD")
            plot_cosine_without = gr.Plot(label="Cosine Alignment — Without ΔD")

    run_btn.click(
        fn=run_delta_d_comparison,
        inputs=[neurons_input, k_slider, tau_slider, samples_slider, seed_slider],
        outputs=[plot_entropy_with, plot_cosine_with, plot_entropy_without, plot_cosine_without],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=[BASE_DIR])
