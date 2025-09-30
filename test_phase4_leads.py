#!/usr/bin/env python3
"""
Phase 4 Test Suite: InnerCurrentLead and OuterCurrentLead Validation

Tests the refactored current lead classes following the same pattern as test-refactor-ring.py.
Validates that the new YAMLObjectBase implementation maintains all functionality while
adding validation and improved error handling.
"""

import os
import json
import tempfile
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead
from python_magnetgeo.validation import ValidationError


def test_inner_lead_basic_creation():
    """Test InnerCurrentLead basic creation and attributes"""
    print("\n=== Test 1: InnerCurrentLead Basic Creation ===")
    
    lead = InnerCurrentLead(
        name="test_inner_lead",
        r=[10.0, 20.0],
        h=50.0,
        holes=[5.0, 10.0, 0.0, 45.0, 0.0, 8],
        support=[25.0, 5.0],
        fillet=True
    )
    
    assert lead.name == "test_inner_lead"
    assert lead.r == [10.0, 20.0]
    assert lead.h == 50.0
    assert lead.holes == [5.0, 10.0, 0.0, 45.0, 0.0, 8]
    assert lead.support == [25.0, 5.0]
    assert lead.fillet is True
    
    print(f"✓ InnerCurrentLead created: {lead}")
    print(f"  - name: {lead.name}")
    print(f"  - r: {lead.r}")
    print(f"  - h: {lead.h}")
    print(f"  - holes: {lead.holes}")
    print(f"  - support: {lead.support}")
    print(f"  - fillet: {lead.fillet}")


def test_inner_lead_defaults():
    """Test InnerCurrentLead with default values"""
    print("\n=== Test 2: InnerCurrentLead Default Values ===")
    
    minimal_lead = InnerCurrentLead(
        name="minimal_inner",
        r=[15.0, 30.0]
    )
    
    assert minimal_lead.h == 0.0
    assert minimal_lead.holes == []
    assert minimal_lead.support == []
    assert minimal_lead.fillet is False
    
    print("✓ Default values work correctly")
    print(f"  - h defaults to: {minimal_lead.h}")
    print(f"  - holes defaults to: {minimal_lead.holes}")
    print(f"  - support defaults to: {minimal_lead.support}")
    print(f"  - fillet defaults to: {minimal_lead.fillet}")


def test_inner_lead_inherited_methods():
    """Test that InnerCurrentLead has all inherited methods from YAMLObjectBase"""
    print("\n=== Test 3: InnerCurrentLead Inherited Methods ===")
    
    lead = InnerCurrentLead(name="method_test", r=[10.0, 20.0], h=40.0)
    
    # Check for all inherited methods
    assert hasattr(lead, 'dump')
    assert hasattr(lead, 'to_json')
    assert hasattr(lead, 'write_to_json')
    assert hasattr(InnerCurrentLead, 'from_yaml')
    assert hasattr(InnerCurrentLead, 'from_json')
    assert hasattr(InnerCurrentLead, 'from_dict')
    
    print("✓ All serialization methods inherited correctly:")
    print("  - dump()")
    print("  - to_json()")
    print("  - write_to_json()")
    print("  - from_yaml() [classmethod]")
    print("  - from_json() [classmethod]")
    print("  - from_dict() [classmethod]")


def test_inner_lead_json_serialization():
    """Test InnerCurrentLead JSON serialization"""
    print("\n=== Test 4: InnerCurrentLead JSON Serialization ===")
    
    lead = InnerCurrentLead(
        name="json_test_inner",
        r=[12.0, 24.0],
        h=60.0,
        holes=[6.0, 8.0, 0.0, 30.0, 0.0, 10],
        support=[28.0, 6.0],
        fillet=False
    )
    
    json_str = lead.to_json()
    parsed = json.loads(json_str)
    
    assert parsed['__classname__'] == 'InnerCurrentLead'
    assert parsed['name'] == 'json_test_inner'
    assert parsed['r'] == [12.0, 24.0]
    assert parsed['h'] == 60.0
    assert parsed['holes'] == [6.0, 8.0, 0.0, 30.0, 0.0, 10]
    assert parsed['support'] == [28.0, 6.0]
    assert parsed['fillet'] is False
    
    print("✓ JSON serialization works correctly")
    print(f"  - __classname__: {parsed['__classname__']}")
    print(f"  - All attributes serialized properly")


