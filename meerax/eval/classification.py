from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc_roc: float | None
    support: int

    def __str__(self) -> str:
        lines = [
            f"Accuracy : {self.accuracy:.4f}",
            f"Precision: {self.precision:.4f}",
            f"Recall   : {self.recall:.4f}",
            f"F1       : {self.f1:.4f}",
        ]
        if self.auc_roc is not None:
            lines.append(f"AUC-ROC  : {self.auc_roc:.4f}")
        lines.append(f"Support  : {self.support}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, float | int | None]:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "auc_roc": self.auc_roc,
            "support": self.support,
        }


def evaluate_classifier(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray | None = None,
    average: str = "binary",
) -> ClassificationMetrics:
    """Compute a standard classification metric bundle.

    Args:
        y_true:  Ground-truth labels.
        y_pred:  Hard predictions.
        y_prob:  Probability estimates for AUC-ROC (1-D for binary, 2-D for multiclass).
        average: Averaging strategy passed to sklearn ('binary', 'macro', 'weighted').
    """
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    auc: float | None = None
    if y_prob is not None:
        try:
            prob = y_prob if y_prob.ndim == 1 else y_prob[:, 1]
            auc = float(roc_auc_score(y_true, prob))
        except ValueError:
            pass

    return ClassificationMetrics(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        recall=float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        f1=float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        auc_roc=auc,
        support=int(len(y_true)),
    )
