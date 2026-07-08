import numpy as np

from forge.eval.classification import evaluate_classifier


def test_perfect_classifier():
    y = np.array([0, 1, 0, 1, 1])
    m = evaluate_classifier(y, y)
    assert m.accuracy == 1.0
    assert m.f1 == 1.0
    assert m.support == 5


def test_auc_computed_with_probs():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.8, 0.9])
    m = evaluate_classifier(y_true, y_pred, y_prob=y_prob)
    assert m.auc_roc is not None
    assert m.auc_roc == 1.0


def test_auc_none_without_probs():
    y = np.array([0, 1, 0, 1])
    m = evaluate_classifier(y, y)
    assert m.auc_roc is None


def test_to_dict_keys():
    y = np.array([0, 1, 0, 1])
    d = evaluate_classifier(y, y).to_dict()
    assert set(d.keys()) == {"accuracy", "precision", "recall", "f1", "auc_roc", "support"}


def test_str_output():
    y = np.array([0, 1, 0, 1])
    s = str(evaluate_classifier(y, y))
    assert "Accuracy" in s
    assert "F1" in s
