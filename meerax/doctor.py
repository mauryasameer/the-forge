from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

PYPI_URL = "https://pypi.org/pypi/meerax/json"
PYPI_TIMEOUT = 3.0


@dataclass
class CheckResult:
    name: str
    status: str  # "pass" | "warn" | "fail"
    message: str


def check_single_python_version(root: Path) -> CheckResult:
    ci_path = root / ".github" / "workflows" / "ci.yml"
    if not ci_path.exists():
        return CheckResult("single-python-version", "warn", "no .github/workflows/ci.yml found")
    content = ci_path.read_text()
    if re.search(r"python-version:\s*\[[^\]]*,", content):
        return CheckResult("single-python-version", "fail", "ci.yml declares a Python version matrix")
    return CheckResult("single-python-version", "pass", "no Python version matrix in ci.yml")


def check_no_planning_docs(root: Path) -> CheckResult:
    offenders = [rel for rel in ("docs/specs", "docs/plans") if (root / rel).exists()]
    if offenders:
        return CheckResult("no-planning-docs", "fail", f"found: {', '.join(offenders)}")
    return CheckResult("no-planning-docs", "pass", "no docs/specs or docs/plans directory")


def check_license_present(root: Path) -> CheckResult:
    if any((root / name).exists() for name in ("LICENSE", "LICENSE.txt", "LICENSE.md")):
        return CheckResult("license-present", "pass", "LICENSE file found")
    return CheckResult("license-present", "fail", "no LICENSE file at repo root")


def check_version_consistency(root: Path) -> CheckResult:
    version_path = root / "VERSION"
    readme_path = root / "README.md"
    if not version_path.exists():
        return CheckResult("version-consistency", "warn", "no VERSION file found")
    version = version_path.read_text().strip()
    if not readme_path.exists():
        return CheckResult("version-consistency", "warn", "no README.md found")
    match = re.search(r"version-([0-9]+\.[0-9]+\.[0-9]+)-", readme_path.read_text())
    if not match:
        return CheckResult("version-consistency", "warn", "no version badge found in README.md")
    if match.group(1) != version:
        return CheckResult(
            "version-consistency",
            "fail",
            f"VERSION is {version} but README badge shows {match.group(1)}",
        )
    return CheckResult("version-consistency", "pass", f"VERSION and README badge both {version}")


def check_changelog_entry(root: Path) -> CheckResult:
    version_path = root / "VERSION"
    changelog_path = root / "CHANGELOG.md"
    if not version_path.exists() or not changelog_path.exists():
        return CheckResult("changelog-entry", "warn", "VERSION or CHANGELOG.md missing")
    version = version_path.read_text().strip()
    if f"[{version}]" not in changelog_path.read_text():
        return CheckResult("changelog-entry", "fail", f"no CHANGELOG.md entry for {version}")
    return CheckResult("changelog-entry", "pass", f"CHANGELOG.md has an entry for {version}")


def check_meerax_pin_freshness(root: Path) -> CheckResult:
    requirements_path = root / "requirements.txt"
    if not requirements_path.exists():
        return CheckResult("meerax-pin-freshness", "warn", "no requirements.txt found")
    match = re.search(r"meerax(?:\[[^\]]*\])?==([0-9]+\.[0-9]+\.[0-9]+)", requirements_path.read_text())
    if not match:
        return CheckResult("meerax-pin-freshness", "warn", "no pinned meerax==<version> dependency found")
    pinned = match.group(1)
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=PYPI_TIMEOUT) as resp:
            latest = json.loads(resp.read())["info"]["version"]
    except (urllib.error.URLError, OSError, TimeoutError):
        return CheckResult("meerax-pin-freshness", "warn", "could not reach PyPI to check the latest meerax version")
    if pinned != latest:
        return CheckResult(
            "meerax-pin-freshness",
            "warn",
            f"pinned to meerax=={pinned}, latest is {latest}",
        )
    return CheckResult("meerax-pin-freshness", "pass", f"pinned to latest meerax=={latest}")


def check_dependabot_present(root: Path) -> CheckResult:
    dependabot_path = root / ".github" / "dependabot.yml"
    if not dependabot_path.exists():
        return CheckResult("dependabot-present", "warn", "no .github/dependabot.yml found")
    if 'target-branch: "dev"' not in dependabot_path.read_text():
        return CheckResult(
            "dependabot-present",
            "fail",
            "dependabot.yml found but doesn't set target-branch: dev — PRs will target main directly",
        )
    return CheckResult("dependabot-present", "pass", "dependabot.yml found, targets dev")


CHECKS = [
    check_single_python_version,
    check_no_planning_docs,
    check_license_present,
    check_version_consistency,
    check_changelog_entry,
    check_meerax_pin_freshness,
    check_dependabot_present,
]


def run_checks(root: Path) -> list[CheckResult]:
    return [check(root) for check in CHECKS]
