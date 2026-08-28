# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.7.1] - 2026-08-28
### Changed
- Bumped `ruff` 0.11.13 → 0.16.4, `pyarrow` 20.0.0 → 25.0.1, `pytest-mock` 3.14.1 → 3.15.1 (Dependabot PRs #54, #55, #56).
- Ruff 0.16.4 newly enforces `PLC0415` (import-not-at-top-level) against the package's ~10 deliberate lazy imports — a pattern used throughout to avoid eager-loading heavy/conflicting ML dependencies (torch, tensorflow, anthropic, openai, ollama, sklearn, statsmodels, nltk, imblearn). Moved `PLC0415` into the project-wide `[tool.ruff.lint] ignore` list instead of suppressing it per file.

### Fixed
- Verified this bump against the real Python 3.12 toolchain (`requires-python = ">=3.12"`) rather than the locally available Python 3.9 environment — the 3.9 run had been silently masking real mypy findings (a stale `# type: ignore` diagnosis) and picking up a stray, untracked worktree during ruff's file walk. All checks (ruff, mypy --strict, full test suite) now verified clean under an actual 3.12 interpreter.

## [1.7.0] - 2026-08-28
### Changed
- `mypy` now runs with real `strict = true` instead of just `ignore_missing_imports` — the README claimed strict mode before this was actually true. Fixed the 30 errors this surfaced: missing `**kwargs: Any` annotations across all three LLM providers, `dict` → `dict[str, Any]`/`Any` generic type args, `matplotlib.pyplot.Figure`/`.Axes` replaced with direct `matplotlib.figure.Figure`/`matplotlib.axes.Axes` imports (the `plt.` namespace doesn't type-export them), `Dataset` → `Dataset[torch.Tensor]`, and an explicit intermediate variable to stop a `no-any-return` from PyTorch's imprecise arithmetic-operator stubs. 2 narrowly-scoped `# type: ignore` comments remain for genuine third-party stub gaps (documented in each).
- CI's test job now runs `tests/integration/` too — it only ever ran `tests/unit/`, so the 4 integration tests (including the one that scaffolds and runs the `--template llm-report` example) were never actually exercised in CI.
- The release workflow now depends on the same lint/typecheck/test checks as CI before building or publishing — previously it would build and publish to PyPI off nothing but `twine check`, with no guarantee tests had ever run against the tagged commit. Lint/typecheck/test logic is shared between `ci.yml` and `release.yml` via a new local reusable workflow (`.github/workflows/_checks.yml`) instead of being duplicated.
- `pip install mypy>=1.10 pandas-stubs` was unquoted in CI — the shell parses the bare `>` as an output redirect, silently creating a file named `=1.10` and installing an unconstrained `mypy` instead of respecting the `>=1.10` floor. Fixed to `pip install "mypy>=1.10" pandas-stubs`.
- Modernized license metadata to PEP 639 / Metadata 2.4: `license = "MIT"` + `license-files = ["LICENSE"]` instead of the older `license = { text = "MIT" }` table, and dropped the now-redundant `License :: OSI Approved :: MIT License` classifier. Requires `setuptools>=77` (bumped from `>=69`); verified with a real `python -m build` + `twine check`.

### Fixed
- README overclaimed "zero ignored errors" for mypy — 2 real `# type: ignore` comments exist for genuine stub gaps. Wording corrected to name them instead of denying they exist.
- README's unit test count had drifted again (said 137, actually 143 even before this release's own new tests).

All of these were caught by an external review after this session's own final "everything's fixed" summary — a reminder that ecosystem-wide claims need the same verification discipline as any other code claim.

[1.7.0]: https://github.com/mauryasameer/the-forge/compare/v1.6.1...v1.7.0

## [1.6.1] - 2026-08-28
### Fixed
- This repo's own `.github/dependabot.yml` never got `target-branch: dev` — the scaffold template and both downstream repos were fixed in v1.4.1, but the-forge's own file at the repo root was missed. The next scan here would have opened PRs against `main` directly, same as the original incident.
- `meerax doctor`'s `dependabot-present` check now verifies `target-branch: dev` is actually set, not just that the file exists — this exact gap should have been caught by doctor and wasn't.

[1.6.1]: https://github.com/mauryasameer/the-forge/compare/v1.6.0...v1.6.1

## [1.6.0] - 2026-08-28
### Added
- `meerax new`/`meerax init --template llm-report` — an opt-in, genuinely functional example on top of the bare skeleton: a narrative service that calls any `meerax.llm` provider, a report service that builds an HTML summary via `meerax.report`, and an `app.py` wiring them together with real, passing tests. Not stub methods to fill in — verified by scaffolding it for real and running its generated test suite as a subprocess in this repo's own integration tests.
- `ensure_meerax_dependency()` now accepts `extras`, so the template's `meerax[llm]` pin gets generated correctly.

This closes roadmap phase 4's one deferred item — the recurring "provider-swap service + HTML report" shape, proven twice already (trend-whisperer, pixel-drift), is now reusable without generating speculative or fake business logic.

[1.6.0]: https://github.com/mauryasameer/the-forge/compare/v1.5.0...v1.6.0

## [1.5.0] - 2026-08-28
### Added
- `ARCHITECTURE.md` — documents the provider-abstraction pattern, the `src/{core,providers,services}` layering, why meerax exists, and why the standards-enforcement layer (`meerax doctor` + the reusable CI workflow) exists.
- `SECURITY.md` — API key handling, dependency-update review guidance, reporting.
- `meerax bump <version>` — updates VERSION, the README version badge, and inserts a dated CHANGELOG heading in one step. Doesn't write CHANGELOG content or a compare-link footer, since only a human (or an AI assistant) who knows what changed can write those honestly. Used to bump this very release.

Roadmap phase 4 (of the ecosystem audit) — the last phase, closing out the "make future apps cheaper to build" goal. The one item not shipped here — an opt-in `--template` for the recurring "provider-swap service + HTML report" shape — is being built separately as its own real, runnable example rather than speculative stub code.

[1.5.0]: https://github.com/mauryasameer/the-forge/compare/v1.4.1...v1.5.0

## [1.4.1] - 2026-08-28
### Fixed
- The scaffold's generated `dependabot.yml` didn't set `target-branch`, so Dependabot defaulted to opening PRs against `main` directly — violating this ecosystem's PR-into-dev-only convention. All 17 PRs Dependabot opened across the three repos on first scan had to be retargeted by hand — and even after retargeting, asking Dependabot to `@dependabot rebase` silently reset several of them back to `main`, so 8 dependency bumps landed there directly before this was caught. Recovered by merging `main`'s extra commits back into `dev`. Lesson: don't use Dependabot's own rebase command to fix a PR whose base you changed by hand — it appears to re-derive the target branch from the update branch's own stale config rather than the current one.

[1.4.1]: https://github.com/mauryasameer/the-forge/compare/v1.4.0...v1.4.1

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
