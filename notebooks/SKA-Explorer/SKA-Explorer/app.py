# SKA Interactive Gradio App
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
        self.entropy = [None] * len(layer_sizes)

        self.entropy_history = [[] for _ in range(len(layer_sizes))]
        self.cosine_history = [[] for _ in range(len(layer_sizes))]
        self.output_history = []

        self.frobenius_history = [[] for _ in range(len(layer_sizes))]
        self.weight_frobenius_history = [[] for _ in range(len(layer_sizes))]
        self.net_history = [[] for _ in range(len(layer_sizes))]
        self.tensor_net_total = [0.0] * len(layer_sizes)

    def forward(self, x):
        batch_size = x.shape[0]
        x = x.view(batch_size, -1)
        for l in range(len(self.layer_sizes)):
            z = torch.mm(x, self.weights[l]) + self.biases[l]
            frobenius_norm = torch.norm(z, p='fro')
            self.frobenius_history[l].append(frobenius_norm.item())
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
                    cos_theta = dot_product / (z_norm * delta_d_norm)
                    self.cosine_history[l].append(cos_theta.item())
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


def get_mnist_subset(samples_per_class, data_seed=0):
    """Select N samples per class from MNIST."""
    images_list = []
    labels_list = []
    targets = mnist_dataset.targets.numpy()
    rng = np.random.RandomState(data_seed)
    for digit in range(10):
        all_indices = np.where(targets == digit)[0]
        rng.shuffle(all_indices)
        indices = all_indices[:samples_per_class]
        for idx in indices:
            img, label = mnist_dataset[idx]
            images_list.append(img)
            labels_list.append(label)
    images = torch.stack(images_list)
    return images


