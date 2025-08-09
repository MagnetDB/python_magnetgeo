# File: new-tests/test_integration.py
import pytest
import json
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

# Import all classes for testing
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Screen import Screen
from python_magnetgeo.MSite import MSite
from python_magnetgeo.Probe import Probe
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D

class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_insert_workflow(self, temp_yaml_file, temp_json_file):
        """Test complete Insert creation, serialization, and loading workflow"""
        # Create ModelAxi
        axi = ModelAxi("workflow_axi", 30.0, [3.0, 2.5], [10.0, 12.0])
        
        # Create Shape
        shape = Shape("workflow_shape", "rectangular", 8, [90.0] * 4, 0, "CENTER")
        
        # Create Helix
        helix = Helix("workflow_helix", [12.0, 22.0], [0.0, 60.0], 1.8, False, True, axi, shape)
        
        # Create Ring
        ring = Ring("workflow_ring", [10.0, 24.0], [25.0, 35.0])
        
        # Create Probe
        probe = Probe("workflow_probe", "current_taps", ["I1", "I2"], [[15.0, 0.0, 30.0], [19.0, 0.0, 45.0]])
        
        # Create Insert
        insert = Insert(
            name="workflow_insert",
            helices=[helix],
            rings=[ring],
            currentleads=["inner_lead"],
            hangles=[0.0, 180.0],
            rangles=[0.0, 90.0, 180.0, 270.0],
            innerbore=8.0,
            outerbore=26.0,
            probes=[probe]
        )
        
        # Test geometric operations
        rb, zb = insert.boundingBox()
        assert rb[0] == 12.0  # helix r min
        assert rb[1] == 22.0  # helix r max
        
        # Test intersection
        collision = insert.intersect([15.0, 20.0], [20.0, 50.0])
        assert collision is True
        
        # Test serialization
        json_str = insert.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Insert"
        assert len(parsed["probes"]) == 1
        
        # Test helix-specific operations
        helix_type = helix.get_type()
        assert isinstance(helix_type, str)
        
        insulator_material, insulator_count = helix.insulators()
        assert isinstance(insulator_material, str)
        assert isinstance(insulator_count, (int, float))

    def test_magnet_site_integration(self):
        """Test complete MSite with multiple magnet types"""
        # Create different magnet types
        helix = Helix("site_helix", [10.0, 20.0], [0.0, 50.0], 2.0, True, False, None, None)
        insert = Insert("site_insert", [helix], [], [], [], [], 8.0, 25.0, [])
        
        supra = Supra("site_supra", [30.0, 45.0], [60.0, 120.0], 4, "YBCO")
        supras = Supras("site_supras", [supra], 28.0, 50.0, [])
        
        screen = Screen("site_screen", [0.0, 60.0], [0.0, 150.0])
        
        # Create MSite
        msite = MSite(
            name="integration_msite",
            magnets=[insert, supras],
            screens=[screen],
            z_offset=[0.0, 65.0],
            r_offset=[0.0, 0.0],
            paralax=[0.0, 0.0]
        )
        
        # Test MSite operations
        rb, zb = msite.boundingBox()
        assert isinstance(rb, list)
        assert isinstance(zb, list)
        
        # Bounding box should encompass all magnets
        assert rb[0] <= 10.0  # Include insert
        assert rb[1] >= 45.0  # Include supras
        assert zb[0] <= 0.0   # Include insert
        assert zb[1] >= 120.0 # Include supras

    def test_probe_workflow_integration(self):
        """Test complete probe integration workflow"""
        # Create voltage tap probes
        voltage_probes = Probe(
            name="integration_voltage",
            probe_type="voltage_taps", 
            index=["V1", "V2", "V3", "V4"],
            locations=[
                [14.0, 0.0, 10.0],
                [16.0, 0.0, 20.0], 
                [18.0, 0.0, 30.0],
                [20.0, 0.0, 40.0]
            ]
        )
        
        # Create temperature probes
        temp_probes = Probe(
            name="integration_temperature",
            probe_type="temperature",
            index=[1, 2, 3],
            locations=[
                [15.0, 2.5, 15.0],
                [17.0, -2.5, 25.0],
                [19.0, 0.0, 35.0]
            ]
        )
        
        # Test probe operations
        assert voltage_probes.get_probe_count() == 4
        assert temp_probes.get_probe_count() == 3
        
        # Test probe lookup
        v2_info = voltage_probes.get_probe_by_index("V2")
        assert v2_info["location"] == [16.0, 0.0, 20.0]
        
        t2_info = temp_probes.get_probe_by_index(2)
        assert t2_info["location"] == [17.0, -2.5, 25.0]
        
        # Test adding probes
        voltage_probes.add_probe("V5", [22.0, 0.0, 50.0])
        assert voltage_probes.get_probe_count() == 5
        
        # Test location filtering
        voltage_locs = voltage_probes.get_locations_by_type("voltage_taps")
        temp_locs = temp_probes.get_locations_by_type("temperature")
        
        assert len(voltage_locs) == 5  # Including added probe
        assert len(temp_locs) == 3
        
        # Test with Insert
        helix = Helix("probe_helix", [12.0, 24.0], [0.0, 60.0], 2.2, True, True, None, None)
        insert_with_probes = Insert(
            name="probe_integration_insert",
            helices=[helix],
            rings=[],
            currentleads=["lead1"],
            hangles=[0.0],
            rangles=[0.0, 90.0],
            innerbore=10.0,
            outerbore=26.0,
            probes=[voltage_probes, temp_probes]
        )
        
        assert len(insert_with_probes.probes) == 2
        assert insert_with_probes.probes[0].probe_type == "voltage_taps"
        assert insert_with_probes.probes[1].probe_type == "temperature"

    def test_serialization_integration(self, temp_json_file):
        """Test serialization preserves all data through complex workflows"""
        # Create complex nested structure
        axi = ModelAxi("serial_axi", 20.0, [2.0, 3.0, 2.5], [8.0, 9.0, 8.5])
        shape = Shape("serial_shape", "hexagonal", 12, [60.0] * 6, 1, "ALTERNATE")
        helix = Helix("serial_helix", [15.0, 30.0], [5.0, 85.0], 3.0, False, True, axi, shape)
        
        ring1 = Ring("serial_ring1", [13.0, 32.0], [35.0, 45.0])
        ring2 = Ring("serial_ring2", [13.0, 32.0], [55.0, 65.0])
        
        probe = Probe("serial_probe", "hall_sensors", ["H1", "H2"], [[20.0, 5.0, 40.0], [25.0, -5.0, 60.0]])
        
        insert = Insert(
            name="serialization_insert",
            helices=[helix],
            rings=[ring1, ring2],
            currentleads=["inner", "outer"],
            hangles=[0.0, 120.0, 240.0],
            rangles=[30.0, 90.0, 150.0, 210.0, 270.0, 330.0],
            innerbore=11.0,
            outerbore=35.0,
            probes=[probe]
        )
        
        # Serialize to JSON
        json_str = insert.to_json()
        parsed = json.loads(json_str)
        
        # Verify all nested structures preserved
        assert parsed["__classname__"] == "Insert"
        assert parsed["name"] == "serialization_insert"
        assert len(parsed["helices"]) == 1
        assert len(parsed["rings"]) == 2
        assert len(parsed["probes"]) == 1
        
        # Verify helix nested data
        helix_data = parsed["helices"][0]
        assert helix_data["__classname__"] == "Helix"
        assert "modelaxi" in helix_data
        assert "shape" in helix_data
        
        # Verify probe data
        probe_data = parsed["probes"][0]
        assert probe_data["__classname__"] == "Probe"
        assert probe_data["probe_type"] == "hall_sensors"
        assert len(probe_data["locations"]) == 2

    def test_geometric_consistency_integration(self):
        """Test geometric operations are consistent across complex structures"""
        # Create objects with known geometric relationships
        inner_helix = Helix("inner", [10.0, 15.0], [0.0, 100.0], 1.0, True, False, None, None)
        outer_helix = Helix("outer", [20.0, 25.0], [10.0, 90.0], 1.5, False, True, None, None)
        
        separator_ring = Ring("separator", [8.0, 27.0], [45.0, 55.0])
        
        insert = Insert(
            name="geometric_insert",
            helices=[inner_helix, outer_helix],
            rings=[separator_ring],
            currentleads=[],
            hangles=[],
            rangles=[],
            innerbore=8.0,
            outerbore=30.0,
            probes=[]
        )
        
        # Test individual bounding boxes
        inner_rb, inner_zb = inner_helix.boundingBox()
        outer_rb, outer_zb = outer_helix.boundingBox()
        ring_rb, ring_zb = separator_ring.boundingBox()
        
        # Test insert bounding box encompasses all
        insert_rb, insert_zb = insert.boundingBox()
        
        # Insert should encompass all helices
        assert insert_rb[0] <= min(inner_rb[0], outer_rb[0])
        assert insert_rb[1] >= max(inner_rb[1], outer_rb[1])
        
        # Insert z should be extended by ring height
        ring_height = ring_zb[1] - ring_zb[0]  # 10.0
        expected_z_min = min(inner_zb[0], outer_zb[0]) - ring_height
        expected_z_max = max(inner_zb[1], outer_zb[1]) + ring_height
        
        assert insert_zb[0] == expected_z_min  # 0.0 - 10.0 = -10.0
        assert insert_zb[1] == expected_z_max  # 100.0 + 10.0 = 110.0
        
        # Test intersection consistency
        test_rect_r = [12.0, 23.0]  # Overlaps both helices
        test_rect_z = [20.0, 80.0]  # Overlaps both helices
        
        inner_intersect = inner_helix.intersect(test_rect_r, test_rect_z)
        outer_intersect = outer_helix.intersect(test_rect_r, test_rect_z)
        insert_intersect = insert.intersect(test_rect_r, test_rect_z)
        
        # If individual components intersect, insert should intersect
        if inner_intersect or outer_intersect:
            assert insert_intersect is True

    def test_error_handling_integration(self):
        """Test error handling across the system"""
        # Test invalid probe locations
        with pytest.raises(ValueError):
            Probe("bad_probe", "voltage", ["V1"], [[10.0, 20.0]])  # Only 2 coordinates
        
        # Test invalid detail level
        supra = Supra("detail_test", [10.0, 20.0], [0.0, 50.0], 3, "LTS")
        with pytest.raises(Exception):
            supra.set_Detail("invalid_detail_level")
        
        # Test probe index not found
        probe = Probe("index_test", "temperature", [1, 2, 3], [[1, 0, 0], [2, 0, 0], [3, 0, 0]])
        with pytest.raises(ValueError):
            probe.get_probe_by_index(999)
        
        # Test from_dict with missing required fields
        incomplete_data = {"name": "incomplete"}  # Missing required fields
        
        with pytest.raises((KeyError, TypeError)):
            Helix.from_dict(incomplete_data)


if __name__ == "__main__":
    """Run the test suite"""
    import sys
    import subprocess
    
    # Run pytest with verbose output
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "new-tests/", 
        "-v", 
        "--tb=short",
        "--strict-markers"
    ])
    
    sys.exit(result.returncode)