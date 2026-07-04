# SKA Lagrangian Explorer - Gradio App
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
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

        self.frobenius_history = [[] for _ in range(len(layer_sizes))]
        self.knowledge_flow_history = [[] for _ in range(len(layer_sizes))]
        self.lagrangian_history = [[] for _ in range(len(layer_sizes))]

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
                Phi = delta_Z / learning_rate
                phi_norm = torch.norm(delta_Z, p='fro') / learning_rate
                self.knowledge_flow_history[l].append(phi_norm.item())
                # Lagrangian: L = -Σ z · D'(z) · Φ
                D_prime = self.D[l] * (1 - self.D[l])
                L = -torch.sum(self.Z[l] * D_prime * Phi).item()
                self.lagrangian_history[l].append(L)

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
            self.lagrangian_history[l] = []


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


def make_layer_fig(l, z_plot, phi_plot, lag_plot, min_len):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    sc = ax.scatter(z_plot, phi_plot, lag_plot,
                    c=range(min_len), cmap='viridis', s=50, alpha=0.7)
    cbar = fig.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label('Step Index K')

    try:
        from scipy.interpolate import griddata
        xi = np.linspace(min(z_plot), max(z_plot), 20)
        yi = np.linspace(min(phi_plot), max(phi_plot), 20)
        xi, yi = np.meshgrid(xi, yi)
        zi = griddata((z_plot, phi_plot), lag_plot, (xi, yi), method='cubic')
        ax.plot_surface(xi, yi, zi, cmap='viridis', alpha=0.5,
                        linewidth=0, antialiased=True)
    except Exception:
        pass

    ax.plot(z_plot, phi_plot, lag_plot, 'k-', alpha=0.3)

    ax.set_xlabel('Frobenius Norm of Knowledge Tensor')
    ax.set_ylabel('Frobenius Norm of Knowledge Flow')
    ax.set_zlabel('Lagrangian Value')
    ax.set_title(f'Layer {l+1}: Lagrangian vs z  and \u017c Magnitudes')
    ax.view_init(elev=10, azim=60)
    fig.tight_layout()
    return fig


def run_lagrangian(n1, n2, n3, n4, K, tau, samples_per_class, data_seed):
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

    figs = []
    for l in range(len(layer_sizes)):
        z_norm = model.frobenius_history[l]
        phi = model.knowledge_flow_history[l]
        lag = model.lagrangian_history[l]
        frob = z_norm[1:len(phi) + 1]
        min_len = min(len(phi), len(frob), len(lag))
        if min_len < 2:
            fig = plt.figure(figsize=(10, 8))
            fig.text(0.5, 0.5, f'Layer {l+1}: Not enough data',
                     ha='center', va='center', fontsize=14)
            figs.append(fig)
            continue
        z_plot = np.array(frob[:min_len])
        phi_plot = np.array(phi[:min_len])
        lag_plot = np.array(lag[:min_len])
        figs.append(make_layer_fig(l, z_plot, phi_plot, lag_plot, min_len))

    return figs[0], figs[1], figs[2], figs[3]


with gr.Blocks(title="SKA Lagrangian Explorer") as demo:
    gr.Image(os.path.join(BASE_DIR, "logo.png"), show_label=False, height=100, container=False)
    gr.Markdown("# SKA Lagrangian Explorer")
    gr.Markdown("Visualize the Lagrangian trajectory of each layer in the 3D space: knowledge magnitude, knowledge flow, and Lagrangian value.")

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
            run_btn = gr.Button("Run Lagrangian", variant="primary")

            gr.Markdown("---")
            gr.Markdown("### Definitions")
            gr.Markdown(
                "| Quantity | Definition |\n|---|---|\n"
                "| **\u2112(z, \u017c, t)** | \u2212z \u00b7 \u03c3(z)(1\u2212\u03c3(z)) \u00b7 \u017c |\n"
                "| **H** | (1/ln2) \u00b7 \u222b \u2112 dt |"
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
            gr.Markdown(
                "Each layer traces a 3D trajectory in knowledge space — "
                "knowledge magnitude on the x-axis, knowledge flow rate on the y-axis, and the Lagrangian value on the z-axis. "
                "The color encodes the step index K (viridis: dark = early, bright = late). "
                "The surface is interpolated from the trajectory points and reveals the Lagrangian landscape."
            )

            gr.Markdown("---")
            gr.Markdown("### Important Note")
            gr.Markdown(
                "The layered SKA Neural Network presented here is a discrete approximation (a \u201cshadow\u201d) of the underlying continuous "
                "[Riemannian Neural Field (RNF)](https://doi.org/10.13140/RG.2.2.35650.24001).\n\n"
                "It is provided for educational purposes only to illustrate the core mechanism of local entropy reduction through decision shifts \u0394D.\n\n"
                "The true SKA dynamics and all its deeper properties live in the continuous RNF. "
                "The layered discretization is useful for teaching and rapid experimentation, but it is not the complete theory.\n\n"
                "This is also true for classical neural networks."
            )

        with gr.Column(scale=2):
            plot_l1 = gr.Plot(label="Layer 1 — Lagrangian 3D")
            plot_l2 = gr.Plot(label="Layer 2 — Lagrangian 3D")
            plot_l3 = gr.Plot(label="Layer 3 — Lagrangian 3D")
            plot_l4 = gr.Plot(label="Layer 4 — Lagrangian 3D")

    run_btn.click(
        fn=run_lagrangian,
        inputs=[n1_input, n2_input, n3_input, n4_input, k_slider, tau_slider, samples_slider, seed_slider],
        outputs=[plot_l1, plot_l2, plot_l3, plot_l4],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=[BASE_DIR])
