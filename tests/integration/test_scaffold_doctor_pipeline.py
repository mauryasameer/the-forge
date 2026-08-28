from unittest.mock import MagicMock, patch

from meerax.cli import main
from meerax.doctor import run_checks


def test_a_freshly_scaffolded_and_released_project_passes_doctor(tmp_path):
    """A project scaffolded by `meerax new`, once given a LICENSE and a
    CHANGELOG entry for its own release, should pass every doctor check —
    scaffold and doctor drifting apart would break this."""
    root = tmp_path / "my-project"
    exit_code = main(["new", "my-project", "--path", str(tmp_path)])
    assert exit_code == 0

    (root / "LICENSE").write_text("MIT")
    (root / "CHANGELOG.md").write_text("## [0.1.0] - 2026-08-28\n### Added\n- Initial release\n")

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.read.return_value = b'{"info": {"version": "0.1.0"}}'
    with patch("meerax.doctor.urllib.request.urlopen", return_value=mock_resp):
        results = run_checks(root)

    failures = [r for r in results if r.status == "fail"]
    assert failures == []


def test_meerax_init_retrofit_also_passes_doctor(tmp_path):
    """`meerax init` retrofitting an existing directory should produce a
    layout that's just as doctor-clean as a fresh `meerax new`."""
    root = tmp_path / "existing-notebook-project"
    root.mkdir()
    (root / "analysis.ipynb").write_text("{}")

    exit_code = main(["init", "--path", str(root)])
    assert exit_code == 0

    (root / "LICENSE").write_text("MIT")
    (root / "CHANGELOG.md").write_text("## [0.1.0] - 2026-08-28\n### Added\n- Initial release\n")

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.read.return_value = b'{"info": {"version": "0.1.0"}}'
    with patch("meerax.doctor.urllib.request.urlopen", return_value=mock_resp):
        results = run_checks(root)

    failures = [r for r in results if r.status == "fail"]
    assert failures == []
