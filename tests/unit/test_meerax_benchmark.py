import json

import numpy as np
import pytest

from benchmarks.meerax_benchmark import (
    bench_evaluate_classifier,
    bench_evaluate_forecast,
    bench_load_csv,
    bench_report_build,
    bench_stratified_split,
    bench_time_split,
    record_results,
    run_all,
)


@pytest.fixture
def tiny_benchmark(monkeypatch):
    monkeypatch.setattr("benchmarks.meerax_benchmark.ROW_COUNTS", [50])
    monkeypatch.setattr("benchmarks.meerax_benchmark.SECTION_COUNTS", [1])
    monkeypatch.setattr("benchmarks.meerax_benchmark.N_TRIALS", 1)


@pytest.mark.parametrize(
    "bench_fn",
    [
        bench_load_csv,
        bench_stratified_split,
        bench_time_split,
        bench_evaluate_classifier,
        bench_evaluate_forecast,
    ],
)
def test_bench_functions_return_one_timing_per_row_count(tiny_benchmark, bench_fn):
    rng = np.random.default_rng(0)
    results = bench_fn(rng)
    assert results.keys() == {"50"}
    assert all(isinstance(v, float) and v >= 0 for v in results.values())


def test_bench_report_build_returns_one_timing_per_section_count(tiny_benchmark):
    rng = np.random.default_rng(0)
    results = bench_report_build(rng)
    assert results.keys() == {"1"}
    assert all(isinstance(v, float) and v >= 0 for v in results.values())


def test_run_all_covers_every_benchmark(tiny_benchmark):
    results = run_all()
    assert set(results.keys()) == {
        "load_csv_seconds",
        "stratified_split_seconds",
        "time_split_seconds",
        "evaluate_classifier_seconds",
        "evaluate_forecast_seconds",
        "report_build_seconds",
    }


def test_record_results_appends_one_json_line(tiny_benchmark, tmp_path, monkeypatch):
    history_path = tmp_path / "history.jsonl"
    monkeypatch.setattr("benchmarks.meerax_benchmark.HISTORY_PATH", history_path)

    record_results(run_all())
    record_results(run_all())

    lines = history_path.read_text().strip().splitlines()
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert {"meerax_version", "timestamp", "python_version", "platform", "results"} <= entry.keys()
