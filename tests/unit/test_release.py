from meerax.release import bump_version


def _write(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_bump_writes_version_file(tmp_path):
    bump_version(tmp_path, "1.2.3")
    assert (tmp_path / "VERSION").read_text() == "1.2.3\n"


def test_bump_updates_existing_version_file(tmp_path):
    _write(tmp_path / "VERSION", "1.0.0\n")
    bump_version(tmp_path, "1.1.0")
    assert (tmp_path / "VERSION").read_text() == "1.1.0\n"


def test_bump_updates_readme_badge(tmp_path):
    _write(
        tmp_path / "README.md",
        "# my-project\n\n![Version](https://img.shields.io/badge/version-1.0.0-blue)\n",
    )
    bump_version(tmp_path, "1.1.0")
    content = (tmp_path / "README.md").read_text()
    assert "version-1.1.0-blue" in content
    assert "version-1.0.0-blue" not in content


def test_bump_leaves_other_readme_content_untouched(tmp_path):
    _write(
        tmp_path / "README.md",
        "# my-project\n\n![Version](https://img.shields.io/badge/version-1.0.0-blue)\n\nSome body text.\n",
    )
    bump_version(tmp_path, "2.0.0")
    content = (tmp_path / "README.md").read_text()
    assert "Some body text." in content


def test_bump_inserts_changelog_heading_before_existing_entries(tmp_path):
    _write(
        tmp_path / "CHANGELOG.md",
        "# Changelog\n\nAll notable changes.\n\n## [1.0.0] - 2026-01-01\n### Added\n- initial\n",
    )
    bump_version(tmp_path, "1.1.0")
    content = (tmp_path / "CHANGELOG.md").read_text()
    lines = content.splitlines()
    new_idx = next(i for i, line in enumerate(lines) if line == "## [1.1.0] - " + _today())
    old_idx = next(i for i, line in enumerate(lines) if line.startswith("## [1.0.0]"))
    assert new_idx < old_idx


def test_bump_appends_changelog_heading_when_no_existing_entries(tmp_path):
    _write(tmp_path / "CHANGELOG.md", "# Changelog\n\nAll notable changes.\n")
    bump_version(tmp_path, "0.1.0")
    content = (tmp_path / "CHANGELOG.md").read_text()
    assert f"## [0.1.0] - {_today()}" in content


def test_bump_is_idempotent_for_changelog_heading(tmp_path):
    _write(tmp_path / "CHANGELOG.md", "# Changelog\n\n")
    bump_version(tmp_path, "1.0.0")
    first = (tmp_path / "CHANGELOG.md").read_text()
    bump_version(tmp_path, "1.0.0")
    second = (tmp_path / "CHANGELOG.md").read_text()
    assert first == second
    assert second.count("## [1.0.0]") == 1


def test_bump_returns_summary_mentioning_old_and_new_version(tmp_path):
    _write(tmp_path / "VERSION", "1.0.0\n")
    summary = bump_version(tmp_path, "2.0.0")
    assert "1.0.0" in summary
    assert "2.0.0" in summary


def test_bump_skips_missing_readme_and_changelog(tmp_path):
    summary = bump_version(tmp_path, "1.0.0")
    assert (tmp_path / "VERSION").read_text() == "1.0.0\n"
    assert "1.0.0" in summary


def test_bump_rejects_invalid_version_string(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        bump_version(tmp_path, "not-a-version")


def _today() -> str:
    from datetime import date

    return date.today().isoformat()
