# Architecture

Why this ecosystem is shaped the way it is, for whoever (including future you) opens one of
these repos cold.

## Separate repos, not a monorepo

`meerax` (this repo) is the shared core. Every application built on it — `trend-whisperer`,
`pixel-drift`, and whatever comes next — lives in its own repo with its own version, its own
CI, its own release cadence. None of them vendor or fork meerax's code; they all depend on the
published `meerax` PyPI package.

This trades a small amount of duplication (every app repo has its own `pyproject.toml`,
`ci.yml`, etc. — mitigated by the [reusable CI workflow](.github/workflows/reusable-ci.yml) and
[`meerax new`](README.md#scaffolding-projects)) for real independence: pixel-drift's TensorFlow
dependency never has to coexist with trend-whisperer's statsmodels dependency in the same
environment, and a bug in one app can't block a release of another.

## The provider abstraction pattern

Every app in this ecosystem follows the same rule: **before writing any implementation of an
external dependency, define an abstract interface for it in `src/core/interfaces.py`.**

Concretely, this looks like:

- trend-whisperer: `ForecastProvider` (ABC) → `VARForecastProvider`, `VARMAXForecastProvider`,
  `VECMForecastProvider` — swap the statsmodels backend with one constructor argument.
- pixel-drift: `GeneratorFactory` (ABC) → `Pix2PixGeneratorFactory` (real, used in production) and
  a `_TinyFactory` test double — swap in a fast stub for tests without touching training logic.
- meerax itself: `LLMProvider` (ABC) → `ClaudeProvider`, `OpenAIProvider`, `OllamaProvider` — every
  app that needs an LLM call depends on the interface, not a specific vendor's SDK.

**Why this matters in practice, not in theory:** pixel-drift's real-factory training test and its
stub-factory tests exercise the exact same `CycleGANTrainer` code path — the trainer has no idea
which `GeneratorFactory` it was handed. That's what makes it possible to have a training-loop
test suite that runs in seconds (stub) alongside one that proves the real U-Net actually works
(real factory, marked `@pytest.mark.slow`). Without the interface, those would be two different,
divergent code paths.

## The `src/{core,providers,services}` layering

- `src/core/` — interfaces only. No implementation, no I/O, no third-party imports beyond typing.
- `src/providers/` — concrete implementations of `core`'s interfaces. Each provider owns exactly
  one third-party dependency (one statsmodels model, one generator backend, one LLM SDK).
- `src/services/` — orchestration. Services depend on `core` interfaces, never on a specific
  `providers/` class directly — they receive a provider instance through their constructor.
- `src/app.py` — the one place that actually chooses which concrete provider to instantiate,
  based on a CLI flag (`--provider varmax`, `--llm-provider claude`, etc.).

Dependency direction is one-way: `app` → `services` → `core` ← `providers`. A service file that
imports directly from `providers/` instead of depending on the `core` interface is a sign the
pattern has slipped.

## Why `meerax` exists at all

Every app in this ecosystem needs some subset of: an LLM call, a metrics report, a plotted
figure, an HTML summary, structured logging. Before meerax, each app would reimplement these
from scratch, and a fix to one (e.g. the LLM multimodal image-support work) would need to be
manually ported to every other app. meerax exists so that work happens once, gets tested once
(currently 93%+ coverage, mypy-clean), and every app picks up the fix by bumping one dependency
pin — which `meerax doctor` checks for automatically.

## The standards-enforcement layer

PROJECT_STANDARDS.md defines the rules (single Python version, no committed planning docs, one
provider-abstraction pattern, etc.), but a markdown file has no memory of its own — every rule in
it was violated at least once in this ecosystem's own history before enforcement existed:

- the single-Python-version rule regressed after being fixed once
- planning docs leaked onto two public `main` branches before a manual review caught it
- a dependency pin sat five releases stale without anyone noticing

`meerax doctor` and the [reusable CI workflow](.github/workflows/reusable-ci.yml) exist
specifically to close that gap: every app's CI now checks its own compliance on every push,
instead of relying on a human (or an AI assistant) remembering to re-read the standards doc.
