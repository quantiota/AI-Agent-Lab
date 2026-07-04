# SKA Single Digit Entropy State Explorer
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
import gradio as gr
import io
import os
from datetime import datetime
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load MNIST from local data
transform = transforms.Compose([transforms.ToTensor()])
mnist_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)


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
        self.frobenius_history = [[] for _ in range(len(layer_sizes))]
        self.weight_frobenius_history = [[] for _ in range(len(layer_sizes))]
        self.net_history = [[] for _ in range(len(layer_sizes))]
        self.tensor_net_total = [0.0] * len(layer_sizes)
        self.output_history = []

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

    def calculate_entropy(self):
        total_entropy = 0
        for l in range(len(self.layer_sizes)):
            if self.Z[l] is not None and self.D_prev[l] is not None and self.D[l] is not None and self.Z_prev[l] is not None:
                self.delta_D[l] = self.D[l] - self.D_prev[l]
                delta_Z = self.Z[l] - self.Z_prev[l]
                H_lk = (-1 / np.log(2)) * (self.Z[l] * self.delta_D[l])
                layer_entropy = torch.sum(H_lk)
                self.entropy[l] = layer_entropy.item()
                self.entropy_history[l].append(layer_entropy.item())

                dot_product = torch.sum(self.Z[l] * self.delta_D[l])
                z_norm = torch.norm(self.Z[l])
                delta_d_norm = torch.norm(self.delta_D[l])
                if z_norm > 0 and delta_d_norm > 0:
                    self.cosine_history[l].append((dot_product / (z_norm * delta_d_norm)).item())
                else:
                    self.cosine_history[l].append(0.0)

                total_entropy += layer_entropy
                D_prime = self.D[l] * (1 - self.D[l])
                nabla_z_H = (1 / np.log(2)) * self.Z[l] * D_prime
                tensor_net_step = torch.sum(delta_Z * (self.D[l] - nabla_z_H))
                self.net_history[l].append(tensor_net_step.item())
                self.tensor_net_total[l] += tensor_net_step.item()
        return total_entropy

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
            self.frobenius_history[l] = []
            self.weight_frobenius_history[l] = []
            self.net_history[l] = []
            self.tensor_net_total[l] = 0.0
            self.output_history = []


def get_mnist_single_digit(digit, samples, data_seed=0):
    targets = mnist_dataset.targets.numpy()
    rng = np.random.RandomState(data_seed)
    all_indices = np.where(targets == digit)[0]
    rng.shuffle(all_indices)
    images_list = [mnist_dataset[idx][0] for idx in all_indices[:samples]]
    return torch.stack(images_list)


