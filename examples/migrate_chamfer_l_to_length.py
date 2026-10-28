#!/usr/bin/env python3
"""
Migrate Chamfer YAML files: rename the 'l' key to 'length'.

Applies only inside !<Chamfer> blocks, leaving all other YAML content
untouched.  Run with --dry-run first to preview changes.

Usage:
    python migrate_chamfer_l_to_length.py path/to/file.yaml
    python migrate_chamfer_l_to_length.py path/to/dir/
    python migrate_chamfer_l_to_length.py --dry-run path/to/dir/
"""

import argparse
import re
import sys
from pathlib import Path


def migrate_content(content: str) -> tuple[str, int]:
    """
    Replace 'l:' with 'length:' inside every !<Chamfer> block.

    Returns (new_content, number_of_replacements).
    """
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    changes = 0

    in_chamfer = False
    content_indent: int | None = None  # indent of the first key inside the block

    for line in lines:
        stripped = line.lstrip()
        line_indent = len(line) - len(stripped)

        # ── enter a Chamfer block ──────────────────────────────────────────
        # Matches both "!<Chamfer>" and "- !<Chamfer>" (list items)
        if "!<Chamfer>" in line:
            in_chamfer = True
            content_indent = None
            result.append(line)
            continue

        # ── track / exit the current Chamfer block ─────────────────────────
        if in_chamfer and stripped and not stripped.startswith("#"):
            if content_indent is None:
                content_indent = line_indent          # first real key sets the baseline

            if stripped.startswith("!<") or line_indent < content_indent:
                in_chamfer = False
                content_indent = None

        # ── apply replacement inside the block ────────────────────────────
        if in_chamfer:
            new_line = re.sub(r"^(\s*)l:\s", r"\1length: ", line)
            if new_line != line:
                changes += 1
                line = new_line

        result.append(line)

    return "".join(result), changes


def migrate_file(path: Path, dry_run: bool) -> int:
    """Migrate one file; return number of replacements made."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  ERROR reading {path}: {exc}", file=sys.stderr)
        return 0

    new_content, n = migrate_content(content)
    if n == 0:
        return 0

    label = "Would update" if dry_run else "Updated"
    suffix = "s" if n != 1 else ""
    print(f"{label}: {path}  ({n} replacement{suffix})")

    if not dry_run:
        path.write_text(new_content, encoding="utf-8")

    return n


def collect_yaml_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(path.rglob("*.yaml"))
            files.extend(path.rglob("*.yml"))
        else:
            files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", metavar="PATH", help="YAML files or directories")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    files = collect_yaml_files(args.paths)
    if not files:
        print("No YAML files found.")
        return

    total = sum(migrate_file(f, dry_run=args.dry_run) for f in files)

    if total == 0:
        print("No Chamfer 'l:' keys found — nothing to do.")
    elif args.dry_run:
        print(f"\n{total} replacement(s) would be made. Re-run without --dry-run to apply.")
    else:
        print(f"\n{total} replacement(s) applied.")


if __name__ == "__main__":
    main()
