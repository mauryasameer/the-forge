def pyproject_toml(project_name: str) -> str:
    return f'''[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "PIE", "PLC"]
ignore = ["E501", "B008", "UP007", "PIE790"]

[tool.ruff.lint.per-file-ignores]
"scripts/*" = ["PLC0415", "T201"]
"tests/*" = ["S101", "PLC0415"]
"conftest.py" = ["PLC0415"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
'''


def ci_yml() -> str:
    return '''name: CI

on: [push, pull_request]

jobs:
  ci:
    uses: mauryasameer/the-forge/.github/workflows/reusable-ci.yml@main
'''


def dependabot_yml() -> str:
    return '''version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    target-branch: "dev"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    target-branch: "dev"
    schedule:
      interval: "weekly"
'''


def gitignore() -> str:
    return '''__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
*.egg-info/
dist/
build/
.venv/
.DS_Store
src/data/*
!src/data/.gitignore
'''


def conftest_py() -> str:
    return '''import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
'''


def readme_md(project_name: str) -> str:
    return f'''# {project_name}

![Version](https://img.shields.io/badge/version-0.1.0-blue)

## Setup

```bash
pip install -r requirements.txt
```

## Testing

```bash
pytest tests/ -v
```
'''


def changelog_md() -> str:
    return '''# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
'''


def version_file() -> str:
    return "0.1.0\n"


def task_md(project_name: str) -> str:
    return f'''# {project_name} — Task Tracker

Live progress tracker. Keep this in sync with actual state.

## Backlog
'''


def data_gitignore() -> str:
    return '''*
!.gitignore
'''


def llm_report_narrative_service_py() -> str:
    return '''from __future__ import annotations

from meerax.llm import LLMProvider


def generate_narrative(prompt: str, llm: LLMProvider) -> str:
    """Generate narrative text from a prompt using any LLMProvider."""
    return llm.generate(prompt).content
'''


def llm_report_report_service_py() -> str:
    return '''from __future__ import annotations

from pathlib import Path

from meerax.report import ReportBuilder, ReportSection


def build_narrative_report(title: str, narrative: str, output: str | Path) -> Path:
    """Build a one-section HTML report from generated narrative text."""
    rb = ReportBuilder(title)
    rb.add_section(ReportSection(title="Narrative", content=narrative))
    return rb.save(output)
'''


def llm_report_app_py(project_name: str) -> str:
    return f'''from __future__ import annotations

import argparse
import sys

from meerax.llm import ClaudeProvider, OllamaProvider, OpenAIProvider

from src.services.narrative_service import generate_narrative
from src.services.report_service import build_narrative_report

LLM_PROVIDERS: dict[str, type] = {{
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="{project_name}")
    parser.add_argument("--prompt", required=True, help="Prompt to send to the LLM")
    parser.add_argument("--llm-provider", choices=list(LLM_PROVIDERS.keys()), default="ollama")
    parser.add_argument("--title", default="{project_name} Report")
    parser.add_argument("--output", default="reports/report.html")
    args = parser.parse_args(argv)

    llm = LLM_PROVIDERS[args.llm_provider]()
    narrative = generate_narrative(args.prompt, llm)
    output_path = build_narrative_report(args.title, narrative, args.output)
    print(f"report written to {{output_path}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def llm_report_test_narrative_service_py() -> str:
    return '''from meerax.llm import LLMProvider, LLMResponse

from src.services.narrative_service import generate_narrative


class _StubProvider(LLMProvider):
    def generate(self, prompt, system=None, images=None, **kwargs):
        return LLMResponse(content=f"narrative for: {prompt}", model="stub", input_tokens=1, output_tokens=1)

    def chat(self, messages, system=None, **kwargs):
        raise NotImplementedError


def test_generate_narrative_returns_llm_response_content():
    narrative = generate_narrative("summarize this quarter", _StubProvider())
    assert narrative == "narrative for: summarize this quarter"
'''


def llm_report_test_report_service_py() -> str:
    return '''from src.services.report_service import build_narrative_report


def test_build_narrative_report_writes_html_file(tmp_path):
    output = tmp_path / "report.html"

    result = build_narrative_report("Test Report", "some narrative text", output)

    assert result == output
    assert output.exists()
    html = output.read_text()
    assert "Test Report" in html
    assert "some narrative text" in html
'''


def llm_report_test_pipeline_py() -> str:
    return '''from unittest.mock import MagicMock

from meerax.llm import LLMResponse

from src.app import main


def test_pipeline_writes_report(tmp_path, monkeypatch):
    import src.app as app_module

    stub_provider_cls = MagicMock()
    stub_provider_cls.return_value.generate.return_value = LLMResponse(
        content="a real generated narrative", model="stub", input_tokens=1, output_tokens=1
    )
    monkeypatch.setitem(app_module.LLM_PROVIDERS, "ollama", stub_provider_cls)

    output = tmp_path / "report.html"
    exit_code = main(["--prompt", "test prompt", "--output", str(output)])

    assert exit_code == 0
    assert output.exists()
    assert "a real generated narrative" in output.read_text()
'''
