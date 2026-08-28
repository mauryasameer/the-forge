from meerax.scaffold import templates


def test_pyproject_toml_includes_project_name():
    content = templates.pyproject_toml("my-project")
    assert 'name = "my-project"' in content
    assert 'target-version = "py312"' in content
    assert 'requires-python = ">=3.12"' in content
    assert 'build-backend = "setuptools.build_meta"' in content


def test_ci_yml_calls_the_shared_reusable_workflow():
    content = templates.ci_yml()
    assert "uses: mauryasameer/the-forge/.github/workflows/reusable-ci.yml@main" in content
    assert "matrix" not in content


def test_dependabot_yml_configures_pip_and_github_actions():
    content = templates.dependabot_yml()
    assert 'package-ecosystem: "pip"' in content
    assert 'package-ecosystem: "github-actions"' in content
    assert 'interval: "weekly"' in content


def test_dependabot_yml_targets_dev_not_main():
    content = templates.dependabot_yml()
    assert content.count('target-branch: "dev"') == 2


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
