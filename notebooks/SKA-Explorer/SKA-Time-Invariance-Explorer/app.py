# SKA Time-Invariance Explorer - Gradio App
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

# Fixed architecture and characteristic time as per arXiv:2504.03214v1
LAYER_SIZES = [256, 128, 64, 10]
TAU = 0.5

# Exact 6 (eta, K) configurations from the paper — all satisfy eta * K = 0.5
CONFIGS = [
    (0.020,   25),
    (0.010,   50),
    (0.005,  100),
    (0.0033, 150),
    (0.0025, 200),
    (0.001,  500),
]

CONFIG_COLORS = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B']


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
        self.output_history = []

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

    def ska_update(self, inputs, learning_rate=0.01):
        for l in range(len(self.layer_sizes)):
            if self.delta_D[l] is not None:
                prev_output = inputs.view(inputs.shape[0], -1) if l == 0 else self.D_prev[l-1]
                d_prime = self.D[l] * (1 - self.D[l])
                gradient = -1 / np.log(2) * (self.Z[l] * d_prime + self.delta_D[l])
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
            self.output_history = []


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


def run_time_invariance(samples_per_class, data_seed):
    samples_per_class = int(samples_per_class)
    data_seed = int(data_seed)

    inputs = get_mnist_subset(samples_per_class, data_seed)

    results = []
    for eta, K in CONFIGS:
        torch.manual_seed(42)
        np.random.seed(42)
        model = SKAModel(input_size=784, layer_sizes=LAYER_SIZES, K=K)
        model.initialize_tensors(inputs.size(0))

        for k in range(K):
            model.forward(inputs)
            if k > 0:
                model.calculate_entropy()
                model.ska_update(inputs, eta)
            model.D_prev = [d.clone().detach() if d is not None else None for d in model.D]
            model.Z_prev = [z.clone().detach() if z is not None else None for z in model.Z]

        results.append((eta, K, model.entropy_history, model.cosine_history))

    layer_colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728']
    layer_labels = ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4']

    # Plot 1: Entropy — 2x3 grid, one subplot per (eta, K) config, 4 layer curves each
    fig1, axes1 = plt.subplots(3, 2, figsize=(14, 18))
    for idx, (eta, K, entropy_history, _) in enumerate(results):
        ax = axes1[idx // 2][idx % 2]
        for l in range(len(LAYER_SIZES)):
            ax.plot(entropy_history[l], color=layer_colors[l],
                    label=layer_labels[l], linewidth=1.5)
        ax.set_title(f"Entropy Evolution Across Layers (Single Pass)\nη={eta:.4f}, K={K}", fontsize=10)
        ax.set_xlabel("Step Index K")
        ax.set_ylabel("Entropy")
        ax.legend(fontsize=8)
        ax.grid(True)
    fig1.suptitle(
        f"Time-Invariance — Entropy  |  T = η·K = {TAU}  |  [256, 128, 64, 10]",
        fontsize=13, y=1.01
    )
    fig1.tight_layout()

    # Plot 2: Cosine alignment — 2x3 grid, one subplot per (eta, K) config, 4 layer curves each
    fig2, axes2 = plt.subplots(3, 2, figsize=(14, 18))
    for idx, (eta, K, _, cosine_history) in enumerate(results):
        ax = axes2[idx // 2][idx % 2]
        for l in range(len(LAYER_SIZES)):
            ax.plot(cosine_history[l], color=layer_colors[l],
                    label=layer_labels[l], linewidth=1.5)
        ax.set_title(f"Cos(θ) Alignment Evolution Across Layers (Single Pass)\nη={eta:.4f}, K={K}", fontsize=10)
        ax.set_xlabel("Step Index K")
        ax.set_ylabel("Cos(θ)")
        ax.legend(fontsize=8)
        ax.grid(True)
    fig2.suptitle(
        f"Time-Invariance — Cosine Alignment  |  T = η·K = {TAU}  |  [256, 128, 64, 10]",
        fontsize=13, y=1.01
    )
    fig2.tight_layout()

    return fig1, fig2


with gr.Blocks(title="SKA Time-Invariance Explorer") as demo:
    gr.Image(os.path.join(BASE_DIR, "logo.png"), show_label=False, height=100, container=False)
    gr.Markdown("# SKA Time-Invariance Explorer")
    gr.Markdown("Fix the characteristic time T = η · K = 0.5 and run 6 different (η, K) pairs automatically. All entropy and cosine curves collapse onto the same trajectory — revealing the intrinsic timescale of the architecture [256, 128, 64, 10] on MNIST.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("**Architecture (fixed):** [256, 128, 64, 10]")
            gr.Markdown("**Characteristic time (fixed):** T = η · K = 0.5")
            samples_slider = gr.Slider(1, 100, value=100, step=1, label="Samples per class")
            seed_slider = gr.Slider(0, 99, value=0, step=1, label="Data seed (shuffle samples)")
            run_btn = gr.Button("Run Time-Invariance Test", variant="primary")

            gr.Markdown("---")
            gr.Markdown("### The 6 configurations")
            gr.Markdown(
                "| η | K |\n|---|---|\n"
                "| 0.0200 | 25  |\n"
                "| 0.0100 | 50  |\n"
                "| 0.0050 | 100 |\n"
                "| 0.0033 | 150 |\n"
                "| 0.0025 | 200 |\n"
                "| 0.0010 | 500 |"
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
            gr.HTML('<a href="https://huggingface.co/quant-iota" target="_blank">⬅ All Apps</a>')
            gr.Markdown("---")
            gr.Markdown("### About this App")
            gr.Markdown("Six (η, K) pairs all share the same characteristic time T = η · K = 0.5, the intrinsic timescale of the architecture [256, 128, 64, 10]. Each configuration is run independently and plotted as a function of the step index K. The trajectory shapes remain identical across all configurations while the amplitude scales with η — demonstrating that T is the true timescale of learning, not η or K individually. The characteristic time is the necessary time exposure of the sample to the learning system to complete. T = 0.5 is the characteristic time of the architecture [256, 128, 64, 10] on MNIST.")

        with gr.Column(scale=2):
            plot_entropy = gr.Plot(label="Entropy — 4 Layers")
            plot_cosine  = gr.Plot(label="Cosine Alignment — 4 Layers")

    run_btn.click(
        fn=run_time_invariance,
        inputs=[samples_slider, seed_slider],
        outputs=[plot_entropy, plot_cosine],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=[BASE_DIR])
