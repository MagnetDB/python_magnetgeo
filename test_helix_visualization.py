#!/usr/bin/env python3
"""
Test script for Helix visualization with modelaxi zone.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import pytest

from python_magnetgeo.Helix import Helix
from python_magnetgeo.ModelAxi import ModelAxi

# Skip all tests in this module if matplotlib is not installed
pytest.importorskip("matplotlib")

def test_helix_visualization():
    """Test Helix visualization with modelaxi zone"""
    import matplotlib.pyplot as plt
    
    print("Testing Helix visualization...")
    
    # Create a ModelAxi object
    # Note: sum(pitch * turns) must equal 2*h
    # h=50.0, so we need sum(pitch*turns) = 100.0
    # Example: 2*5.0 + 16*5.0 + 2*5.0 = 10 + 80 + 10 = 100
    modelaxi = ModelAxi(
        name="modelaxi_H1",
        h=50.0,  # Half-height of helical cut zone
        turns=[2, 16, 2],  # Turn counts for each section
        pitch=[5.0, 5.0, 5.0]  # Pitch for each section
    )
    
    # Create a Helix object
    helix = Helix(
        name="H1",
        r=[50.0, 60.0],      # Inner and outer radius
        z=[0.0, 100.0],      # Axial extent
        cutwidth=5.0,
        odd=True,
        dble=False,
        modelaxi=modelaxi
    )
    
    # Test 1: Single helix with modelaxi zone
    print("  - Creating single helix plot with modelaxi zone...")
    ax = helix.plot_axisymmetric(title="Helix with ModelAxi Zone")
    plt.savefig("test_helix_single.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_helix_single.png")
    
    # Test 2: Helix without modelaxi zone
    print("  - Creating helix plot without modelaxi zone...")
    fig, ax = plt.subplots(figsize=(8, 10))
    helix.plot_axisymmetric(
        ax=ax,
        show_modelaxi=False,
        title="Helix (Main Body Only)"
    )
    plt.savefig("test_helix_no_modelaxi.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_helix_no_modelaxi.png")
    
    # Test 3: Multiple helices
    print("  - Creating multiple helices plot...")
    # h=40.0, so sum(pitch*turns) = 80.0
    # Example: 2*4.0 + 16*4.0 + 2*4.0 = 8 + 64 + 8 = 80
    helix2 = Helix(
        name="H2",
        r=[65.0, 75.0],
        z=[0.0, 100.0],
        cutwidth=5.0,
        odd=False,
        dble=False,
        modelaxi=ModelAxi(
            name="modelaxi_H2",
            h=40.0,
            turns=[2, 16, 2],
            pitch=[4.0, 4.0, 4.0]
        )
    )
    
    fig, ax = plt.subplots(figsize=(10, 12))
    helix.plot_axisymmetric(
        ax=ax,
        color='darkgreen',
        alpha=0.6,
        show_legend=False
    )
    helix2.plot_axisymmetric(
        ax=ax,
        color='darkblue',
        alpha=0.6,
        show_legend=False
    )
    ax.set_title("Multiple Helices with ModelAxi Zones", fontsize=14, fontweight='bold')
    plt.savefig("test_helices_multiple.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_helices_multiple.png")
    
    # Test 4: Custom modelaxi styling
    print("  - Creating helix with custom modelaxi styling...")
    fig, ax = plt.subplots(figsize=(8, 10))
    helix.plot_axisymmetric(
        ax=ax,
        color='forestgreen',
        alpha=0.7,
        modelaxi_color='red',
        modelaxi_alpha=0.2,
        title="Custom ModelAxi Styling"
    )
    plt.savefig("test_helix_custom_style.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved as test_helix_custom_style.png")
    
    print("✓ Helix visualization tests passed!\n")


def main():
    """Run Helix visualization tests"""
    print("="*60)
    print("Helix Visualization Test")
    print("="*60)
    print()
    
    test_helix_visualization()
    
    print("="*60)
    print("✓ All tests completed successfully!")
    print("Check the generated PNG files for visual results.")
    print("="*60)


if __name__ == "__main__":
    main()
