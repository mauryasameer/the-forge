# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-07-09

### Added
- `forge.llm` — Abstract `LLMProvider` interface with Claude, OpenAI, and Ollama implementations
- `forge.llm.prompt` — Lightweight `PromptTemplate` for structured LLM prompts
- `forge.eval.classification` — `evaluate_classifier()` returning F1, AUC-ROC, precision, recall
- `forge.eval.timeseries` — `evaluate_forecast()` returning RMSE, MAE, MAPE, SMAPE; `adf_stationarity()` for stationarity testing
- `forge.eval.text` — `bleu_score()` (corpus BLEU-4) and `rouge_l()` (LCS-based ROUGE-L F1)
- `forge.viz.theme` — `apply_forge_theme()` dark matplotlib/seaborn theme matching portfolio aesthetic
- `forge.viz.classification` — `plot_confusion_matrix()` and `plot_roc_curve()`
- `forge.viz.timeseries` — `plot_forecast()` and `plot_decomposition()`
- `forge.data.loader` — `load_csv()` and `load_parquet()` with schema validation
- `forge.data.split` — `stratified_split()` and `time_split()`
- `forge.data.imbalance` — `smote_oversample()` and `random_undersample()` wrappers
- `forge.report.builder` — `ReportBuilder` / `ReportSection` dark-themed self-contained HTML reports
- `forge.logging` — `setup_logger()` structured logger factory
- 34 unit tests with zero external service calls
- CI workflow (ruff lint + pytest on Python 3.11 and 3.12)
- Existing benchmark scripts moved to `benchmarks/`

[0.1.0]: https://github.com/mauryasameer/the-forge/releases/tag/v0.1.0