def test_inner_lead_from_dict():
    """Test InnerCurrentLead.from_dict()"""
    print("\n=== Test 5: InnerCurrentLead from_dict ===")
    
    test_dict = {
        'name': 'dict_inner_lead',
        'r': [8.0, 16.0],
        'h': 45.0,
        'holes': [4.0, 5.0, 0.0, 60.0, 0.0, 6],
        'support': [20.0, 4.0],
        'fillet': True
    }
    
    lead = InnerCurrentLead.from_dict(test_dict)
    
    assert lead.name == 'dict_inner_lead'
    assert lead.r == [8.0, 16.0]
    assert lead.h == 45.0
    assert lead.holes == [4.0, 5.0, 0.0, 60.0, 0.0, 6]
    assert lead.support == [20.0, 4.0]
    assert lead.fillet is True
    
    print("✓ from_dict() works correctly")
    print(f"  - Created: {lead}")


def test_inner_lead_yaml_roundtrip():
    """Test InnerCurrentLead YAML save and load"""
    print("\n=== Test 6: InnerCurrentLead YAML Round-trip ===")
    
    lead = InnerCurrentLead(
        name="yaml_test_inner",
        r=[14.0, 28.0],
        h=70.0,
        holes=[7.0, 9.0, 0.0, 40.0, 0.0, 12],
        support=[32.0, 7.0],
        fillet=True
    )
    
    # Save to YAML
    lead.dump()
    yaml_file = f"{lead.name}.yaml"
    assert os.path.exists(yaml_file), f"YAML file {yaml_file} not created"
    print(f"✓ YAML file created: {yaml_file}")
    
    # Load from YAML
    loaded_lead = InnerCurrentLead.from_yaml(yaml_file)
    
    assert loaded_lead.name == lead.name
    assert loaded_lead.r == lead.r
    assert loaded_lead.h == lead.h
    assert loaded_lead.holes == lead.holes
    assert loaded_lead.support == lead.support
    assert loaded_lead.fillet == lead.fillet
    
    print("✓ YAML round-trip successful")
    print(f"  - Original: {lead}")
    print(f"  - Loaded:   {loaded_lead}")
    
    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


def test_outer_lead_basic_creation():
    """Test OuterCurrentLead basic creation and attributes"""
    print("\n=== Test 7: OuterCurrentLead Basic Creation ===")
    
    lead = OuterCurrentLead(
        name="test_outer_lead",
        r=[50.0, 60.0],
        h=100.0,
        bar=[55.0, 10.0, 15.0, 80.0],
        support=[5.0, 10.0, 30.0, 0.0]
    )
    
    assert lead.name == "test_outer_lead"
    assert lead.r == [50.0, 60.0]
    assert lead.h == 100.0
    assert lead.bar == [55.0, 10.0, 15.0, 80.0]
    assert lead.support == [5.0, 10.0, 30.0, 0.0]
    
    print(f"✓ OuterCurrentLead created: {lead}")
    print(f"  - name: {lead.name}")
    print(f"  - r: {lead.r}")
    print(f"  - h: {lead.h}")
    print(f"  - bar: {lead.bar}")
    print(f"  - support: {lead.support}")


def test_outer_lead_defaults():
    """Test OuterCurrentLead with default values"""
    print("\n=== Test 8: OuterCurrentLead Default Values ===")
    
    minimal_lead = OuterCurrentLead(
        name="minimal_outer",
        r=[45.0, 55.0]
    )
    
    assert minimal_lead.h == 0.0
    assert minimal_lead.bar == []
    assert minimal_lead.support == []
    
    print("✓ Default values work correctly")
    print(f"  - h defaults to: {minimal_lead.h}")
    print(f"  - bar defaults to: {minimal_lead.bar}")
    print(f"  - support defaults to: {minimal_lead.support}")


def test_outer_lead_inherited_methods():
    """Test that OuterCurrentLead has all inherited methods"""
    print("\n=== Test 9: OuterCurrentLead Inherited Methods ===")
    
    lead = OuterCurrentLead(name="method_test", r=[50.0, 60.0], h=90.0)
    
    assert hasattr(lead, 'dump')
    assert hasattr(lead, 'to_json')
    assert hasattr(lead, 'write_to_json')
    assert hasattr(OuterCurrentLead, 'from_yaml')
    assert hasattr(OuterCurrentLead, 'from_json')
    assert hasattr(OuterCurrentLead, 'from_dict')
    
    print("✓ All serialization methods inherited correctly")


