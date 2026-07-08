from pathlib import Path

import pytest

from forge.data.loader import load_csv


def test_load_csv_basic(tmp_path: Path):
    csv = tmp_path / "test.csv"
    csv.write_text("a,b,c\n1,2,3\n4,5,6\n")
    df = load_csv(csv)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b", "c"]


def test_load_csv_required_columns(tmp_path: Path):
    csv = tmp_path / "test.csv"
    csv.write_text("a,b\n1,2\n")
    df = load_csv(csv, required_columns=["a", "b"])
    assert "a" in df.columns


def test_load_csv_missing_column_raises(tmp_path: Path):
    csv = tmp_path / "test.csv"
    csv.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError, match="Missing required columns"):
        load_csv(csv, required_columns=["a", "b", "missing_col"])


def test_load_csv_not_found():
    with pytest.raises(FileNotFoundError):
        load_csv("/nonexistent/path/data.csv")
