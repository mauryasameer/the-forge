from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class TimeSeriesMetrics:
    rmse: float
    mae: float
    mape: float | None
    smape: float

    def __str__(self) -> str:
        lines = [
            f"RMSE : {self.rmse:.4f}",
            f"MAE  : {self.mae:.4f}",
        ]
        if self.mape is not None:
            lines.append(f"MAPE : {self.mape:.4f}%")
        lines.append(f"SMAPE: {self.smape:.4f}%")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, float | None]:
        return {"rmse": self.rmse, "mae": self.mae, "mape": self.mape, "smape": self.smape}


def evaluate_forecast(y_true: np.ndarray[Any, Any], y_pred: np.ndarray[Any, Any]) -> TimeSeriesMetrics:
    """Standard regression metrics for time-series forecasts."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))

    nonzero = y_true != 0
    mape = (
        float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100)
        if nonzero.any()
        else None
    )

    denom = (np.abs(y_true) + np.abs(y_pred)) / 2
    safe = denom != 0
    smape = float(np.mean(np.abs(y_true[safe] - y_pred[safe]) / denom[safe]) * 100) if safe.any() else 0.0

    return TimeSeriesMetrics(rmse=rmse, mae=mae, mape=mape, smape=smape)


def adf_stationarity(series: np.ndarray[Any, Any]) -> dict[str, float | bool]:
    """Augmented Dickey-Fuller test. Returns p-value and stationarity decision."""
    from statsmodels.tsa.stattools import adfuller

    result = adfuller(series, autolag="AIC", result_object=False)
    return {
        "adf_stat": float(result[0]),
        "p_value": float(result[1]),
        "is_stationary": bool(result[1] < 0.05),
        "critical_1pct": float(result[4]["1%"]),
        "critical_5pct": float(result[4]["5%"]),
    }
