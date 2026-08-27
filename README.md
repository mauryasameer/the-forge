# meerax

![Version](https://img.shields.io/badge/version-1.0.0-c8a96e)
![Python](https://img.shields.io/badge/python-3.12-00e5cc)
![License](https://img.shields.io/badge/license-MIT-informational)

Shared ML utilities — LLM providers, evaluation metrics, visualization, and report generation.
Used as an in-house dependency across all of Sameer Maurya's ML projects and organization.
Source repo: [the-forge](https://github.com/mauryasameer/the-forge) — kept its original name;
only the installable package was renamed to `meerax`.

## Install

```bash
pip install git+https://github.com/mauryasameer/the-forge.git@v1.0.0
```

Or pin in `requirements.txt`:

```
meerax @ git+https://github.com/mauryasameer/the-forge.git@v1.0.0
```

Once published to PyPI, this becomes `pip install meerax` / `meerax==1.0.0`.

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
skeleton, pins `requirements.txt` to the current `meerax` release, and runs `git init`.

`meerax init` fills in whatever's missing from that same layout without touching files that
already exist, and reports any top-level files it doesn't recognize (e.g. notebooks) so you can
move them into `src/` by hand.

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
│   ├── cli.py           # `meerax new` / `meerax init` command entry point
│   ├── vision/          # Image dataset loader + translation-grid plotting
│   └── logging.py       # Structured logger
├── benchmarks/          # Standalone ML benchmark scripts
├── tests/
│   └── unit/            # 80 unit tests, zero external deps
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── VERSION
```

---

[sameer-portfolio](https://github.com/mauryasameer/sameer-portfolio) · [mauryasameer.com](https://www.mauryasameer.com)