def run_ska(neurons_str, K, tau, samples_per_class, data_seed):
    # Parse layer sizes
    try:
        layer_sizes = [int(x.strip()) for x in neurons_str.split(",")]
    except ValueError:
        return None, None, None

    K = int(K)
    samples_per_class = int(samples_per_class)
    data_seed = int(data_seed)
    learning_rate = tau / K

    # Get data
    inputs = get_mnist_subset(samples_per_class, data_seed)

    # Create model
    torch.manual_seed(42)
    np.random.seed(42)
    model = SKAModel(input_size=784, layer_sizes=layer_sizes, K=K)
    model.initialize_tensors(inputs.size(0))

    # Run SKA
    for k in range(K):
        outputs = model.forward(inputs)
        model.output_history.append(outputs.mean(dim=0).detach().cpu().numpy())
        if k > 0:
            batch_entropy = model.calculate_entropy()
            model.ska_update(inputs, learning_rate)
            for l in range(len(model.layer_sizes)):
                weight_norm = torch.norm(model.weights[l], p='fro')
                model.weight_frobenius_history[l].append(weight_norm.item())
        model.D_prev = [d.clone().detach() if d is not None else None for d in model.D]
        model.Z_prev = [z.clone().detach() if z is not None else None for z in model.Z]

    num_layers = len(layer_sizes)

    # Plot 1: Entropy trajectory
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    for l in range(num_layers):
        ax1.plot(model.entropy_history[l], label=f"Layer {l+1}")
    ax1.set_title('Entropy Evolution Across Layers')
    ax1.set_xlabel('Step Index K')
    ax1.set_ylabel('Entropy')
    ax1.legend()
    ax1.grid(True)
    fig1.tight_layout()

    # Plot 2: Cosine alignment
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    for l in range(num_layers):
        ax2.plot(model.cosine_history[l], label=f"Layer {l+1}")
    ax2.set_title('Cos(θ) Alignment Evolution Across Layers')
    ax2.set_xlabel('Step Index K')
    ax2.set_ylabel('Cos(θ)')
    ax2.legend()
    ax2.grid(True)
    fig2.tight_layout()

    # Plot 3: Output neuron activation
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    output_data = np.array(model.output_history)
    num_neurons = output_data.shape[1]
    for i in range(num_neurons):
        ax3.plot(output_data[:, i], label=f"Neuron {i}")
    ax3.set_title('Output Neuron Activation Evolution')
    ax3.set_xlabel('Step Index K')
    ax3.set_ylabel('Mean Neuron Activation')
    ax3.legend(loc='upper right', bbox_to_anchor=(1.15, 1), fontsize=7)
    ax3.grid(True)
    fig3.tight_layout()

    # Plot 4: Frobenius norm (Z tensor)
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    for l in range(num_layers):
        ax4.plot(model.frobenius_history[l], label=f"Layer {l+1}")
    ax4.set_title('Z Tensor Frobenius Norm Evolution Across Layers')
    ax4.set_xlabel('Step Index K')
    ax4.set_ylabel('Frobenius Norm')
    ax4.legend()
    ax4.grid(True)
    fig4.tight_layout()

    # Plot 5: Entropy vs Frobenius scatter
    fig5, axes5 = plt.subplots(2, (num_layers + 1) // 2, figsize=(12, 8))
    axes5 = axes5.flatten() if num_layers > 1 else [axes5]
    for l in range(num_layers):
        ax = axes5[l]
        entropy_data = model.entropy_history[l]
        frobenius_data = model.frobenius_history[l][1:]
        min_len = min(len(entropy_data), len(frobenius_data))
        if min_len < 2:
            ax.set_title(f"Layer {l+1}: Not enough data")
            continue
        entropy_data = entropy_data[:min_len]
        frobenius_data = frobenius_data[:min_len]
        sc = ax.scatter(frobenius_data, entropy_data, c=range(min_len), cmap='Blues_r', s=50, alpha=0.8)
        ax.plot(frobenius_data, entropy_data, 'k-', alpha=0.3)
        plt.colorbar(sc, ax=ax, label='Step')
        ax.set_xlabel('Frobenius Norm of Z')
        ax.set_ylabel('Entropy')
        ax.set_title(f'Layer {l+1}: Entropy vs. Knowledge Magnitude')
        ax.grid(True, alpha=0.3)
    for l in range(num_layers, len(axes5)):
        axes5[l].set_visible(False)
    fig5.tight_layout()

    return fig1, fig2, fig3, fig4, fig5



with gr.Blocks(title="SKA - Structured Knowledge Accumulation") as demo:
    gr.Image("logo.png", show_label=False, height=100, container=False)
    gr.Markdown("# SKA - Structured Knowledge Accumulation")
    gr.Markdown("Interactive visualization of the SKA forward learning algorithm on MNIST. Adjust architecture, steps K, and learning budget τ to explore entropy dynamics.")

    with gr.Row():
        with gr.Column(scale=1):
            neurons_input = gr.Textbox(label="Layer sizes (comma-separated)", value="256, 128, 64, 10")
            k_slider = gr.Slider(1, 200, value=50, step=1, label="K (forward steps)")
            tau_slider = gr.Slider(0.1, 0.75, value=0.5, step=0.01, label="Learning budget τ (τ = η.K)")
            samples_slider = gr.Slider(1, 100, value=100, step=1, label="Samples per class")
            seed_slider = gr.Slider(0, 99, value=0, step=1, label="Data seed (shuffle samples)")
            run_btn = gr.Button("Run SKA", variant="primary")

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
            gr.Markdown("SKA learns without backpropagation. Each forward pass accumulates knowledge by minimizing entropy layer by layer. Adjust the architecture, learning budget τ, and number of steps K to explore how the entropy trajectory evolves.")


        with gr.Column(scale=2):
            plot_entropy = gr.Plot(label="Entropy Trajectory")
            plot_cosine = gr.Plot(label="Cosine Alignment")
            plot_output = gr.Plot(label="Output Neuron Activation")
            plot_frobenius = gr.Plot(label="Z Tensor Frobenius Norm")
            plot_entropy_vs_frob = gr.Plot(label="Entropy vs Frobenius")

    run_btn.click(
        fn=run_ska,
        inputs=[neurons_input, k_slider, tau_slider, samples_slider, seed_slider],
        outputs=[plot_entropy, plot_cosine, plot_output, plot_frobenius, plot_entropy_vs_frob],
    )

domain = os.environ.get("DOMAIN")
if domain:
    print(f"Public URL (via nginx + SSO): https://gradio.{domain}")

demo.launch(server_name="0.0.0.0", server_port=7860)
