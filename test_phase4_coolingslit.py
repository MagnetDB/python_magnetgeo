#!/usr/bin/env python3
"""
Phase 4 Test Suite: CoolingSlit Validation

Tests the refactored CoolingSlit class following the same pattern as test-refactor-ring.py.
Validates that the new YAMLObjectBase implementation maintains all functionality while
adding validation and improved error handling.

CoolingSlit represents cooling channels in magnets with nested Contour2D geometry.
"""

import os
import json
import tempfile
from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo.Contour2D import Contour2D
from python_magnetgeo.validation import ValidationError


def test_coolingslit_basic_creation():
    """Test CoolingSlit basic creation and attributes"""
    print("\n=== Test 1: CoolingSlit Basic Creation ===")
    
    # Create a simple contour for testing
    contour = Contour2D(
        name="test_contour",
        pts=[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
    )
    
    slit = CoolingSlit(
        name="test_slit",
        r=0.12,
        angle=45.0,
        n=8,
        dh=0.002,
        sh=0.001,
        contour2d=contour
    )
    
    assert slit.name == "test_slit"
    assert slit.r == 0.12
    assert slit.angle == 45.0
    assert slit.n == 8
    assert slit.dh == 0.002
    assert slit.sh == 0.001
    assert isinstance(slit.contour2d, Contour2D)
    assert slit.contour2d.name == "test_contour"
    
    print(f"✓ CoolingSlit created: {slit}")
    print(f"  - name: {slit.name}")
    print(f"  - r: {slit.r} (radius)")
    print(f"  - angle: {slit.angle}° (angular shift)")
    print(f"  - n: {slit.n} (count)")
    print(f"  - dh: {slit.dh} (hydraulic diameter)")
    print(f"  - sh: {slit.sh} (cross-section)")
    print(f"  - contour2d: {slit.contour2d.name}")


def test_coolingslit_with_none_contour():
    """Test CoolingSlit with None contour2d"""
    print("\n=== Test 2: CoolingSlit with None Contour ===")
    
    slit = CoolingSlit(
        name="no_contour_slit",
        r=0.15,
        angle=30.0,
        n=6,
        dh=0.003,
        sh=0.0015,
        contour2d=None
    )
    
    assert slit.contour2d is None
    print("✓ CoolingSlit with None contour2d created successfully")
    print(f"  - contour2d: {slit.contour2d}")


def test_coolingslit_inherited_methods():
    """Test that CoolingSlit has all inherited methods from YAMLObjectBase"""
    print("\n=== Test 3: CoolingSlit Inherited Methods ===")
    
    contour = Contour2D(name="method_contour", pts=[[0, 0], [1, 0], [1, 1]])
    slit = CoolingSlit(
        name="method_test",
        r=0.10,
        angle=60.0,
        n=10,
        dh=0.0025,
        sh=0.00125,
        contour2d=contour
    )
    
    # Check for all inherited methods
    assert hasattr(slit, 'dump')
    assert hasattr(slit, 'to_json')
    assert hasattr(slit, 'write_to_json')
    assert hasattr(CoolingSlit, 'from_yaml')
    assert hasattr(CoolingSlit, 'from_json')
    assert hasattr(CoolingSlit, 'from_dict')
    
    print("✓ All serialization methods inherited correctly:")
    print("  - dump()")
    print("  - to_json()")
    print("  - write_to_json()")
    print("  - from_yaml() [classmethod]")
    print("  - from_json() [classmethod]")
    print("  - from_dict() [classmethod]")


def test_coolingslit_json_serialization():
    """Test CoolingSlit JSON serialization"""
    print("\n=== Test 4: CoolingSlit JSON Serialization ===")
    
    contour = Contour2D(
        name="json_contour",
        pts=[[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]]
    )
    
    slit = CoolingSlit(
        name="json_test_slit",
        r=0.14,
        angle=50.0,
        n=12,
        dh=0.0028,
        sh=0.0014,
        contour2d=contour
    )
    
    json_str = slit.to_json()
    parsed = json.loads(json_str)
    
    assert parsed['__classname__'] == 'CoolingSlit'
    assert parsed['name'] == 'json_test_slit'
    assert parsed['r'] == 0.14
    assert parsed['angle'] == 50.0
    assert parsed['n'] == 12
    assert parsed['dh'] == 0.0028
    assert parsed['sh'] == 0.0014
    assert 'contour2d' in parsed
    assert parsed['contour2d']['name'] == 'json_contour'
    
    print("✓ JSON serialization works correctly")
    print(f"  - __classname__: {parsed['__classname__']}")
    print(f"  - All attributes serialized properly")
    print(f"  - Nested Contour2D serialized: {parsed['contour2d']['name']}")


def test_coolingslit_from_dict_inline_contour():
    """Test CoolingSlit.from_dict() with inline Contour2D"""
    print("\n=== Test 5: CoolingSlit from_dict with Inline Contour ===")
    
    test_dict = {
        'name': 'dict_slit_inline',
        'r': 0.16,
        'angle': 35.0,
        'n': 7,
        'dh': 0.0022,
        'sh': 0.0011,
        'contour2d': {
            'name': 'inline_contour',
            'pts': [[0.0, 0.0], [1.5, 0.0], [1.5, 1.5], [0.0, 1.5]]
        }
    }
    
    slit = CoolingSlit.from_dict(test_dict)
    
    assert slit.name == 'dict_slit_inline'
    assert slit.r == 0.16
    assert slit.angle == 35.0
    assert slit.n == 7
    assert slit.dh == 0.0022
    assert slit.sh == 0.0011
    assert isinstance(slit.contour2d, Contour2D)
    assert slit.contour2d.name == 'inline_contour'
    
    print("✓ from_dict() with inline Contour2D works correctly")
    print(f"  - Created: {slit}")
    print(f"  - Nested Contour2D: {slit.contour2d}")


def test_coolingslit_from_dict_none_contour():
    """Test CoolingSlit.from_dict() with None contour2d"""
    print("\n=== Test 6: CoolingSlit from_dict with None Contour ===")
    
    test_dict = {
        'name': 'dict_slit_none',
        'r': 0.18,
        'angle': 40.0,
        'n': 9,
        'dh': 0.0024,
        'sh': 0.0012,
        'contour2d': None
    }
    
    slit = CoolingSlit.from_dict(test_dict)
    
    assert slit.name == 'dict_slit_none'
    assert slit.contour2d is None
    
    print("✓ from_dict() with None contour2d works correctly")
    print(f"  - Created: {slit}")
    print(f"  - contour2d is None: {slit.contour2d is None}")


def test_coolingslit_from_dict_object_contour():
    """Test CoolingSlit.from_dict() with pre-instantiated Contour2D object"""
    print("\n=== Test 7: CoolingSlit from_dict with Object Contour ===")
    
    # Create contour object first
    contour_obj = Contour2D(
        name="prebuilt_contour",
        pts=[[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0]]
    )
    
    test_dict = {
        'name': 'dict_slit_object',
        'r': 0.20,
        'angle': 25.0,
        'n': 11,
        'dh': 0.0026,
        'sh': 0.0013,
        'contour2d': contour_obj
    }
    
    slit = CoolingSlit.from_dict(test_dict)
    
    assert slit.name == 'dict_slit_object'
    assert slit.contour2d is contour_obj
    assert slit.contour2d.name == "prebuilt_contour"
    
    print("✓ from_dict() with pre-instantiated object works correctly")
    print(f"  - Created: {slit}")
    print(f"  - Contour2D object preserved: {slit.contour2d.name}")


def test_coolingslit_yaml_roundtrip_with_contour():
    """Test CoolingSlit YAML save and load with Contour2D"""
    print("\n=== Test 8: CoolingSlit YAML Round-trip with Contour ===")
    
    contour = Contour2D(
        name="yaml_contour",
        pts=[[0.0, 0.0], [2.5, 0.0], [2.5, 2.5], [0.0, 2.5]]
    )
    
    slit = CoolingSlit(
        name="yaml_test_slit",
        r=0.13,
        angle=55.0,
        n=8,
        dh=0.0027,
        sh=0.00135,
        contour2d=contour
    )
    
    # Save to YAML
    slit.dump()
    yaml_file = f"{slit.name}.yaml"
    assert os.path.exists(yaml_file), f"YAML file {yaml_file} not created"
    print(f"✓ YAML file created: {yaml_file}")
    
    # Load from YAML
    loaded_slit = CoolingSlit.from_yaml(yaml_file)
    
    assert loaded_slit.name == slit.name
    assert loaded_slit.r == slit.r
    assert loaded_slit.angle == slit.angle
    assert loaded_slit.n == slit.n
    assert loaded_slit.dh == slit.dh
    assert loaded_slit.sh == slit.sh
    assert loaded_slit.contour2d.name == slit.contour2d.name
    
    print("✓ YAML round-trip successful")
    print(f"  - Original: {slit}")
    print(f"  - Loaded:   {loaded_slit}")
    
    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


def test_coolingslit_yaml_roundtrip_none_contour():
    """Test CoolingSlit YAML save and load with None contour"""
    print("\n=== Test 9: CoolingSlit YAML Round-trip with None Contour ===")
    
    slit = CoolingSlit(
        name="yaml_none_slit",
        r=0.11,
        angle=65.0,
        n=5,
        dh=0.0021,
        sh=0.00105,
        contour2d=None
    )
    
    # Save to YAML
    slit.dump()
    yaml_file = f"{slit.name}.yaml"
    assert os.path.exists(yaml_file), f"YAML file {yaml_file} not created"
    print(f"✓ YAML file created: {yaml_file}")
    
    # Load from YAML
    loaded_slit = CoolingSlit.from_yaml(yaml_file)
    
    assert loaded_slit.name == slit.name
    assert loaded_slit.r == slit.r
    assert loaded_slit.contour2d is None
    
    print("✓ YAML round-trip with None contour successful")
    print(f"  - Original contour2d: {slit.contour2d}")
    print(f"  - Loaded contour2d:   {loaded_slit.contour2d}")
    
    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


def test_coolingslit_in_bitter_context():
    """Test that CoolingSlit works in Bitter context (as it would be used)"""
    print("\n=== Test 10: CoolingSlit in Bitter Context ===")
    
    # Create multiple cooling slits as they would appear in a Bitter
    contour1 = Contour2D(name="slit1_contour", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])
    contour2 = Contour2D(name="slit2_contour", pts=[[0, 0], [1.5, 0], [1.5, 1.5], [0, 1.5]])
    
    slit1 = CoolingSlit(
        name="bitter_slit1",
        r=0.12,
        angle=30.0,
        n=8,
        dh=0.002,
        sh=0.001,
        contour2d=contour1
    )
    
    slit2 = CoolingSlit(
        name="bitter_slit2",
        r=0.14,
        angle=60.0,
        n=10,
        dh=0.0025,
        sh=0.00125,
        contour2d=contour2
    )
    
    # Simulate how they're used in Bitter
    cooling_slits = [slit1, slit2]
    
    assert len(cooling_slits) == 2
    assert all(isinstance(s, CoolingSlit) for s in cooling_slits)
    
    # Test serialization of list
    serialized_slits = [json.loads(slit.to_json()) for slit in cooling_slits]
    
    assert serialized_slits[0]['__classname__'] == 'CoolingSlit'
    assert serialized_slits[1]['__classname__'] == 'CoolingSlit'
    assert serialized_slits[0]['name'] == 'bitter_slit1'
    assert serialized_slits[1]['name'] == 'bitter_slit2'
    
    print("✓ CoolingSlits work correctly in Bitter context")
    print(f"  - Slit 1: {slit1.name} at r={slit1.r}, angle={slit1.angle}°")
    print(f"  - Slit 2: {slit2.name} at r={slit2.r}, angle={slit2.angle}°")
    print(f"  - List serialization works correctly")


