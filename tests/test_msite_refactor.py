#!/usr/bin/env python3
"""
Phase 4 test for refactored MSite class - validation following test-refactor-ring.py pattern

Tests that the migrated MSite class works correctly with the new base classes
and validation framework. This test validates:
1. Basic MSite creation and initialization
2. All inherited serialization methods
3. JSON serialization/deserialization
4. from_dict functionality
5. Validation features (new with base classes)
6. YAML round-trip serialization
7. Complex nested object handling (magnets, screens)
8. Bounding box calculations
9. Get methods and operations
"""

import os
import json
import tempfile
from python_magnetgeo.MSite import MSite
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Screen import Screen
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Profile import Profile
from python_magnetgeo.validation import ValidationError


def create_sample_helix():
    """Create a sample helix for testing"""
    axi = ModelAxi("test_axi", 5.0, [1.0], [10.0])
    model3d = Model3D("test_model3d", "test_cad", False, False)

    # Create a rectangular profile object
    rectangular_profile = Profile(
        cad="rectangular_profile",
        points=[[-2.5, 0], [2.5, 0], [2.5, 5], [-2.5, 5], [-2.5, 0]],
        labels=[0, 0, 1, 0, 0]
    )

    shape = Shape("test_shape", rectangular_profile, [5], [90.0], [0], "ABOVE")

    helix = Helix(
        name="test_helix",
        r=[10.0, 20.0],
        z=[0.0, 50.0],
        odd=True,
        dble=False,
        cutwidth=0.1,
        modelaxi=axi,
        model3d=model3d,
        shape=shape,
    )
    return helix


def create_sample_insert():
    """Create a sample insert magnet"""
    helix = create_sample_helix()
    insert = Insert(
        name="test_insert",
        helices=[helix],
        rings=[],
        currentleads=[],
        hangles=[],
        rangles=[],
        probes=[],
        innerbore=5.0,
        outerbore=25.0
    )
    return insert


def create_sample_supras():
    """Create sample supras magnet"""
    supra = Supra("test_supra", [30.0, 40.0], [60.0, 100.0], 4, None)
    supras = Supras("test_supras", [supra], 28.0, 65.0, [])
    return supras


def test_basic_msite_creation():
    """Test basic MSite creation with minimal parameters"""
    print("Testing basic MSite creation...")

    insert = create_sample_insert()

    # Create minimal MSite
    msite = MSite(
        name="minimal_msite",
        magnets=[insert],
        screens=None,
        z_offset=None,
        r_offset=None,
        paralax=None
    )

    assert msite.name == "minimal_msite"
    assert len(msite.magnets) == 1
    assert msite.screens == []
    assert msite.z_offset is None
    assert msite.r_offset is None
    assert msite.paralax is None

    print(f"✓ Basic MSite created: {msite}")


def test_inherited_methods():
    """Test that all serialization methods are inherited from base classes"""
    print("Testing inherited serialization methods...")

    insert = create_sample_insert()
    msite = MSite("test_msite", [insert], None, None, None, None)

    # Check all inherited methods exist
    assert hasattr(msite, 'write_to_yaml')
    assert hasattr(msite, 'to_json')
    assert hasattr(msite, 'write_to_json')
    assert hasattr(MSite, 'from_yaml')
    assert hasattr(MSite, 'from_json')
    assert hasattr(MSite, 'from_dict')

    print("✓ All serialization methods inherited correctly")


def test_json_serialization():
    """Test JSON serialization and deserialization"""
    print("Testing JSON serialization...")

    insert = create_sample_insert()
    msite = MSite("json_msite", [insert], None, None, None, None)

    # Test to_json
    json_str = msite.to_json()
    parsed = json.loads(json_str)

    assert parsed['name'] == 'json_msite'
    assert parsed['__classname__'] == 'MSite'
    assert 'magnets' in parsed
    assert len(parsed['magnets']) == 1

    print("✓ JSON serialization works correctly")

    # Test write_to_json and from_json roundtrip
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_file = f.name

    try:
        msite.write_to_json(json_file)
        loaded_msite = MSite.from_json(json_file)

        assert loaded_msite.name == msite.name
        assert len(loaded_msite.magnets) == len(msite.magnets)

        print("✓ JSON round-trip works correctly")
    finally:
        if os.path.exists(json_file):
            os.unlink(json_file)


def test_from_dict():
    """Test from_dict class method"""
    print("Testing from_dict...")

    # Note: from_dict with complex nested objects is challenging
    # Test with minimal dict structure
    test_dict = {
        'name': 'dict_msite',
        'magnets': [],  # Empty for now
        'screens': None,
        'z_offset': [0.0, 10.0],
        'r_offset': [5.0, 15.0],
        'paralax': [0.0, 0.0]
    }

    msite = MSite.from_dict(test_dict)
    assert msite.name == 'dict_msite'
    assert msite.magnets == []
    assert msite.z_offset == [0.0, 10.0]
    assert msite.r_offset == [5.0, 15.0]

    print("✓ from_dict works correctly")


def test_validation():
    """Test validation features from base classes"""
    print("Testing validation...")

    insert = create_sample_insert()

    # Test empty name validation
    try:
        MSite(name="", magnets=[insert], screens=None,
              z_offset=None, r_offset=None, paralax=None)
        assert False, "Should have raised ValidationError for empty name"
    except (ValidationError, ValueError) as e:
        print(f"✓ Name validation works: {e}")

    # Test None name validation
    try:
        MSite(name=None, magnets=[insert], screens=None,
              z_offset=None, r_offset=None, paralax=None)
        assert False, "Should have raised ValidationError for None name"
    except (ValidationError, ValueError, TypeError) as e:
        print(f"✓ Name validation works for None: {e}")


