def pyproject_toml(project_name: str) -> str:
    return f'''[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.11"

[tool.ruff]
target-version = "py311"
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
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -r requirements.txt pytest==8.*
      - run: pytest tests/unit/ -v --tb=short
      - run: pytest tests/integration/ -v --tb=short

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install ruff==0.11.13
      - run: ruff check .
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
