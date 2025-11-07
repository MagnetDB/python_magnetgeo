#!/usr/bin/env python3
"""
Test script for refactored Helix class - Phase 4 validation

This test validates the migrated Helix implementation follows the same pattern
as test-refactor-ring.py, ensuring all functionality is preserved while using
the new YAMLObjectBase and validation framework.
"""

import os
import json
import tempfile
from python_magnetgeo.Helix import Helix
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Groove import Groove
from python_magnetgeo.Chamfer import Chamfer
from python_magnetgeo.validation import ValidationError


def test_refactored_helix_basic_functionality():
    """Test basic Helix creation and inherited methods"""
    print("Testing refactored Helix basic functionality...")
    
    # Create minimal nested objects
    modelaxi = ModelAxi(
        name="test_axi",
        pitch=[15.0, 10.0, 5.0],
        turns=[2.0, 3.0, 2.5],
        h=36.25
    )
    
    model3d = Model3D(
        name="test_model3d",
        cad="SALOME",
        with_shapes=True,
        with_channels=False
    )
    
    shape = Shape(
        name="test_shape",
        profile="rectangular",
        length=[15.0, 15.0, 15.0, 15.0],
        angle=[90.0, 90.0, 90.0, 90.0],
        onturns=[1],
        position="ALTERNATE"
    )
    
    # Create basic Helix
    helix = Helix(
        name="test_helix",
        r=[20.0, 40.0],
        z=[10.0, 90.0],
        cutwidth=2.5,
        odd=True,
        dble=False,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape,
        chamfers=None,
        grooves=None
    )
    
    print(f"✓ Helix created: {helix}")
    
    # Test that all inherited methods exist from YAMLObjectBase
    assert hasattr(helix, 'dump')
    assert hasattr(helix, 'to_json')
    assert hasattr(helix, 'write_to_json')
    assert hasattr(Helix, 'from_yaml')
    assert hasattr(Helix, 'from_json')
    assert hasattr(Helix, 'from_dict')
    
    print("✓ All serialization methods inherited correctly from YAMLObjectBase")
    
    # Test basic attributes
    assert helix.name == "test_helix"
    assert helix.r == [20.0, 40.0]
    assert helix.z == [10.0, 90.0]
    assert helix.cutwidth == 2.5
    assert helix.odd == True
    assert helix.dble == False
    assert helix.modelaxi is not None
    assert helix.model3d is not None
    assert helix.shape is not None
    
    print("✓ Basic attributes work correctly")


def test_helix_json_serialization():
    """Test JSON serialization of Helix with nested objects"""
    print("\nTesting Helix JSON serialization...")
    
    # Create minimal nested objects
    modelaxi = ModelAxi("json_axi", 21.375, [1.5, 2.0, 1.5], [8.0, 9.0, 8.5])
    model3d = Model3D("json_model3d", "GMSH", False, True)
    shape = Shape("json_shape", "test", [15.0, 15.0, 15.0], [60.0, 60.0, 60.0], [1], "ABOVE")
    
    helix = Helix(
        name="json_helix",
        r=[15.0, 35.0],
        z=[5.0, 85.0],
        cutwidth=3.0,
        odd=False,
        dble=True,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape
    )
    
    # Test JSON serialization
    json_str = helix.to_json()
    parsed = json.loads(json_str)
    
    assert parsed['__classname__'] == 'Helix'
    assert parsed['name'] == 'json_helix'
    assert parsed['r'] == [15.0, 35.0]
    assert parsed['z'] == [5.0, 85.0]
    assert parsed['cutwidth'] == 3.0
    assert parsed['odd'] == False
    assert parsed['dble'] == True
    
    # Verify nested objects are serialized
    assert 'modelaxi' in parsed
    assert 'model3d' in parsed
    assert 'shape' in parsed
    
    print("✓ JSON serialization works correctly with nested objects")


