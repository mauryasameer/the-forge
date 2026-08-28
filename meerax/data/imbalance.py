from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def smote_oversample(
    X: np.ndarray[Any, Any],
    y: np.ndarray[Any, Any],
    random_state: int = 42,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """SMOTE oversampling. Requires imbalanced-learn."""
    try:
        from imblearn.over_sampling import SMOTE
    except ImportError as exc:
        raise ImportError("Install imbalanced-learn: pip install imbalanced-learn") from exc
    X_res, y_res = SMOTE(random_state=random_state).fit_resample(X, y)
    logger.info("SMOTE: %d → %d samples", len(y), len(y_res))
    return X_res, y_res


def random_undersample(
    X: np.ndarray[Any, Any],
    y: np.ndarray[Any, Any],
    random_state: int = 42,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Random majority-class undersampling. Requires imbalanced-learn."""
    try:
        from imblearn.under_sampling import RandomUnderSampler
    except ImportError as exc:
        raise ImportError("Install imbalanced-learn: pip install imbalanced-learn") from exc
    X_res, y_res = RandomUnderSampler(random_state=random_state).fit_resample(X, y)
    logger.info("RandomUnderSampler: %d → %d samples", len(y), len(y_res))
    return X_res, y_res
