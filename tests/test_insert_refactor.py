#!/usr/bin/env python3
"""
Fixed test suite for Insert class - Phase 4 validation
Corrects the YAML round-trip test to avoid FileNotFoundError with string references
"""

import os
import json
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead
from python_magnetgeo.Probe import Probe
from python_magnetgeo.validation import ValidationError


def test_insert_yaml_roundtrip():
    """Test YAML dump and load roundtrip"""
    print("\n=== Test 9: YAML Round-trip (Fixed) ===")

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

    # FIX: Create InnerCurrentLead object instead of using string reference
    # String references like ["inner"] would require the file "inner.yaml" to exist
    inner_lead = InnerCurrentLead(
        name="yaml_inner_lead",
        r=[13.0, 23.0],
        h=60.0,
        holes=[],
        support=[],
        fillet=False
    )

    insert = Insert(
        name="yaml_insert",
        helices=[helix],
        rings=[],
        currentleads=[inner_lead],  # FIX: Use object instead of string reference
        hangles=[0.0],
        rangles=[],
        innerbore=9.0,
        outerbore=27.0,
        probes=[]
    )

    # Dump to YAML
    insert.write_to_yaml()
    yaml_file = f"{insert.name}.yaml"

    assert os.path.exists(yaml_file), "YAML file not created"
    print(f"✓ YAML dump created: {yaml_file}")

    # Load back
    loaded_insert = Insert.from_yaml(yaml_file, debug=False)

    assert loaded_insert.name == insert.name
    assert loaded_insert.innerbore == insert.innerbore
    assert loaded_insert.outerbore == insert.outerbore
    assert len(loaded_insert.helices) == len(insert.helices)
    assert len(loaded_insert.currentleads) == len(insert.currentleads)

    print("✓ YAML round-trip successful")
    print(f"  - Original: {insert.name}")
    print(f"  - Loaded: {loaded_insert.name}")
    print(f"  - Helices: {len(loaded_insert.helices)}")
    print(f"  - Current leads: {len(loaded_insert.currentleads)}")

    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


def test_insert_yaml_with_string_references():
    """Test Insert YAML loading with string references (when files exist)"""
    print("\n=== Test 9b: YAML with String References (Optional) ===")

    # This test demonstrates how string references work when the referenced files exist
    # First, create and save the referenced current lead
    inner_lead = InnerCurrentLead(
        name="inner",  # This will create "inner.yaml"
        r=[13.0, 23.0],
        h=60.0,
        holes=[],
        support=[],
        fillet=False
    )
    inner_lead.write_to_yaml()

    helix = Helix(
        name="yaml_ref_helix",
        r=[13.0, 23.0],
        z=[5.0, 55.0],
        cutwidth=1.7,
        odd=False,
        dble=True,
        modelaxi=None,
        model3d=None,
        shape=None
    )

    # Now create Insert with string reference
    insert = Insert(
        name="yaml_ref_insert",
        helices=[helix],
        rings=[],
        currentleads=["inner"],  # String reference to "inner.yaml"
        hangles=[180.0],
        rangles=[],
        innerbore=9.0,
        outerbore=27.0,
        probes=[]
    )

    # Dump to YAML
    insert.write_to_yaml()
    yaml_file = f"{insert.name}.yaml"

    assert os.path.exists(yaml_file), "YAML file not created"
    assert os.path.exists("inner.yaml"), "Referenced lead file not found"
    print(f"✓ YAML files created: {yaml_file}, inner.yaml")

    # Load back - this should resolve the string reference
    loaded_insert = Insert.from_yaml(yaml_file, debug=False)

    assert loaded_insert.name == insert.name
    assert len(loaded_insert.currentleads) == 1
    # The string reference should be resolved to the actual object
    assert hasattr(loaded_insert.currentleads[0], 'name')

    print("✓ YAML with string references successful")
    print(f"  - Insert loaded: {loaded_insert.name}")
    print(f"  - Current lead resolved from string reference: {loaded_insert.currentleads[0].name}")

    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
    if os.path.exists("inner.yaml"):
        os.unlink("inner.yaml")
        print(f"✓ Cleaned up: {yaml_file}, inner.yaml")


def test_insert_empty_currentleads():
    """Test Insert with empty currentleads list"""
    print("\n=== Test 9c: Empty Current Leads ===")

    helix = Helix(
        name="no_leads_helix",
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
        name="no_leads_insert",
        helices=[helix],
        rings=[],
        currentleads=[],  # Empty list - no current leads
        hangles=[0.0],
        rangles=[],
        innerbore=9.0,
        outerbore=27.0,
        probes=[]
    )

    # Dump to YAML
    insert.write_to_yaml()
    yaml_file = f"{insert.name}.yaml"

    assert os.path.exists(yaml_file), "YAML file not created"
    print(f"✓ YAML dump created: {yaml_file}")

    # Load back
    loaded_insert = Insert.from_yaml(yaml_file, debug=False)

    assert loaded_insert.name == insert.name
    assert len(loaded_insert.currentleads) == 0

    print("✓ YAML round-trip with empty currentleads successful")
    print(f"  - Insert loaded: {loaded_insert.name}")
    print(f"  - Current leads: {len(loaded_insert.currentleads)} (empty)")

    # Cleanup
    if os.path.exists(yaml_file):
        os.unlink(yaml_file)
        print(f"✓ Cleaned up: {yaml_file}")


# Summary of the fix:
print("\n" + "=" * 70)
print("FIX EXPLANATION: YAML Round-trip Test")
print("=" * 70)
print("""
PROBLEM:
  The original test used: currentleads=["inner"]
  This is a string reference that tells Insert to load "inner.yaml"
  When loading from YAML, it tried to find "inner.yaml" → FileNotFoundError

SOLUTION:
  Three test approaches are now provided:

  1. test_insert_yaml_roundtrip() [MAIN FIX]
     - Uses actual InnerCurrentLead objects
     - No file dependencies
     - Always works

  2. test_insert_yaml_with_string_references() [OPTIONAL]
     - Demonstrates how string references work
     - Creates referenced files first
     - Shows real-world usage pattern

  3. test_insert_empty_currentleads() [EDGE CASE]
     - Tests with no current leads at all
     - Validates empty list handling

RECOMMENDATION:
  Use approach #1 for unit tests (no external dependencies)
  Use approach #2 for integration tests (tests file loading)
  Use approach #3 to verify edge cases
""")
print("=" * 70)


if __name__ == "__main__":
    print("\nRunning fixed Insert YAML tests...\n")

    tests = [
        test_insert_yaml_roundtrip,
        test_insert_yaml_with_string_references,
        test_insert_empty_currentleads,
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
        print("\n🎉 All fixed Insert YAML tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed.")

    exit(0 if failed == 0 else 1)
