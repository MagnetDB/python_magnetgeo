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
import argparse
import python_magnetgeo as pmg

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
    # Ensure all YAML constructors are registered
    # This is needed because lazy loading doesn't import classes until accessed
    pmg.verify_class_registration()

    # Split input_file into basedir and basename
    basedir = os.path.dirname(input_file)
    basename = os.path.basename(input_file)

    # Change to basedir if it's not empty and not '.'
    if basedir and basedir != '.':
        print(f"Changing directory to: {basedir}")
        os.chdir(basedir)
        input_path = basename
    else:
        input_path = input_file

    print(f"Loading: {input_path}")

    # Load the object using getObject from utils
    object = pmg.load(input_path)
    logger.debug(object)

    print(f"Loaded: {type(object)}")
    print(f"Object: {object}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description='Check an YAML file.',
        epilog='Example: %(prog)s data/HL-31_H1.yaml'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input Helix YAML file'
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)

    try:
        check_yaml(args.input_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
