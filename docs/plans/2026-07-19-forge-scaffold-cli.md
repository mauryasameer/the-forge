# Forge Scaffold CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `forge` CLI (`forge new <name>` / `forge init`) to the sameer-forge package that scaffolds or retrofits a PROJECT_STANDARDS.md-compliant project layout and wires in the `sameer-forge` dependency.

**Architecture:** Two new modules — `forge/scaffold/templates.py` (pure string-returning template functions) and `forge/scaffold/skeleton.py` (directory/file skeleton definition + create/retrofit logic + requirements.txt dependency injection) — consumed by a thin `forge/cli.py` argparse entry point registered via `[project.scripts]`.

**Tech Stack:** Python 3.11+ stdlib only (`argparse`, `pathlib`, `dataclasses`, `subprocess`). No new runtime dependency.

## Global Constraints

- Python `>=3.11`, target-version `py311`, line-length 120 (matches `the-forge/pyproject.toml`).
- Ruff pinned to `0.11.13` everywhere it's referenced (matches this repo's own pin) — never a different version in generated CI or in this repo's own tooling.
- No `typing.List`/`Dict`/`Optional` — use `list[str]`, `dict[str, Any]`, `X | None`.
- No `print()` outside CLI-facing code — `forge/cli.py` is CLI-facing, `forge/scaffold/*.py` must not print.
- No new third-party dependency for the-forge package itself.
- Every commit message uses `feat:`/`test:`/`docs:`/`chore:` imperative-mood prefixes, no AI/Claude/Anthropic attribution anywhere.
- All work happens on `feature/scaffold-cli` (already branched off `dev`) — never commit to `main` or `dev` directly.
- `VERSION` and `CHANGELOG.md` for the-forge package itself are **not** touched on this branch — the MINOR version bump to `0.2.0` happens at release-merge time, out of scope for this plan.
- Working directory for all commands below: `/Users/sameermaurya/Downloads/dev/the-forge`.

---

### Task 1: Template functions

**Files:**
- Create: `forge/scaffold/__init__.py`
- Create: `forge/scaffold/templates.py`
- Test: `tests/unit/test_scaffold_templates.py`

**Interfaces:**
- Produces: `templates.pyproject_toml(project_name: str) -> str`, `templates.ci_yml() -> str`, `templates.gitignore() -> str`, `templates.conftest_py() -> str`, `templates.readme_md(project_name: str) -> str`, `templates.changelog_md() -> str`, `templates.version_file() -> str`, `templates.task_md(project_name: str) -> str`, `templates.data_gitignore() -> str`. Consumed by Task 2's skeleton module.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_scaffold_templates.py
from forge.scaffold import templates


def test_pyproject_toml_includes_project_name():
    content = templates.pyproject_toml("my-project")
    assert 'name = "my-project"' in content
    assert 'target-version = "py311"' in content


def test_ci_yml_pins_ruff_version():
    content = templates.ci_yml()
    assert "ruff==0.11.13" in content
    assert "pytest tests/unit/" in content
    assert "pytest tests/integration/" in content


def test_gitignore_ignores_src_data_contents():
    content = templates.gitignore()
    assert "src/data/*" in content
    assert "!src/data/.gitignore" in content


def test_conftest_py_inserts_root_into_syspath():
    content = templates.conftest_py()
    assert "sys.path.insert(0" in content


def test_readme_md_includes_project_name():
    content = templates.readme_md("my-project")
    assert "# my-project" in content


def test_changelog_md_has_unreleased_section():
    content = templates.changelog_md()
    assert "## [Unreleased]" in content


def test_version_file_is_semver_with_newline():
    assert templates.version_file() == "0.1.0\n"


def test_task_md_includes_project_name():
    content = templates.task_md("my-project")
    assert "my-project" in content


