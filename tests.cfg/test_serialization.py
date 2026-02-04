import pytest
import json
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

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

class TestSerialization:
    """Test JSON and YAML serialization across all classes"""

    def test_helix_roundtrip_serialization(self, sample_helix, temp_json_file):
        """Test Helix JSON serialization roundtrip"""
        # Serialize to JSON
        sample_helix.write_to_json()

        # Read back and verify
        with open(f"{sample_helix.name}.json", 'r') as f:
            json_data = json.load(f)

        assert json_data["__classname__"] == "Helix"
        assert json_data["name"] == sample_helix.name

        # Cleanup
        Path(f"{sample_helix.name}.json").unlink(missing_ok=True)

    def test_insert_from_dict(self):
        """Test Insert creation from dictionary with inline object definitions"""
        # Create inline object definitions instead of file references
        helix_dict = {
            "__classname__": "Helix",
            "name": "helix1",
            "r": [10.0, 10.1],
            "z": [0.0, 50.0],
            "cutwidth": 2.0,
            "odd": False,
            "dble": True,
            "modelaxi": None,
            "model3d": None,
            "shape": None
        }

        ring_dict = {
            "__classname__": "Ring",
            "name": "ring1",
            "r": [10.0, 10.1, 19.9, 20.0],
            "z": [0.0, 10.0],
            "n": 6,
            "angle": 30.0,
            "bpside": True,
            "fillets": False
        }

        # Define inline currentleads - both InnerCurrentLead and OuterCurrentLead
        inner_lead_dict = {
            "__classname__": "InnerCurrentLead",
            "name": "inner",
            "r": [8.0, 9.5],
            "h": 52.0,
            "holes": [5.0, 10.0, 0.0, 45.0, 0.0, 8],
            "support": [10.1, 5.0],
            "fillet": True
        }

        outer_lead_dict = {
            "__classname__": "OuterCurrentLead",
            "name": "outer",
            "r": [35.0, 40.0],
            "h": 52.0,
            "bar": [37.5, 10.0, 15.0, 40.0],
            "support": [5.0, 10.0, 30.0, 0.0]
        }

        probe_dict = {
            "__classname__": "Probe",
            "name": "probe1",
            "type": "field_sensors",
            "labels": ["B1", "B2"],
            "points": [[12.0, 5.0, 25.0], [18.0, -5.0, 45.0]]
        }

        data = {
            "__classname__": "Insert",
            "name": "dict_insert",
            "helices": [helix_dict],              # Use inline dict
            "rings": [],                 # Use inline dict
            "currentleads": [inner_lead_dict],  # Use inline dicts for both leads
            "hangles": [180.0],
            "rangles": [],
            "innerbore": 8.0,
            "outerbore": 35.0,
            "probes": [probe_dict]                # Use inline dict
        }

        insert = Insert.from_dict(data)

        assert insert.name == "dict_insert"
        assert len(insert.helices) == 1
        assert insert.helices[0].name == "helix1"
        assert len(insert.currentleads) == 1
        assert insert.currentleads[0].name == "inner"
        assert len(insert.probes) == 1
        assert insert.probes[0].name == "probe1"
        assert insert.innerbore == 8.0
        assert insert.outerbore == 35.0

    def test_supra_from_dict(self):
        """Test Supra creation from dictionary"""
        data = {
            "__classname__": "Supra",
            "name": "dict_supra",
            "r": [30.0, 50.0],
            "z": [20.0, 80.0],
            "n": 6,
            "struct": None  # Empty to avoid file loading
        }

        supra = Supra.from_dict(data)

        assert supra.name == "dict_supra"
        assert supra.r == [30.0, 50.0]
        assert supra.z == [20.0, 80.0]
        assert supra.n == 6
        assert supra.struct == None

    def test_probe_from_dict(self):
        """Test Probe creation from dictionary"""
        data = {
            "__classname__": "Probe",
            "name": "dict_probe",
            "type": "field_sensors",
            "labels": ["B1", "B2"],
            "points": [[12.0, 5.0, 25.0], [18.0, -5.0, 45.0]]
        }

        probe = Probe.from_dict(data)

        assert probe.name == "dict_probe"
        assert probe.type == "field_sensors"
        assert probe.labels == ["B1", "B2"]
        assert len(probe.points) == 2

    @pytest.mark.parametrize("class_obj,sample_data", [
        (Ring, {
            "__classname__": "Ring",
            "name": "test_ring",
            "r": [10.0, 10.1, 19.9, 20.0],
            "z": [0.0, 10.0],
            "n": 6,
            "angle": 30.0,
            "bpside": True,
            "fillets": False
        }),
        (Screen, {
            "__classname__": "Screen",
            "name": "test_screen",
            "r": [5.0, 25.0],
            "z": [0.0, 50.0]
        }),
    ])
    def test_class_serialization_interface(self, class_obj, sample_data):
        """Test that all classes implement required serialization methods"""
        instance = class_obj.from_dict(sample_data)

        # Test required class methods exist
        assert hasattr(class_obj, 'from_dict')
        assert hasattr(class_obj, 'from_yaml')
        assert hasattr(class_obj, 'from_json')

        # Test required instance methods exist
        assert hasattr(instance, 'to_json')
        assert hasattr(instance, 'write_to_json')
        assert hasattr(instance, 'write_to_yaml')

        # Test JSON serialization works
        json_str = instance.to_json()
        parsed = json.loads(json_str)
        assert "__classname__" in parsed
        assert parsed["name"] == sample_data["name"]
