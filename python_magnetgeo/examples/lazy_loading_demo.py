#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Demonstration of lazy loading in python_magnetgeo.

This script shows different patterns for using lazy loading to:
1. Reduce initial import time
2. Load only needed classes
3. Work efficiently with YAML files
4. Access package-level utilities

Usage:
    python lazy_loading_demo.py
"""

import sys
import time


def demo_basic_lazy_loading():
    """Demonstrate basic lazy loading pattern."""
    print("=" * 60)
    print("Demo 1: Basic Lazy Loading")
    print("=" * 60)

    # Time the initial import
    start = time.time()
    import python_magnetgeo as pmg
    import_time = time.time() - start

    print(f"✓ Package imported in {import_time*1000:.2f}ms")
    print("  (Only core utilities loaded, not geometry classes)")

    # Access a class (triggers lazy import)
    start = time.time()
    helix_class = pmg.Helix
    helix_time = time.time() - start

    print(f"✓ Helix class loaded in {helix_time*1000:.2f}ms")

    # Second access is instant (cached)
    start = time.time()
    helix_class2 = pmg.Helix
    cached_time = time.time() - start

    print(f"✓ Helix class (cached) accessed in {cached_time*1000:.2f}ms")
    print()


def demo_yaml_loading():
    """Demonstrate YAML loading with lazy loading."""
    print("=" * 60)
    print("Demo 2: YAML Loading Pattern")
    print("=" * 60)

    import python_magnetgeo as pmg

    print("Step 1: Register YAML constructors")
    pmg.verify_class_registration()
    print("✓ All geometry classes registered for YAML parsing")

    print("\nStep 2: Load YAML file (example)")
    print("  helix = pmg.load('data/HL-31_H1.yaml')")
    print("  # This would load the Helix from YAML")

    print("\nAlternative: Type-specific loading (no registration needed)")
    print("  helix = pmg.Helix.from_yaml('data/HL-31_H1.yaml')")
    print("  # Accessing pmg.Helix triggers import automatically")
    print()


def demo_selective_loading():
    """Demonstrate loading only needed classes."""
    print("=" * 60)
    print("Demo 3: Selective Class Loading")
    print("=" * 60)

    import python_magnetgeo as pmg

    print("Scenario: Working only with Helix and Ring")
    print()

    # Access only the classes you need
    print("Loading only Helix and Ring classes...")
    helix_class = pmg.Helix
    ring_class = pmg.Ring

    print(f"✓ {helix_class.__name__} available")
    print(f"✓ {ring_class.__name__} available")

    # Other classes remain unloaded
    print("\nOther classes (Bitter, Supra, etc.) remain unloaded")
    print("  → Saves memory and import time")
    print()


def demo_package_utilities():
    """Demonstrate package-level utility functions."""
    print("=" * 60)
    print("Demo 4: Package Utilities")
    print("=" * 60)

    import python_magnetgeo as pmg

    print("Available utilities:")
    print()

    print("1. Loading functions:")
    print("   - pmg.load(filename)        # Load YAML/JSON")
    print("   - pmg.loadObject(filename)  # Legacy alias")
    print()

    print("2. Class registration:")
    print("   - pmg.verify_class_registration()")
    print("   - pmg.list_registered_classes()")
    print()

    print("3. Logging:")
    print("   - pmg.configure_logging(level=pmg.INFO)")
    print("   - pmg.get_logger(__name__)")
    print("   - pmg.set_level(pmg.DEBUG)")
    print()

    # List available geometry classes
    print("4. Available geometry classes:")
    geometry_classes = [
        'Insert', 'Helix', 'Ring', 'Bitter', 'Supra', 'Screen',
        'Shape', 'Profile', 'ModelAxi', 'Model3D', 'Chamfer', 'Groove'
    ]
    for cls_name in geometry_classes:
        if hasattr(pmg, cls_name):
            print(f"   ✓ pmg.{cls_name}")
    print()


def demo_best_practices():
    """Show recommended patterns."""
    print("=" * 60)
    print("Demo 5: Best Practices")
    print("=" * 60)

    print("\n✓ RECOMMENDED: Import package once")
    print("   import python_magnetgeo as pmg")
    print("   pmg.verify_class_registration()  # For YAML loading")
    print("   obj = pmg.load('config.yaml')")
    print()

    print("✓ GOOD: Type-specific loading")
    print("   from python_magnetgeo import Helix")
    print("   helix = Helix.from_yaml('helix.yaml')")
    print()

    print("⚠ DISCOURAGED: Importing all classes explicitly")
    print("   from python_magnetgeo import Helix, Ring, Insert, ...")
    print("   # Defeats the purpose of lazy loading")
    print()

    print("⚠ AVOID: Multiple imports")
    print("   from python_magnetgeo.Helix import Helix")
    print("   from python_magnetgeo.Ring import Ring")
    print("   # Use package-level access instead")
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Python MagnetGeo - Lazy Loading Demo" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    demos = [
        demo_basic_lazy_loading,
        demo_yaml_loading,
        demo_selective_loading,
        demo_package_utilities,
        demo_best_practices
    ]

    for i, demo in enumerate(demos, 1):
        demo()
        if i < len(demos):
            input("Press Enter to continue...")
            print()

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("For more information, see:")
    print("  - README.md (Quick Start section)")
    print("  - python_magnetgeo/__init__.py (implementation)")
    print("  - examples/check_magnetgeo_yaml.py (practical example)")
    print()


if __name__ == "__main__":
    main()
