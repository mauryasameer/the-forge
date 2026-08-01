from __future__ import annotations

import matplotlib.pyplot as plt
import torch

from forge.vision.dataset import denormalize
from forge.viz.theme import apply_forge_theme


def plot_translation_grid(rows: list[tuple[str, torch.Tensor]]) -> plt.Figure:
    """Plot a row of labeled images side by side.

    Each item is (label, tensor), where tensor is a (3, H, W) image in [-1, 1].
    """
    apply_forge_theme()
    fig, axes = plt.subplots(1, len(rows), figsize=(4 * len(rows), 4))
    if len(rows) == 1:
        axes = [axes]
    for ax, (label, tensor) in zip(axes, rows, strict=True):
        image = denormalize(tensor).permute(1, 2, 0).detach().cpu().numpy()
        ax.imshow(image)
        ax.set_title(label)
        ax.axis("off")
    fig.tight_layout()
    return fig