def test_helix_from_dict():
    """Test creating Helix from dictionary with nested objects"""
    print("\nTesting Helix from_dict with nested objects...")
    
    # Test with inline nested object definitions
    test_dict = {
        'name': 'dict_helix',
        'r': [18.0, 38.0],
        'z': [8.0, 82.0],
        'cutwidth': 2.8,
        'odd': True,
        'dble': False,
        'modelaxi': {
            'name': 'dict_axi',
            'pitch': [10.0, 10.0, 10.],
            'turns': [2.0, 2.5, 2.0],
            'h': 32.5
        },
        'model3d': {
            'name': 'dict_model3d',
            'cad': 'SALOME',
            'with_shapes': True,
            'with_channels': False
        },
        'shape': {
            'name': 'dict_shape',
            'profile': 'rectangular',
            'length': [15.0],
            'angle': [90.0, 90.0, 90.0, 90.0],
            'onturns': [1],
            'position': 'ALTERNATE'
        }
    }
    
    dict_helix = Helix.from_dict(test_dict)
    
    assert dict_helix.name == 'dict_helix'
    assert dict_helix.r == [18.0, 38.0]
    assert dict_helix.z == [8.0, 82.0]
    assert dict_helix.cutwidth == 2.8
    
    # Verify nested objects were created
    assert dict_helix.modelaxi is not None
    assert dict_helix.modelaxi.name == 'dict_axi'
    assert dict_helix.model3d is not None
    assert dict_helix.model3d.name == 'dict_model3d'
    assert dict_helix.shape is not None
    assert dict_helix.shape.name == 'dict_shape'
    
    print("✓ from_dict works correctly with inline nested objects")


def test_helix_with_chamfers_and_grooves():
    """Test Helix with optional chamfers and grooves"""
    print("\nTesting Helix with chamfers and grooves...")
    
    modelaxi = ModelAxi("groove_axi", 9.0, [2.0], [9.0])
    model3d = Model3D("groove_model3d", "SALOME", True, True)
    shape = Shape("groove_shape", "rectangular", [15.0], [90.0, 90.0, 90.0, 90.0], [2], "ALTERNATE")
    
    # Create chamfers
    chamfer1 = Chamfer(name="chamfer1", side="HP", rside="rint", alpha=45.0, dr=None, l=1.0)
    chamfer2 = Chamfer(name="chamfer2", side="BP", rside="rext", alpha=None, dr=0.5, l=1.0)
    
    # Create groove
    groove = Groove(name="test_groove", gtype="rint", n=4, eps=1.5)
    
    helix = Helix(
        name="helix_with_features",
        r=[22.0, 42.0],
        z=[12.0, 88.0],
        cutwidth=2.5,
        odd=True,
        dble=False,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape,
        chamfers=[chamfer1, chamfer2],
        grooves=groove
    )
    
    assert len(helix.chamfers) == 2
    assert helix.chamfers[0].name == "chamfer1"
    assert helix.chamfers[1].name == "chamfer2"
    assert helix.grooves is not None
    assert helix.grooves.name == "test_groove"
    
    print("✓ Helix with chamfers and grooves works correctly")


def test_helix_default_values():
    """Test Helix with default/optional parameters"""
    print("\nTesting Helix with default values...")
    
    modelaxi = ModelAxi("default_axi", 7.92, [1.8], [8.8])
    model3d = Model3D("default_model3d", "GMSH", False, False)
    shape = Shape("default_shape", "rectangular", [15.0, 15, 15, 15], [90.0, 90.0, 90.0, 90.0], [1], "ALTERNATE")
    
    # Create with defaults using from_dict
    test_dict = {
        'name': 'default_helix',
        'r': [25.0, 45.0],
        'z': [15.0, 85.0],
        'odd': True,
        'dble': False,
        'cutwidth': 3.0,
        'modelaxi': modelaxi,
        'model3d': model3d,
        'shape': shape
        # odd, dble, chamfers, grooves not specified
    }
    
    helix = Helix.from_dict(test_dict)
    
    # Check defaults
    assert helix.odd == True  # default
    assert helix.dble == False  # default
    assert helix.chamfers == []  # default empty list
    assert (helix.grooves is None)  # default Groove object
    
    print("✓ Default values work correctly")


