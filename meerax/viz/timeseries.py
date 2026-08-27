from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from meerax.viz.theme import MEERAX_ACCENT, MEERAX_CYBER


def plot_forecast(
    actual: np.ndarray,
    predicted: np.ndarray,
    title: str = "Forecast vs Actual",
    ax: plt.Axes | None = None,
) -> plt.Figure:
    fig, ax = (ax.get_figure(), ax) if ax is not None else plt.subplots(figsize=(10, 4))
    ax.plot(actual, color=MEERAX_ACCENT, label="Actual", lw=1.5)
    ax.plot(predicted, color=MEERAX_CYBER, label="Predicted", lw=1.5, linestyle="--")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_decomposition(
    series: np.ndarray,
    period: int = 12,
    title: str = "Seasonal Decomposition",
) -> plt.Figure:
    from statsmodels.tsa.seasonal import seasonal_decompose

    result = seasonal_decompose(series, model="additive", period=period)
    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    components = [result.observed, result.trend, result.seasonal, result.resid]
    labels = ["Observed", "Trend", "Seasonal", "Residual"]
    for ax, data, label in zip(axes, components, labels, strict=False):
        ax.plot(data, color=MEERAX_CYBER, lw=1.2)
        ax.set_ylabel(label, fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    return fig