def plot_convergence_comparison(history):
    if not history:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No history yet — run at least one architecture.", ha='center', va='center')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf)

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(history), 1)))

    fig = plt.figure(figsize=(14, 30))
    ax1 = fig.add_subplot(311, projection='3d')  # L1, L2, L3
    ax2 = fig.add_subplot(312, projection='3d')  # L1, L2, L4
    ax3 = fig.add_subplot(313, projection='3d')  # L2, L3, L4

    for i, run in enumerate(history):
        h = run["entropy_history_norm"]
        if len(h) < 3:
            continue

        H1 = np.array(h[0])
        H2 = np.array(h[1])
        H3 = np.array(h[2])
        H4 = np.array(h[3]) if len(h) > 3 else np.zeros_like(H1)
        color = colors[i % len(colors)]
        label = f"{run['architecture']} K={run['K']} τ={run['tau']:.2f}"

        ax1.plot(H1, H2, H3, color=color, linewidth=1.5, alpha=0.8, label=label)
        ax1.scatter(H1[0], H2[0], H3[0], color='green', s=60, zorder=5)
        ax1.scatter(H1[-1], H2[-1], H3[-1], color='red', s=60, zorder=5)
        for k in range(0, len(H1), max(1, len(H1) // 5)):
            ax1.scatter(H1[k], H2[k], H3[k], color='black', s=15, zorder=5)

        ax2.plot(H1, H2, H4, color=color, linewidth=1.5, alpha=0.8, label=label)
        ax2.scatter(H1[0], H2[0], H4[0], color='green', s=60, zorder=5)
        ax2.scatter(H1[-1], H2[-1], H4[-1], color='red', s=60, zorder=5)
        for k in range(0, len(H1), max(1, len(H1) // 5)):
            ax2.scatter(H1[k], H2[k], H4[k], color='black', s=15, zorder=5)

        ax3.plot(H2, H3, H4, color=color, linewidth=1.5, alpha=0.8, label=label)
        ax3.scatter(H2[0], H3[0], H4[0], color='green', s=60, zorder=5)
        ax3.scatter(H2[-1], H3[-1], H4[-1], color='red', s=60, zorder=5)
        for k in range(0, len(H2), max(1, len(H2) // 5)):
            ax3.scatter(H2[k], H3[k], H4[k], color='black', s=15, zorder=5)

    digit = history[0]["digit"]
    ax1.set_xlabel("Layer 1 (h/n)", fontsize=8)
    ax1.set_ylabel("Layer 2 (h/n)", fontsize=8)
    ax1.set_zlabel("Layer 3 (h/n)", fontsize=8)
    ax1.set_title("3D Trajectory (L1, L2, L3)\n● start  ● end", fontsize=10)
    ax1.legend(fontsize=6, loc='upper left')

    ax2.set_xlabel("Layer 1 (h/n)", fontsize=8)
    ax2.set_ylabel("Layer 2 (h/n)", fontsize=8)
    ax2.set_zlabel("Layer 4 (h/n)", fontsize=8)
    ax2.set_title("3D Trajectory (L1, L2, L4)\n● start  ● end", fontsize=10)
    ax2.legend(fontsize=6, loc='upper left')

    ax3.set_xlabel("Layer 2 (h/n)", fontsize=8)
    ax3.set_ylabel("Layer 3 (h/n)", fontsize=8)
    ax3.set_zlabel("Layer 4 (h/n)", fontsize=8)
    ax3.set_title("3D Trajectory (L2, L3, L4)\n● start  ● end", fontsize=10)
    ax3.legend(fontsize=6, loc='upper left')

    fig.suptitle(f"4D Entropy State Trajectories — Digit {digit} — Architecture Comparison", fontsize=12, y=1.01)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)


def run_ska(digit, n1, n2, n3, n4, K, tau, samples, data_seed, history):
    digit = int(digit)
    layer_sizes = [int(n1), int(n2), int(n3), int(n4)]
    neurons_str = ", ".join(str(n) for n in layer_sizes)

    K = int(K)
    samples = int(samples)
    data_seed = int(data_seed)
    learning_rate = tau / K

    inputs = get_mnist_single_digit(digit, samples, data_seed)

    torch.manual_seed(42)
    np.random.seed(42)
    model = SKAModel(input_size=784, layer_sizes=layer_sizes, K=K)
    model.initialize_tensors(inputs.size(0))

    for k in range(K):
        outputs = model.forward(inputs)
        model.output_history.append(outputs.mean(dim=0).detach().cpu().numpy())
        if k > 0:
            model.calculate_entropy()
            model.ska_update(inputs, learning_rate)
            for l in range(len(model.layer_sizes)):
                model.weight_frobenius_history[l].append(torch.norm(model.weights[l], p='fro').item())
        model.D_prev = [d.clone().detach() if d is not None else None for d in model.D]
        model.Z_prev = [z.clone().detach() if z is not None else None for z in model.Z]

    num_layers = len(layer_sizes)

    convergence_state = [
        model.entropy_history[l][-1] / layer_sizes[l] if model.entropy_history[l] else 0.0
        for l in range(num_layers)
    ]

    entropy_history_norm = [
        [v / layer_sizes[l] for v in model.entropy_history[l]]
        for l in range(num_layers)
    ]

    run = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "digit": digit,
        "architecture": neurons_str,
        "K": K,
        "tau": tau,
        "samples": samples,
        "seed": data_seed,
        "convergence_state": convergence_state,
        "entropy_history_norm": entropy_history_norm,
    }
    history = history + [run]

    # Plot 1: normalized entropy trajectory (current run)
    fig1, axes1 = plt.subplots(num_layers, 1, figsize=(10, 3 * num_layers), sharex=True)
    if num_layers == 1:
        axes1 = [axes1]
    for l in range(num_layers):
        axes1[l].plot(entropy_history_norm[l])
        axes1[l].set_title(f"Layer {l+1} ({layer_sizes[l]} neurons): Normalized Entropy", fontsize=11)
        axes1[l].set_ylabel("h / n_neurons")
        axes1[l].grid(True)
    axes1[-1].set_xlabel("Step Index K")
    fig1.suptitle(f"Digit {digit} | Architecture: [{neurons_str}] | K={K} | τ={tau:.2f}", fontsize=12)
    fig1.tight_layout()

    fig2 = plot_convergence_comparison(history)

    return fig1, fig2, history


def clear_history():
    return plot_convergence_comparison([]), []


with gr.Blocks(title="SKA Single Digit Explorer") as demo:
    gr.Image(os.path.join(BASE_DIR, "logo.png"), show_label=False, height=100, container=False)
    gr.Markdown("# SKA Single Digit Explorer")
    gr.Markdown("Explore the 4D entropy state trajectory for a single digit across different architectures.")

    with gr.Row():
        with gr.Column(scale=1):
            digit_selector = gr.Radio(
                choices=[str(d) for d in range(10)],
                value="0",
                label="Select Digit"
            )
            n1_input = gr.Slider(8, 512, value=256, step=8, label="Layer 1 — neurons")
            n2_input = gr.Slider(8, 512, value=128, step=8, label="Layer 2 — neurons")
            n3_input = gr.Slider(8, 256, value=64,  step=8, label="Layer 3 — neurons")
            n4_input = gr.Slider(2, 64,  value=10,  step=1, label="Layer 4 — neurons")
            k_slider = gr.Slider(1, 200, value=50, step=1, label="K (forward steps)")
            tau_slider = gr.Slider(0.1, 0.75, value=0.5, step=0.01, label="Learning budget τ (τ = η.K)")
            samples_slider = gr.Slider(1, 100, value=100, step=1, label="Samples")
            seed_slider = gr.Slider(0, 99, value=0, step=1, label="Data seed")
            run_btn = gr.Button("Run & Archive", variant="primary")
            clear_btn = gr.Button("Clear History", variant="stop")

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
            gr.Markdown("Select a digit and explore how its 4D entropy state trajectory changes with architecture. Each digit has a unique geometric fingerprint — compare architectures for the same digit to probe the entropy manifold.")

        with gr.Column(scale=2):
            plot_current = gr.Plot(label="Current Run: Normalized Entropy Trajectory")
            plot_comparison = gr.Image(label="4D Entropy State Trajectory")

    history_state = gr.State([])

    run_btn.click(
        fn=run_ska,
        inputs=[digit_selector, n1_input, n2_input, n3_input, n4_input, k_slider, tau_slider, samples_slider, seed_slider, history_state],
        outputs=[plot_current, plot_comparison, history_state],
    )
    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[plot_comparison, history_state],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=[BASE_DIR])