#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Script to split an Helix YAML file into separate files for modelaxi and shape objects.

This script:
1. Loads an Helix YAML file
2. Writes separate YAML files for:
   - Helix.modelaxi object (saved as <helix_name>_modelaxi.yaml)
   - Helix.shape object (saved as <helix_name>_shape.yaml)
3. Creates a new Helix YAML file where:
   - modelaxi is the name of the corresponding modelaxi yaml file without extension
   - shape is the name of the corresponding shape yaml file without extension

Usage:
    python split_helix_yaml.py <helix_yaml_file>

Example:
    python split_helix_yaml.py data/HL-31_H1.yaml
"""

import sys
import yaml
import os
import glob
import argparse

import python_magnetgeo as pmg
pmg.verify_class_registration()  # Required for YAML loading


from python_magnetgeo.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

def check_yaml(input_file):
    """
    Load magnetgeo YAML file.

    Args:
        input_file: Path to the input YAML file

    Returns:
    """
    # Split input_file into basedir and basename
    basedir = os.path.dirname(input_file)
    basename = os.path.basename(input_file)

    # Change to basedir if it's not empty and not '.'
    if basedir and basedir != '.':
        logger.debug(f"Changing directory to: {basedir}")
        os.chdir(basedir)
        input_path = basename
    else:
        input_path = input_file

    logger.debug(f"Loading: {input_path}")

    # Load the object using getObject from utils
    object = pmg.load(input_path)
    logger.debug(object)

    # print(f"Loaded: {type(object)}")
    # print(f"Object: {object}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description='Check an YAML file.',
        epilog='Example: %(prog)s data/HL-31_H1.yaml data/*.yaml'
    )
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Path(s) to input YAML file(s); glob patterns (e.g. "data/*.yaml") are supported'
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
            check_yaml(input_file)
        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            import traceback
            traceback.print_exc()
            errors += 1

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
