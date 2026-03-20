#!/usr/bin/env python3
"""
Test loading Helix from YAML files with 'axi' and 'm3d' field names.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from python_magnetgeo.Helix import Helix

print("="*60)
print("Testing Helix YAML Loading (axi/m3d compatibility)")
print("="*60)
print()

# Test loading from actual YAML file
yaml_file = "data/HL-31_H1.yaml"

try:
    print(f"Loading Helix from {yaml_file}...")
    helix = Helix.from_yaml(yaml_file)
    
    print(f"✓ Successfully loaded: {helix.name}")
    print(f"  Radial extent: {helix.r}")
    print(f"  Axial extent: {helix.z}")
    print(f"  Cutwidth: {helix.cutwidth}")
    print(f"  Has ModelAxi: {helix.modelaxi is not None}")
    if helix.modelaxi:
        print(f"    ModelAxi h: {helix.modelaxi.h}")
        print(f"    ModelAxi turns: {len(helix.modelaxi.turns)} sections")
    print(f"  Has Model3D: {helix.model3d is not None}")
    if helix.model3d:
        print(f"    Model3D cad: {helix.model3d.cad}")
        print(f"    With channels: {helix.model3d.with_channels}")
        print(f"    With shapes: {helix.model3d.with_shapes}")
    print()
    
    # Try visualization
    try:
        import matplotlib.pyplot as plt
        print("Testing visualization...")
        ax = helix.plot_axisymmetric(title=f"Helix: {helix.name}")
        plt.savefig("test_helix_from_yaml.png", dpi=150, bbox_inches='tight')
        print("✓ Visualization saved to test_helix_from_yaml.png")
        plt.close()
    except ImportError:
        print("! Matplotlib not installed - skipping visualization")
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)
    
except FileNotFoundError:
    print(f"✗ File not found: {yaml_file}")
    print("  Trying alternative file...")
    
    # Try another file
    import os
    yaml_files = [f for f in os.listdir('data') if f.startswith('HL-31_H') and f.endswith('.yaml')]
    if yaml_files:
        yaml_file = f"data/{yaml_files[0]}"
        print(f"\nLoading from {yaml_file}...")
        helix = Helix.from_yaml(yaml_file)
        print(f"✓ Successfully loaded: {helix.name}")
    else:
        print("  No suitable YAML files found")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
