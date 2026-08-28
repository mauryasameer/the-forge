from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv(
    path: str | Path,
    required_columns: list[str] | None = None,
    dtype: Any = None,
) -> pd.DataFrame:
    """Load a CSV with optional schema validation.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if required_columns are absent from the file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    df = pd.read_csv(path, dtype=dtype)
    logger.info("Loaded %d rows × %d cols from %s", len(df), len(df.columns), path.name)
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def load_parquet(
    path: str | Path,
    required_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Load a Parquet file with optional schema validation."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    df = pd.read_parquet(path)
    logger.info("Loaded %d rows × %d cols from %s", len(df), len(df.columns), path.name)
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df
