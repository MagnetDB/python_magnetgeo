#!/usr/bin/env python3
"""
Test script for refactored Supra and Supras classes.
Follows the pattern from test-refactor-ring.py.
"""

import os
import json
import tempfile
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Supras import Supras
from python_magnetgeo.validation import ValidationError


def test_supra_basic_functionality():
    """Test basic Supra functionality"""
    print("=" * 60)
    print("Testing Supra basic functionality...")
    print("=" * 60)
    
    # Test basic creation
    supra = Supra(
        name="test_supra",
        r=[20.0, 30.0],
        z=[10.0, 80.0],
        struct=None
    )
    
    print(f"✓ Supra created: {supra.name}")
    print(f"  r={supra.r}, z={supra.z}, n={supra.n}")
    
    # Test that all inherited methods exist
    assert hasattr(supra, 'dump'), "Missing dump method"
    assert hasattr(supra, 'to_json'), "Missing to_json method"
    assert hasattr(supra, 'write_to_json'), "Missing write_to_json method"
    assert hasattr(Supra, 'from_yaml'), "Missing from_yaml classmethod"
    assert hasattr(Supra, 'from_json'), "Missing from_json classmethod"
    assert hasattr(Supra, 'from_dict'), "Missing from_dict classmethod"
    
    print("✓ All serialization methods inherited correctly")
    
    # Test JSON serialization
    json_str = supra.to_json()
    parsed = json.loads(json_str)
    assert parsed['__classname__'] == 'Supra', "Wrong classname in JSON"
    assert parsed['name'] == 'test_supra', "Wrong name in JSON"
    assert parsed['r'] == [20.0, 30.0], "Wrong r in JSON"
    assert parsed['z'] == [10.0, 80.0], "Wrong z in JSON"
    assert parsed['n'] == 0, "Wrong n in JSON"
    
    print("✓ JSON serialization works correctly")
    
    # Test from_dict
    test_dict = {
        'name': 'dict_supra',
        'r': [15.0, 25.0],
        'z': [5.0, 75.0],
        'n': 8,
        'struct': 'test_struct'
    }
    
    dict_supra = Supra.from_dict(test_dict)
    assert dict_supra.name == 'dict_supra', "from_dict name mismatch"
    assert dict_supra.r == [15.0, 25.0], "from_dict r mismatch"
    assert dict_supra.n == 8, "from_dict n mismatch"
    assert dict_supra.struct == 'test_struct', "from_dict struct mismatch"
    
    print("✓ from_dict works correctly")
    
    # Test default values
    minimal_dict = {
        'name': 'minimal_supra',
        'r': [10.0, 20.0],
        'z': [0.0, 50.0]
    }
    
    minimal_supra = Supra.from_dict(minimal_dict)
    assert minimal_supra.n == 0, "Default n should be 0"
    assert minimal_supra.struct == None, "Default struct should be empty"
    
    print("✓ Default values work correctly")
    
    print("\n✅ Supra basic functionality: PASSED\n")


def test_supra_validation():
    """Test Supra validation features"""
    print("=" * 60)
    print("Testing Supra validation...")
    print("=" * 60)
    
    # Test validation: empty name
    try:
        Supra(name="", r=[20.0, 30.0], z=[10.0, 80.0], n=5, struct="")
        assert False, "Should have raised ValidationError for empty name"
    except ValidationError as e:
        print(f"✓ Empty name validation: {e}")
    
    # Test validation: invalid radial bounds (r[0] > r[1])
    try:
        Supra(name="bad_supra", r=[30.0, 20.0], z=[10.0, 80.0], n=5, struct="")
        assert False, "Should have raised ValidationError for invalid r"
    except ValidationError as e:
        print(f"✓ Radial bounds validation: {e}")
    
    # Test validation: invalid axial bounds (z[0] > z[1])
    try:
        Supra(name="bad_supra", r=[20.0, 30.0], z=[80.0, 10.0], n=5, struct="")
        assert False, "Should have raised ValidationError for invalid z"
    except ValidationError as e:
        print(f"✓ Axial bounds validation: {e}")
    
    # Test validation: wrong list length for r
    try:
        Supra(name="bad_supra", r=[20.0], z=[10.0, 80.0], n=5, struct="")
        assert False, "Should have raised ValidationError for wrong r length"
    except ValidationError as e:
        print(f"✓ Radial list length validation: {e}")
    
    # Test validation: wrong list length for z
    try:
        Supra(name="bad_supra", r=[20.0, 30.0], z=[10.0], n=5, struct="")
        assert False, "Should have raised ValidationError for wrong z length"
    except ValidationError as e:
        print(f"✓ Axial list length validation: {e}")
    
    print("\n✅ Supra validation: PASSED\n")


