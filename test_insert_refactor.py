#!/usr/bin/env python3
"""
Test script for refactored Insert class - Phase 4 validation
Follows the pattern of test-refactor-ring.py
"""

import os
import json
import tempfile
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Probe import Probe
from python_magnetgeo.validation import ValidationError

def test_insert_basic_creation():
    """Test basic Insert creation with nested objects"""
    print("\n=== Test 1: Basic Insert Creation ===")
    
    # Create nested objects
    axi = ModelAxi("test_axi", 30.0, [3.0, 2.5], [10.0, 12.0])
    model3d = Model3D("test_model3d", "SALOME", False, False)
    shape = Shape("test_shape", "rectangular", 8, [90.0] * 4, 0, "CENTER")
    
    helix = Helix(
        name="test_helix",
        r=[12.0, 22.0],
        z=[0.0, 60.0],
        cutwidth=1.8,
        odd=False,
        dble=True,
        modelaxi=axi,
        model3d=model3d,
        shape=shape
    )
    
    ring = Ring(
        name="test_ring",
        r=[10.0, 20.0, 24.0, 28.0],
        z=[25.0, 35.0],
        n=6,
        angle=30.0,
        bpside=True,
        fillets=False
    )
    
    probe = Probe(
        name="test_probe",
        type="voltage_taps",
        labels=["V1", "V2"],
        points=[[15.0, 0.0, 30.0], [19.0, 0.0, 45.0]]
    )
    
    # Create Insert
    insert = Insert(
        name="test_insert",
        helices=[helix],
        rings=[ring],
        currentleads=["inner_lead"],
        hangles=[0.0, 180.0],
        rangles=[0.0, 90.0, 180.0, 270.0],
        innerbore=8.0,
        outerbore=26.0,
        probes=[probe]
    )
    
    print(f"✓ Insert created: {insert.name}")
    print(f"  - Helices: {len(insert.helices)}")
    print(f"  - Rings: {len(insert.rings)}")
    print(f"  - Probes: {len(insert.probes)}")
    print(f"  - Inner bore: {insert.innerbore}")
    print(f"  - Outer bore: {insert.outerbore}")
    
    assert insert.name == "test_insert"
    assert len(insert.helices) == 1
    assert len(insert.rings) == 1
    assert len(insert.probes) == 1
    assert insert.innerbore == 8.0
    assert insert.outerbore == 26.0
    
    print("✓ All basic attributes verified")


