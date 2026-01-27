#!/usr/bin/env python3
"""
Test script for Phase 4 refactored classes: Chamfer, Groove, ModelAxi

Tests that the refactored classes work correctly with the new base classes
and validation framework, following the spirit of test-refactor-ring.py
"""

import os
import json
import tempfile
import math
from python_magnetgeo.Chamfer import Chamfer
from python_magnetgeo.Groove import Groove
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.validation import ValidationError


def test_refactored_chamfer():
    """Test that refactored Chamfer has identical functionality"""
    print("=" * 60)
    print("Testing refactored Chamfer functionality...")
    print("=" * 60)

    # Test basic creation with alpha
    chamfer_alpha = Chamfer(
        name="test_chamfer_alpha", side="HP", rside="rint", alpha=30.0, dr=None, l=10.0
    )

    print(f"✓ Chamfer (alpha) created: {chamfer_alpha}")

    # Test basic creation with dr
    chamfer_dr = Chamfer(
        name="test_chamfer_dr", side="BP", rside="rext", alpha=None, dr=5.0, l=10.0
    )

    print(f"✓ Chamfer (dr) created: {chamfer_dr}")

    # Test that all inherited methods exist
    assert hasattr(chamfer_alpha, "write_to_yaml")
    assert hasattr(chamfer_alpha, "to_json")
    assert hasattr(chamfer_alpha, "write_to_json")
    assert hasattr(Chamfer, "from_yaml")
    assert hasattr(Chamfer, "from_json")
    assert hasattr(Chamfer, "from_dict")

    print("✓ All serialization methods inherited correctly")

    # Test JSON serialization
    json_str = chamfer_alpha.to_json()
    parsed = json.loads(json_str)
    assert parsed["name"] == "test_chamfer_alpha"
    assert parsed["side"] == "HP"
    assert parsed["rside"] == "rint"
    assert parsed["alpha"] == 30.0
    assert parsed["l"] == 10.0
    assert parsed["__classname__"] == "Chamfer"

    print("✓ JSON serialization works")

    # Test from_dict with alpha
    dict_alpha = {
        "name": "dict_chamfer_alpha",
        "side": "HP",
        "rside": "rint",
        "alpha": 45.0,
        "l": 15.0,
    }

    dict_chamfer = Chamfer.from_dict(dict_alpha)
    assert dict_chamfer.name == "dict_chamfer_alpha"
    assert dict_chamfer.alpha == 45.0
    assert dict_chamfer.dr is None

    print("✓ from_dict works (alpha)")

    # Test from_dict with dr
    dict_dr = {"name": "dict_chamfer_dr", "side": "BP", "rside": "rext", "dr": 7.5, "l": 20.0}

    dict_chamfer_dr = Chamfer.from_dict(dict_dr)
    assert dict_chamfer_dr.name == "dict_chamfer_dr"
    assert dict_chamfer_dr.dr == 7.5
    assert dict_chamfer_dr.alpha is None

    print("✓ from_dict works (dr)")

    # Test getDr method
    dr_calculated = chamfer_alpha.getDr()
    expected_dr = 10.0 * math.tan(math.pi / 180.0 * 30.0)
    assert abs(dr_calculated - expected_dr) < 1e-6
    print(f"✓ getDr() works: {dr_calculated:.6f} (expected: {expected_dr:.6f})")

    # Test getAngle method
    angle_calculated = chamfer_dr.getAngle()
    expected_angle = math.atan2(5.0, 10.0) * 180.0 / math.pi
    assert abs(angle_calculated - expected_angle) < 1e-6
    print(f"✓ getAngle() works: {angle_calculated:.6f} (expected: {expected_angle:.6f})")

    # Test YAML round-trip
    chamfer_alpha.write_to_yaml()
    print("✓ YAML dump works")

    loaded_chamfer = Chamfer.from_yaml("test_chamfer_alpha.yaml", debug=True)
    assert loaded_chamfer.name == chamfer_alpha.name
    assert loaded_chamfer.side == chamfer_alpha.side
    assert loaded_chamfer.alpha == chamfer_alpha.alpha

    print("✓ YAML round-trip works")

    # Clean up
    if os.path.exists("test_chamfer_alpha.yaml"):
        os.unlink("test_chamfer_alpha.yaml")

    print("✓ Chamfer successfully refactored!\n")


