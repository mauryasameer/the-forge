from __future__ import annotations

import pandas as pd


def stratified_split(
    df: pd.DataFrame,
    target_col: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stratified train / val / test split preserving class balance."""
    from sklearn.model_selection import train_test_split

    test_ratio = 1.0 - train_ratio - val_ratio
    if test_ratio <= 0:
        raise ValueError("train_ratio + val_ratio must be < 1.0")

    train, temp = train_test_split(
        df,
        test_size=val_ratio + test_ratio,
        stratify=df[target_col],
        random_state=random_state,
    )
    val, test = train_test_split(
        temp,
        test_size=test_ratio / (val_ratio + test_ratio),
        stratify=temp[target_col],
        random_state=random_state,
    )
    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def time_split(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chronological train / val / test split — no shuffling."""
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    return (
        df.iloc[:train_end].copy(),
        df.iloc[train_end:val_end].copy(),
        df.iloc[val_end:].copy(),
    )