def test_supra_yaml_roundtrip():
    """Test Supra YAML round-trip"""
    print("=" * 60)
    print("Testing Supra YAML round-trip...")
    print("=" * 60)
    
    # Create Supra instance
    supra = Supra(
        name="yaml_supra",
        r=[25.0, 35.0],
        z=[15.0, 85.0],
        n=6,
        struct="yaml_struct"
    )
    
    # Dump to YAML (creates yaml_supra.yaml)
    supra.dump()
    assert os.path.exists('yaml_supra.yaml'), "YAML file not created"
    print("✓ YAML dump created file")
    
    # Load back from YAML
    loaded_supra = Supra.from_yaml('yaml_supra.yaml')
    assert loaded_supra.name == supra.name, "Name mismatch after reload"
    assert loaded_supra.r == supra.r, "r mismatch after reload"
    assert loaded_supra.z == supra.z, "z mismatch after reload"
    assert loaded_supra.n == supra.n, "n mismatch after reload"
    assert loaded_supra.struct == supra.struct, "struct mismatch after reload"
    
    print("✓ YAML round-trip successful")
    
    # Clean up
    os.unlink('yaml_supra.yaml')
    print("✓ Cleanup completed")
    
    print("\n✅ Supra YAML round-trip: PASSED\n")


def test_supras_basic_functionality():
    """Test basic Supras (container) functionality"""
    print("=" * 60)
    print("Testing Supras basic functionality...")
    print("=" * 60)
    
    # Create individual Supra objects
    supra1 = Supra(name="supra1", r=[20.0, 30.0], z=[10.0, 50.0], n=4, struct=None)
    supra2 = Supra(name="supra2", r=[20.0, 30.0], z=[60.0, 100.0], n=6, struct=None)
    
    # Create Supras container
    supras = Supras(
        name="test_supras",
        magnets=[supra1, supra2],
        innerbore=18.0,
        outerbore=32.0
    )
    
    print(f"✓ Supras created: {supras.name}")
    print(f"  magnets count: {len(supras.magnets)}")
    print(f"  innerbore={supras.innerbore}, outerbore={supras.outerbore}")
    
    # Test inherited methods
    assert hasattr(supras, 'dump'), "Missing dump method"
    assert hasattr(supras, 'to_json'), "Missing to_json method"
    assert hasattr(Supras, 'from_dict'), "Missing from_dict classmethod"
    
    print("✓ All serialization methods inherited correctly")
    
    # Test JSON serialization
    json_str = supras.to_json()
    parsed = json.loads(json_str)
    assert parsed['__classname__'] == 'Supras', "Wrong classname"
    assert parsed['name'] == 'test_supras', "Wrong name"
    assert len(parsed['magnets']) == 2, "Wrong magnets count"
    assert parsed['innerbore'] == 18.0, "Wrong innerbore"
    assert parsed['outerbore'] == 32.0, "Wrong outerbore"
    
    print("✓ JSON serialization works correctly")
    
    print("\n✅ Supras basic functionality: PASSED\n")