def test_data_gitignore_ignores_everything_but_itself():
    content = templates.data_gitignore()
    assert content.strip().splitlines() == ["*", "!.gitignore"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_scaffold_templates.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'forge.scaffold'`

- [ ] **Step 3: Create the empty package marker**

Create `forge/scaffold/__init__.py` as a zero-byte file (no content — `forge.scaffold` just needs
to be an importable package).

- [ ] **Step 4: Write templates.py**

```python
# forge/scaffold/templates.py
def pyproject_toml(project_name: str) -> str:
    return f'''[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.backends.legacy:build"

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
      - run: pip install -r requirements.txt
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
    return "0.1.0\\n"


def task_md(project_name: str) -> str:
    return f'''# {project_name} — Task Tracker

Live progress tracker. Keep this in sync with actual state.

## Backlog
'''


def data_gitignore() -> str:
    return '''*
!.gitignore
'''
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_scaffold_templates.py -v`
Expected: PASS (9 passed)

- [ ] **Step 6: Commit**

```bash
git add forge/scaffold/__init__.py forge/scaffold/templates.py tests/unit/test_scaffold_templates.py
git commit -m "feat: add scaffold template functions"
```

---

### Task 2: Skeleton definition + create/retrofit logic

**Files:**
- Create: `forge/scaffold/skeleton.py`
- Test: `tests/unit/test_scaffold_skeleton.py`

**Interfaces:**
- Consumes: all functions from `forge.scaffold.templates` (Task 1).
- Produces: `skeleton.ScaffoldResult` dataclass with fields `created: list[Path]`, `skipped: list[Path]`, `unrecognized: list[Path]`; `skeleton.create_tree(root: Path, project_name: str) -> ScaffoldResult`; `skeleton.retrofit_tree(root: Path, project_name: str) -> ScaffoldResult`; `skeleton.ensure_forge_dependency(root: Path, version: str) -> str` (returns `"created"`, `"appended"`, or `"unchanged"`). Consumed by Task 4's `cli.py`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_scaffold_skeleton.py
from pathlib import Path

from forge.scaffold.skeleton import create_tree, ensure_forge_dependency, retrofit_tree

EXPECTED_DIRS = [
    "src/core",
    "src/providers",
    "src/services",
    "src/utils",
    "src/data",
    "tests/unit",
    "tests/integration",
    "tests/test_data",
    "scripts",
    ".github/workflows",
]

EXPECTED_FILES = [
    "pyproject.toml",
    ".github/workflows/ci.yml",
    ".gitignore",
    "conftest.py",
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "task.md",
    "src/data/.gitignore",
]


def test_create_tree_creates_all_dirs_and_files(tmp_path):
    root = tmp_path / "my-project"
    result = create_tree(root, "my-project")

    for rel_dir in EXPECTED_DIRS:
        assert (root / rel_dir).is_dir()
    for rel_file in EXPECTED_FILES:
        assert (root / rel_file).is_file()
    assert len(result.created) == len(EXPECTED_DIRS) + len(EXPECTED_FILES)
    assert result.skipped == []


def test_retrofit_tree_only_creates_missing(tmp_path):
    root = tmp_path / "existing-project"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "core").mkdir()
    existing_readme = root / "README.md"
    existing_readme.write_text("# Pre-existing content\n")

    result = retrofit_tree(root, "existing-project")

    assert (root / "src" / "core") in result.skipped
    assert existing_readme.read_text() == "# Pre-existing content\n"
    assert (root / "src" / "providers") in result.created
    assert (root / "task.md").is_file()


def test_retrofit_tree_is_idempotent(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    retrofit_tree(root, "proj")
    second = retrofit_tree(root, "proj")

    assert second.created == []
    assert len(second.skipped) > 0


def test_retrofit_tree_reports_unrecognized_entries(tmp_path):
    root = tmp_path / "notebook-project"
    root.mkdir()
    (root / "analysis.ipynb").write_text("{}")

    result = retrofit_tree(root, "notebook-project")

    assert root / "analysis.ipynb" in result.unrecognized


def test_ensure_forge_dependency_creates_when_missing(tmp_path):
    status = ensure_forge_dependency(tmp_path, "0.2.0")
    content = (tmp_path / "requirements.txt").read_text()

    assert status == "created"
    assert "sameer-forge @ git+https://github.com/mauryasameer/the-forge.git@v0.2.0" in content


def test_ensure_forge_dependency_appends_when_file_exists_without_it(tmp_path):
    (tmp_path / "requirements.txt").write_text("pandas>=2.2\n")
    status = ensure_forge_dependency(tmp_path, "0.2.0")
    content = (tmp_path / "requirements.txt").read_text()

    assert status == "appended"
    assert "pandas>=2.2" in content
    assert "sameer-forge" in content


def test_ensure_forge_dependency_noop_when_already_present(tmp_path):
    (tmp_path / "requirements.txt").write_text(
        "sameer-forge @ git+https://github.com/mauryasameer/the-forge.git@v0.1.0\n"
    )
    status = ensure_forge_dependency(tmp_path, "0.2.0")

    assert status == "unchanged"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_scaffold_skeleton.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'forge.scaffold.skeleton'`

- [ ] **Step 3: Write minimal implementation**

```python
# forge/scaffold/skeleton.py
from dataclasses import dataclass, field
from pathlib import Path

from forge.scaffold import templates

GITKEEP_DIRS = [
    "src/core",
    "src/providers",
    "src/services",
    "src/utils",
    "tests/unit",
    "tests/integration",
    "tests/test_data",
    "scripts",
]

ALL_DIRS = [*GITKEEP_DIRS, "src/data", ".github/workflows"]

SKELETON_FILES = {
    "pyproject.toml": lambda name: templates.pyproject_toml(name),
    ".github/workflows/ci.yml": lambda name: templates.ci_yml(),
    ".gitignore": lambda name: templates.gitignore(),
    "conftest.py": lambda name: templates.conftest_py(),
    "README.md": lambda name: templates.readme_md(name),
    "CHANGELOG.md": lambda name: templates.changelog_md(),
    "VERSION": lambda name: templates.version_file(),
    "task.md": lambda name: templates.task_md(name),
    "src/data/.gitignore": lambda name: templates.data_gitignore(),
    **{f"{d}/.gitkeep": (lambda name: "") for d in GITKEEP_DIRS},
}

RECOGNIZED_TOP_LEVEL = {
    "src",
    "tests",
    "scripts",
    ".github",
    "conftest.py",
    "pyproject.toml",
    "requirements.txt",
    "VERSION",
    "CHANGELOG.md",
    "task.md",
    "README.md",
    ".gitignore",
}

FORGE_DEP_MARKER = "sameer-forge"
FORGE_REPO_URL = "https://github.com/mauryasameer/the-forge.git"


@dataclass
class ScaffoldResult:
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    unrecognized: list[Path] = field(default_factory=list)


def create_tree(root: Path, project_name: str) -> ScaffoldResult:
    root.mkdir(parents=True, exist_ok=False)
    result = ScaffoldResult()
    for rel_dir in ALL_DIRS:
        dir_path = root / rel_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        result.created.append(dir_path)
    for rel_file, template_fn in SKELETON_FILES.items():
        file_path = root / rel_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(template_fn(project_name))
        result.created.append(file_path)
    return result


def retrofit_tree(root: Path, project_name: str) -> ScaffoldResult:
    result = ScaffoldResult()
    for rel_dir in ALL_DIRS:
        dir_path = root / rel_dir
        if dir_path.exists():
            result.skipped.append(dir_path)
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            result.created.append(dir_path)
    for rel_file, template_fn in SKELETON_FILES.items():
        file_path = root / rel_file
        if file_path.exists():
            result.skipped.append(file_path)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(template_fn(project_name))
            result.created.append(file_path)
    result.unrecognized = _find_unrecognized(root)
    return result


def _find_unrecognized(root: Path) -> list[Path]:
    unrecognized = []
    for entry in sorted(root.iterdir()):
        if entry.name == ".git":
            continue
        if entry.name not in RECOGNIZED_TOP_LEVEL:
            unrecognized.append(entry)
    return unrecognized


def ensure_forge_dependency(root: Path, version: str) -> str:
    dep_line = f"sameer-forge @ git+{FORGE_REPO_URL}@v{version}\\n"
    req_path = root / "requirements.txt"
    if not req_path.exists():
        req_path.write_text(dep_line)
        return "created"
    content = req_path.read_text()
    if FORGE_DEP_MARKER in content:
        return "unchanged"
    if content and not content.endswith("\\n"):
        content += "\\n"
    req_path.write_text(content + dep_line)
    return "appended"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_scaffold_skeleton.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add forge/scaffold/skeleton.py tests/unit/test_scaffold_skeleton.py
git commit -m "feat: add scaffold create/retrofit tree logic"
```

---

### Task 3: `forge` CLI entry point

**Files:**
- Create: `forge/cli.py`
- Modify: `pyproject.toml` (add `[project.scripts]`)
- Test: `tests/unit/test_cli.py`

**Interfaces:**
- Consumes: `forge.scaffold.skeleton.create_tree`, `retrofit_tree`, `ensure_forge_dependency` (Task 2); `forge.__version__` (existing, `forge/__init__.py`).
- Produces: `cli.build_parser() -> argparse.ArgumentParser`, `cli.cmd_new(args) -> int`, `cli.cmd_init(args) -> int`, `cli.main(argv: list[str] | None = None) -> int`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_cli.py
from pathlib import Path

from forge.cli import main


def test_new_creates_project_and_git_repo(tmp_path):
    exit_code = main(["new", "my-project", "--path", str(tmp_path)])
    root = tmp_path / "my-project"

    assert exit_code == 0
    assert (root / "src" / "core").is_dir()
    assert (root / ".git").is_dir()
    assert "sameer-forge" in (root / "requirements.txt").read_text()


def test_new_fails_if_directory_already_exists(tmp_path, capsys):
    (tmp_path / "my-project").mkdir()
    exit_code = main(["new", "my-project", "--path", str(tmp_path)])

    assert exit_code == 1
    assert "already exists" in capsys.readouterr().err


def test_init_retrofits_existing_directory(tmp_path, capsys):
    root = tmp_path / "existing"
    root.mkdir()
    (root / "analysis.ipynb").write_text("{}")

    exit_code = main(["init", "--path", str(root)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert (root / "src" / "core").is_dir()
    assert not (root / ".git").exists()
    assert "analysis.ipynb" in out


def test_init_fails_if_directory_missing(tmp_path, capsys):
    exit_code = main(["init", "--path", str(tmp_path / "nope")])

    assert exit_code == 1
    assert "does not exist" in capsys.readouterr().err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'forge.cli'`

- [ ] **Step 3: Write minimal implementation**

```python
# forge/cli.py
import argparse
import subprocess
import sys
from pathlib import Path

import forge
from forge.scaffold.skeleton import create_tree, ensure_forge_dependency, retrofit_tree


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.path) / args.name
    if root.exists():
        print(f"error: {root} already exists", file=sys.stderr)
        return 1
    result = create_tree(root, args.name)
    ensure_forge_dependency(root, forge.__version__)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    print(f"created {len(result.created)} files/dirs in {root}")
    for path in result.created:
        print(f"  create {path.relative_to(root)}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 1
    result = retrofit_tree(root, root.resolve().name)
    dep_status = ensure_forge_dependency(root, forge.__version__)
    print(f"created {len(result.created)}, skipped {len(result.skipped)} (already present)")
    for path in result.created:
        print(f"  create {path.relative_to(root)}")
    for path in result.skipped:
        print(f"  skip   {path.relative_to(root)}")
    print(f"requirements.txt: {dep_status}")
    if result.unrecognized:
        print("unrecognized top-level entries (move into src/ manually):")
        for path in result.unrecognized:
            print(f"  ? {path.relative_to(root)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="scaffold a new project")
    new_parser.add_argument("name")
    new_parser.add_argument("--path", default=".")
    new_parser.set_defaults(func=cmd_new)

    init_parser = subparsers.add_parser("init", help="retrofit an existing project")
    init_parser.add_argument("--path", default=".")
    init_parser.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

Also add to `pyproject.toml`, directly below the `[project]` table's closing (after `classifiers`, before `dependencies` or after — anywhere at top level is valid TOML):

```toml
[project.scripts]
forge = "forge.cli:main"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_cli.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Reinstall in editable mode so the `forge` command picks up the new entry point, then verify manually**

Run: `pip install -e . && forge new /tmp/manual-check-project --path /tmp && ls /tmp/manual-check-project`
Expected: prints created file list, directory listing shows `src/`, `tests/`, `pyproject.toml`, etc.

- [ ] **Step 6: Commit**

```bash
git add forge/cli.py pyproject.toml tests/unit/test_cli.py
git commit -m "feat: add forge new/init CLI entry point"
```

---

### Task 4: Update README and CHANGELOG-adjacent docs for the new CLI

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing new — documents Task 3's `forge new` / `forge init` commands.

- [ ] **Step 1: Run the actual test count so the README stays accurate**

Run: `pytest tests/ --collect-only -q | tail -1`
Expected: a line like `54 tests collected in N.NNs` — note the number, it replaces the `34 unit tests` claim below.

- [ ] **Step 2: Add a "Scaffolding Projects" section**

Insert after the `## Modules` table (before `## Quick Start`) in `README.md`:

```markdown
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
```

- [ ] **Step 3: Update the Project Structure tree**

In the `## Project Structure` section, change:

```
├── forge/              # Installable package
│   ├── llm/            # LLM provider abstraction
│   ├── eval/           # Evaluation metrics
│   ├── viz/            # Visualization utilities
│   ├── data/           # Data loading, splitting, resampling
│   ├── report/         # HTML report builder
│   └── logging.py      # Structured logger
```

to:

```
├── forge/              # Installable package
│   ├── llm/            # LLM provider abstraction
│   ├── eval/           # Evaluation metrics
│   ├── viz/            # Visualization utilities
│   ├── data/           # Data loading, splitting, resampling
│   ├── report/         # HTML report builder
│   ├── scaffold/       # Project skeleton templates + create/retrofit logic
│   ├── cli.py          # `forge new` / `forge init` command entry point
│   └── logging.py      # Structured logger
```

And update the `tests/` line's unit test count to the number from Step 1:

```
├── tests/
│   └── unit/           # <N> unit tests, zero external deps
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: document forge new/init CLI in README"
```

---

## Self-Review Notes

- Spec coverage: `forge new` (Task 3), `forge init` (Task 3), non-destructive retrofit (Task 2 tests), unrecognized-entry reporting (Task 2 + 3), requirements.txt create/append/unchanged (Task 2), no new dependency (argparse/pathlib/dataclasses/subprocess only), README consistency rule (Task 4), version bump deferred to release (documented in Global Constraints, no task touches VERSION/CHANGELOG for the-forge itself) — all covered.
- Type consistency checked: `ScaffoldResult` fields (`created`, `skipped`, `unrecognized`) match usage in `cli.py` and all test files; `ensure_forge_dependency` return values (`"created"`/`"appended"`/`"unchanged"`) match test assertions and `cli.py` print statement.
