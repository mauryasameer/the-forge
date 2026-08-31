from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"


def _content(name: str) -> str:
    return (WORKFLOWS_DIR / name).read_text()


def test_checks_workflow_is_callable():
    assert "workflow_call" in _content("_checks.yml")


def test_checks_workflow_runs_both_unit_and_integration_tests():
    content = _content("_checks.yml")
    assert "tests/unit/" in content
    assert "tests/integration/" in content


def test_checks_workflow_pins_mypy_to_an_exact_version():
    content = _content("_checks.yml")
    assert '"mypy==2.3.1"' in content
    assert "pip install mypy==2.3.1" not in content
    assert ">=1.10" not in content


def test_ci_workflow_calls_shared_checks():
    content = _content("ci.yml")
    assert "uses: ./.github/workflows/_checks.yml" in content


def test_release_workflow_depends_on_checks_before_publishing():
    content = _content("release.yml")
    assert "uses: ./.github/workflows/_checks.yml" in content
    assert "needs: checks" in content


def test_benchmarks_workflow_is_manual_only_not_a_required_check():
    content = _content("benchmarks.yml")
    assert "workflow_dispatch" in content
    assert "push:" not in content
    assert "pull_request:" not in content
