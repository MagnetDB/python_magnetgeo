#!/usr/bin/env python3
"""
Test YAML serialization of nested objects with YAML tags.

Verifies that to_yaml() properly handles embedded YAMLObjectBase objects,
ensuring they are serialized with their YAML tags (!<ClassName>).
"""

import pytest
import yaml
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Ring import Ring


def test_bitter_with_modelaxi_yaml_tags():
    """Test that Bitter with ModelAxi has both YAML tags in output"""
    print("\n=== Testing Bitter with nested ModelAxi YAML tags ===")

    # Create a ModelAxi object
    modelaxi = ModelAxi(
        name="helix.d",
        h=500,
        pitch=[1000],
        turns=[1]
    )

    # Create a Bitter object with embedded ModelAxi
    bitter = Bitter(
        name="Tore",
        r=[75, 100.2],
        z=[-500, 500],
        odd=True,
        modelaxi=modelaxi,
        coolingslits=[],
        tierod=None,
        innerbore=0,
        outerbore=0
    )

    # Convert to YAML
    yaml_str = bitter.to_yaml()

    print("Generated YAML:")
    print(yaml_str)

    # Verify the YAML contains the expected tags
    assert "!<Bitter>" in yaml_str, "Missing Bitter YAML tag"
    assert "!<ModelAxi>" in yaml_str, "Missing ModelAxi YAML tag"

    # Verify the structure
    assert "name: Tore" in yaml_str or "name: 'Tore'" in yaml_str
    assert "modelaxi:" in yaml_str
    assert "h: 500" in yaml_str
    assert "pitch:" in yaml_str

    print("✓ Bitter YAML tag found")
    print("✓ ModelAxi YAML tag found")
    print("✓ YAML structure correct")

    # Verify it can be loaded back
    loaded_bitter = yaml.load(yaml_str, Loader=yaml.FullLoader)

    assert loaded_bitter.name == "Tore"
    assert loaded_bitter.modelaxi is not None
    assert loaded_bitter.modelaxi.name == "helix.d"
    assert loaded_bitter.modelaxi.h == 500
    assert loaded_bitter.r == [75, 100.2]

    print("✓ YAML round-trip successful")


def test_insert_with_nested_objects_yaml_tags():
    """Test that Insert with Helix and Ring has all YAML tags - SIMPLIFIED"""
    print("\n=== Testing Insert with nested Helix YAML tag (simplified) ===")

    # Simplified test - just verify that Insert properly serializes a Helix with ModelAxi
    modelaxi = ModelAxi(
        name="helix_model.d",
        h=40,
        pitch=[8],
        turns=[10]
    )

    helix = Helix(
        name="H1",
        r=[10, 20],
        z=[0, 100],
        cutwidth=2.0,
        odd=False,
        dble=True,
        modelaxi=modelaxi,
        model3d=None,
        shape=None
    )

    # Create an Insert with just one helix (no rings needed)
    insert = Insert(
        name="TestInsert",
        helices=[helix],
        rings=[],
        currentleads=[],
        hangles=[],
        rangles=[],
        innerbore=5,
        outerbore=30,
        probes=[]
    )

    # Convert to YAML
    yaml_str = insert.to_yaml()

    print("Generated YAML:")
    print(yaml_str[:500])

    # Verify all YAML tags are present
    assert "!<Insert>" in yaml_str, "Missing Insert YAML tag"
    assert "!<Helix>" in yaml_str, "Missing Helix YAML tag"
    assert "!<ModelAxi>" in yaml_str, "Missing ModelAxi YAML tag"

    print("✓ Insert YAML tag found")
    print("✓ Helix YAML tag found")
    print("✓ ModelAxi YAML tag found (nested in Helix)")

    # Verify structure
    assert "name: TestInsert" in yaml_str
    assert "helices:" in yaml_str

    print("✓ YAML structure correct")

    # Verify round-trip
    loaded_insert = yaml.load(yaml_str, Loader=yaml.FullLoader)

    assert loaded_insert.name == "TestInsert"
    assert len(loaded_insert.helices) == 1
    assert loaded_insert.helices[0].name == "H1"
    assert loaded_insert.helices[0].modelaxi.name == "helix_model.d"

    print("✓ YAML round-trip successful with all nested objects")


def test_yaml_no_classname_field():
    """Verify that YAML tags are used, not __classname__ fields"""
    print("\n=== Testing that YAML uses tags, not __classname__ ===")

    # h=500 means total height = 1000mm
    # pitch * turns = 200 * 5 = 1000mm ✓
    modelaxi = ModelAxi(
        name="test.d",
        h=500,
        pitch=[200],
        turns=[5]
    )

    bitter = Bitter(
        name="Test",
        r=[50, 75],
        z=[-100, 100],
        odd=True,
        modelaxi=modelaxi,
        coolingslits=[],
        tierod=None,
        innerbore=0,
        outerbore=0
    )

    yaml_str = bitter.to_yaml()

    # Verify we have YAML tags
    assert "!<Bitter>" in yaml_str
    assert "!<ModelAxi>" in yaml_str

    # Verify we DON'T have __classname__ fields in YAML output
    # (they should only be in JSON)
    assert "__classname__" not in yaml_str, "YAML should use tags, not __classname__ fields"

    print("✓ YAML uses tags (!<ClassName>), not __classname__ fields")


def test_compare_yaml_vs_json_format():
    """Compare YAML and JSON output to ensure they have correct formats"""
    print("\n=== Comparing YAML vs JSON formats ===")

    # h=1200 means total height = 2400mm
    # pitch * turns = 300 * 8 = 2400mm ✓
    modelaxi = ModelAxi(
        name="compare.d",
        h=1200,
        pitch=[300],
        turns=[8]
    )

    bitter = Bitter(
        name="Compare",
        r=[60, 80],
        z=[-150, 150],
        odd=False,
        modelaxi=modelaxi,
        coolingslits=[],
        tierod=None,
        innerbore=0,
        outerbore=0
    )

    yaml_str = bitter.to_yaml()
    json_str = bitter.to_json()

    print("\nYAML output (first 200 chars):")
    print(yaml_str[:200])

    print("\nJSON output (first 200 chars):")
    print(json_str[:200])

    # YAML should have tags
    assert "!<Bitter>" in yaml_str
    assert "!<ModelAxi>" in yaml_str
    assert "__classname__" not in yaml_str

    # JSON should have __classname__ fields
    assert '"__classname__": "Bitter"' in json_str
    assert '"__classname__": "ModelAxi"' in json_str
    assert "!<" not in json_str

    print("✓ YAML format uses tags (!<ClassName>)")
    print("✓ JSON format uses __classname__ fields")
    print("✓ Both formats are distinct and correct")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing YAML Nested Objects with Tags")
    print("=" * 70)

    test_bitter_with_modelaxi_yaml_tags()
    test_insert_with_nested_objects_yaml_tags()
    test_yaml_no_classname_field()
    test_compare_yaml_vs_json_format()

    print("\n" + "=" * 70)
    print("All tests passed! ✓")
    print("=" * 70)
