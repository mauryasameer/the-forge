import matplotlib.pyplot as plt
import numpy as np

from meerax.viz.classification import plot_confusion_matrix, plot_roc_curve


def test_plot_confusion_matrix_returns_figure():
    cm = np.array([[50, 10], [5, 35]])
    fig = plot_confusion_matrix(cm, labels=["neg", "pos"])

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2  # plot axis + colorbar axis
    assert fig.axes[0].get_title() == "Confusion Matrix"


def test_plot_confusion_matrix_uses_provided_axis():
    cm = np.array([[10, 2], [1, 20]])
    fig, ax = plt.subplots()

    result = plot_confusion_matrix(cm, ax=ax, title="Custom")

    assert result is fig
    assert ax.get_title() == "Custom"


def test_plot_roc_curve_returns_figure():
    fpr = np.array([0.0, 0.1, 0.5, 1.0])
    tpr = np.array([0.0, 0.4, 0.8, 1.0])

    fig = plot_roc_curve(fpr, tpr, auc=0.87)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    assert fig.axes[0].get_title() == "ROC Curve"


def test_plot_roc_curve_uses_provided_axis():
    fpr = np.array([0.0, 1.0])
    tpr = np.array([0.0, 1.0])
    fig, ax = plt.subplots()

    result = plot_roc_curve(fpr, tpr, auc=0.5, ax=ax, title="Custom ROC")

    assert result is fig
    assert ax.get_title() == "Custom ROC"