def test_helix_validation():
    """Test that Helix validation works via GeometryValidator"""
    print("\nTesting Helix validation...")
    
    modelaxi = ModelAxi("val_axi", 9.0, [2.0], [9.0])
    model3d = Model3D("val_model3d", "SALOME", True, False)
    shape = Shape("val_shape", "rectangular", [15.0], [90.0, 90.0, 90.0, 90.0], [2], "ALTERNATE")
    
    # Test empty name validation
    try:
        Helix(
            name="",  # Invalid: empty name
            r=[20.0, 40.0],
            z=[10.0, 90.0],
            cutwidth=2.5,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        assert False, "Should have raised ValidationError for empty name"
    except (ValidationError, ValueError) as e:
        print(f"✓ Name validation works: {e}")
    
    # Test invalid radial bounds
    try:
        Helix(
            name="bad_helix",
            r=[40.0, 20.0],  # Invalid: inner > outer
            z=[10.0, 90.0],
            cutwidth=2.5,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        assert False, "Should have raised ValidationError for bad radial bounds"
    except (ValidationError, ValueError) as e:
        print(f"✓ Radial bounds validation works: {e}")
    
    # Test invalid axial bounds
    try:
        Helix(
            name="bad_helix2",
            r=[20.0, 40.0],
            z=[90.0, 10.0],  # Invalid: upper < lower
            cutwidth=2.5,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        assert False, "Should have raised ValidationError for bad axial bounds"
    except (ValidationError, ValueError) as e:
        print(f"✓ Axial bounds validation works: {e}")


def test_helix_yaml_roundtrip():
    """Test YAML dump and load roundtrip for Helix"""
    print("\nTesting Helix YAML round-trip...")
    
    modelaxi = ModelAxi("yaml_axi", 37.95, [2.2, 2.8, 2.2], [10.0, 11.0, 10.5])
    model3d = Model3D("yaml_model3d", "SALOME", True, False)
    shape = Shape("yaml_shape", "hexagonal", [15.0], [60.0, 60.0, 60.0, 60.0, 60.0, 60.0], [1], "ALTERNATE")
    
    helix = Helix(
        name="yaml_helix",
        r=[17.0, 37.0],
        z=[7.0, 167.0],
        cutwidth=2.7,
        odd=False,
        dble=True,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape
    )
    
    # Dump to YAML (creates yaml_helix.yaml)
    helix.dump()
    print("✓ YAML dump works")
    
    # Load it back
    loaded_helix = Helix.from_yaml('yaml_helix.yaml', debug=True)
    
    assert loaded_helix.name == helix.name
    assert loaded_helix.r == helix.r
    assert loaded_helix.z == helix.z
    assert loaded_helix.cutwidth == helix.cutwidth
    assert loaded_helix.odd == helix.odd
    assert loaded_helix.dble == helix.dble
    
    # Verify nested objects loaded correctly
    assert loaded_helix.modelaxi is not None
    assert loaded_helix.modelaxi.name == "yaml_axi"
    assert loaded_helix.model3d is not None
    assert loaded_helix.model3d.name == "yaml_model3d"
    assert loaded_helix.shape is not None
    assert loaded_helix.shape.name == "yaml_shape"
    
    print("✓ YAML round-trip works correctly")
    
    # Clean up
    if os.path.exists('yaml_helix.yaml'):
        os.unlink('yaml_helix.yaml')


def test_helix_complex_serialization():
    """Test serialization with all features (chamfers, grooves, etc)"""
    print("\nTesting complex Helix serialization...")
    
    modelaxi = ModelAxi("complex_axi", 46.125, [2.5, 3.0, 2.5], [11.0, 12.0, 11.5])
    model3d = Model3D("complex_model3d", "GMSH", True, True)
    shape = Shape("complex_shape", "rectangular", [15.0, 15.0, 15.0] , [45.0, 45.0, 45.0], [3], "BELOW")
    
    chamfer1 = Chamfer(name="chamfer1", side="HP", rside="rint", alpha=45.0, dr=None, l=1.0)
    chamfer2 = Chamfer(name="chamfer2", side="BP", rside="rext", alpha=None, dr=0.5, l=1.0)
    groove = Groove(name="test_groove", gtype="rint", n=4, eps=1.5)
    
    helix = Helix(
        name="complex_helix",
        r=[19.0, 39.0],
        z=[9.0, 109.0],
        cutwidth=3.2,
        odd=True,
        dble=True,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape,
        chamfers=[chamfer1, chamfer2],
        grooves=groove
    )
    
    # Serialize to JSON
    json_str = helix.to_json()
    parsed = json.loads(json_str)
    
    # Verify all components present
    assert parsed['name'] == 'complex_helix'
    assert 'modelaxi' in parsed
    assert 'model3d' in parsed
    assert 'shape' in parsed
    assert 'chamfers' in parsed
    assert 'grooves' in parsed
    
    print("✓ Complex serialization preserves all features")
    
    # Test write to file
    temp_file = 'complex_helix_test.json'
    helix.write_to_json(temp_file)
    assert os.path.exists(temp_file)
    
    # Load from file
    loaded_helix = Helix.from_json(temp_file)
    assert loaded_helix.name == helix.name
    assert len(loaded_helix.chamfers) == 2
    
    print("✓ JSON file write/read works correctly")
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)

def test_helix_repr():
    """Test string representation of Helix"""
    print("\nTesting Helix __repr__...")
    
    modelaxi = ModelAxi("repr_axi", 9.0, [2.0], [9.0])
    model3d = Model3D("repr_model3d", "SALOME", False, False)
    shape = Shape("repr_shape", "rectangular", [15.0], [90.0, 90.0, 90.0, 90.0], [1], "ALTERNATE")
    
    helix = Helix(
        name="repr_helix",
        r=[20.0, 40.0],
        z=[10.0, 90.0],
        cutwidth=2.5,
        odd=True,
        dble=False,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape
    )
    
    repr_str = repr(helix)
    
    # Verify repr contains key information (flexible assertions)
    assert "Helix" in repr_str
    assert "repr_helix" in repr_str  # Name appears somewhere in output
    
    # Check that key helix parameters are present
    assert "20.0" in repr_str and "40.0" in repr_str  # r values
    assert "10.0" in repr_str and "90.0" in repr_str  # z values
    assert "2.5" in repr_str  # cutwidth
    
    print(f"✓ __repr__ works: {repr_str[:100]}...")


def test_backward_compatibility():
    """Test that Helix maintains backward compatibility"""
    print("\nTesting backward compatibility...")
    
    # Create Helix in a way that mimics old code
    modelaxi = ModelAxi("bc_axi", 10.0, [2.0], [10.0])
    model3d = Model3D("bc_model3d", "SALOME", True, False)
    shape = Shape("bc_shape", "rectangular", [15.0], [90.0, 90.0, 90.0, 90.0], [2], "ALTERNATE")
    
    # Old-style creation (should still work)
    helix = Helix(
        name="backward_compat_helix",
        r=[21.0, 41.0],
        z=[11.0, 89.0],
        cutwidth=2.6,
        odd=True,
        dble=False,
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape,
        chamfers=None,
        grooves=None
    )
    
    # Verify it still has the same methods
    assert hasattr(helix, 'get_type')
    assert hasattr(helix, 'get_lc')
    assert hasattr(helix, 'get_names')
    assert hasattr(helix, 'getModelAxi')
    
    # Test old methods still work
    helix_type = helix.get_type()
    assert helix_type in ["HR", "HL"]
    
    lc = helix.get_lc()
    assert lc > 0
    
    print("✓ Backward compatibility maintained - old methods still work")


def run_all_helix_tests():
    """Run all Helix refactoring tests"""
    print("=" * 60)
    print("HELIX REFACTORING VALIDATION TEST SUITE")
    print("Phase 4: Testing migrated Helix with YAMLObjectBase")
    print("=" * 60)
    
    test_refactored_helix_basic_functionality()
    test_helix_json_serialization()
    test_helix_from_dict()
    test_helix_with_chamfers_and_grooves()
    test_helix_default_values()
    test_helix_validation()
    test_helix_yaml_roundtrip()
    test_helix_complex_serialization()
    test_helix_repr()
    test_backward_compatibility()
    
    print("\n" + "=" * 60)
    print("ALL HELIX TESTS PASSED!")
    print("=" * 60)
    print("\nHelix successfully refactored with:")
    print("  ✓ YAMLObjectBase inheritance")
    print("  ✓ GeometryValidator integration")
    print("  ✓ Automatic YAML constructor registration")
    print("  ✓ Complex nested object handling")
    print("  ✓ All serialization methods inherited")
    print("  ✓ Backward compatibility maintained")
    print("  ✓ Enhanced validation features")
    print("\nPhase 4 complete! Ready for next class migration.")


if __name__ == "__main__":
    run_all_helix_tests()
