from forge.scaffold import templates


def test_pyproject_toml_includes_project_name():
    content = templates.pyproject_toml("my-project")
    assert 'name = "my-project"' in content
    assert 'target-version = "py312"' in content
    assert 'requires-python = ">=3.12"' in content
    assert 'build-backend = "setuptools.build_meta"' in content


def test_ci_yml_uses_single_python_version_not_a_matrix():
    content = templates.ci_yml()
    assert "matrix" not in content
    assert 'python-version: "3.12"' in content


def test_ci_yml_pins_ruff_version():
    content = templates.ci_yml()
    assert "ruff==0.11.13" in content
    assert "pytest tests/unit/" in content
    assert "pytest tests/integration/" in content


def test_ci_yml_installs_pytest_for_test_job():
    content = templates.ci_yml()
    assert "pip install -r requirements.txt pytest==8.*" in content


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