def test_refactored_groove():
    """Test that refactored Groove has identical functionality"""
    print("=" * 60)
    print("Testing refactored Groove functionality...")
    print("=" * 60)

    # Test basic creation
    groove = Groove(name="test_groove", gtype="rint", n=4, eps=2.5)

    print(f"✓ Groove created: {groove}")

    # Test default constructor
    empty_groove = Groove()
    assert empty_groove.name == ""
    assert empty_groove.gtype is None
    assert empty_groove.n == 0
    assert empty_groove.eps == 0
    print("✓ Default Groove created successfully")

    # Test that all inherited methods exist
    assert hasattr(groove, "write_to_yaml")
    assert hasattr(groove, "to_json")
    assert hasattr(groove, "write_to_yaml")
    assert hasattr(Groove, "from_yaml")
    assert hasattr(Groove, "from_json")
    assert hasattr(Groove, "from_dict")

    print("✓ All serialization methods inherited correctly")

    # Test JSON serialization
    json_str = groove.to_json()
    parsed = json.loads(json_str)
    assert parsed["name"] == "test_groove"
    assert parsed["gtype"] == "rint"
    assert parsed["n"] == 4
    assert parsed["eps"] == 2.5
    assert parsed["__classname__"] == "Groove"

    print("✓ JSON serialization works")

    # Test from_dict with all fields
    dict_full = {"name": "dict_groove", "gtype": "rext", "n": 6, "eps": 3.0}

    dict_groove = Groove.from_dict(dict_full)
    assert dict_groove.name == "dict_groove"
    assert dict_groove.gtype == "rext"
    assert dict_groove.n == 6
    assert dict_groove.eps == 3.0

    print("✓ from_dict works (full)")

    # Test from_dict with optional name
    dict_no_name = {"gtype": "rint", "n": 2, "eps": 1.5}

    dict_groove_no_name = Groove.from_dict(dict_no_name)
    assert dict_groove_no_name.name == ""
    assert dict_groove_no_name.gtype == "rint"

    print("✓ from_dict works (optional name)")

    # Test YAML round-trip
    groove.write_to_yaml()
    print("✓ YAML dump works")

    loaded_groove = Groove.from_yaml("test_groove.yaml", debug=True)
    assert loaded_groove.name == groove.name
    assert loaded_groove.gtype == groove.gtype
    assert loaded_groove.n == groove.n
    assert loaded_groove.eps == groove.eps

    print("✓ YAML round-trip works")

    # Clean up
    if os.path.exists("test_groove.yaml"):
        os.unlink("test_groove.yaml")

    print("✓ Groove successfully refactored!\n")


def test_refactored_modelaxi():
    """Test that refactored ModelAxi has identical functionality"""
    print("=" * 60)
    print("Testing refactored ModelAxi functionality...")
    print("=" * 60)

    # Test basic creation
    modelaxi = ModelAxi(
        name="test_modelaxi", h=112.5, turns=[10.0, 20.0, 15.0], pitch=[5.0, 5.0, 5.0]
    )

    print(f"✓ ModelAxi created: {modelaxi}")

    # Test default constructor
    try:
        empty_modelaxi = ModelAxi()
        assert False, "Should have raised ValidationError for empty name"
    except ValidationError as e:
        print(f"✓ Empty name validation: {e}")

    # Test that all inherited methods exist
    assert hasattr(modelaxi, "write_to_yaml")
    assert hasattr(modelaxi, "to_json")
    assert hasattr(modelaxi, "write_to_json")
    assert hasattr(ModelAxi, "from_yaml")
    assert hasattr(ModelAxi, "from_json")
    assert hasattr(ModelAxi, "from_dict")

    print("✓ All serialization methods inherited correctly")

    # Test JSON serialization
    json_str = modelaxi.to_json()
    parsed = json.loads(json_str)
    assert parsed["name"] == "test_modelaxi"
    assert parsed["h"] == 112.5
    assert parsed["turns"] == [10.0, 20.0, 15.0]
    assert parsed["pitch"] == [5.0, 5.0, 5.0]
    assert parsed["__classname__"] == "ModelAxi"

    print("✓ JSON serialization works")

    # Test from_dict
    dict_data = {
        "name": "dict_modelaxi",
        "h": 30.0,
        "turns": [5.0, 10.0, 5.0],
        "pitch": [3.0, 3.0, 3.0],
    }

    dict_modelaxi = ModelAxi.from_dict(dict_data)
    assert dict_modelaxi.name == "dict_modelaxi"
    assert dict_modelaxi.h == 30.0
    assert dict_modelaxi.turns == [5.0, 10.0, 5.0]
    assert dict_modelaxi.pitch == [3.0, 3.0, 3.0]

    print("✓ from_dict works")

    # Test get_Nturns method
    nturns = modelaxi.get_Nturns()
    assert nturns == 45.0  # 10 + 20 + 15
    print(f"✓ get_Nturns() works: {nturns}")

    # Test compact method - similar pitches
    test_turns = [10.0, 10.0, 10.0, 5.0, 5.0]
    test_pitch = [5.0, 5.0, 5.0, 3.0, 3.0]
    modelaxi_compact = ModelAxi(name="compact_test", h=90.0, turns=test_turns, pitch=test_pitch)

    new_turns, new_pitch = modelaxi_compact.compact()
    assert len(new_turns) == 2  # Should compact to 2 groups
    assert new_turns[0] == 30.0  # 10 + 10 + 10
    assert new_turns[1] == 10.0  # 5 + 5
    assert new_pitch[0] == 5.0
    assert new_pitch[1] == 3.0

    print(f"✓ compact() works: {test_turns} -> {new_turns}")

    # Test YAML round-trip
    modelaxi.write_to_yaml()
    print("✓ YAML dump works")

    loaded_modelaxi = ModelAxi.from_yaml("test_modelaxi.yaml", debug=True)
    assert loaded_modelaxi.name == modelaxi.name
    assert loaded_modelaxi.h == modelaxi.h
    assert loaded_modelaxi.turns == modelaxi.turns
    assert loaded_modelaxi.pitch == modelaxi.pitch

    print("✓ YAML round-trip works")

    # Clean up
    if os.path.exists("test_modelaxi.yaml"):
        os.unlink("test_modelaxi.yaml")

    print("✓ ModelAxi successfully refactored!\n")