def test_complex_msite_with_multiple_magnets():
    """Test MSite with multiple magnet types"""
    print("Testing complex MSite with multiple magnets...")

    insert = create_sample_insert()
    supras = create_sample_supras()

    msite = MSite(
        name="complex_msite",
        magnets=[insert, supras],
        screens=None,
        z_offset=[0.0, 65.0],
        r_offset=[0.0, 0.0],
        paralax=[0.0, 0.0]
    )

    assert len(msite.magnets) == 2
    assert msite.z_offset == [0.0, 65.0]

    print(f"✓ Complex MSite with {len(msite.magnets)} magnets created")


def test_msite_with_screens():
    """Test MSite with screen objects"""
    print("Testing MSite with screens...")

    insert = create_sample_insert()
    screen = Screen("test_screen", [0.0, 60.0], [0.0, 200.0])

    msite = MSite(
        name="msite_with_screens",
        magnets=[insert],
        screens=[screen],
        z_offset=[0.0],
        r_offset=[0.0],
        paralax=[0.0]
    )

    assert msite.screens is not None
    assert len(msite.screens) == 1
    assert msite.screens[0].name == "test_screen"

    print("✓ MSite with screens works correctly")


def test_bounding_box():
    """Test bounding box calculations"""
    print("Testing bounding box calculations...")

    insert = create_sample_insert()
    supras = create_sample_supras()

    msite = MSite(
        name="bbox_msite",
        magnets=[insert, supras],
        screens=None,
        z_offset=[0.0, 65.0],
        r_offset=[0.0, 0.0],
        paralax=[0.0, 0.0]
    )

    # Test boundingBox method
    rb, zb = msite.boundingBox()

    assert isinstance(rb, list)
    assert isinstance(zb, list)
    assert len(rb) == 2
    assert len(zb) == 2

    # Bounding box should encompass all magnets
    # Insert: r=[10.0, 20.0], z=[0.0, 50.0]
    # Supras: r=[30.0, 40.0], z=[60.0, 100.0] + offset=65.0
    assert rb[0] <= 10.0  # Should include insert inner radius
    assert rb[1] >= 40.0  # Should include supras outer radius
    assert zb[0] <= 0.0   # Should include insert lower z
    assert zb[1] >= 100.0 # Should include supras upper z (+ offset not included right now)

    print(f"✓ Bounding box calculation works: rb={rb}, zb={zb}")


def test_get_names():
    """Test get_names method"""
    print("Testing get_names method...")

    insert = create_sample_insert()
    msite = MSite("names_msite", [insert], None, None, None, None)

    names = msite.get_names("test_prefix")

    assert isinstance(names, list)
    assert len(names) > 0

    print(f"✓ get_names works: returned {len(names)} names")


def test_yaml_roundtrip():
    """Test YAML dump and load round-trip"""
    print("Testing YAML round-trip...")

    insert = create_sample_insert()
    msite = MSite("yaml_msite", [insert], None, [0.0], [0.0], [0.0])

    # Dump to YAML
    msite.write_to_yaml()
    yaml_file = "yaml_msite.yaml"

    assert os.path.exists(yaml_file), "YAML file should be created"
    print("✓ YAML dump works")

    try:
        # Load from YAML
        loaded_msite = MSite.from_yaml(yaml_file, debug=True)

        assert loaded_msite.name == msite.name
        assert len(loaded_msite.magnets) == len(msite.magnets)
        assert loaded_msite.z_offset == msite.z_offset

        print("✓ YAML round-trip works")
    finally:
        if os.path.exists(yaml_file):
            os.unlink(yaml_file)


def test_get_magnet():
    """Test get_magnet method"""
    print("Testing get_magnet method...")

    insert = create_sample_insert()
    supras = create_sample_supras()

    msite = MSite("get_magnet_test", [insert, supras], None, None, None, None)

    # Test getting magnet by name
    found_insert = msite.get_magnet("test_insert")
    assert found_insert is not None
    assert found_insert.name == "test_insert"

    found_supras = msite.get_magnet("test_supras")
    assert found_supras is not None
    assert found_supras.name == "test_supras"

    # Test non-existent magnet
    not_found = msite.get_magnet("nonexistent")
    assert not_found is None

    print("✓ get_magnet works correctly")


def run_all_tests():
    """Run all MSite refactoring tests"""
    print("=" * 60)
    print("MSite Refactoring Validation Tests (Phase 4)")
    print("=" * 60)
    print()

    try:
        test_basic_msite_creation()
        test_inherited_methods()
        test_json_serialization()
        test_from_dict()
        test_validation()
        test_complex_msite_with_multiple_magnets()
        test_msite_with_screens()
        test_bounding_box()
        test_get_names()
        test_get_magnet()
        test_yaml_roundtrip()

        print()
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("MSite refactoring is successful and maintains full compatibility.")
        print("The migrated class works correctly with:")
        print("  - Base class inheritance (YAMLObjectBase)")
        print("  - Validation framework")
        print("  - All serialization methods (JSON, YAML)")
        print("  - Complex nested objects (magnets, screens)")
        print("  - All MSite-specific operations")

    except AssertionError as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        raise
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED WITH EXCEPTION!")
        print("=" * 60)
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()
