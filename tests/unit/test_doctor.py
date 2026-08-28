from unittest.mock import MagicMock, patch

from meerax.doctor import run_checks


def _write(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _result(results, name):
    return next(r for r in results if r.name == name)


def _pypi_response(version: str):
    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.read.return_value = f'{{"info": {{"version": "{version}"}}}}'.encode()
    return mock_resp


def test_single_python_version_passes_without_matrix(tmp_path):
    _write(tmp_path / ".github/workflows/ci.yml", 'python-version: "3.12"\n')
    result = _result(run_checks(tmp_path), "single-python-version")
    assert result.status == "pass"


def test_single_python_version_fails_with_matrix(tmp_path):
    _write(tmp_path / ".github/workflows/ci.yml", "python-version: [\"3.11\", \"3.12\"]\n")
    result = _result(run_checks(tmp_path), "single-python-version")
    assert result.status == "fail"


def test_single_python_version_warns_when_ci_missing(tmp_path):
    result = _result(run_checks(tmp_path), "single-python-version")
    assert result.status == "warn"


def test_no_planning_docs_passes_when_absent(tmp_path):
    result = _result(run_checks(tmp_path), "no-planning-docs")
    assert result.status == "pass"


def test_no_planning_docs_fails_when_docs_specs_present(tmp_path):
    _write(tmp_path / "docs/specs/design.md", "# design")
    result = _result(run_checks(tmp_path), "no-planning-docs")
    assert result.status == "fail"
    assert "docs/specs" in result.message


def test_no_planning_docs_fails_when_docs_plans_present(tmp_path):
    _write(tmp_path / "docs/plans/plan.md", "# plan")
    result = _result(run_checks(tmp_path), "no-planning-docs")
    assert result.status == "fail"
    assert "docs/plans" in result.message


def test_license_present_passes_when_license_exists(tmp_path):
    _write(tmp_path / "LICENSE", "MIT")
    result = _result(run_checks(tmp_path), "license-present")
    assert result.status == "pass"


def test_license_present_fails_when_missing(tmp_path):
    result = _result(run_checks(tmp_path), "license-present")
    assert result.status == "fail"


def test_version_consistency_passes_when_matching(tmp_path):
    _write(tmp_path / "VERSION", "1.2.3\n")
    _write(tmp_path / "README.md", "![Version](https://img.shields.io/badge/version-1.2.3-blue)\n")
    result = _result(run_checks(tmp_path), "version-consistency")
    assert result.status == "pass"


def test_version_consistency_fails_when_mismatched(tmp_path):
    _write(tmp_path / "VERSION", "1.2.3\n")
    _write(tmp_path / "README.md", "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n")
    result = _result(run_checks(tmp_path), "version-consistency")
    assert result.status == "fail"
    assert "1.2.3" in result.message
    assert "1.0.0" in result.message


def test_version_consistency_warns_when_version_file_missing(tmp_path):
    _write(tmp_path / "README.md", "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n")
    result = _result(run_checks(tmp_path), "version-consistency")
    assert result.status == "warn"


def test_changelog_entry_passes_when_present(tmp_path):
    _write(tmp_path / "VERSION", "1.2.3\n")
    _write(tmp_path / "CHANGELOG.md", "## [1.2.3] - 2026-08-28\n### Added\n- stuff\n")
    result = _result(run_checks(tmp_path), "changelog-entry")
    assert result.status == "pass"


def test_changelog_entry_fails_when_missing_entry(tmp_path):
    _write(tmp_path / "VERSION", "1.2.3\n")
    _write(tmp_path / "CHANGELOG.md", "## [1.0.0] - 2026-08-01\n### Added\n- stuff\n")
    result = _result(run_checks(tmp_path), "changelog-entry")
    assert result.status == "fail"


def test_meerax_pin_freshness_passes_when_current(tmp_path):
    _write(tmp_path / "requirements.txt", "meerax==1.2.3\nnumpy>=1.26\n")
    with patch("meerax.doctor.urllib.request.urlopen", return_value=_pypi_response("1.2.3")):
        result = _result(run_checks(tmp_path), "meerax-pin-freshness")
    assert result.status == "pass"


def test_meerax_pin_freshness_warns_when_stale(tmp_path):
    _write(tmp_path / "requirements.txt", "meerax==0.2.0\nnumpy>=1.26\n")
    with patch("meerax.doctor.urllib.request.urlopen", return_value=_pypi_response("1.2.3")):
        result = _result(run_checks(tmp_path), "meerax-pin-freshness")
    assert result.status == "warn"
    assert "0.2.0" in result.message
    assert "1.2.3" in result.message


def test_meerax_pin_freshness_handles_extras(tmp_path):
    _write(tmp_path / "requirements.txt", "meerax[llm,vision]==1.2.3\n")
    with patch("meerax.doctor.urllib.request.urlopen", return_value=_pypi_response("1.2.3")):
        result = _result(run_checks(tmp_path), "meerax-pin-freshness")
    assert result.status == "pass"


def test_meerax_pin_freshness_warns_when_pypi_unreachable(tmp_path):
    _write(tmp_path / "requirements.txt", "meerax==1.2.3\n")
    with patch("meerax.doctor.urllib.request.urlopen", side_effect=OSError("no network")):
        result = _result(run_checks(tmp_path), "meerax-pin-freshness")
    assert result.status == "warn"


def test_meerax_pin_freshness_warns_when_requirements_missing(tmp_path):
    result = _result(run_checks(tmp_path), "meerax-pin-freshness")
    assert result.status == "warn"


def test_dependabot_present_passes_when_targeting_dev(tmp_path):
    _write(tmp_path / ".github/dependabot.yml", 'version: 2\nupdates:\n  - target-branch: "dev"\n')
    result = _result(run_checks(tmp_path), "dependabot-present")
    assert result.status == "pass"


def test_dependabot_present_warns_when_missing(tmp_path):
    result = _result(run_checks(tmp_path), "dependabot-present")
    assert result.status == "warn"


def test_dependabot_present_fails_when_not_targeting_dev(tmp_path):
    _write(tmp_path / ".github/dependabot.yml", "version: 2\nupdates:\n  - package-ecosystem: pip\n")
    result = _result(run_checks(tmp_path), "dependabot-present")
    assert result.status == "fail"
    assert "target-branch" in result.message
