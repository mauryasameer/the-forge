"""
meerax_benchmark.py
Benchmarks meerax's own core operations — CSV loading, splitting, classification/
timeseries eval metrics, and HTML report generation — across representative sizes.

Run:    python benchmarks/meerax_benchmark.py
Append: python benchmarks/meerax_benchmark.py --record

--record appends one JSON line per run to benchmarks/results/history.jsonl, keyed by
the installed meerax version, so performance can be compared release to release. Run
it (with --record) as part of cutting a release, alongside `meerax bump`, and commit
the updated history.jsonl in the same commit.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import meerax
from meerax.data.loader import load_csv
from meerax.data.split import stratified_split, time_split
from meerax.eval.classification import evaluate_classifier
from meerax.eval.timeseries import evaluate_forecast
from meerax.report.builder import ReportBuilder, ReportSection

ROW_COUNTS = [1_000, 10_000, 100_000]
SECTION_COUNTS = [1, 10, 50]
N_TRIALS = 3

HISTORY_PATH = Path(__file__).parent / "results" / "history.jsonl"


def _time(fn: Any, *args: Any, **kwargs: Any) -> float:
    times = []
    for _ in range(N_TRIALS):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)
    return float(np.median(times))


def _make_classification_df(n: int, rng: np.random.Generator) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "feature_a": rng.standard_normal(n),
            "feature_b": rng.standard_normal(n),
            "label": rng.integers(0, 2, n),
        }
    )


def bench_load_csv(rng: np.random.Generator) -> dict[str, float]:
    results = {}
    for n in ROW_COUNTS:
        df = _make_classification_df(n, rng)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            df.to_csv(path, index=False)
            results[str(n)] = _time(load_csv, path)
    return results


def bench_stratified_split(rng: np.random.Generator) -> dict[str, float]:
    results = {}
    for n in ROW_COUNTS:
        df = _make_classification_df(n, rng)
        results[str(n)] = _time(stratified_split, df, "label")
    return results


def bench_time_split(rng: np.random.Generator) -> dict[str, float]:
    results = {}
    for n in ROW_COUNTS:
        df = _make_classification_df(n, rng)
        results[str(n)] = _time(time_split, df)
    return results


def bench_evaluate_classifier(rng: np.random.Generator) -> dict[str, float]:
    results = {}
    for n in ROW_COUNTS:
        y_true = rng.integers(0, 2, n)
        y_pred = rng.integers(0, 2, n)
        y_prob = rng.uniform(0, 1, n)
        results[str(n)] = _time(evaluate_classifier, y_true, y_pred, y_prob)
    return results


def bench_evaluate_forecast(rng: np.random.Generator) -> dict[str, float]:
    results = {}
    for n in ROW_COUNTS:
        y_true = rng.standard_normal(n).cumsum()
        y_pred = y_true + rng.standard_normal(n)
        results[str(n)] = _time(evaluate_forecast, y_true, y_pred)
    return results


def bench_report_build(rng: np.random.Generator) -> dict[str, float]:
    # rng is unused here (report content is static) but kept so every bench_fn shares
    # the same bench_fn(rng) signature that run_all() calls uniformly.
    results = {}
    for n_sections in SECTION_COUNTS:

        def build_and_save(n_sections: int = n_sections) -> None:
            rb = ReportBuilder("Benchmark Report", subtitle="v0.0.0")
            for i in range(n_sections):
                rb.add_section(
                    ReportSection(
                        title=f"Section {i}",
                        content="Lorem ipsum benchmark content.",
                        metrics={"accuracy": 0.9, "f1": 0.85},
                    )
                )
            with tempfile.TemporaryDirectory() as tmp:
                rb.save(Path(tmp) / "report.html")

        results[str(n_sections)] = _time(build_and_save)
    return results


def run_all() -> dict[str, dict[str, float]]:
    rng = np.random.default_rng(42)
    return {
        "load_csv_seconds": bench_load_csv(rng),
        "stratified_split_seconds": bench_stratified_split(rng),
        "time_split_seconds": bench_time_split(rng),
        "evaluate_classifier_seconds": bench_evaluate_classifier(rng),
        "evaluate_forecast_seconds": bench_evaluate_forecast(rng),
        "report_build_seconds": bench_report_build(rng),
    }


def print_results(results: dict[str, dict[str, float]]) -> None:
    for name, sizes in results.items():
        print(f"\n{name}")
        print(f"{'size':>10}  {'median (s)':>12}")
        for size, seconds in sizes.items():
            print(f"{size:>10}  {seconds:>12.4f}")


def record_results(results: dict[str, dict[str, float]]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "meerax_version": meerax.__version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "results": results,
    }
    with HISTORY_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"\nAppended to {HISTORY_PATH}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record",
        action="store_true",
        help="Append this run's results to benchmarks/results/history.jsonl",
    )
    args = parser.parse_args(argv)

    print(f"meerax {meerax.__version__} — benchmarking core operations\n")
    results = run_all()
    print_results(results)
    if args.record:
        record_results(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