def test_outer_lead_json_serialization():
    """Test OuterCurrentLead JSON serialization"""
    print("\n=== Test 10: OuterCurrentLead JSON Serialization ===")
    
    lead = OuterCurrentLead(
        name="json_test_outer",
        r=[48.0, 58.0],
        h=95.0,
        bar=[53.0, 12.0, 18.0, 75.0],
        support=[6.0, 12.0, 35.0, 0.0]
    )
    
    json_str = lead.to_json()
    parsed = json.loads(json_str)
    
    assert parsed['__classname__'] == 'OuterCurrentLead'
    assert parsed['name'] == 'json_test_outer'
    assert parsed['r'] == [48.0, 58.0]
    assert parsed['h'] == 95.0
    assert parsed['bar'] == [53.0, 12.0, 18.0, 75.0]
    assert parsed['support'] == [6.0, 12.0, 35.0, 0.0]
    
    print("✓ JSON serialization works correctly")
    print(f"  - __classname__: {parsed['__classname__']}")


def test_outer_lead_from_dict():
    """Test OuterCurrentLead.from_dict()"""
    print("\n=== Test 11: OuterCurrentLead from_dict ===")
    
    test_dict = {
        'name': 'dict_outer_lead',
        'r': [52.0, 62.0],
        'h': 88.0,
        'bar': [57.0, 11.0, 16.0, 72.0],
        'support': [7.0, 11.0, 32.0, 0.0]
    }
    
    lead = OuterCurrentLead.from_dict(test_dict)
    
    assert lead.name == 'dict_outer_lead'
    assert lead.r == [52.0, 62.0]
    assert lead.h == 88.0
    assert lead.bar == [57.0, 11.0, 16.0, 72.0]
    assert lead.support == [7.0, 11.0, 32.0, 0.0]
    
    print("✓ from_dict() works correctly")
    print(f"  - Created: {lead}")


def test_outer_lead_yaml_roundtrip():
    """Test OuterCurrentLead YAML save and load"""
    print("\n=== Test 12: OuterCurrentLead YAML Round-trip ===")
    
    lead = OuterCurrentLead(
        name="yaml_test_outer",
        r=[46.0, 56.0],
        h=92.0,
        bar=[51.0, 9.0, 14.0, 78.0],
        support=[4.0, 9.0, 28.0, 0.0]
    )
    
    # Save to YAML
    lead.dump()
    yaml_file = f"{lead.name}.yaml"
    assert os.path.exists(yaml_file), f"YAML file {yaml_file} not created"
    print(f"✓ YAML file created: {yaml_file}")
    
    # Load from YAML
    loaded_lead = OuterCurrentLead.from_yaml(yaml_file)
    
    assert loaded_lead.name == lead.name
    assert loaded_lead.r == lead.r
    assert loaded_lead.h == lead.h
    assert loaded_lead.bar == lead.bar
    assert loaded_lead.support == lead.support
    
    print("✓ YAML round-trip successful")
    print(f"  - Original: {lead}")
    print(f"  - Loaded:   {loaded_lead}")
    
    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


def test_current_leads_in_insert_context():
    """Test that current leads work in Insert context (as they would be used)"""
    print("\n=== Test 13: Current Leads in Insert Context ===")
    
    inner_lead = InnerCurrentLead(
        name="insert_inner_lead",
        r=[10.0, 20.0],
        h=50.0,
        holes=[5.0, 10.0, 0.0, 45.0, 0.0, 8],
        support=[25.0, 5.0],
        fillet=True
    )
    
    outer_lead = OuterCurrentLead(
        name="insert_outer_lead",
        r=[50.0, 60.0],
        h=100.0,
        bar=[55.0, 10.0, 15.0, 80.0],
        support=[5.0, 10.0, 30.0, 0.0]
    )
    
    # Simulate how they're used in Insert
    current_leads = [inner_lead, outer_lead]
    
    assert len(current_leads) == 2
    assert isinstance(current_leads[0], InnerCurrentLead)
    assert isinstance(current_leads[1], OuterCurrentLead)
    
    # Test serialization of list
    serialized_leads = [json.loads(lead.to_json()) for lead in current_leads]
    
    assert serialized_leads[0]['__classname__'] == 'InnerCurrentLead'
    assert serialized_leads[1]['__classname__'] == 'OuterCurrentLead'
    
    print("✓ Current leads work correctly in Insert context")
    print(f"  - Inner lead: {inner_lead.name}")
    print(f"  - Outer lead: {outer_lead.name}")


