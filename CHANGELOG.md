# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.5.0] - 2026-08-28
### Added
- `ARCHITECTURE.md` — documents the provider-abstraction pattern, the `src/{core,providers,services}` layering, why meerax exists, and why the standards-enforcement layer (`meerax doctor` + the reusable CI workflow) exists.
- `SECURITY.md` — API key handling, dependency-update review guidance, reporting.
- `meerax bump <version>` — updates VERSION, the README version badge, and inserts a dated CHANGELOG heading in one step. Doesn't write CHANGELOG content or a compare-link footer, since only a human (or an AI assistant) who knows what changed can write those honestly. Used to bump this very release.

Roadmap phase 4 (of the ecosystem audit) — the last phase, closing out the "make future apps cheaper to build" goal. The one item not shipped here — an opt-in `--template` for the recurring "provider-swap service + HTML report" shape — is being built separately as its own real, runnable example rather than speculative stub code.

[1.5.0]: https://github.com/mauryasameer/the-forge/compare/v1.4.1...v1.5.0

## [1.4.0] - 2026-08-28
### Added
- `.github/dependabot.yml` (pip + github-actions, weekly) — added to this repo, and to the `meerax new`/`meerax init` scaffold so every future project gets it automatically.
- `meerax doctor` now checks for a Dependabot config too (warns, doesn't fail — not having one yet isn't a hard standards violation the way a missing LICENSE is).

Closes the last item of roadmap phase 3 (of the ecosystem audit).

[1.4.0]: https://github.com/mauryasameer/the-forge/compare/v1.3.0...v1.4.0

