import subprocess
import sys

from meerax.scaffold.skeleton import create_tree


def test_scaffolded_llm_report_template_passes_its_own_tests(tmp_path):
    """The strongest proof this template is a real, working example rather
    than speculative stub code: scaffold it for real and run the tests it
    generates, in a subprocess, exactly as a new project's own CI would."""
    root = tmp_path / "my-app"
    create_tree(root, "my-app", template="llm-report")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "3 passed" in result.stdout
