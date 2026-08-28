from collections.abc import Callable
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
    ".github/dependabot.yml": lambda name: templates.dependabot_yml(),
    ".gitignore": lambda name: templates.gitignore(),
    "conftest.py": lambda name: templates.conftest_py(),
    "README.md": lambda name: templates.readme_md(name),
    "CHANGELOG.md": lambda name: templates.changelog_md(),
    "VERSION": lambda name: templates.version_file(),
    "task.md": lambda name: templates.task_md(name),
    "src/data/.gitignore": lambda name: templates.data_gitignore(),
}

GITKEEP_FILES = {f"{d}/.gitkeep": (lambda name: "") for d in GITKEEP_DIRS}

@dataclass
class ProjectTemplate:
    extras: list[str]
    files: dict[str, Callable[[str], str]]


TEMPLATES: dict[str, ProjectTemplate] = {
    "llm-report": ProjectTemplate(
        extras=["llm"],
        files={
            "src/services/narrative_service.py": lambda name: templates.llm_report_narrative_service_py(),
            "src/services/report_service.py": lambda name: templates.llm_report_report_service_py(),
            "src/app.py": lambda name: templates.llm_report_app_py(name),
            "tests/unit/test_narrative_service.py": lambda name: templates.llm_report_test_narrative_service_py(),
            "tests/unit/test_report_service.py": lambda name: templates.llm_report_test_report_service_py(),
            "tests/integration/test_pipeline.py": lambda name: templates.llm_report_test_pipeline_py(),
        },
    ),
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

MEERAX_DEP_MARKER = "meerax"


@dataclass
class ScaffoldResult:
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    unrecognized: list[Path] = field(default_factory=list)


def _template_files(template: str | None) -> dict[str, Callable[[str], str]]:
    if template is None:
        return {}
    if template not in TEMPLATES:
        raise ValueError(f"unknown template: {template!r} (available: {sorted(TEMPLATES)})")
    return TEMPLATES[template].files


def create_tree(root: Path, project_name: str, template: str | None = None) -> ScaffoldResult:
    template_files = _template_files(template)
    root.mkdir(parents=True, exist_ok=False)
    result = ScaffoldResult()
    for rel_dir in ALL_DIRS:
        dir_path = root / rel_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        result.created.append(dir_path)
    for rel_file, template_fn in {**MAIN_FILES, **template_files}.items():
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


def retrofit_tree(root: Path, project_name: str, template: str | None = None) -> ScaffoldResult:
    template_files = _template_files(template)
    result = ScaffoldResult()
    for rel_dir in ALL_DIRS:
        dir_path = root / rel_dir
        if dir_path.exists():
            result.skipped.append(dir_path)
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            result.created.append(dir_path)
    for rel_file, template_fn in {**MAIN_FILES, **template_files}.items():
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


def ensure_meerax_dependency(root: Path, version: str, extras: list[str] | None = None) -> str:
    extras_suffix = f"[{','.join(extras)}]" if extras else ""
    dep_line = f"meerax{extras_suffix}=={version}\n"
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
