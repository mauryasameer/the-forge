import matplotlib.pyplot as plt
import numpy as np

from meerax.viz.timeseries import plot_decomposition, plot_forecast


def test_plot_forecast_returns_figure():
    actual = np.array([1.0, 2.0, 3.0, 4.0])
    predicted = np.array([1.1, 1.9, 3.2, 3.8])

    fig = plot_forecast(actual, predicted)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    assert fig.axes[0].get_title() == "Forecast vs Actual"


def test_plot_forecast_uses_provided_axis():
    actual = np.array([1.0, 2.0])
    predicted = np.array([1.0, 2.0])
    fig, ax = plt.subplots()

    result = plot_forecast(actual, predicted, ax=ax, title="Custom")

    assert result is fig
    assert ax.get_title() == "Custom"


def test_plot_decomposition_returns_figure_with_four_axes():
    rng = np.random.default_rng(0)
    t = np.arange(48)
    series = 10 + 0.1 * t + 3 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 0.5, size=48)

    fig = plot_decomposition(series, period=12)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 4
    assert fig._suptitle.get_text() == "Seasonal Decomposition"
