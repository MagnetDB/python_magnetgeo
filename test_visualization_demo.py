#!/usr/bin/env python3
"""
Demo script to test the new visualization capabilities for Ring and Screen.

This script demonstrates:
1. Creating Ring and Screen objects
2. Using the plot_axisymmetric() method
3. Customizing plot appearance
4. Creating subplot layouts
"""

import sys
from pathlib import Path

# Add parent directory to path to import python_magnetgeo
sys.path.insert(0, str(Path(__file__).parent))

import pytest

from python_magnetgeo.Ring import Ring
from python_magnetgeo.Screen import Screen

# Skip all tests in this module if matplotlib is not installed
pytest.importorskip("matplotlib")

def test_ring_visualization():
    """Test Ring visualization"""
    import matplotlib.pyplot as plt
    
    print("Testing Ring visualization...")
    
    # Create a few ring objects (r values must be in ascending order)
    ring1 = Ring(
        name="R1",
        r=[100.0, 110.0, 120.0, 130.0],
        z=[0.0, 30.0]
    )
    
    ring2 = Ring(
        name="R2",
        r=[100.0, 110.0, 120.0, 130.0],
        z=[80.0, 110.0],
        n=8,
        angle=20.0
    )
    
    ring3 = Ring(
        name="R3",
        r=[100.0, 110.0, 120.0, 130.0],
        z=[160.0, 190.0]
    )
    
    # Test 1: Single ring plot
    print("  - Creating single ring plot...")
    ax = ring1.plot_axisymmetric(title="Single Ring")
    plt.savefig("test_ring_single.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_ring_single.png")
    
    # Test 2: Multiple rings on same axes
    print("  - Creating multiple rings plot...")
    fig, ax = plt.subplots(figsize=(8, 10))
    ring1.plot_axisymmetric(ax=ax, color='steelblue', show_legend=False)
    ring2.plot_axisymmetric(ax=ax, color='coral', show_legend=False)
    ring3.plot_axisymmetric(ax=ax, color='seagreen', show_legend=False)
    ax.set_title("Multiple Rings", fontsize=14, fontweight='bold')
    plt.savefig("test_rings_multiple.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_rings_multiple.png")
    
    print("✓ Ring visualization tests passed!\n")


def test_screen_visualization():
    """Test Screen visualization"""
    import matplotlib.pyplot as plt
    
    print("Testing Screen visualization...")
    
    # Create screen objects
    screen1 = Screen(
        name="Inner_Shield",
        r=[50.0, 60.0],
        z=[0.0, 200.0]
    )
    
    screen2 = Screen(
        name="Outer_Shield",
        r=[150.0, 160.0],
        z=[-50.0, 250.0]
    )
    
    # Test 1: Single screen plot
    print("  - Creating single screen plot...")
    ax = screen1.plot_axisymmetric(title="Magnetic Screen")
    plt.savefig("test_screen_single.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_screen_single.png")
    
    # Test 2: Multiple screens
    print("  - Creating multiple screens plot...")
    fig, ax = plt.subplots(figsize=(8, 10))
    screen1.plot_axisymmetric(ax=ax, color='lightgray', show_legend=False)
    screen2.plot_axisymmetric(ax=ax, color='silver', show_legend=False)
    ax.set_title("Multiple Screens", fontsize=14, fontweight='bold')
    plt.savefig("test_screens_multiple.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_screens_multiple.png")
    
    print("✓ Screen visualization tests passed!\n")


def test_combined_visualization():
    """Test combined Ring and Screen visualization"""
    import matplotlib.pyplot as plt
    
    print("Testing combined Ring + Screen visualization...")
    
    # Create rings (r values in ascending order)
    ring1 = Ring("R1", [100.0, 110.0, 120.0, 130.0], [50.0, 80.0])
    ring2 = Ring("R2", [100.0, 110.0, 120.0, 130.0], [120.0, 150.0])
    
    # Create screens
    inner_screen = Screen("Inner_Screen", [80.0, 90.0], [0.0, 200.0])
    outer_screen = Screen("Outer_Screen", [140.0, 150.0], [0.0, 200.0])
    
    # Combined plot
    print("  - Creating combined plot...")
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Plot screens first (background)
    inner_screen.plot_axisymmetric(ax=ax, color='lightgray', alpha=0.3, show_legend=False)
    outer_screen.plot_axisymmetric(ax=ax, color='lightgray', alpha=0.3, show_legend=False)
    
    # Plot rings on top
    ring1.plot_axisymmetric(ax=ax, color='steelblue', alpha=0.6, show_legend=False)
    ring2.plot_axisymmetric(ax=ax, color='coral', alpha=0.6, show_legend=False)
    
    ax.set_title("Magnet Assembly: Rings + Screens", fontsize=14, fontweight='bold')
    plt.savefig("test_combined.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_combined.png")
    
    print("✓ Combined visualization test passed!\n")


def main():
    """Run all visualization tests"""
    print("="*60)
    print("Ring and Screen Visualization Demo")
    print("="*60)
    print()
    
    test_ring_visualization()
    test_screen_visualization()
    test_combined_visualization()
    
    print("="*60)
    print("✓ All visualization tests completed!")
    print("Check the generated PNG files for visual results.")
    print("="*60)


if __name__ == "__main__":
    main()
