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
