import numpy as np
from sklearn.metrics import roc_curve

from meerax.eval import evaluate_classifier
from meerax.report import ReportBuilder, ReportSection
from meerax.viz import apply_meerax_theme
from meerax.viz.classification import plot_confusion_matrix, plot_roc_curve


def test_classification_eval_viz_report_pipeline(tmp_path):
    """The README's own Quick Start example, exercised end-to-end for real."""
    apply_meerax_theme()
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 2, size=200)
    y_prob = np.clip(y_true + rng.normal(0, 0.4, size=200), 0, 1)
    y_pred = (y_prob > 0.5).astype(int)

    metrics = evaluate_classifier(y_true, y_pred, y_prob=y_prob)
    assert 0.0 <= metrics.accuracy <= 1.0
    assert metrics.auc_roc is not None

    cm = np.array(
        [
            [int(((y_true == 0) & (y_pred == 0)).sum()), int(((y_true == 0) & (y_pred == 1)).sum())],
            [int(((y_true == 1) & (y_pred == 0)).sum()), int(((y_true == 1) & (y_pred == 1)).sum())],
        ]
    )
    cm_fig = plot_confusion_matrix(cm, labels=["neg", "pos"])
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_fig = plot_roc_curve(fpr, tpr, auc=metrics.auc_roc)

    rb = ReportBuilder("Integration Test Report", subtitle="eval -> viz -> report pipeline")
    rb.add_section(
        ReportSection(
            title="Performance",
            metrics=metrics.to_dict(),
            figures=[cm_fig, roc_fig],
            content="End-to-end pipeline check.",
        )
    )
    output = tmp_path / "report.html"
    rb.save(output)

    assert output.exists()
    html = output.read_text()
    assert "Integration Test Report" in html
    assert "Performance" in html
    for key in metrics.to_dict():
        assert key in html
    assert html.count("<img") == 2
