#!/usr/bin/env python3
"""
Example: Insert visualization with multiple helices.

Demonstrates how to visualize a complete magnet insert assembly
with multiple helical coils and their modelaxi zones.
"""

from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D

print("="*60)
print("Insert Visualization Example")
print("="*60)
print()

# Create 3 concentric helices
helices = []
for i in range(3):
    # Each helix has modelaxi with sum(pitch*turns) = 2*h
    # h=50-(i*5) → sum = 100-(i*10)
    h_val = 50.0 - (i * 5.0)
    n_middle_turns = 16 - (i * 2)
    
    modelaxi = ModelAxi(
        name=f"modelaxi_H{i+1}",
        h=h_val,
        turns=[2, n_middle_turns, 2],
        pitch=[5.0, 5.0, 5.0]
    )
    
    model3d = Model3D(name="", cad=f"H{i+1}", with_channels=False, with_shapes=False)
    
    helix = Helix(
        name=f"H{i+1}",
        r=[30.0 + i*15.0, 40.0 + i*15.0],  # Concentric layers
        z=[0.0, 100.0],
        cutwidth=3.0,
        odd=(i % 2 == 0),
        dble=False,
        modelaxi=modelaxi,
        model3d=model3d
    )
    helices.append(helix)
    print(f"Created {helix.name}: r={helix.r}, modelaxi.h={helix.modelaxi.h}")

# Create the Insert
insert = Insert(
    name="Example_Insert",
    helices=helices,
    rings=[],
    currentleads=[],
    hangles=[0.0] * len(helices),
    rangles=[],
    innerbore=25.0,
    outerbore=75.0
)

print(f"\nCreated Insert '{insert.name}' with {len(insert.helices)} helices")
print()

try:
    import matplotlib.pyplot as plt
    
    # Visualize the insert
    print("Generating visualization...")
    ax = insert.plot_axisymmetric(
        title=f"Insert Assembly: {insert.name}",
        figsize=(12, 14),
        show_modelaxi=True
    )
    
    plt.savefig("example_insert.png", dpi=150, bbox_inches='tight')
    print("✓ Saved visualization to example_insert.png")
    
    plt.close()
    
    print("\n" + "="*60)
    print("✓ Example completed successfully!")
    print("="*60)
    
except ImportError:
    print("! Matplotlib not installed")
    print("  Install with: pip install matplotlib")
