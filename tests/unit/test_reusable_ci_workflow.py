from pathlib import Path

WORKFLOW_PATH = Path(__file__).parent.parent.parent / ".github" / "workflows" / "reusable-ci.yml"


def _content() -> str:
    return WORKFLOW_PATH.read_text()


def test_reusable_ci_workflow_exists():
    assert WORKFLOW_PATH.exists()


def test_reusable_ci_workflow_is_callable():
    content = _content()
    assert "workflow_call" in content


def test_reusable_ci_workflow_uses_single_python_version_not_a_matrix():
    content = _content()
    assert "matrix" not in content
    assert 'default: "3.12"' in content


def test_reusable_ci_workflow_pins_ruff_version():
    content = _content()
    assert 'default: "0.11.13"' in content


def test_reusable_ci_workflow_installs_pytest_for_test_job():
    content = _content()
    assert "pip install -r requirements.txt pytest==8.*" in content
    assert "pytest tests/unit/" in content
    assert "pytest tests/integration/" in content


def test_reusable_ci_workflow_runs_meerax_doctor():
    content = _content()
    assert "meerax doctor" in content
