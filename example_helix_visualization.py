#!/usr/bin/env python3
"""
Comprehensive example showing Helix with modelaxi zone visualization.

Demonstrates:
1. Single Helix with modelaxi zone
2. Helix without modelaxi zone
3. Combined Helix + Ring + Screen assembly
"""

from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.Screen import Screen
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D

print("="*60)
print("Helix + ModelAxi Visualization Example")
print("="*60)
print()

# Create a Helix with modelaxi
# Note: sum(pitch * turns) must equal 2*h
# h=50.0 → sum = 100.0
# 2*5 + 16*5 + 2*5 = 10 + 80 + 10 = 100 ✓
modelaxi = ModelAxi(
    name="modelaxi_H1",
    h=50.0,
    turns=[2, 16, 2],
    pitch=[5.0, 5.0, 5.0]
)

model3d = Model3D(
    with_channels=False,
    with_shapes=False,
    cad="example"
)

helix = Helix(
    name="H1",
    r=[50.0, 60.0],
    z=[0.0, 100.0],
    cutwidth=5.0,
    odd=True,
    dble=False,
    modelaxi=modelaxi,
    model3d=model3d
)

print("Created Helix:")
print(f"  Name: {helix.name}")
print(f"  Radial extent: {helix.r[0]} to {helix.r[1]} mm")
print(f"  Axial extent: {helix.z[0]} to {helix.z[1]} mm")
print(f"  ModelAxi zone: -{helix.modelaxi.h} to +{helix.modelaxi.h} mm")
print()

try:
    import matplotlib.pyplot as plt
    
    # Example 1: Helix with modelaxi zone
    print("Example 1: Helix with ModelAxi zone")
    ax = helix.plot_axisymmetric(
        title="Helix H1 with ModelAxi Zone",
        figsize=(10, 12)
    )
    plt.savefig("example_helix_with_modelaxi.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved to example_helix_with_modelaxi.png")
    plt.close()
    
    # Example 2: Helix without modelaxi zone
    print("\nExample 2: Helix without ModelAxi zone")
    ax = helix.plot_axisymmetric(
        title="Helix H1 (Main Body Only)",
        show_modelaxi=False,
        figsize=(10, 12)
    )
    plt.savefig("example_helix_without_modelaxi.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved to example_helix_without_modelaxi.png")
    plt.close()
    
    # Example 3: Complete assembly with Helix, Ring, and Screen
    print("\nExample 3: Complete magnet assembly")
    
    # Create Ring
    ring = Ring(
        name="Ring_H1H2",
        r=[50.0, 55.0, 60.0, 65.0],
        z=[110.0, 130.0]
    )
    
    # Create Screen
    inner_screen = Screen(
        name="Inner_Shield",
        r=[40.0, 45.0],
        z=[-20.0, 150.0]
    )
    
    outer_screen = Screen(
        name="Outer_Shield",
        r=[70.0, 75.0],
        z=[-20.0, 150.0]
    )
    
    # Combined plot
    fig, ax = plt.subplots(figsize=(12, 14))
    
    # Plot screens (background)
    inner_screen.plot_axisymmetric(
        ax=ax,
        color='lightgray',
        alpha=0.3,
        show_legend=False
    )
    outer_screen.plot_axisymmetric(
        ax=ax,
        color='lightgray',
        alpha=0.3,
        show_legend=False
    )
    
    # Plot helix with modelaxi zone
    helix.plot_axisymmetric(
        ax=ax,
        color='darkgreen',
        alpha=0.6,
        modelaxi_color='orange',
        modelaxi_alpha=0.25,
        show_legend=False
    )
    
    # Plot ring
    ring.plot_axisymmetric(
        ax=ax,
        color='steelblue',
        alpha=0.6,
        show_legend=False
    )
    
    ax.set_title("Magnet Assembly: Helix + Ring + Screens", 
                 fontsize=14, fontweight='bold')
    
    # Add legend manually
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='darkgreen', alpha=0.6, label='Helix'),
        Patch(facecolor='orange', alpha=0.25, label='ModelAxi Zone'),
        Patch(facecolor='steelblue', alpha=0.6, label='Ring'),
        Patch(facecolor='lightgray', alpha=0.3, hatch='///', label='Screen')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.savefig("example_complete_assembly.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved to example_complete_assembly.png")
    plt.close()
    
    print("\n" + "="*60)
    print("✓ All examples completed successfully!")
    print("Check the generated PNG files:")
    print("  - example_helix_with_modelaxi.png")
    print("  - example_helix_without_modelaxi.png")
    print("  - example_complete_assembly.png")
    print("="*60)
    
except ImportError:
    print("! Matplotlib not installed")
    print("  Install with: pip install matplotlib")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
