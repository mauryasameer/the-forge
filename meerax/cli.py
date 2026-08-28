from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import meerax
from meerax.doctor import run_checks
from meerax.release import bump_version
from meerax.scaffold.skeleton import create_tree, ensure_meerax_dependency, retrofit_tree

_STATUS_ICON = {"pass": "✓", "warn": "!", "fail": "✗"}


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.path) / args.name
    if root.exists():
        print(f"error: {root} already exists", file=sys.stderr)
        return 1
    result = create_tree(root, args.name)
    ensure_meerax_dependency(root, meerax.__version__)
    try:
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"error: git init failed: {exc}", file=sys.stderr)
        return 1
    print(f"created {len(result.created)} files/dirs in {root}")
    for path in result.created:
        print(f"  create {path.relative_to(root)}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 1
    result = retrofit_tree(root, root.resolve().name)
    dep_status = ensure_meerax_dependency(root, meerax.__version__)
    print(f"created {len(result.created)}, skipped {len(result.skipped)} (already present)")
    for path in result.created:
        print(f"  create {path.relative_to(root)}")
    for path in result.skipped:
        print(f"  skip   {path.relative_to(root)}")
    print(f"requirements.txt: {dep_status}")
    if result.unrecognized:
        print("unrecognized top-level entries (move into src/ manually):")
        for path in result.unrecognized:
            print(f"  ? {path.relative_to(root)}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.path)
    results = run_checks(root)
    for result in results:
        icon = _STATUS_ICON[result.status]
        print(f"  {icon} {result.name}: {result.message}")
    failures = [r for r in results if r.status == "fail"]
    warnings = [r for r in results if r.status == "warn"]
    print(f"{len(results) - len(failures) - len(warnings)} passed, {len(warnings)} warned, {len(failures)} failed")
    return 1 if failures else 0


def cmd_bump(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 1
    try:
        summary = bump_version(root, args.version)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(summary)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="meerax")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="scaffold a new project")
    new_parser.add_argument("name")
    new_parser.add_argument("--path", default=".")
    new_parser.set_defaults(func=cmd_new)

    init_parser = subparsers.add_parser("init", help="retrofit an existing project")
    init_parser.add_argument("--path", default=".")
    init_parser.set_defaults(func=cmd_init)

    doctor_parser = subparsers.add_parser("doctor", help="check a project against PROJECT_STANDARDS.md")
    doctor_parser.add_argument("--path", default=".")
    doctor_parser.set_defaults(func=cmd_doctor)

    bump_parser = subparsers.add_parser("bump", help="bump VERSION, README badge, and CHANGELOG heading")
    bump_parser.add_argument("version")
    bump_parser.add_argument("--path", default=".")
    bump_parser.set_defaults(func=cmd_bump)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