def test_insert_inherited_methods():
    """Test that Insert has all inherited serialization methods"""
    print("\n=== Test 2: Inherited Serialization Methods ===")
    
    # Create minimal Insert for testing
    helix = Helix(
        name="minimal_helix",
        r=[10.0, 20.0],
        z=[0.0, 50.0],
        cutwidth=2.0,
        odd=False,
        dble=False,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    insert = Insert(
        name="minimal_insert",
        helices=[helix],
        rings=[],
        currentleads=[],
        hangles=[0.0],
        rangles=[0.0],
        innerbore=5.0,
        outerbore=25.0,
        probes=[]
    )
    
    # Check all inherited methods exist
    required_methods = ['dump', 'to_json', 'write_to_json', 'from_yaml', 'from_json', 'from_dict']
    for method in required_methods:
        if method in ['from_yaml', 'from_json', 'from_dict']:
            assert hasattr(Insert, method), f"Missing class method: {method}"
        else:
            assert hasattr(insert, method), f"Missing instance method: {method}"
    
    print("✓ All serialization methods inherited correctly")


def test_insert_json_serialization():
    """Test JSON serialization and deserialization"""
    print("\n=== Test 3: JSON Serialization ===")
    
    helix = Helix(
        name="json_helix",
        r=[15.0, 25.0],
        z=[10.0, 70.0],
        cutwidth=1.5,
        odd=True,
        dble=False,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    insert = Insert(
        name="json_insert",
        helices=[helix],
        rings=[],
        currentleads=["outer_lead"],
        hangles=[0.0, 90.0],
        rangles=[45.0, 135.0],
        innerbore=10.0,
        outerbore=30.0,
        probes=[]
    )
    
    # Test JSON serialization
    json_str = insert.to_json()
    parsed = json.loads(json_str)
    
    assert parsed['name'] == 'json_insert'
    assert parsed['__classname__'] == 'Insert'
    assert parsed['innerbore'] == 10.0
    assert parsed['outerbore'] == 30.0
    assert len(parsed['hangles']) == 2
    assert len(parsed['rangles']) == 2
    
    print("✓ JSON serialization works correctly")
    print(f"  - Serialized name: {parsed['name']}")
    print(f"  - Class type: {parsed['__classname__']}")


def test_insert_from_dict():
    """Test Insert creation from dictionary"""
    print("\n=== Test 4: from_dict Creation ===")
    
    # Create dict representation
    test_dict = {
        'name': 'dict_insert',
        'helices': ['helix1.yaml', 'helix2.yaml'],
        'rings': ['ring1.yaml'],
        'currentleads': ['inner', 'outer'],
        'hangles': [0.0, 120.0, 240.0],
        'rangles': [0.0, 90.0, 180.0, 270.0],
        'innerbore': 12.0,
        'outerbore': 35.0,
        'probes': []
    }
    
    # Note: from_dict with string references will try to load files
    # For testing, we'll create Insert directly with objects instead
    helix = Helix(
        name="dict_helix",
        r=[14.0, 24.0],
        z=[5.0, 65.0],
        cutwidth=1.8,
        odd=False,
        dble=True,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    dict_with_objects = test_dict.copy()
    dict_with_objects['helices'] = [helix]
    dict_with_objects['rings'] = []
    
    dict_insert = Insert.from_dict(dict_with_objects)
    
    assert dict_insert.name == 'dict_insert'
    assert len(dict_insert.helices) == 1
    assert dict_insert.innerbore == 12.0
    assert dict_insert.outerbore == 35.0
    
    print("✓ from_dict creation works correctly")
    print(f"  - Name: {dict_insert.name}")
    print(f"  - Helices loaded: {len(dict_insert.helices)}")


def test_insert_validation():
    """Test Insert validation catches invalid inputs"""
    print("\n=== Test 5: Input Validation ===")
    
    helix = Helix(
        name="valid_helix",
        r=[10.0, 20.0],
        z=[0.0, 50.0],
        cutwidth=2.0,
        odd=False,
        dble=False,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    # Test 1: Empty name
    try:
        Insert(
            name="",
            helices=[helix],
            rings=[],
            currentleads=[],
            hangles=[0.0],
            rangles=[0.0],
            innerbore=5.0,
            outerbore=25.0,
            probes=[]
        )
        assert False, "Should have raised ValidationError for empty name"
    except ValidationError as e:
        print(f"✓ Empty name validation: {e}")
    
    # Test 2: Invalid bore dimensions (inner >= outer)
    try:
        Insert(
            name="bad_bore",
            helices=[helix],
            rings=[],
            currentleads=[],
            hangles=[0.0],
            rangles=[0.0],
            innerbore=30.0,
            outerbore=20.0,
            probes=[]
        )
        assert False, "Should have raised ValidationError for invalid bore dimensions"
    except ValidationError as e:
        print(f"✓ Invalid bore validation: {e}")
    
    print("✓ All validation checks working correctly")


def test_insert_bounding_box():
    """Test Insert boundingBox calculation"""
    print("\n=== Test 6: BoundingBox Calculation ===")
    
    helix = Helix(
        name="bbox_helix",
        r=[12.0, 22.0],
        z=[0.0, 60.0],
        cutwidth=1.8,
        odd=False,
        dble=False,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    ring = Ring(
        name="bbox_ring",
        r=[10.0, 20.0, 24.0, 28.0],
        z=[25.0, 35.0],
        n=1,
        angle=0.0,
        bpside=True,
        fillets=False
    )
    
    insert = Insert(
        name="bbox_insert",
        helices=[helix],
        rings=[ring],
        currentleads=[],
        hangles=[0.0],
        rangles=[0.0],
        innerbore=8.0,
        outerbore=26.0,
        probes=[]
    )
    
    rb, zb = insert.boundingBox()
    
    # Check radial bounds match helix
    assert rb[0] == 12.0, f"Expected rb[0]=12.0, got {rb[0]}"
    assert rb[1] == 22.0, f"Expected rb[1]=22.0, got {rb[1]}"
    
    # Check z bounds are extended by ring height
    ring_height = abs(ring.z[1] - ring.z[0])
    expected_z_min = helix.z[0] - ring_height
    expected_z_max = helix.z[1] + ring_height
    
    assert zb[0] == expected_z_min, f"Expected zb[0]={expected_z_min}, got {zb[0]}"
    assert zb[1] == expected_z_max, f"Expected zb[1]={expected_z_max}, got {zb[1]}"
    
    print(f"✓ BoundingBox calculated correctly")
    print(f"  - Radial bounds: {rb}")
    print(f"  - Axial bounds: {zb}")
    print(f"  - Ring height adjustment: ±{ring_height}")


def test_insert_intersection():
    """Test Insert intersection detection"""
    print("\n=== Test 7: Intersection Detection ===")
    
    helix = Helix(
        name="intersect_helix",
        r=[10.0, 20.0],
        z=[0.0, 50.0],
        cutwidth=2.0,
        odd=False,
        dble=False,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    insert = Insert(
        name="intersect_insert",
        helices=[helix],
        rings=[],
        currentleads=[],
        hangles=[0.0],
        rangles=[0.0],
        innerbore=5.0,
        outerbore=25.0,
        probes=[]
    )
    
    # Test 1: Overlapping rectangle
    overlap_r = [15.0, 25.0]
    overlap_z = [20.0, 70.0]
    assert insert.intersect(overlap_r, overlap_z) == True
    print("✓ Detects overlapping rectangle")
    
    # Test 2: Non-overlapping rectangle (in r)
    no_overlap_r = [30.0, 40.0]
    no_overlap_z = [0.0, 50.0]
    assert insert.intersect(no_overlap_r, no_overlap_z) == False
    print("✓ Detects non-overlapping rectangle (r-dimension)")
    
    # Test 3: Non-overlapping rectangle (in z)
    no_overlap_r2 = [10.0, 20.0]
    no_overlap_z2 = [100.0, 150.0]
    assert insert.intersect(no_overlap_r2, no_overlap_z2) == False
    print("✓ Detects non-overlapping rectangle (z-dimension)")


def test_insert_get_nhelices():
    """Test Insert helix counting"""
    print("\n=== Test 8: Helix Counting ===")
    
    helix1 = Helix("h1", [10.0, 20.0], [0.0, 50.0], 2.0, False, False, None, None, None)
    helix2 = Helix("h2", [25.0, 35.0], [60.0, 110.0], 1.5, True, False, None, None, None)
    helix3 = Helix("h3", [40.0, 50.0], [0.0, 50.0], 1.8, False, True, None, None, None)
    
    insert = Insert(
        name="multi_helix",
        helices=[helix1, helix2, helix3],
        rings=[],
        currentleads=[],
        hangles=[0.0],
        rangles=[0.0],
        innerbore=5.0,
        outerbore=55.0,
        probes=[]
    )
    
    count = insert.get_nhelices()
    assert count == 3, f"Expected 3 helices, got {count}"
    
    print(f"✓ get_nhelices() returns correct count: {count}")


def test_insert_yaml_roundtrip():
    """Test YAML dump and load roundtrip"""
    print("\n=== Test 9: YAML Round-trip ===")
    
    helix = Helix(
        name="yaml_helix",
        r=[13.0, 23.0],
        z=[5.0, 55.0],
        cutwidth=1.7,
        odd=False,
        dble=True,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    insert = Insert(
        name="yaml_insert",
        helices=[helix],
        rings=[],
        currentleads=["inner"],
        hangles=[0.0, 180.0],
        rangles=[0.0, 90.0],
        innerbore=9.0,
        outerbore=27.0,
        probes=[]
    )
    
    # Dump to YAML
    insert.dump()
    yaml_file = f"{insert.name}.yaml"
    
    assert os.path.exists(yaml_file), "YAML file not created"
    print(f"✓ YAML dump created: {yaml_file}")
    
    # Load back
    loaded_insert = Insert.from_yaml(yaml_file, debug=True)
    
    assert loaded_insert.name == insert.name
    assert loaded_insert.innerbore == insert.innerbore
    assert loaded_insert.outerbore == insert.outerbore
    assert len(loaded_insert.helices) == len(insert.helices)
    
    print("✓ YAML round-trip successful")
    print(f"  - Original: {insert.name}")
    print(f"  - Loaded: {loaded_insert.name}")
    
    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


def test_insert_with_probes():
    """Test Insert with Probe objects"""
    print("\n=== Test 10: Insert with Probes ===")
    
    helix = Helix(
        name="probe_helix",
        r=[15.0, 25.0],
        z=[10.0, 70.0],
        cutwidth=1.8,
        odd=False,
        dble=False,
        modelaxi=None,
        model3d=None,
        shape=None
    )
    
    probe1 = Probe(
        name="voltage_probe",
        type="voltage_taps",
        labels=["V1", "V2", "V3"],
        points=[[18.0, 0.0, 20.0], [18.0, 0.0, 40.0], [18.0, 0.0, 60.0]]
    )
    
    probe2 = Probe(
        name="current_probe",
        type="current_taps",
        labels=["I1", "I2"],
        points=[[20.0, 0.0, 30.0], [20.0, 0.0, 50.0]]
    )
    
    insert = Insert(
        name="probed_insert",
        helices=[helix],
        rings=[],
        currentleads=[],
        hangles=[0.0],
        rangles=[0.0],
        innerbore=10.0,
        outerbore=30.0,
        probes=[probe1, probe2]
    )
    
    assert len(insert.probes) == 2
    assert insert.probes[0].name == "voltage_probe"
    assert insert.probes[1].name == "current_probe"
    
    print("✓ Insert with probes created successfully")
    print(f"  - Probe 1: {insert.probes[0].name} ({len(insert.probes[0].labels)} taps)")
    print(f"  - Probe 2: {insert.probes[1].name} ({len(insert.probes[1].labels)} taps)")


def run_all_tests():
    """Run all Insert tests"""
    print("=" * 70)
    print("TESTING REFACTORED INSERT CLASS (Phase 4)")
    print("=" * 70)
    
    tests = [
        test_insert_basic_creation,
        test_insert_inherited_methods,
        test_insert_json_serialization,
        test_insert_from_dict,
        test_insert_validation,
        test_insert_bounding_box,
        test_insert_intersection,
        test_insert_get_nhelices,
        test_insert_yaml_roundtrip,
        test_insert_with_probes
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 All Insert tests passed! Phase 4 validation complete.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review the errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
