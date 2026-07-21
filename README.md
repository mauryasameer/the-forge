# The Forge

![Version](https://img.shields.io/badge/version-0.2.1-c8a96e)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-00e5cc)
![License](https://img.shields.io/badge/license-MIT-informational)

Shared ML utilities — LLM providers, evaluation metrics, visualization, and report generation. Used as an in-house dependency across all of Sameer Maurya's ML projects.

## Install

```bash
pip install git+https://github.com/mauryasameer/the-forge.git@v0.2.1
```

Or pin in `requirements.txt`:

```
sameer-forge @ git+https://github.com/mauryasameer/the-forge.git@v0.2.1
```

## Modules

| Module | What it gives you |
|---|---|
| `forge.llm` | Swap-in LLM backends — Claude, OpenAI, Ollama behind one interface |
| `forge.eval.classification` | F1, AUC-ROC, precision, recall in one call |
| `forge.eval.timeseries` | RMSE, MAPE, SMAPE, ADF stationarity test |
| `forge.eval.text` | BLEU-4, ROUGE-L for caption / summary quality |
| `forge.viz` | Dark-themed matplotlib plots (confusion matrix, ROC, forecast, decomposition) |
| `forge.data` | CSV/parquet loaders with schema validation, stratified + time splits, SMOTE |
| `forge.report` | Self-contained dark-themed HTML model-card report builder |
| `forge.logging` | One-call structured logger factory |

## Scaffolding Projects

Every project in the ecosystem follows the same PROJECT_STANDARDS.md layout and depends on
`sameer-forge`. The `forge` CLI (installed alongside the package) generates or retrofits that
layout:

```bash
# brand-new project
forge new my-project --path ~/dev

# retrofit an existing, non-empty directory — additive only, never overwrites
cd ~/dev/my-existing-notebook-project
forge init
```

`forge new` creates the full `src/{core,providers,services,utils,data}` + `tests/` + CI
skeleton, pins `requirements.txt` to the current `sameer-forge` release, and runs `git init`.

`forge init` fills in whatever's missing from that same layout without touching files that
already exist, and reports any top-level files it doesn't recognize (e.g. notebooks) so you can
move them into `src/` by hand.

## Quick Start

```python
from forge.llm import ClaudeProvider, PromptTemplate
from forge.eval import evaluate_classifier
from forge.viz import apply_forge_theme
from forge.report import ReportBuilder, ReportSection

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
apply_forge_theme()
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
from forge.llm import ClaudeProvider, OpenAIProvider, OllamaProvider

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
├── forge/              # Installable package
│   ├── llm/            # LLM provider abstraction
│   ├── eval/           # Evaluation metrics
│   ├── viz/            # Visualization utilities
│   ├── data/           # Data loading, splitting, resampling
│   ├── report/         # HTML report builder
│   ├── scaffold/       # Project skeleton templates + create/retrofit logic
│   ├── cli.py          # `forge new` / `forge init` command entry point
│   └── logging.py      # Structured logger
├── benchmarks/         # Standalone ML benchmark scripts
├── tests/
│   └── unit/           # 58 unit tests, zero external deps
├── pyproject.toml
├── requirements.txt
└── VERSION
```

---

[sameer-portfolio](https://github.com/mauryasameer/sameer-portfolio) · [mauryasameer.com](https://www.mauryasameer.com)
