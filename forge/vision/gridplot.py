from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from forge.viz.theme import apply_forge_theme

if TYPE_CHECKING:
    import torch


def _to_display_array(image: torch.Tensor | np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray):
        # Lazy: importing torch/torchvision at module scope forces their CUDA/triton
        # native libraries to load, which segfaults when a caller also has TensorFlow
        # loaded in the same process (e.g. a TF-based project using only the numpy path).
        import torch

        from forge.vision.dataset import denormalize

        if isinstance(image, torch.Tensor):
            return denormalize(image).permute(1, 2, 0).detach().cpu().numpy()
    array = np.clip((np.asarray(image, dtype=np.float32) + 1.0) / 2.0, 0.0, 1.0)
    if array.ndim == 3 and array.shape[-1] == 1:
        array = array[..., 0]
    return array


def plot_translation_grid(rows: list[tuple[str, torch.Tensor | np.ndarray]]) -> plt.Figure:
    """Plot a row of labeled images side by side.

    Each item is (label, image), where image is either:
    - a torch.Tensor, channels-first (3, H, W), in [-1, 1]
    - a np.ndarray, channels-last (H, W, C) or (H, W), in [-1, 1]
    """
    apply_forge_theme()
    fig, axes = plt.subplots(1, len(rows), figsize=(4 * len(rows), 4))
    if len(rows) == 1:
        axes = [axes]
    for ax, (label, image) in zip(axes, rows, strict=True):
        ax.imshow(_to_display_array(image))
        ax.set_title(label)
        ax.axis("off")
    fig.tight_layout()
    return fig