## [1.3.0] - 2026-08-28
### Added
- `mypy` type checking wired into CI as its own required job. Fixed the ~19 real errors it found on first run: matplotlib's `Figure | SubFigure | None` typing on `plt.subplots()`/`ax.get_figure()` (narrowed with `assert isinstance(fig, plt.Figure)`), `Image.BICUBIC` → the properly-typed `Image.Resampling.BICUBIC`, and two genuine narrow-type gaps in the Claude/OpenAI providers' message-content handling and `usage`-can-be-`None` handling.
- `pytest-cov` wired into CI with an 85% minimum coverage gate. Immediately found `meerax.viz.classification` and `meerax.viz.timeseries` had **zero** test coverage — the same untested-module pattern as `data.imbalance` from v1.0.1, just missed in the original audit. Added real tests for both; overall coverage is now 93%.
- The reusable CI workflow now reports coverage for downstream apps too (`--cov=src`), though without an enforced threshold yet — both existing apps are already at 82-98%, but a blanket gate wasn't imposed without auditing what's realistically coverable there first (e.g. `@tf.function`-decorated training loops are notoriously coverage-tool-unfriendly).
- A real `tests/integration/` suite for meerax itself, previously just an empty stub since v0.1.0: an eval → viz → report pipeline test (the README's own Quick Start example, exercised for real) and a scaffold → doctor round-trip test (a freshly `meerax new`'d or `meerax init`'d project, once given a LICENSE and CHANGELOG entry, passes every doctor check).

Roadmap phase 3 (of the ecosystem audit) — quality hardening now that phase 2's enforcement layer exists.

[1.3.0]: https://github.com/mauryasameer/the-forge/compare/v1.2.0...v1.3.0

## [1.2.0] - 2026-08-28
### Added
- `.github/workflows/reusable-ci.yml` — the lint+test logic previously duplicated verbatim in every scaffolded project's `ci.yml` now lives in one place, called via `uses:`. Also runs `meerax doctor` as part of the test job.
- The `meerax new`/`meerax init` scaffold's generated `ci.yml` now calls this reusable workflow instead of embedding a full copy.

Closes the other half of Phase 2 (of the ecosystem audit): a fix to the shared CI logic — like the missing-pytest-install bug fixed in v0.2.1 — now propagates to every project that uses it, instead of needing to be manually reapplied to each one.

[1.2.0]: https://github.com/mauryasameer/the-forge/compare/v1.1.0...v1.2.0

## [1.1.0] - 2026-08-28
### Added
- `meerax doctor` — checks a project against PROJECT_STANDARDS.md: no Python version matrix in CI, no committed `docs/specs`/`docs/plans`, LICENSE present, VERSION/README/CHANGELOG consistency, and whether the project's `meerax` pin is current with the latest PyPI release. Exits non-zero on any failing check, safe to run in CI.

This is Phase 2 of the ecosystem audit's roadmap — closing the gap where standards drift (stale Python-version matrices, leaked planning docs, stale dependency pins) was only ever caught by manual review, never by any repo's own CI.

[1.1.0]: https://github.com/mauryasameer/the-forge/compare/v1.0.1...v1.1.0

## [1.0.1] - 2026-08-28
### Fixed
- Scaffold's `ensure_meerax_dependency()` still templated a `git+https://...` dependency line for newly scaffolded projects — stale now that `meerax` is genuinely on PyPI. New projects now get a plain `meerax==<version>` pin.
- `meerax.data.imbalance` (`smote_oversample`, `random_undersample`) had zero test coverage since v0.1.0.

[1.0.1]: https://github.com/mauryasameer/the-forge/compare/v1.0.0...v1.0.1

## [1.0.0] - 2026-08-28
### Changed
- **Breaking:** package renamed from `sameer-forge` (import `forge`) to `meerax` (import `meerax`), ahead of publishing to PyPI for use across the organization. The PyPI distribution name `sameer-forge` was available, but the `forge` import namespace was not — an unrelated, already-published PyPI package also claims `forge`, which would silently collide with this package's files if both were ever installed in the same environment. The `meerax new`/`meerax init` CLI commands replace `forge new`/`forge init`.
- Version is now single-sourced from `VERSION` (via `[tool.setuptools.dynamic]` at build time, `importlib.metadata.version()` at runtime) instead of being duplicated across `VERSION`, `pyproject.toml`, and `meerax/__init__.py`.
- Added `parquet` as its own optional-dependency extra instead of bundling `pyarrow` directly into `all`.

### Added
- Real `LICENSE` file (MIT) — previously declared in `pyproject.toml` but not actually included in the repo or distribution archives.
- `project.urls` metadata (Homepage, Repository, Issues, Changelog).
- GitHub Actions release workflow publishing to PyPI via Trusted Publishing on version tags.

[1.0.0]: https://github.com/mauryasameer/the-forge/compare/v0.5.3...v1.0.0

## [0.5.3] - 2026-08-26
### Fixed
- `forge.vision`'s package `__init__` and `gridplot._to_display_array` eagerly imported torch/torchvision even for pure-numpy callers, forcing torch's CUDA/triton native libraries to load. Loading torch alongside TensorFlow in the same process (as a TF-based project using only `gridplot`'s numpy path does) segfaults on Linux. Both now defer the torch import until a `torch.Tensor` input actually needs it.

[0.5.3]: https://github.com/mauryasameer/the-forge/compare/v0.5.2...v0.5.3

## [0.5.2] - 2026-08-26
### Fixed
- Removed committed design specs and implementation plans (`docs/specs/`, `docs/plans/`) from the repo — these reveal the AI-assisted development process regardless of folder naming, against standing project rule.

[0.5.2]: https://github.com/mauryasameer/the-forge/compare/v0.5.1...v0.5.2

## [0.5.1] - 2026-08-26
### Fixed
- CI and the `forge new`/`forge init` scaffold's generated `ci.yml` both tested against a
  `["3.11", "3.12"]` Python version matrix, against explicit standing instruction to support
  exactly one Python version. Both now test/lint Python 3.12 only. `requires-python` narrowed to
  `>=3.12`, ruff `target-version` bumped to `py312`, README Python badge updated.

[0.5.1]: https://github.com/mauryasameer/the-forge/compare/v0.5.0...v0.5.1

## [0.5.0] - 2026-08-26
### Added
- `LLMProvider.generate()` accepts an optional `images: list[bytes] | None` parameter (raw PNG
  bytes) across all three providers (Claude, OpenAI, Ollama), each encoding into its own wire
  format. Fully backward compatible. First unit tests ever written for these three providers.

### Fixed
- CI never installed `anthropic`/`openai`/`ollama`, so the new provider tests failed in CI (but
  passed locally with the `llm` extra installed) until this was caught and fixed.

[0.5.0]: https://github.com/mauryasameer/the-forge/compare/v0.4.0...v0.5.0

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