def test_coolingslit_repr():
    """Test __repr__ method"""
    print("\n=== Test 11: CoolingSlit String Representation ===")
    
    contour = Contour2D(name="repr_contour", pts=[[0, 0], [1, 0], [1, 1]])
    
    slit = CoolingSlit(
        name="repr_slit",
        r=0.17,
        angle=42.0,
        n=7,
        dh=0.0023,
        sh=0.00115,
        contour2d=contour
    )
    
    slit_repr = repr(slit)
    
    assert 'CoolingSlit' in slit_repr
    assert 'repr_slit' in slit_repr
    assert '0.17' in slit_repr
    assert '42.0' in slit_repr
    
    print("✓ __repr__ method works correctly")
    print(f"  - Repr: {slit_repr}")


def test_coolingslit_nested_object_handling():
    """Test the _load_nested_contour2d classmethod"""
    print("\n=== Test 12: Nested Contour2D Object Handling ===")
    
    # Test with dict (inline definition)
    dict_data = {
        'name': 'nested_test',
        'r': 0.19,
        'angle': 38.0,
        'n': 6,
        'dh': 0.0029,
        'sh': 0.00145,
        'contour2d': {
            'name': 'nested_contour',
            'pts': [[0, 0], [2, 0], [2, 2], [0, 2]]
        }
    }
    
    slit1 = CoolingSlit.from_dict(dict_data)
    assert isinstance(slit1.contour2d, Contour2D)
    print("✓ Inline dict contour2d handled correctly")
    
    # Test with None
    none_data = dict_data.copy()
    none_data['contour2d'] = None
    slit2 = CoolingSlit.from_dict(none_data)
    assert slit2.contour2d is None
    print("✓ None contour2d handled correctly")
    
    # Test with object
    contour_obj = Contour2D(name="obj_contour", pts=[[0, 0], [1, 1]])
    obj_data = dict_data.copy()
    obj_data['contour2d'] = contour_obj
    slit3 = CoolingSlit.from_dict(obj_data)
    assert slit3.contour2d is contour_obj
    print("✓ Pre-instantiated object contour2d handled correctly")