def test_cross_class_integration():
    """Test that Phase 4 classes work together correctly"""
    print("=" * 60)
    print("Testing cross-class integration...")
    print("=" * 60)

    # Create instances of all three classes
    chamfer = Chamfer(
        name="integration_chamfer", side="HP", rside="rint", alpha=45.0, dr=None, l=10.0
    )

    groove = Groove(name="integration_groove", gtype="rint", n=4, eps=2.0)

    modelaxi = ModelAxi(name="integration_modelaxi", h=75.0, turns=[10.0, 20.0], pitch=[5.0, 5.0])

    # Test that they can all be serialized independently
    chamfer_json = json.loads(chamfer.to_json())
    groove_json = json.loads(groove.to_json())
    modelaxi_json = json.loads(modelaxi.to_json())

    assert chamfer_json["__classname__"] == "Chamfer"
    assert groove_json["__classname__"] == "Groove"
    assert modelaxi_json["__classname__"] == "ModelAxi"

    print("✓ All classes serialize independently")

    # Test that they can be part of nested structures (as in Helix)
    helix_like_structure = {
        "name": "test_helix",
        "modelaxi": modelaxi_json,
        "chamfers": [chamfer_json],
        "grooves": groove_json,
    }

    # Verify structure integrity
    assert helix_like_structure["modelaxi"]["name"] == "integration_modelaxi"
    assert helix_like_structure["chamfers"][0]["name"] == "integration_chamfer"
    assert helix_like_structure["grooves"]["name"] == "integration_groove"

    print("✓ Classes integrate in nested structures")
    print("✓ Cross-class integration successful!\n")


def test_validation_edge_cases():
    """Test validation and edge cases for Phase 4 classes"""
    print("=" * 60)
    print("Testing validation and edge cases...")
    print("=" * 60)

    # Chamfer: Test that getDr() fails when neither alpha nor dr is set
    chamfer_no_params = Chamfer(
        name="invalid_chamfer", side="HP", rside="rint", alpha=None, dr=None, l=10.0
    )

    try:
        chamfer_no_params.getDr()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Chamfer validation works: {e}")

    # Test that getAngle() fails when neither alpha nor dr is set
    try:
        chamfer_no_params.getAngle()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Chamfer validation works: {e}")

    # ModelAxi: Test compact with empty pitch
    empty_pitch_model = ModelAxi(
        name="empty_pitch", h=50.0, turns=[10.0, 20.0], pitch=[2, 4]  # Empty pitch
    )

    new_turns, new_pitch = empty_pitch_model.compact()
    assert new_turns == [10.0, 20.0]
    assert new_pitch == [2, 4]
    print("✓ ModelAxi handles empty pitch correctly")

    # Test compact with single element
    single_model = ModelAxi(name="single", h=37.5, turns=[15.0], pitch=[5.0])

    new_turns, new_pitch = single_model.compact()
    assert new_turns == [15.0]
    assert new_pitch == [5.0]
    print("✓ ModelAxi handles single element correctly")

    # Test compact with very similar pitches (within tolerance)
    similar_model = ModelAxi(
        name="similar",
        h=75.0,
        turns=[10.0, 10.0, 10.0],
        pitch=[5.0, 5.00001, 4.99999],  # Within default tolerance
    )

    new_turns, new_pitch = similar_model.compact(tol=1e-4)
    assert len(new_turns) == 1  # Should compact all together
    assert new_turns[0] == 30.0
    print("✓ ModelAxi compact tolerance works correctly")

    print("✓ All validation edge cases handled correctly!\n")


def run_all_tests():
    """Run all Phase 4 tests"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + " " * 10 + "PHASE 4 CLASS REFACTORING TESTS" + " " * 16 + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")

    try:
        test_refactored_chamfer()
        test_refactored_groove()
        test_refactored_modelaxi()
        test_cross_class_integration()
        test_validation_edge_cases()

        print("\n")
        print("=" * 60)
        print("=" * 60)
        print("    ALL PHASE 4 TESTS PASSED SUCCESSFULLY!")
        print("    Chamfer, Groove, and ModelAxi are fully refactored")
        print("=" * 60)
        print("=" * 60)
        print("\n")

        return True

    except Exception as e:
        print("\n")
        print("!" * 60)
        print(f"TEST FAILED: {e}")
        print("!" * 60)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
