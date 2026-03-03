#!/usr/bin/env python3
"""
Test Insert visualization with multiple helices.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D

print("="*60)
print("Insert Visualization Test")
print("="*60)
print()

# Create helices for the insert
# h=50.0 → sum(pitch*turns) = 100.0
modelaxi1 = ModelAxi(
    name="modelaxi_H1",
    h=50.0,
    turns=[2, 16, 2],
    pitch=[5.0, 5.0, 5.0]
)

model3d1 = Model3D(name="", cad="H1", with_channels=False, with_shapes=False)

helix1 = Helix(
    name="H1",
    r=[30.0, 40.0],
    z=[0.0, 100.0],
    cutwidth=3.0,
    odd=True,
    dble=False,
    modelaxi=modelaxi1,
    model3d=model3d1
)

# h=45.0 → sum(pitch*turns) = 90.0
modelaxi2 = ModelAxi(
    name="modelaxi_H2",
    h=45.0,
    turns=[2, 14, 2],
    pitch=[5.0, 5.0, 5.0]
)

model3d2 = Model3D(name="", cad="H2", with_channels=False, with_shapes=False)

helix2 = Helix(
    name="H2",
    r=[45.0, 55.0],
    z=[0.0, 100.0],
    cutwidth=3.0,
    odd=False,
    dble=False,
    modelaxi=modelaxi2,
    model3d=model3d2
)

# h=40.0 → sum(pitch*turns) = 80.0
modelaxi3 = ModelAxi(
    name="modelaxi_H3",
    h=40.0,
    turns=[2, 12, 2],
    pitch=[5.0, 5.0, 5.0]
)

model3d3 = Model3D(name="", cad="H3", with_channels=False, with_shapes=False)

helix3 = Helix(
    name="H3",
    r=[60.0, 70.0],
    z=[0.0, 100.0],
    cutwidth=3.0,
    odd=True,
    dble=False,
    modelaxi=modelaxi3,
    model3d=model3d3
)

# Create Insert
insert = Insert(
    name="Test_Insert",
    helices=[helix1, helix2, helix3],
    rings=[],
    currentleads=[],
    hangles=[0.0, 0.0, 0.0],
    rangles=[],
    innerbore=25.0,
    outerbore=75.0
)

print(f"Created Insert: {insert.name}")
print(f"  Number of helices: {len(insert.helices)}")
for i, h in enumerate(insert.helices):
    print(f"    {i+1}. {h.name}: r={h.r}, z={h.z}")
print()

try:
    import matplotlib.pyplot as plt
    
    # Test 1: Insert with modelaxi zones
    print("Test 1: Insert with ModelAxi zones")
    ax = insert.plot_axisymmetric(
        title=f"Insert: {insert.name} (with ModelAxi zones)",
        figsize=(12, 14)
    )
    plt.savefig("test_insert_with_modelaxi.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved as test_insert_with_modelaxi.png")
    plt.close()
    
    # Test 2: Insert without modelaxi zones
    print("\nTest 2: Insert without ModelAxi zones")
    ax = insert.plot_axisymmetric(
        title=f"Insert: {insert.name} (main bodies only)",
        show_modelaxi=False,
        figsize=(12, 14)
    )
    plt.savefig("test_insert_no_modelaxi.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved as test_insert_no_modelaxi.png")
    plt.close()
    
    # Test 3: Insert with custom colors
    print("\nTest 3: Insert with custom helix colors")
    ax = insert.plot_axisymmetric(
        title=f"Insert: {insert.name} (custom colors)",
        helix_colors=['darkblue', 'darkred', 'darkgreen'],
        helix_alpha=0.7,
        figsize=(12, 14)
    )
    plt.savefig("test_insert_custom_colors.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved as test_insert_custom_colors.png")
    plt.close()
    
    print("\n" + "="*60)
    print("✓ All Insert visualization tests passed!")
    print("="*60)
    
except ImportError:
    print("! Matplotlib not installed - skipping visualization tests")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
