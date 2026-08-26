# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.4.0] - 2026-08-26
### Added
- `forge.vision.gridplot.plot_translation_grid()` now accepts `np.ndarray` images (channels-last
  `(H,W,C)` or `(H,W)`, in `[-1,1]`) alongside the existing `torch.Tensor` support, so
  TensorFlow/Keras-based projects can use it without forge taking a TensorFlow dependency —
  callers pass `tensor.numpy()`. Strictly additive; existing torch-only callers unaffected.

### Fixed
- README was out of date since the v0.3.0 release: missing the `forge.vision` module from the
  Modules table and Project Structure tree, and a stale unit test count (58, actually 72).

[0.4.0]: https://github.com/mauryasameer/the-forge/compare/v0.3.0...v0.4.0

## [0.3.0] - 2026-08-01
### Added
- `forge.vision` module: `get_device()` (CUDA/MPS/CPU auto-detection), `ImageFolderDataset`
  with normalize/denormalize helpers, `plot_translation_grid()` for labeled before/after
  image comparisons. New `vision` optional-dependency extra (`torch`, `torchvision`, `pillow`).

[0.3.0]: https://github.com/mauryasameer/the-forge/compare/v0.2.1...v0.3.0

## [0.2.1] - 2026-07-21

### Fixed
- `forge new`/`forge init`'s generated `.github/workflows/ci.yml` only ran `pip install -r requirements.txt` in the test job, which does not include `pytest` — every scaffolded project's CI test job failed with `pytest: command not found`. Test job now installs `pytest==8.*` explicitly, mirroring the lint job's own explicit tool install.

## [0.2.0] - 2026-07-20

### Added
- `forge new <name>` — CLI command scaffolding a fresh PROJECT_STANDARDS.md-compliant project (full `src/`/`tests/`/CI skeleton, pinned `sameer-forge` dependency, `git init`)
- `forge init` — CLI command retrofitting that same layout onto an existing project directory, additive-only, reporting unrecognized top-level entries for manual triage
- `forge.scaffold.templates` — project skeleton file templates
- `forge.scaffold.skeleton` — tree creation/retrofit logic and `requirements.txt` dependency wiring
- 21 new unit tests covering scaffold templates, skeleton logic, and the CLI (58 total)

### Fixed
- `build-backend` in `pyproject.toml` pointed at a non-importable module (`setuptools.backends.legacy:build`), breaking `pip install -e .` and `pip install git+...` for the whole package; corrected to `setuptools.build_meta`

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

[0.2.1]: https://github.com/mauryasameer/the-forge/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mauryasameer/the-forge/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mauryasameer/the-forge/releases/tag/v0.1.0
