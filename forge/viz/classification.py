from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from forge.viz.theme import FORGE_ACCENT, FORGE_CYBER


def plot_confusion_matrix(
    cm: np.ndarray,
    labels: list[str] | None = None,
    title: str = "Confusion Matrix",
    ax: plt.Axes | None = None,
) -> plt.Figure:
    fig, ax = (ax.get_figure(), ax) if ax is not None else plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="YlGnBu", aspect="auto")
    ax.set_title(title)
    ticks = range(cm.shape[0])
    ax.set_xticks(list(ticks))
    ax.set_yticks(list(ticks))
    if labels:
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=10)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    return fig


def plot_roc_curve(
    fpr: np.ndarray,
    tpr: np.ndarray,
    auc: float,
    title: str = "ROC Curve",
    ax: plt.Axes | None = None,
) -> plt.Figure:
    fig, ax = (ax.get_figure(), ax) if ax is not None else plt.subplots(figsize=(5, 4))
    ax.plot(fpr, tpr, color=FORGE_CYBER, lw=2, label=f"AUC = {auc:.3f}")
    ax.plot([0, 1], [0, 1], color=FORGE_ACCENT, lw=1, linestyle="--", label="Random")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right")
    fig.tight_layout()
    return fig
