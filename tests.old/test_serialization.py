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

    @patch('python_magnetgeo.utils.load_objects')
    def test_insert_from_dict(self, mock_load_objects):
        """Test Insert creation from dictionary with mocked file loading"""
        # Mock the file loading to return object instances instead of trying to load files
        mock_load_objects.side_effect = lambda items, registry: items  # Return items as-is
        
        data = {
            "name": "dict_insert",
            "helices": ["helix1", "helix2"],
            "rings": ["ring1"],
            "currentleads": ["lead1"],
            "hangles": [0.0, 180.0],
            "rangles": [0.0, 90.0, 180.0, 270.0],
            "innerbore": 8.0,
            "outerbore": 35.0,
            "probes": ["probe1"]
        }
        
        insert = Insert.from_dict(data)
        
        assert insert.name == "dict_insert"
        assert insert.helices == ["helix1", "helix2"]
        assert insert.rings == ["ring1"]
        assert insert.probes == ["probe1"]
        assert insert.innerbore == 8.0
        assert insert.outerbore == 35.0

    def test_supra_from_dict(self):
        """Test Supra creation from dictionary"""
        data = {
            "name": "dict_supra",
            "r": [30.0, 50.0],
            "z": [20.0, 80.0],
            "n": 6,
            "struct": ""  # Empty to avoid file loading
        }
        
        supra = Supra.from_dict(data)
        
        assert supra.name == "dict_supra"
        assert supra.r == [30.0, 50.0]
        assert supra.z == [20.0, 80.0]
        assert supra.n == 6
        assert supra.struct == ""

    def test_probe_from_dict(self):
        """Test Probe creation from dictionary"""
        data = {
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
        (Ring, {"name": "test_ring", "r": [10.0, 10.1, 19.9, 20.0], "z": [0.0, 10.0], "n": 6, "angle": 30.0, "bpside": True, "fillets": False}),
        (Screen, {"name": "test_screen", "r": [5.0, 25.0], "z": [0.0, 50.0]}),
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
        assert hasattr(instance, 'dump')
        
        # Test JSON serialization works
        json_str = instance.to_json()
        parsed = json.loads(json_str)
        assert "__classname__" in parsed
        assert parsed["name"] == sample_data["name"]