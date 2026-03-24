#!/usr/bin/env python3
"""
find_helix_by_cad.py

Search a directory of python_magnetgeo YAML config files for Helix (or other Part)
definitions whose CAD reference matches a given value.

Usage:
    python find_helix_by_cad.py <yaml_dir> [cad_reference]
    python find_helix_by_cad.py /data/magnetgeo/configs "HL-31-xxx.brep"
    python find_helix_by_cad.py /data/magnetgeo/configs   # list all CAD refs

Optional flags:
    --type helix|ring|bitter|all    restrict search to a Part type (default: all)
    --field cad|model3d|modelaxi    restrict which CAD field to inspect (default: all)
    --recursive                     walk subdirectories
"""

import argparse
import csv
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

import python_magnetgeo as pmg
pmg.verify_class_registration()  # Required for YAML loading


# Map of Part type → where to look for a CAD reference in the object attributes.
# Each entry is a list of dotted attribute paths tried in order.
CAD_FIELD_MAP = {
    "helix":  ["model3d.cad", "modelaxi.cad", "cad"],
    "ring":   ["cad"],
    "bitter": ["model3d.cad", "modelaxi.cad", "cad"],
    "screen": ["cad"],
    "lead":   ["cad"],
    "supra":  ["cad"],
}

CLASSNAME_TO_TYPE = {
    "Helix":            "helix",
    "Ring":             "ring",
    "Bitter":           "bitter",
    "BitterMagnet":     "bitter",
    "Screen":           "screen",
    "InnerCurrentLead": "lead",
    "CurrentLead":      "lead",
    "Supra":            "supra",
}


def get_nested_attr(obj, dotted_path: str):
    """Traverse nested object attributes with a dotted path. Returns None if missing."""
    node = obj
    for part in dotted_path.split("."):
        if node is None:
            return None
        node = getattr(node, part, None)
    return node


def extract_cad_refs(obj, part_type: str) -> dict[str, str]:
    """Return {field_path: value} for all CAD fields found in obj for the given part_type."""
    found = {}
    for path in CAD_FIELD_MAP.get(part_type, ["cad"]):
        val = get_nested_attr(obj, path)
        if val:
            found[path] = val
    return found


def detect_part_type(obj) -> str | None:
    """Infer Part type from object class name."""
    return CLASSNAME_TO_TYPE.get(type(obj).__name__)


def search(yaml_dir: Path, cad_ref: str | None, type_filter: str, recursive: bool) -> list[dict]:
    pattern = "**/*.yaml" if recursive else "*.yaml"
    matches = []

    for yaml_file in sorted(yaml_dir.glob(pattern)):
        try:
            obj = pmg.load(str(yaml_file.resolve()))
        except Exception as e:
            print(f"  [warn] could not load {yaml_file}: {e}", file=sys.stderr)
            continue

        part_type = detect_part_type(obj)
        if part_type is None:
            continue

        if type_filter != "all" and part_type != type_filter:
            continue

        cad_refs = extract_cad_refs(obj, part_type)
        for field_path, value in cad_refs.items():
            # If no cad_ref given, collect all; otherwise support substring match
            if cad_ref is None or cad_ref in value or value in cad_ref:
                matches.append({
                    "file":      yaml_file,
                    "part_type": part_type,
                    "field":     field_path,
                    "cad_value": value,
                    "name":      getattr(obj, "name", "<unnamed>"),
                })

    return matches


def main():
    parser = argparse.ArgumentParser(description="Find YAML configs by CAD reference")
    parser.add_argument("--yaml_dir",    help="Directory containing YAML config files")
    parser.add_argument("--cad_ref",     nargs="?", default=None,
                        help="CAD reference string to look for (omit to list all)")
    parser.add_argument("--type",      default="all",
                        choices=["helix", "ring", "bitter", "screen", "lead", "supra", "all"],
                        help="Restrict search to a specific Part type")
    parser.add_argument("--field",     default=None,
                        help="Restrict to a specific field path (e.g. model3d.cad)")
    parser.add_argument("--recursive", action="store_true",
                        help="Walk subdirectories")
    parser.add_argument("--output", default="cad_refs.csv",
                        help="Output CSV file (default: cad_refs.csv)")
    args = parser.parse_args()

    yaml_dir = Path(args.yaml_dir)
    if not yaml_dir.is_dir():
        print(f"Error: {yaml_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    results = search(yaml_dir, args.cad_ref, args.type, args.recursive)

    # Optional: filter by specific field
    if args.field:
        results = [r for r in results if r["field"] == args.field]

    if not results:
        msg = f"No matches found for CAD ref: {args.cad_ref!r}" if args.cad_ref else "No CAD refs found."
        print(msg)
        sys.exit(0)

    title = f"Found {len(results)} match(es) for {args.cad_ref!r}" if args.cad_ref else f"Found {len(results)} CAD ref(s)"
    table = Table(title=title, show_lines=True)
    table.add_column("File", style="cyan", no_wrap=False)
    table.add_column("Name", style="green")
    table.add_column("Part Type", style="magenta")
    table.add_column("CAD Value", style="yellow")
    for r in results:
        table.add_row(str(r["file"]), r["name"], r["part_type"], r["cad_value"])
    Console().print(table)

    csv_path = Path(args.output)
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "name", "part_type", "cad_value"])
        writer.writeheader()
        writer.writerows({"file": r["file"], "name": r["name"], "part_type": r["part_type"], "cad_value": r["cad_value"]} for r in results)
    print(f"Results saved to {csv_path}")

if __name__ == "__main__":
    main()
