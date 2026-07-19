# Forge Scaffold CLI

## Problem

Every ML project in `/Users/sameermaurya/Downloads/dev/` is meant to follow PROJECT_STANDARDS.md
(a fixed `src/{core,providers,services,utils,data}` + `tests/` + CI layout) and depend on
`sameer-forge` for shared LLM/eval/viz/report utilities. Today that layout is created by hand
per project, which is slow and drifts from the standard. There is also no repeatable way to
retrofit the standard layout onto an existing, non-empty project directory (e.g. the notebooks
under `Projects/`) without risking overwriting work already there.

## Goals

- One command to scaffold a brand-new project that is PROJECT_STANDARDS.md-compliant from the
  first commit and already depends on `sameer-forge`.
- One command to retrofit the same layout onto an existing project directory, additively —
  never touching or moving files that already exist.
- No new runtime dependency for the-forge package itself.

## Non-goals

- Migrating the six existing notebook projects — each gets its own follow-up design/plan that
  uses this CLI as a building block.
- Populating `src/` with actual business logic — the CLI creates structure and stub files only.

## Architecture

New `forge/scaffold/` subpackage inside the-forge repo:

- `forge/scaffold/templates.py` — Python string templates (f-strings / functions returning
  strings) for every generated file: `pyproject.toml`, `.github/workflows/ci.yml`, `.gitignore`,
  `conftest.py`, `README.md` stub, `CHANGELOG.md` seed entry, `VERSION` (`0.1.0`), `task.md`.
  Templates are plain Python, not files copied via `package_data` — this avoids MANIFEST.in /
  packaging edge cases when the package is installed via `pip install git+...`.
- `forge/scaffold/skeleton.py` — declares the directory/file skeleton as a data structure (list
  of dir paths, list of (path, template_fn) pairs) shared by both commands, plus the write logic:
  - `create_tree(root: Path) -> ScaffoldResult` — writes everything, used by `new`.
  - `retrofit_tree(root: Path) -> ScaffoldResult` — writes only what's missing, used by `init`.
  - `ScaffoldResult` records `created: list[Path]`, `skipped: list[Path]` (already existed),
    `unrecognized: list[Path]` (top-level files/dirs found in the target that aren't part of the
    skeleton and aren't `.git`/hidden — e.g. stray `*.ipynb`).
- `forge/cli.py` — argparse entry point, two subcommands:
  - `forge new <name> [--path DIR]`
  - `forge init [--path .]`
- `pyproject.toml` gains `[project.scripts] forge = "forge.cli:main"`.

## CLI behavior

### `forge new <name> [--path DIR]`

1. Resolve target dir: `DIR/<name>` (default `DIR` = cwd). Error if it already exists (non-empty
   or empty) — `new` is for creating a directory that doesn't exist yet; use `init` for existing
   dirs.
2. Call `create_tree`, writing the full skeleton described in PROJECT_STANDARDS.md section 1.
3. Write `requirements.txt` with `sameer-forge @ git+https://github.com/mauryasameer/the-forge.git@v<version>`,
   where `<version>` is `forge.__version__` read from the installed forge package at CLI runtime
   (so a project scaffolded with forge v0.2.0 pins to `v0.2.0`).
4. `git init` the new directory.
5. Print created file/dir list.

### `forge init [--path .]`

1. Target dir must already exist (default: cwd). Error if it does not.
2. Call `retrofit_tree`: for each skeleton dir/file, create it only if missing. Never overwrite
   or move an existing file — this includes `requirements.txt`, `pyproject.toml`, etc.
3. `requirements.txt` handling: if the file exists and does not already contain a `sameer-forge`
   dependency line, append one (same pinned-tag format as `new`). If it doesn't exist, create it
   with just that line.
4. Print a three-part summary: files/dirs **created**, files/dirs **already present** (skipped),
   and **unrecognized top-level entries** (e.g. `*.ipynb`, loose scripts) with a note to move them
   into `src/` manually per PROJECT_STANDARDS.md.
5. Does not `git init` — assumes the directory may or may not already be a repo; doesn't touch
   git state at all.

## Error handling

- `new` on an existing path → hard error, non-zero exit, no partial writes.
- `init` on a non-existent path → hard error, non-zero exit.
- Both commands are otherwise best-effort additive; a failure writing one file does not roll back
  files already written (acceptable — reruns are idempotent since existing files are skipped).

## Testing

`tests/unit/test_scaffold.py`:
- `create_tree` on an empty tmp dir produces every path in the skeleton.
- `retrofit_tree` on a tmp dir pre-populated with a subset of skeleton files only creates the
  missing ones; pre-existing file contents are byte-identical before/after.
- `retrofit_tree` run twice in a row is idempotent (second run creates nothing new, no errors).
- `retrofit_tree` on a dir containing an unrecognized file (e.g. `notes.ipynb`) reports it in
  `unrecognized` and does not move/delete it.
- `requirements.txt` dependency-line logic: appends when file exists without the line, creates
  when absent, no-ops when already present.

`tests/unit/test_cli.py`:
- `forge new` end-to-end via `argparse` invocation into a tmp dir, asserting directory created
  and `git init` ran (`.git` exists).
- `forge init` end-to-end, asserting summary output includes created/skipped/unrecognized
  sections.

## Versioning

New backward-compatible feature → MINOR bump: `0.1.0` → `0.2.0`. Branch `feature/scaffold-cli`
off `dev` (this branch), PR into `dev`, then release-merge `dev` → `main`, tag `v0.2.0`. Update
`CHANGELOG.md` and the `VERSION` file as part of the release commit, not this feature branch.
