#!/usr/bin/env python3
"""
Simple example demonstrating the new visualization features for Ring and Screen.

Usage:
    python example_visualization.py
"""

from python_magnetgeo.Ring import Ring
from python_magnetgeo.Screen import Screen

# Example 1: Visualize a single Ring
print("Example 1: Single Ring visualization")
ring = Ring(
    name="Ring_H1H2",
    r=[19.3, 24.2, 25.1, 30.7],  # 4 radii in ascending order
    z=[0, 20],                    # axial bounds
    n=6,                          # 6 cooling slits
    angle=46                      # each 46 degrees wide
)

# Plot it - matplotlib is optional
try:
    import matplotlib.pyplot as plt
    ax = ring.plot_axisymmetric(title="Example Ring")
    plt.savefig("example_ring.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved visualization to example_ring.png")
    plt.close()
except ImportError:
    print("  ! Matplotlib not installed - skipping visualization")

# Example 2: Visualize a single Screen
print("\nExample 2: Single Screen visualization")
screen = Screen(
    name="Magnetic_Shield",
    r=[50.0, 60.0],     # inner and outer radius
    z=[0.0, 200.0]      # axial extent
)

try:
    import matplotlib.pyplot as plt
    ax = screen.plot_axisymmetric(title="Example Screen")
    plt.savefig("example_screen.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved visualization to example_screen.png")
    plt.close()
except ImportError:
    print("  ! Matplotlib not installed - skipping visualization")

# Example 3: Combined visualization
print("\nExample 3: Combined Ring + Screen visualization")
try:
    import matplotlib.pyplot as plt
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Plot screen (background)
    screen.plot_axisymmetric(
        ax=ax, 
        color='lightgray', 
        alpha=0.3,
        show_legend=False
    )
    
    # Plot ring (foreground)
    ring.plot_axisymmetric(
        ax=ax, 
        color='steelblue', 
        alpha=0.7,
        show_legend=False
    )
    
    ax.set_title("Magnet Assembly", fontsize=14, fontweight='bold')
    plt.savefig("example_combined.png", dpi=150, bbox_inches='tight')
    print("  ✓ Saved visualization to example_combined.png")
    plt.close()
    
except ImportError:
    print("  ! Matplotlib not installed - skipping visualization")

print("\n✓ All examples completed!")
print("\nNote: The visualization feature is optional and requires matplotlib.")
print("Install with: pip install matplotlib")
