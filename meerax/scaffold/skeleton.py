from dataclasses import dataclass, field
from pathlib import Path

from meerax.scaffold import templates

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

MAIN_FILES = {
    "pyproject.toml": lambda name: templates.pyproject_toml(name),
    ".github/workflows/ci.yml": lambda name: templates.ci_yml(),
    ".gitignore": lambda name: templates.gitignore(),
    "conftest.py": lambda name: templates.conftest_py(),
    "README.md": lambda name: templates.readme_md(name),
    "CHANGELOG.md": lambda name: templates.changelog_md(),
    "VERSION": lambda name: templates.version_file(),
    "task.md": lambda name: templates.task_md(name),
    "src/data/.gitignore": lambda name: templates.data_gitignore(),
}

GITKEEP_FILES = {f"{d}/.gitkeep": (lambda name: "") for d in GITKEEP_DIRS}

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

MEERAX_DEP_MARKER = "meerax"
MEERAX_REPO_URL = "https://github.com/mauryasameer/the-forge.git"


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
    for rel_file, template_fn in MAIN_FILES.items():
        file_path = root / rel_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(template_fn(project_name))
        result.created.append(file_path)
    for rel_file, template_fn in GITKEEP_FILES.items():
        file_path = root / rel_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(template_fn(project_name))
        # .gitkeep files are written to disk but not tracked in result
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
    for rel_file, template_fn in MAIN_FILES.items():
        file_path = root / rel_file
        if file_path.exists():
            result.skipped.append(file_path)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(template_fn(project_name))
            result.created.append(file_path)
    for rel_file, template_fn in GITKEEP_FILES.items():
        file_path = root / rel_file
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(template_fn(project_name))
        # .gitkeep files are written to disk but never tracked in result
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


def ensure_meerax_dependency(root: Path, version: str) -> str:
    dep_line = f"meerax @ git+{MEERAX_REPO_URL}@v{version}\n"
    req_path = root / "requirements.txt"
    if not req_path.exists():
        req_path.write_text(dep_line)
        return "created"
    content = req_path.read_text()
    if MEERAX_DEP_MARKER in content:
        return "unchanged"
    if content and not content.endswith("\n"):
        content += "\n"
    req_path.write_text(content + dep_line)
    return "appended"
