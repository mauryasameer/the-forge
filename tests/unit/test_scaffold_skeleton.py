from meerax.scaffold.skeleton import GITKEEP_DIRS, create_tree, ensure_meerax_dependency, retrofit_tree

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
    ".github/dependabot.yml",
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


def test_create_tree_with_llm_report_template_adds_extra_files(tmp_path):
    root = tmp_path / "my-app"
    create_tree(root, "my-app", template="llm-report")

    assert (root / "src/services/narrative_service.py").is_file()
    assert (root / "src/services/report_service.py").is_file()
    assert (root / "src/app.py").is_file()
    assert (root / "tests/unit/test_narrative_service.py").is_file()
    assert (root / "tests/unit/test_report_service.py").is_file()
    assert (root / "tests/integration/test_pipeline.py").is_file()


def test_create_tree_rejects_unknown_template(tmp_path):
    import pytest

    with pytest.raises(ValueError, match="unknown template"):
        create_tree(tmp_path / "my-app", "my-app", template="not-a-real-template")


def test_retrofit_tree_with_llm_report_template_adds_extra_files(tmp_path):
    root = tmp_path / "existing-project"
    root.mkdir()

    retrofit_tree(root, "existing-project", template="llm-report")

    assert (root / "src/app.py").is_file()
    assert (root / "src/services/narrative_service.py").is_file()


def test_ensure_meerax_dependency_with_extras(tmp_path):
    status = ensure_meerax_dependency(tmp_path, "1.5.0", extras=["llm"])
    content = (tmp_path / "requirements.txt").read_text()

    assert status == "created"
    assert "meerax[llm]==1.5.0" in content


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


def test_ensure_meerax_dependency_creates_when_missing(tmp_path):
    status = ensure_meerax_dependency(tmp_path, "0.2.0")
    content = (tmp_path / "requirements.txt").read_text()

    assert status == "created"
    assert "meerax==0.2.0" in content


def test_ensure_meerax_dependency_appends_when_file_exists_without_it(tmp_path):
    (tmp_path / "requirements.txt").write_text("pandas>=2.2\n")
    status = ensure_meerax_dependency(tmp_path, "0.2.0")
    content = (tmp_path / "requirements.txt").read_text()

    assert status == "appended"
    assert "pandas>=2.2" in content
    assert "meerax" in content


def test_ensure_meerax_dependency_noop_when_already_present(tmp_path):
    (tmp_path / "requirements.txt").write_text("meerax==0.1.0\n")
    status = ensure_meerax_dependency(tmp_path, "0.2.0")

    assert status == "unchanged"


def test_gitkeep_files_excluded_from_result_symmetric(tmp_path):
    root = tmp_path / "proj"

    # First call: create tree from scratch
    result1 = create_tree(root, "proj")

    # Verify .gitkeep files exist on disk
    for rel_dir in GITKEEP_DIRS:
        assert (root / rel_dir / ".gitkeep").is_file(), f"{rel_dir}/.gitkeep should exist"

    # Verify .gitkeep files are NOT in result.created
    for path in result1.created:
        assert not path.name == ".gitkeep", f".gitkeep should not be in created: {path}"

    # Verify .gitkeep files are NOT in result.skipped
    for path in result1.skipped:
        assert not path.name == ".gitkeep", f".gitkeep should not be in skipped: {path}"

    # Second call: retrofit tree (should be idempotent)
    result2 = retrofit_tree(root, "proj")

    # Verify .gitkeep files still exist on disk
    for rel_dir in GITKEEP_DIRS:
        assert (root / rel_dir / ".gitkeep").is_file(), f"{rel_dir}/.gitkeep should still exist"

    # Verify .gitkeep files are NOT in result.created on second call
    for path in result2.created:
        assert not path.name == ".gitkeep", f".gitkeep should not be in created on retrofit: {path}"

    # Verify .gitkeep files are NOT in result.skipped on second call (critical fix)
    for path in result2.skipped:
        assert not path.name == ".gitkeep", f".gitkeep should not be in skipped on retrofit: {path}"
