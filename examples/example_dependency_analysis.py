#!/usr/bin/env python3
"""
Real-world example: Analyze file dependencies from configurations.

This demonstrates using get_required_files() on magnet geometry
configurations to understand dependencies before loading.
"""

from python_magnetgeo.Helix import Helix


def create_example_with_file_refs():
    """
    Create an example dictionary with file references to show the analysis.
    """
    print("=" * 70)
    print("Example 1: Helix configuration with file references")
    print("=" * 70)

    example_data = {
        "name": "HL-31_H1",
        "r": [19.3, 24.2],
        "z": [-226, 108],
        "cutwidth": 0.22,
        "odd": True,
        "dble": True,
        "modelaxi": "HL-31_H1_modelaxi",  # Would load file
        "model3d": "HL-31_H1_model3d",  # Would load file
        "shape": "HL-31_H1_shape",  # Would load file
        "chamfers": None,
        "grooves": None,
    }

    print("Configuration:")
    for key, value in example_data.items():
        if key in ["modelaxi", "model3d", "shape", "chamfers", "grooves"]:
            print(f"  {key}: {value}")

    print("\nDry-run analysis:")
    files = Helix.get_required_files(example_data, debug=True)

    print("\nFiles that would be loaded:")
    for f in sorted(files):
        print(f"  - {f}")

    print()
    return files


def create_example_inline():
    """
    Example with inline definitions - no files needed.
    """
    print("=" * 70)
    print("Example 2: Helix configuration with inline objects")
    print("=" * 70)

    example_data = {
        "name": "HL-31_H2",
        "r": [24.2, 29.0],
        "z": [108, 442],
        "cutwidth": 0.22,
        "odd": False,
        "dble": True,
        "modelaxi": {  # Inline - no file
            "num": 20,
            "h": 86.51,
            "turns": [0.29] * 20,
        },
        "model3d": {  # Inline - no file
            "with_shapes": False,
            "with_channels": False,
        },
        "shape": None,
        "chamfers": None,
        "grooves": None,
    }

    print("Configuration has inline definitions for modelaxi and model3d")

    print("\nDry-run analysis:")
    files = Helix.get_required_files(example_data, debug=True)

    print("\nFiles that would be loaded:")
    if files:
        for f in sorted(files):
            print(f"  - {f}")
    else:
        print("  (none - all objects are inline or None)")

    print()
    return files


def create_example_mixed():
    """
    Example with both file refs and inline objects.
    """
    print("=" * 70)
    print("Example 3: Mixed file references and inline objects")
    print("=" * 70)

    example_data = {
        "name": "HR-insert",
        "r": [30.0, 40.0],
        "z": [0, 200],
        "cutwidth": 1.5,
        "odd": True,
        "dble": False,
        "modelaxi": "HR_modelaxi",  # File reference
        "model3d": {  # Inline
            "with_shapes": True,
            "with_channels": True,
        },
        "shape": "HR_shape",  # File reference
        "chamfers": [
            "chamfer_top",  # File reference
            {  # Inline
                "name": "chamfer_bottom",
                "dr": 1.0,
                "dz": 1.0,
            },
        ],
        "grooves": {  # Inline
            "gtype": "rint",
            "n": 12,
            "eps": 2.0,
        },
    }

    print("Configuration has:")
    print("  - modelaxi: file reference")
    print("  - model3d: inline dict")
    print("  - shape: file reference")
    print("  - chamfers: mixed (1 file + 1 inline)")
    print("  - grooves: inline dict")

    print("\nDry-run analysis:")
    files = Helix.get_required_files(example_data, debug=True)

    print("\nFiles that would be loaded:")
    for f in sorted(files):
        print(f"  - {f}")

    print()
    return files


if __name__ == "__main__":
    # Show examples with different scenarios
    files1 = create_example_with_file_refs()
    files2 = create_example_inline()
    files3 = create_example_mixed()

    print("=" * 70)
    print("Use Cases for get_required_files()")
    print("=" * 70)
    print("1. PRE-FLIGHT VALIDATION")
    print("   Check if all required files exist before loading:")
    import os

    print("\n   Checking files from Example 1:")
    for f in sorted(files1):
        exists = os.path.exists(f)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"     {status}: {f}")

    print("\n2. DEPENDENCY ANALYSIS")
    print("   Understand configuration structure before loading")
    print("   - Example 1: 3 file dependencies")
    print("   - Example 2: 0 file dependencies (all inline)")
    print("   - Example 3: 3 file dependencies (mixed)")

    print("\n3. PERFORMANCE OPTIMIZATION")
    print("   - Pre-fetch files in distributed systems")
    print("   - Parallel download from remote storage")
    print("   - Cache invalidation strategies")

    print("\n4. ERROR PREVENTION")
    print("   - Detect missing files early")
    print("   - Avoid partial object construction")
    print("   - Better error messages")

    print("\n" + "=" * 70)
    print("Key Benefits")
    print("=" * 70)
    print("• No file I/O during analysis (dry-run)")
    print("• Recursive dependency detection")
    print("• Works with mixed file/inline configs")
    print("• Available for all geometry classes")
    print("• Enables validation pipelines")

