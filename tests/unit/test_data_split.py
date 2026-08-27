import pandas as pd
import pytest

from meerax.data.split import stratified_split, time_split


def _make_df(n: int = 100) -> pd.DataFrame:
    return pd.DataFrame({"x": range(n), "label": [i % 2 for i in range(n)]})


def test_stratified_split_sizes():
    df = _make_df(100)
    train, val, test = stratified_split(df, "label", train_ratio=0.7, val_ratio=0.15)
    assert len(train) + len(val) + len(test) == 100
    assert abs(len(train) - 70) <= 2


def test_stratified_split_invalid_ratio():
    df = _make_df(100)
    with pytest.raises(ValueError):
        stratified_split(df, "label", train_ratio=0.8, val_ratio=0.3)


def test_time_split_order():
    df = _make_df(100)
    train, val, test = time_split(df, train_ratio=0.8, val_ratio=0.1)
    assert train["x"].iloc[-1] < val["x"].iloc[0]
    assert val["x"].iloc[-1] < test["x"].iloc[0]


def test_time_split_no_overlap():
    df = _make_df(100)
    train, val, test = time_split(df)
    assert set(train.index).isdisjoint(val.index)
    assert set(val.index).isdisjoint(test.index)
