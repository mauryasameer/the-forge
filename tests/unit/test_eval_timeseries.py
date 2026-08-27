import numpy as np
import pytest

from meerax.eval.timeseries import evaluate_forecast


def test_perfect_forecast():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    m = evaluate_forecast(y, y)
    assert m.rmse == 0.0
    assert m.mae == 0.0
    assert m.smape == 0.0


def test_rmse_calculation():
    y_true = np.array([1.0, 2.0])
    y_pred = np.array([2.0, 3.0])
    m = evaluate_forecast(y_true, y_pred)
    assert m.rmse == pytest.approx(1.0)
    assert m.mae == pytest.approx(1.0)


def test_mape_none_for_zero_actuals():
    y_true = np.array([0.0, 0.0])
    y_pred = np.array([1.0, 2.0])
    m = evaluate_forecast(y_true, y_pred)
    assert m.mape is None


def test_to_dict_keys():
    y = np.ones(5)
    d = evaluate_forecast(y, y).to_dict()
    assert set(d.keys()) == {"rmse", "mae", "mape", "smape"}
