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
