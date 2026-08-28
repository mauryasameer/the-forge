from __future__ import annotations

import re
from datetime import date
from pathlib import Path

VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def bump_version(root: Path, new_version: str) -> str:
    """Bump VERSION, the README version badge, and insert a CHANGELOG heading.

    Only touches files that exist; each edit is idempotent (safe to re-run for
    the same version). Does not write CHANGELOG entry content or a compare-link
    footer — those need a human (or an AI assistant) who knows what changed.
    """
    if not VERSION_PATTERN.match(new_version):
        raise ValueError(f"not a valid X.Y.Z version: {new_version!r}")

    version_path = root / "VERSION"
    old_version = version_path.read_text().strip() if version_path.exists() else None
    version_path.write_text(f"{new_version}\n")
    updated = ["VERSION"]

    readme_path = root / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        new_content = re.sub(r"version-[0-9]+\.[0-9]+\.[0-9]+-", f"version-{new_version}-", content)
        if new_content != content:
            readme_path.write_text(new_content)
            updated.append("README.md badge")

    changelog_path = root / "CHANGELOG.md"
    if changelog_path.exists():
        content = changelog_path.read_text()
        if f"[{new_version}]" not in content:
            heading = f"## [{new_version}] - {date.today().isoformat()}\n"
            match = re.search(r"^## \[", content, flags=re.MULTILINE)
            if match:
                insert_at = match.start()
                content = content[:insert_at] + heading + "\n" + content[insert_at:]
            else:
                content = content.rstrip("\n") + f"\n\n{heading}"
            changelog_path.write_text(content)
            updated.append("CHANGELOG.md heading")

    return f"bumped {old_version or '(none)'} -> {new_version}: updated {', '.join(updated)}"