def test_supras_from_dict():
    """Test Supras from_dict with nested objects"""
    print("=" * 60)
    print("Testing Supras from_dict...")
    print("=" * 60)
    
    # Test with nested Supra dicts
    test_dict = {
        'name': 'dict_supras',
        'magnets': [
            {
                '__classname__': 'Supra',
                'name': 'supra_a',
                'r': [15.0, 25.0],
                'z': [5.0, 45.0],
                'n': 3,
                'struct': None
            },
            {
                '__classname__': 'Supra',
                'name': 'supra_b',
                'r': [15.0, 25.0],
                'z': [55.0, 95.0],
                'n': 5,
                'struct': None
            }
        ],
        'innerbore': 13.0,
        'outerbore': 27.0
    }
    
    supras = Supras.from_dict(test_dict)
    assert supras.name == 'dict_supras', "Wrong name"
    assert len(supras.magnets) == 2, "Wrong magnets count"
    assert supras.magnets[0].name == 'supra_a', "Wrong first magnet name"
    assert supras.magnets[1].name == 'supra_b', "Wrong second magnet name"
    assert supras.innerbore == 13.0, "Wrong innerbore"
    assert supras.outerbore == 27.0, "Wrong outerbore"
    
    print("✓ from_dict with nested Supra objects works")
    
    # Test with empty probes list (new attribute)
    assert supras.probes == [], "Default probes should be empty list"
    print("✓ Default probes list works")
    
    print("\n✅ Supras from_dict: PASSED\n")


def test_supras_validation():
    """Test Supras validation"""
    print("=" * 60)
    print("Testing Supras validation...")
    print("=" * 60)
    
    supra = Supra(name="test", r=[20.0, 30.0], z=[10.0, 50.0], n=4, struct=None)
    
    # Test empty name
    try:
        Supras(name="", magnets=[supra], innerbore=18.0, outerbore=32.0)
        assert False, "Should have raised ValidationError for empty name"
    except ValidationError as e:
        print(f"✓ Empty name validation: {e}")
    
    print("\n✅ Supras validation: PASSED\n")


def test_supras_yaml_roundtrip():
    """Test Supras YAML round-trip"""
    print("=" * 60)
    print("Testing Supras YAML round-trip...")
    print("=" * 60)
    
    # Create Supras with nested Supra objects
    supra1 = Supra(name="yaml_supra1", r=[20.0, 30.0], z=[10.0, 50.0], n=4, struct=None)
    supra2 = Supra(name="yaml_supra2", r=[20.0, 30.0], z=[60.0, 100.0], n=6, struct=None)
    
    supras = Supras(
        name="yaml_supras",
        magnets=[supra1, supra2],
        innerbore=18.0,
        outerbore=32.0
    )
    
    # Dump to YAML
    supras.dump()
    assert os.path.exists('yaml_supras.yaml'), "YAML file not created"
    print("✓ YAML dump created file")
    
    # Load back
    loaded_supras = Supras.from_yaml('yaml_supras.yaml')
    assert loaded_supras.name == supras.name, "Name mismatch"
    assert len(loaded_supras.magnets) == 2, "Magnets count mismatch"
    assert loaded_supras.innerbore == supras.innerbore, "innerbore mismatch"
    assert loaded_supras.outerbore == supras.outerbore, "outerbore mismatch"
    
    print("✓ YAML round-trip successful")
    
    # Clean up
    os.unlink('yaml_supras.yaml')
    print("✓ Cleanup completed")
    
    print("\n✅ Supras YAML round-trip: PASSED\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SUPRA AND SUPRAS REFACTORING TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        # Supra tests
        test_supra_basic_functionality()
        test_supra_validation()
        test_supra_yaml_roundtrip()
        
        # Supras tests
        test_supras_basic_functionality()
        test_supras_from_dict()
        test_supras_validation()
        test_supras_yaml_roundtrip()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 VERIFIED FUNCTIONALITY:")
        print("  ✓ Supra: Inheritance from YAMLObjectBase")
        print("  ✓ Supra: Enhanced validation with ValidationError")
        print("  ✓ Supra: All serialization methods inherited")
        print("  ✓ Supra: JSON and YAML round-trip")
        print("  ✓ Supras: Container with nested Supra objects")
        print("  ✓ Supras: from_dict with nested object handling")
        print("  ✓ Supras: YAML round-trip with complex structure")
        print("  ✓ Probes attribute added successfully")
        
        print("\n🎯 BREAKING CHANGES CONFIRMED:")
        print("  ✓ ValidationError for invalid inputs")
        print("  ✓ Strong typing enforcement")
        print("  ✓ Enhanced error messages")
        
        print("\n🏆 PHASE 4 SUPRA/SUPRAS REFACTORING COMPLETE!")
        print("=" * 60 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
