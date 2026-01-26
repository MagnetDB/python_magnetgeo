#!/usr/bin/env python3
"""
Test script demonstrating the get_required_files() dry-run functionality.

This script shows how to analyze a dictionary to identify which files
would be needed to create an object without actually loading them.
"""

from python_magnetgeo.Helix import Helix


def test_helix_with_file_references():
    """Test Helix with string references to external files."""
    print("=" * 70)
    print("Test 1: Helix with file references")
    print("=" * 70)

    helix_data = {
        "name": "H1",
        "r": [15.0, 25.0],
        "z": [0.0, 100.0],
        "cutwidth": 2.0,
        "odd": True,
        "dble": False,
        "modelaxi": "H1_modelaxi",  # Would load H1_modelaxi.yaml
        "model3d": "H1_model3d",  # Would load H1_model3d.yaml
        "shape": "H1_shape",  # Would load H1_shape.yaml
        "chamfers": ["chamfer1", "chamfer2"],  # Would load chamfer1.yaml, chamfer2.yaml
        "grooves": "H1_grooves",  # Would load H1_grooves.yaml
    }

    files = Helix.get_required_files(helix_data, debug=True)
    print("\nRequired files:")
    for f in sorted(files):
        print(f"  - {f}")
    print()


def test_helix_with_inline_objects():
    """Test Helix with inline dictionary definitions (no file loading)."""
    print("=" * 70)
    print("Test 2: Helix with inline objects")
    print("=" * 70)

    helix_data = {
        "name": "H2",
        "r": [20.0, 30.0],
        "z": [10.0, 110.0],
        "cutwidth": 2.5,
        "odd": False,
        "dble": True,
        "modelaxi": {  # Inline dict - no file to load
            "num": 10,
            "h": 8.0,
            "turns": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        },
        "model3d": {  # Inline dict - no file to load
            "with_shapes": False,
            "with_channels": False,
        },
        # shape, chamfers, grooves not specified (None)
    }

    files = Helix.get_required_files(helix_data, debug=True)
    print("\nRequired files:")
    if files:
        for f in sorted(files):
            print(f"  - {f}")
    else:
        print("  (none - all objects are inline)")
    print()


def test_helix_mixed():
    """Test Helix with both file references and inline objects."""
    print("=" * 70)
    print("Test 3: Helix with mixed references")
    print("=" * 70)

    helix_data = {
        "name": "H3",
        "r": [25.0, 35.0],
        "z": [20.0, 120.0],
        "cutwidth": 3.0,
        "odd": True,
        "dble": False,
        "modelaxi": "H3_modelaxi",  # File reference
        "model3d": {  # Inline dict
            "with_shapes": True,
            "with_channels": True,
        },
        "shape": {  # Inline dict (might have nested dependencies)
            "name": "rect",
            "width": 5.0,
            "height": 3.0,
        },
        "chamfers": [
            "chamfer1",  # File reference
            {  # Inline dict
                "name": "chamfer_inline",
                "dr": 1.0,
                "dz": 1.0,
            },
        ],
        "grooves": None,  # Not specified
    }

    files = Helix.get_required_files(helix_data, debug=True)
    print("\nRequired files:")
    if files:
        for f in sorted(files):
            print(f"  - {f}")
    else:
        print("  (none)")
    print()


if __name__ == "__main__":
    test_helix_with_file_references()
    test_helix_with_inline_objects()
    test_helix_mixed()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print("The get_required_files() method performs a dry-run analysis")
    print("to identify which YAML files would be needed to create an object")
    print("from a dictionary, without actually loading any files or creating")
    print("the object.")
    print()
    print("This is useful for:")
    print("  - Dependency analysis")
    print("  - Validation before loading")
    print("  - Understanding object structure")
    print("  - Pre-fetching files in distributed systems")
