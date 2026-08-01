import matplotlib.pyplot as plt
import torch

from forge.vision.gridplot import plot_translation_grid


def test_plot_translation_grid_returns_figure_with_one_axis_per_row():
    rows = [("input", torch.zeros(3, 8, 8)), ("translated", torch.ones(3, 8, 8))]
    fig = plot_translation_grid(rows)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    assert fig.axes[0].get_title() == "input"
    assert fig.axes[1].get_title() == "translated"


def test_plot_translation_grid_handles_single_row():
    fig = plot_translation_grid([("only", torch.zeros(3, 8, 8))])
    assert len(fig.axes) == 1