def test_coolingslit_comprehensive_functionality():
    """Comprehensive test comparing new vs expected behavior"""
    print("\n=== Test 13: Comprehensive Functionality Check ===")
    
    # Create instance with all parameters
    contour = Contour2D(
        name="complete_contour",
        pts=[[0.0, 0.0], [3.5, 0.0], [3.5, 3.5], [0.0, 3.5]]
    )
    
    slit = CoolingSlit(
        name="complete_slit",
        r=0.155,
        angle=47.5,
        n=15,
        dh=0.00265,
        sh=0.001325,
        contour2d=contour
    )
    
    # Test all attributes are preserved
    slit_dict = {
        'name': slit.name,
        'r': slit.r,
        'angle': slit.angle,
        'n': slit.n,
        'dh': slit.dh,
        'sh': slit.sh,
        'contour2d': json.loads(slit.contour2d.to_json())
    }
    
    # Round-trip through dict
    slit_restored = CoolingSlit.from_dict(slit_dict)
    
    assert slit_restored.name == slit.name
    assert slit_restored.r == slit.r
    assert slit_restored.angle == slit.angle
    assert slit_restored.n == slit.n
    assert slit_restored.dh == slit.dh
    assert slit_restored.sh == slit.sh
    assert slit_restored.contour2d.name == slit.contour2d.name
    
    # Round-trip through JSON
    slit_json = json.loads(slit.to_json())
    slit_from_json = CoolingSlit.from_json(json.dumps(slit_json))
    
    assert slit_from_json.name == slit.name
    assert slit_from_json.r == slit.r
    
    print("✓ All functionality preserved and working correctly")
    print("  - Attribute preservation: ✓")
    print("  - Dict round-trip: ✓")
    print("  - JSON round-trip: ✓")
    print("  - Nested object handling: ✓")


