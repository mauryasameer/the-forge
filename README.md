# meerax

![Version](https://img.shields.io/badge/version-1.4.0-c8a96e)
![Python](https://img.shields.io/badge/python-3.12-00e5cc)
![License](https://img.shields.io/badge/license-MIT-informational)

Shared ML utilities — LLM providers, evaluation metrics, visualization, and report generation.
Used as an in-house dependency across all of Sameer Maurya's ML projects and organization.
Source repo: [the-forge](https://github.com/mauryasameer/the-forge) — kept its original name;
only the installable package was renamed to `meerax`.

CI gates on mypy (strict, zero ignored errors) and a minimum 85% test coverage — both enforced
on every PR, not just checked locally.

## Install

```bash
pip install meerax
```

Or pin in `requirements.txt`:

```
meerax==1.4.0
```

## Modules

| Module | What it gives you |
|---|---|
| `meerax.llm` | Swap-in LLM backends — Claude, OpenAI, Ollama behind one interface, text or images |
| `meerax.eval.classification` | F1, AUC-ROC, precision, recall in one call |
| `meerax.eval.timeseries` | RMSE, MAPE, SMAPE, ADF stationarity test |
| `meerax.eval.text` | BLEU-4, ROUGE-L for caption / summary quality |
| `meerax.viz` | Dark-themed matplotlib plots (confusion matrix, ROC, forecast, decomposition) |
| `meerax.data` | CSV/parquet loaders with schema validation, stratified + time splits, SMOTE |
| `meerax.report` | Self-contained dark-themed HTML model-card report builder |
| `meerax.logging` | One-call structured logger factory |
| `meerax.vision` | Image folder dataset loader (PyTorch) + translation-grid plotting (torch or numpy/TF images) |

## Scaffolding Projects

Every project in the ecosystem follows the same PROJECT_STANDARDS.md layout and depends on
`meerax`. The `meerax` CLI (installed alongside the package) generates or retrofits that layout:

```bash
# brand-new project
meerax new my-project --path ~/dev

# retrofit an existing, non-empty directory — additive only, never overwrites
cd ~/dev/my-existing-notebook-project
meerax init
```

`meerax new` creates the full `src/{core,providers,services,utils,data}` + `tests/` + CI
skeleton, pins `requirements.txt` to the current `meerax` release, and runs `git init`. The
generated `ci.yml` calls this repo's [reusable CI workflow](.github/workflows/reusable-ci.yml)
instead of embedding its own copy, so fixes to the shared CI logic reach every project that
uses it without needing to be manually reapplied. Also generates `.github/dependabot.yml`
(pip + github-actions, weekly) so dependency pins don't quietly go stale.

`meerax init` fills in whatever's missing from that same layout without touching files that
already exist, and reports any top-level files it doesn't recognize (e.g. notebooks) so you can
move them into `src/` by hand.

`meerax doctor` checks an existing project against PROJECT_STANDARDS.md — no Python version
matrix, no committed `docs/specs`/`docs/plans`, a LICENSE file, VERSION/README/CHANGELOG
consistency, Dependabot configured, and whether the project's `meerax` pin is current:

```bash
cd ~/dev/my-project
meerax doctor
```

Exits non-zero if anything fails, so it's safe to run in CI.

## Quick Start

```python
from meerax.llm import ClaudeProvider, PromptTemplate
from meerax.eval import evaluate_classifier
from meerax.viz import apply_meerax_theme
from meerax.report import ReportBuilder, ReportSection

# LLM: swap provider without changing downstream code
llm = ClaudeProvider()                         # or OpenAIProvider() / OllamaProvider()
tpl = PromptTemplate("Explain {finding} to a risk manager in 3 sentences.")
response = llm.generate(tpl.render(finding="high AUC-ROC with low recall"))

# Eval
metrics = evaluate_classifier(y_true, y_pred, y_prob=probabilities)
print(metrics)
# Accuracy : 0.9823
# F1       : 0.8741
# AUC-ROC  : 0.9912

# Viz + Report
apply_meerax_theme()
rb = ReportBuilder("Fraud Detection — Model Report v0.1.0")
rb.add_section(ReportSection(
    title="Performance",
    metrics=metrics.to_dict(),
    content=response.content,
))
rb.save("reports/model_report.html")
```

## LLM Provider Interface

All providers implement `LLMProvider.generate()` and `.chat()`. Swap with one line:

```python
from meerax.llm import ClaudeProvider, OpenAIProvider, OllamaProvider

llm = ClaudeProvider()    # needs ANTHROPIC_API_KEY
llm = OpenAIProvider()    # needs OPENAI_API_KEY
llm = OllamaProvider()    # needs Ollama running locally
```

## Benchmarks

Self-contained benchmark scripts in `benchmarks/`:

| Script | Description |
|---|---|
| `kv_cache_benchmark.py` | KV caching simulation at GPT-2 Medium scale |

## Project Structure

```
the-forge/
├── meerax/              # Installable package
│   ├── llm/            # LLM provider abstraction
│   ├── eval/            # Evaluation metrics
│   ├── viz/             # Visualization utilities
│   ├── data/            # Data loading, splitting, resampling
│   ├── report/          # HTML report builder
│   ├── scaffold/        # Project skeleton templates + create/retrofit logic
│   ├── cli.py           # `meerax new` / `init` / `doctor` command entry point
│   ├── doctor.py        # PROJECT_STANDARDS.md compliance checks
│   ├── vision/          # Image dataset loader + translation-grid plotting
│   └── logging.py       # Structured logger
├── benchmarks/          # Standalone ML benchmark scripts
├── tests/
│   ├── unit/            # 117 unit tests, zero external deps
│   └── integration/     # 3 cross-module pipeline tests
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── VERSION
```

---

[sameer-portfolio](https://github.com/mauryasameer/sameer-portfolio) · [mauryasameer.com](https://www.mauryasameer.com)
