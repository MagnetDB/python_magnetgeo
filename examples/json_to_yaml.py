#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Script to load a python_magnetgeo object from a JSON file and dump it to a YAML file.

The JSON file must contain a '__classname__' field to identify the object type.

Usage:
    python json_to_yaml.py file1.json [file2.json ...]

Example:
    python json_to_yaml.py data/helix.json
    python json_to_yaml.py data/*.json
"""

import sys
import json
import os
import glob
import argparse

import python_magnetgeo as pmg

pmg.verify_class_registration()  # Required for YAML loading

from python_magnetgeo.logging_config import get_logger

logger = get_logger(__name__)


def json_to_yaml(input_file: str) -> str:
    """
    Load a python_magnetgeo object from a JSON file and write it to a YAML file.

    Args:
        input_file: Path to the input JSON file (must contain '__classname__' field)

    Returns:
        Path to the output YAML file

    Raises:
        ValueError: If the JSON file does not contain a '__classname__' field
        Exception: If loading or writing fails
    """
    from python_magnetgeo.deserialize import unserialize_object

    basedir = os.path.dirname(os.path.abspath(input_file))
    basename = os.path.basename(input_file)

    cwd = os.getcwd()
    try:
        if basedir and basedir != cwd:
            logger.debug(f"Changing directory to: {basedir}")
            os.chdir(basedir)

        logger.debug(f"Loading JSON: {basename}")
        with open(basename, "r") as f:
            data = json.load(f)
            print(
                f"Loaded JSON data:\n{json.dumps(data, indent=2)}"
            )  # Debug print to verify content

        if "__classname__" not in data:
            raise ValueError(
                f"JSON file '{input_file}' does not contain a '__classname__' field. "
                "This field is required to identify the python_magnetgeo object type."
            )

        obj = unserialize_object(data)
        logger.debug(f"Loaded object of type: {type(obj).__name__}")

        name = getattr(obj, "name", None) or os.path.splitext(basename)[0]
        output_file = os.path.join(basedir, f"{name}.yaml")

        obj.write_to_yaml(directory=basedir)
        logger.info(f"Written YAML: {output_file}")
        return output_file

    finally:
        os.chdir(cwd)


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Load python_magnetgeo object(s) from JSON file(s) and dump to YAML.",
        epilog="Example: %(prog)s helix.json data/*.json",
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        help="Path(s) to input JSON file(s); glob patterns (e.g. 'data/*.json') are supported",
    )

    args = parser.parse_args()

    # Expand glob patterns and collect all matching files
    files = []
    for pattern in args.input_files:
        matched = glob.glob(pattern)
        if matched:
            files.extend(matched)
        else:
            print(f"Warning: no files matched: {pattern}", file=sys.stderr)

    if not files:
        print("Error: no input files found.", file=sys.stderr)
        sys.exit(1)

    errors = 0
    for input_file in files:
        try:
            output = json_to_yaml(input_file)
            print(f"{input_file} -> {output}")
        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            import traceback

            traceback.print_exc()
            errors += 1

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