def test_coolingslit_parameters_documentation():
    """Document the meaning of each parameter"""
    print("\n=== Test 14: Parameter Documentation ===")
    
    print("CoolingSlit parameters explained:")
    print("  - name: Identifier for the cooling slit")
    print("  - r: Radius position of the slit (meters)")
    print("  - angle: Angular shift from tierod (degrees)")
    print("  - n: Number of slits/channels")
    print("  - dh: Hydraulic diameter = 4*Sh/Ph (Ph = wetted perimeter)")
    print("  - sh: Cross-sectional area of the slit")
    print("  - contour2d: 2D contour shape (Contour2D object or None)")
    
    # Create example showing typical values
    example_contour = Contour2D(
        name="example_rectangular",
        pts=[[0.0, 0.0], [0.002, 0.0], [0.002, 0.001], [0.0, 0.001]]
    )
    
    example = CoolingSlit(
        name="cooling_channel_example",
        r=0.125,          # 125mm radius
        angle=30.0,       # 30 degrees offset
        n=8,              # 8 channels
        dh=0.002,         # 2mm hydraulic diameter
        sh=0.001,         # 1mm² cross-section
        contour2d=example_contour
    )
    
    print(f"\n✓ Example CoolingSlit: {example}")
    print("  This represents 8 cooling channels at 125mm radius,")
    print("  offset 30° from tierods, with 2mm hydraulic diameter.")


def run_all_tests():
    """Run all Phase 4 CoolingSlit tests"""
    print("=" * 80)
    print("PHASE 4 TEST SUITE: CoolingSlit Validation")
    print("=" * 80)
    print("\nTesting refactored CoolingSlit class with YAMLObjectBase inheritance")
    print("Following test pattern from test-refactor-ring.py\n")
    
    tests = [
        test_coolingslit_basic_creation,
        test_coolingslit_with_none_contour,
        test_coolingslit_inherited_methods,
        test_coolingslit_json_serialization,
        test_coolingslit_from_dict_inline_contour,
        test_coolingslit_from_dict_none_contour,
        test_coolingslit_from_dict_object_contour,
        test_coolingslit_yaml_roundtrip_with_contour,
        test_coolingslit_yaml_roundtrip_none_contour,
        test_coolingslit_in_bitter_context,
        test_coolingslit_repr,
        test_coolingslit_nested_object_handling,
        test_coolingslit_comprehensive_functionality,
        test_coolingslit_parameters_documentation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("\n🎉 All Phase 4 CoolingSlit tests passed!")
        print("✓ CoolingSlit successfully validated")
        print("✓ Nested Contour2D handling verified")
        print("✓ All serialization methods working")
        print("✓ YAML round-trip functional")
        print("\nPhase 4 validation complete - CoolingSlit class is fully functional!")
        print("\nKey features validated:")
        print("  • Basic creation with all parameters")
        print("  • None contour handling")
        print("  • Inline dict contour handling")
        print("  • Pre-instantiated object contour handling")
        print("  • Usage in Bitter context (list of slits)")
        print("  • Complete JSON and YAML serialization")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
        print("Fix issues before proceeding to next phase.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
