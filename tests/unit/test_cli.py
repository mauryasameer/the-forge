from meerax.cli import main


def test_new_creates_project_and_git_repo(tmp_path):
    exit_code = main(["new", "my-project", "--path", str(tmp_path)])
    root = tmp_path / "my-project"

    assert exit_code == 0
    assert (root / "src" / "core").is_dir()
    assert (root / ".git").is_dir()
    assert "meerax" in (root / "requirements.txt").read_text()


def test_new_fails_if_directory_already_exists(tmp_path, capsys):
    (tmp_path / "my-project").mkdir()
    exit_code = main(["new", "my-project", "--path", str(tmp_path)])

    assert exit_code == 1
    assert "already exists" in capsys.readouterr().err


def test_new_with_llm_report_template_pins_llm_extra(tmp_path):
    exit_code = main(["new", "my-app", "--path", str(tmp_path), "--template", "llm-report"])
    root = tmp_path / "my-app"

    assert exit_code == 0
    assert (root / "src" / "app.py").is_file()
    assert "meerax[llm]==" in (root / "requirements.txt").read_text()


def test_new_rejects_unrecognized_template(tmp_path, capsys):
    import pytest

    with pytest.raises(SystemExit):
        main(["new", "my-app", "--path", str(tmp_path), "--template", "not-real"])
    assert "invalid choice" in capsys.readouterr().err


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


def test_doctor_exits_zero_on_a_freshly_scaffolded_project(tmp_path, monkeypatch):
    from unittest.mock import MagicMock

    root = tmp_path / "my-project"
    main(["new", "my-project", "--path", str(tmp_path)])
    (root / "LICENSE").write_text("MIT")
    (root / "CHANGELOG.md").write_text("## [0.1.0] - 2026-08-28\n### Added\n- Initial release\n")

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.read.return_value = b'{"info": {"version": "1.0.1"}}'
    monkeypatch.setattr("meerax.doctor.urllib.request.urlopen", lambda *a, **k: mock_resp)

    exit_code = main(["doctor", "--path", str(root)])

    assert exit_code == 0


def test_doctor_exits_nonzero_when_planning_docs_present(tmp_path, capsys):
    root = tmp_path / "existing"
    (root / "docs" / "specs").mkdir(parents=True)
    (root / "docs" / "specs" / "design.md").write_text("# design")

    exit_code = main(["doctor", "--path", str(root)])
    out = capsys.readouterr().out

    assert exit_code == 1
    assert "no-planning-docs" in out


def test_bump_updates_version_and_prints_summary(tmp_path, capsys):
    (tmp_path / "VERSION").write_text("1.0.0\n")

    exit_code = main(["bump", "1.1.0", "--path", str(tmp_path)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert (tmp_path / "VERSION").read_text() == "1.1.0\n"
    assert "1.0.0" in out
    assert "1.1.0" in out


def test_bump_fails_on_invalid_version(tmp_path, capsys):
    exit_code = main(["bump", "not-a-version", "--path", str(tmp_path)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "not-a-version" in err


def test_bump_fails_if_directory_missing(tmp_path, capsys):
    exit_code = main(["bump", "1.0.0", "--path", str(tmp_path / "nope")])

    assert exit_code == 1
    assert "does not exist" in capsys.readouterr().err
