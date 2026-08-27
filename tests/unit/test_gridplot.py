import subprocess
import sys

import matplotlib.pyplot as plt
import numpy as np
import torch

from meerax.vision.gridplot import plot_translation_grid


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


def test_plot_translation_grid_accepts_numpy_rgb():
    rows = [("input", np.zeros((8, 8, 3), dtype=np.float32))]
    fig = plot_translation_grid(rows)

    assert len(fig.axes) == 1
    image = fig.axes[0].images[0].get_array()
    assert image.shape == (8, 8, 3)
    assert image.min() >= 0.0 and image.max() <= 1.0


def test_plot_translation_grid_accepts_numpy_grayscale_squeezes_channel():
    rows = [("input", np.ones((8, 8, 1), dtype=np.float32))]
    fig = plot_translation_grid(rows)

    image = fig.axes[0].images[0].get_array()
    assert image.shape == (8, 8)


def test_plot_translation_grid_accepts_mixed_torch_and_numpy_rows():
    rows = [
        ("torch", torch.zeros(3, 8, 8)),
        ("numpy", np.zeros((8, 8, 3), dtype=np.float32)),
    ]
    fig = plot_translation_grid(rows)
    assert len(fig.axes) == 2


def test_numpy_only_usage_does_not_import_torch():
    script = (
        "import sys\n"
        "import numpy as np\n"
        "from meerax.vision.gridplot import plot_translation_grid\n"
        "plot_translation_grid([('a', np.zeros((4, 4, 1), dtype=np.float32))])\n"
        "assert 'torch' not in sys.modules, 'torch was imported for a numpy-only call'\n"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
