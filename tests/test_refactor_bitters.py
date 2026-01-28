#!/usr/bin/env python3
"""
Simple test for refactored Bitters class - Phase 4 validation

Similar to test_refactor_ring.py approach - focused on core functionality.
Tests that the migrated Bitters collection class works correctly with the new base classes.
"""

import os
import json
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.validation import ValidationError


def test_refactored_bitters_functionality():
    """Test that refactored Bitters has identical functionality to original"""
    print("Testing refactored Bitters functionality...")

    # Create some Bitter magnets
    bitter1 = Bitter(
        name="bitter1",
        r=[0.10, 0.15],
        z=[-0.05, 0.0],
        odd=True,
        modelaxi=None,
        coolingslits=[],
        tierod=None
    )

    bitter2 = Bitter(
        name="bitter2",
        r=[0.10, 0.15],
        z=[0.0, 0.05],
        odd=False,
        modelaxi=None,
        coolingslits=[],
        tierod=None
    )

    # Test basic creation
    bitters = Bitters(
        name="test_bitters",
        magnets=[bitter1, bitter2],
        innerbore=0.08,
        outerbore=0.18,
        probes=[]
    )

    print(f"✓ Bitters created: {bitters}")

    # Test that all inherited methods exist
    assert hasattr(bitters, 'write_to_yaml')
    assert hasattr(bitters, 'to_json')
    assert hasattr(bitters, 'write_to_json')
    assert hasattr(Bitters, 'from_yaml')
    assert hasattr(Bitters, 'from_json')
    assert hasattr(Bitters, 'from_dict')

    print("✓ All serialization methods inherited correctly")

    # Test JSON serialization
    json_str = bitters.to_json()
    parsed = json.loads(json_str)
    assert parsed['name'] == 'test_bitters'
    assert parsed['innerbore'] == 0.08
    assert parsed['outerbore'] == 0.18
    assert len(parsed['magnets']) == 2
    assert parsed['__classname__'] == 'Bitters'

    print("✓ JSON serialization works")

    # Test from_dict
    test_dict = {
        'name': 'dict_bitters',
        'magnets': [bitter1, bitter2],
        'innerbore': 0.09,
        'outerbore': 0.19,
        'probes': []
    }

    dict_bitters = Bitters.from_dict(test_dict, debug=True)
    assert dict_bitters.name == 'dict_bitters'
    assert len(dict_bitters.magnets) == 2
    assert dict_bitters.innerbore == 0.09
    assert dict_bitters.outerbore == 0.19

    print("✓ from_dict works")

    # Test boundingBox
    rb, zb = bitters.boundingBox()
    assert rb[0] == 0.10  # min r from both bitters
    assert rb[1] == 0.15  # max r from both bitters
    assert zb[0] == -0.05  # min z from bitter1
    assert zb[1] == 0.05   # max z from bitter2

    print("✓ boundingBox works")

    # Test intersect
    assert bitters.intersect([0.12, 0.14], [-0.02, 0.02]) == True
    assert bitters.intersect([0.20, 0.25], [0.0, 0.1]) == False

    print("✓ intersect works")

    # Test validation
    try:
        Bitters(name="", magnets=[], innerbore=0.1, outerbore=0.2)
        assert False, "Should have raised ValidationError for empty name"
    except ValidationError as e:
        print(f"✓ Validation works: {e}")

    # Test YAML round-trip
    bitters.write_to_yaml()  # This creates test_bitters.yaml
    print("✓ YAML dump works")

    # Now load it back
    loaded_bitters = Bitters.from_yaml('test_bitters.yaml')
    assert loaded_bitters.name == bitters.name
    assert len(loaded_bitters.magnets) == len(bitters.magnets)
    assert loaded_bitters.innerbore == bitters.innerbore
    assert loaded_bitters.outerbore == bitters.outerbore

    print("✓ YAML round-trip works")

    # Clean up
    if os.path.exists('test_bitters.yaml'):
        os.unlink('test_bitters.yaml')

    print("All refactored functionality verified! Bitters.py successfully refactored.\n")


if __name__ == "__main__":
    test_refactored_bitters_functionality()
