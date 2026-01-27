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
from python_magnetgeo.Helix import Helix
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.utils import getObject

from python_magnetgeo.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

def split_helix_yaml(input_file):
    """
    Split an Helix YAML file into separate files for modelaxi and shape.

    Args:
        input_file: Path to the input Helix YAML file

    Returns:
        tuple: (helix_file, modelaxi_file, shape_file) - paths to the created files
    """
    print(f"Loading Helix from: {input_file}")

    # Load the Helix object using getObject from utils
    helix = getObject(input_file)
    logger.debug(helix)


    # Extract the base name (without directory and extension)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.dirname(input_file) or '.'

    # Define output file names
    modelaxi_filename = f"{base_name}_modelaxi"
    if helix.shape is not None:
        shape_filename = f"{base_name}_shape"
    helix_filename = f"{base_name}_split"

    modelaxi_file = os.path.join(output_dir, f"{modelaxi_filename}.yaml")
    shape_file = None
    if helix.shape is not None:
        shape_file = os.path.join(output_dir, f"{shape_filename}.yaml")
    helix_file = os.path.join(output_dir, f"{helix_filename}.yaml")

    # Save modelaxi object to separate file
    print(f"Writing modelaxi to: {modelaxi_file}")
    with open(modelaxi_file, 'w') as f:
        yaml.dump(helix.modelaxi, f, default_flow_style=False)

    # Save shape object to separate file
    if helix.shape is not None:
        print(f"Writing shape to: {shape_file}")
        with open(shape_file, 'w') as f:
            yaml.dump(helix.shape, f, default_flow_style=False)

    # Create a new Helix object with references to the files
    # Store the original objects for reference
    original_modelaxi = helix.modelaxi
    original_shape = helix.shape

    # Replace modelaxi and shape with string references (filenames without extension)
    helix.modelaxi = modelaxi_filename
    if helix.shape is not None:
        helix.shape = shape_filename

    # Save the modified Helix YAML
    print(f"Writing split Helix to: {helix_file}")
    with open(helix_file, 'w') as f:
        yaml.dump(helix, f, default_flow_style=False)

    # Restore original objects (in case the helix object is used later)
    helix.modelaxi = original_modelaxi
    if helix.shape is not None:
        helix.shape = original_shape

    print("\nSplit completed successfully!")
    print(f"  - ModelAxi: {modelaxi_file}")
    if helix.shape is not None:
        print(f"  - Shape: {shape_file}")
    print(f"  - Helix: {helix_file}")

    # Load back the Helix to verify
    print("\nVerifying by loading back the split Helix:")
    helix = getObject(helix_file)
    logger.debug(helix)

    return (helix_file, modelaxi_file, shape_file)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Error: Missing input file argument")
        print(f"\nUsage: {sys.argv[0]} <helix_yaml_file>")
        print(f"\nExample: {sys.argv[0]} data/HL-31_H1.yaml")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    try:
        split_helix_yaml(input_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