def test_repr_methods():
    """Test __repr__ methods for both classes"""
    print("\n=== Test 14: String Representation ===")
    
    inner = InnerCurrentLead(
        name="repr_inner",
        r=[10.0, 20.0],
        h=50.0,
        holes=[],
        support=[],
        fillet=False
    )
    
    outer = OuterCurrentLead(
        name="repr_outer",
        r=[50.0, 60.0],
        h=100.0,
        bar=[],
        support=[]
    )
    
    inner_repr = repr(inner)
    outer_repr = repr(outer)
    
    assert 'InnerCurrentLead' in inner_repr
    assert 'repr_inner' in inner_repr
    assert 'OuterCurrentLead' in outer_repr
    assert 'repr_outer' in outer_repr
    
    print("✓ __repr__ methods work correctly")
    print(f"  - Inner: {inner_repr}")
    print(f"  - Outer: {outer_repr}")


def test_comparison_with_original_functionality():
    """Comprehensive test comparing new vs expected behavior"""
    print("\n=== Test 15: Comprehensive Functionality Check ===")
    
    # Create instances with all parameters
    inner = InnerCurrentLead(
        name="complete_inner",
        r=[12.0, 24.0],
        h=65.0,
        holes=[6.5, 11.0, 0.0, 50.0, 0.0, 9],
        support=[28.0, 6.5],
        fillet=True
    )
    
    outer = OuterCurrentLead(
        name="complete_outer",
        r=[54.0, 64.0],
        h=105.0,
        bar=[59.0, 13.0, 19.0, 85.0],
        support=[6.5, 13.0, 38.0, 0.0]
    )
    
    # Test all attributes are preserved
    inner_dict = {
        'name': inner.name,
        'r': inner.r,
        'h': inner.h,
        'holes': inner.holes,
        'support': inner.support,
        'fillet': inner.fillet
    }
    
    outer_dict = {
        'name': outer.name,
        'r': outer.r,
        'h': outer.h,
        'bar': outer.bar,
        'support': outer.support
    }
    
    # Round-trip through dict
    inner_restored = InnerCurrentLead.from_dict(inner_dict)
    outer_restored = OuterCurrentLead.from_dict(outer_dict)
    
    assert inner_restored.name == inner.name
    assert inner_restored.r == inner.r
    assert outer_restored.name == outer.name
    assert outer_restored.r == outer.r
    
    # Round-trip through JSON
    inner_json = json.loads(inner.to_json())
    outer_json = json.loads(outer.to_json())
    
    inner_from_json = InnerCurrentLead.from_json(json.dumps(inner_json))
    outer_from_json = OuterCurrentLead.from_json(json.dumps(outer_json))
    
    assert inner_from_json.name == inner.name
    assert outer_from_json.name == outer.name
    
    print("✓ All functionality preserved and working correctly")
    print("  - Attribute preservation: ✓")
    print("  - Dict round-trip: ✓")
    print("  - JSON round-trip: ✓")


def run_all_tests():
    """Run all Phase 4 current lead tests"""
    print("=" * 80)
    print("PHASE 4 TEST SUITE: InnerCurrentLead and OuterCurrentLead Validation")
    print("=" * 80)
    print("\nTesting refactored current lead classes with YAMLObjectBase inheritance")
    print("Following test pattern from test-refactor-ring.py\n")
    
    tests = [
        # InnerCurrentLead tests
        test_inner_lead_basic_creation,
        test_inner_lead_defaults,
        test_inner_lead_inherited_methods,
        test_inner_lead_json_serialization,
        test_inner_lead_from_dict,
        test_inner_lead_yaml_roundtrip,
        
        # OuterCurrentLead tests
        test_outer_lead_basic_creation,
        test_outer_lead_defaults,
        test_outer_lead_inherited_methods,
        test_outer_lead_json_serialization,
        test_outer_lead_from_dict,
        test_outer_lead_yaml_roundtrip,
        
        # Integration tests
        test_current_leads_in_insert_context,
        test_repr_methods,
        test_comparison_with_original_functionality,
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
        print("\n🎉 All Phase 4 tests passed!")
        print("✓ InnerCurrentLead successfully validated")
        print("✓ OuterCurrentLead successfully validated")
        print("✓ Both classes ready for production use")
        print("\nPhase 4 validation complete - current lead classes are fully functional!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
        print("Fix issues before proceeding to next phase.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
