import numpy as np

from meerax.data.imbalance import random_undersample, smote_oversample


def _make_imbalanced(majority: int = 50, minority: int = 10, n_features: int = 4):
    rng = np.random.default_rng(0)
    X_majority = rng.normal(loc=0.0, scale=1.0, size=(majority, n_features))
    X_minority = rng.normal(loc=5.0, scale=1.0, size=(minority, n_features))
    X = np.vstack([X_majority, X_minority])
    y = np.array([0] * majority + [1] * minority)
    return X, y


def test_smote_oversample_balances_minority_class():
    X, y = _make_imbalanced(majority=50, minority=10)

    X_res, y_res = smote_oversample(X, y)

    counts = dict(zip(*np.unique(y_res, return_counts=True), strict=True))
    assert counts[0] == counts[1] == 50
    assert X_res.shape[0] == len(y_res)


def test_random_undersample_balances_majority_class():
    X, y = _make_imbalanced(majority=50, minority=10)

    X_res, y_res = random_undersample(X, y)

    counts = dict(zip(*np.unique(y_res, return_counts=True), strict=True))
    assert counts[0] == counts[1] == 10
    assert X_res.shape[0] == len(y_res)
