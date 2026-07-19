from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import forge
from forge.scaffold.skeleton import create_tree, ensure_forge_dependency, retrofit_tree


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.path) / args.name
    if root.exists():
        print(f"error: {root} already exists", file=sys.stderr)
        return 1
    result = create_tree(root, args.name)
    ensure_forge_dependency(root, forge.__version__)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
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
    dep_status = ensure_forge_dependency(root, forge.__version__)
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="scaffold a new project")
    new_parser.add_argument("name")
    new_parser.add_argument("--path", default=".")
    new_parser.set_defaults(func=cmd_new)

    init_parser = subparsers.add_parser("init", help="retrofit an existing project")
    init_parser.add_argument("--path", default=".")
    init_parser.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
