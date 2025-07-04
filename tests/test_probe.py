#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest test suite for the Probe class
"""

import pytest
import tempfile
import os
import yaml
import json
from unittest.mock import patch, mock_open

# Import from the python_magnetgeo package
from python_magnetgeo.Probe import Probe


class TestProbeInit:
    """Test Probe class initialization"""

    def test_valid_initialization(self):
        """Test creating a probe with valid parameters"""
        probe = Probe(
            name="test_probe",
            probe_type="voltage_taps",
            index=["V1", "V2", "V3"],
            locations=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        )
        
        assert probe.name == "test_probe"
        assert probe.probe_type == "voltage_taps"
        assert probe.index == ["V1", "V2", "V3"]
        assert probe.locations == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]

    def test_mixed_index_types(self):
        """Test creating a probe with mixed string and integer indices"""
        probe = Probe(
            name="mixed_probe",
            probe_type="temperature",
            index=["T1", 2, "T3", 4],
            locations=[[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0], [4.0, 4.0, 4.0]]
        )
        
        assert probe.index == ["T1", 2, "T3", 4]
        assert len(probe.locations) == 4

    def test_mismatched_lengths_raises_error(self):
        """Test that mismatched index and locations lengths raise ValueError"""
        with pytest.raises(ValueError, match="index and locations must have the same length"):
            Probe(
                name="bad_probe",
                probe_type="voltage_taps",
                index=["V1", "V2"],
                locations=[[1.0, 2.0, 3.0]]  # Only one location for two indices
            )

    def test_invalid_location_coordinates_raises_error(self):
        """Test that locations with wrong number of coordinates raise ValueError"""
        with pytest.raises(ValueError, match="location 0 must have exactly 3 coordinates"):
            Probe(
                name="bad_coordinates",
                probe_type="temperature",
                index=["T1"],
                locations=[[1.0, 2.0]]  # Only 2 coordinates instead of 3
            )

        with pytest.raises(ValueError, match="location 1 must have exactly 3 coordinates"):
            Probe(
                name="bad_coordinates",
                probe_type="temperature",
                index=["T1", "T2"],
                locations=[[1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0]]  # 4 coordinates instead of 3
            )

    def test_empty_probe(self):
        """Test creating an empty probe"""
        probe = Probe(
            name="empty_probe",
            probe_type="magnetic_field",
            index=[],
            locations=[]
        )
        
        assert probe.get_probe_count() == 0
        assert probe.index == []
        assert probe.locations == []


class TestProbeRepr:
    """Test Probe string representation"""

    def test_repr_format(self):
        """Test that __repr__ returns expected format"""
        probe = Probe(
            name="test_probe",
            probe_type="voltage_taps",
            index=["V1"],
            locations=[[1.0, 2.0, 3.0]]
        )
        
        repr_str = repr(probe)
        assert "Probe(" in repr_str
        assert "name='test_probe'" in repr_str
        assert "probe_type='voltage_taps'" in repr_str
        assert "index=['V1']" in repr_str
        assert "locations=[[1.0, 2.0, 3.0]]" in repr_str


class TestProbeGetMethods:
    """Test Probe getter methods"""

    @pytest.fixture
    def sample_probe(self):
        """Create a sample probe for testing"""
        return Probe(
            name="sample_probe",
            probe_type="temperature",
            index=["T1", "T2", "T3"],
            locations=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        )

    def test_get_probe_count(self, sample_probe):
        """Test getting probe count"""
        assert sample_probe.get_probe_count() == 3

    def test_get_probe_by_index_valid(self, sample_probe):
        """Test getting probe by valid index"""
        probe_info = sample_probe.get_probe_by_index("T2")
        
        expected = {
            "index": "T2",
            "location": [4.0, 5.0, 6.0],
            "probe_type": "temperature"
        }
        assert probe_info == expected

    def test_get_probe_by_index_invalid(self, sample_probe):
        """Test getting probe by invalid index raises ValueError"""
        with pytest.raises(ValueError, match="Probe index T4 not found"):
            sample_probe.get_probe_by_index("T4")

    def test_get_locations_by_type_matching(self, sample_probe):
        """Test getting locations by matching probe type"""
        locations = sample_probe.get_locations_by_type("temperature")
        expected = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        assert locations == expected

    def test_get_locations_by_type_non_matching(self, sample_probe):
        """Test getting locations by non-matching probe type"""
        locations = sample_probe.get_locations_by_type("voltage_taps")
        assert locations == []

    def test_get_locations_by_type_none(self, sample_probe):
        """Test getting locations with None type returns all"""
        locations = sample_probe.get_locations_by_type(None)
        expected = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        assert locations == expected


class TestProbeModification:
    """Test Probe modification methods"""

    @pytest.fixture
    def modifiable_probe(self):
        """Create a probe for modification testing"""
        return Probe(
            name="mod_probe",
            probe_type="voltage_taps",
            index=["V1", "V2"],
            locations=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        )

    def test_add_probe_valid(self, modifiable_probe):
        """Test adding a valid probe"""
        modifiable_probe.add_probe("V3", [7.0, 8.0, 9.0])
        
        assert modifiable_probe.get_probe_count() == 3
        assert "V3" in modifiable_probe.index
        assert [7.0, 8.0, 9.0] in modifiable_probe.locations

    def test_add_probe_invalid_coordinates(self, modifiable_probe):
        """Test adding probe with invalid coordinates raises ValueError"""
        with pytest.raises(ValueError, match="Location must have exactly 3 coordinates"):
            modifiable_probe.add_probe("V3", [7.0, 8.0])  # Only 2 coordinates

    def test_add_probe_duplicate_index(self, modifiable_probe):
        """Test adding probe with duplicate index raises ValueError"""
        with pytest.raises(ValueError, match="Probe index V1 already exists"):
            modifiable_probe.add_probe("V1", [7.0, 8.0, 9.0])

    def test_remove_probe_valid(self, modifiable_probe):
        """Test removing a valid probe"""
        modifiable_probe.remove_probe("V1")
        
        assert modifiable_probe.get_probe_count() == 1
        assert "V1" not in modifiable_probe.index
        assert [1.0, 2.0, 3.0] not in modifiable_probe.locations

    def test_remove_probe_invalid(self, modifiable_probe):
        """Test removing invalid probe raises ValueError"""
        with pytest.raises(ValueError, match="Probe index V3 not found"):
            modifiable_probe.remove_probe("V3")


class TestProbeSerialization:
    """Test Probe serialization methods"""

    @pytest.fixture
    def serialization_probe(self):
        """Create a probe for serialization testing"""
        return Probe(
            name="serial_probe",
            probe_type="magnetic_field",
            index=["B1", "B2"],
            locations=[[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
        )

    @patch('builtins.open', new_callable=mock_open)
    @patch('python_magnetgeo.utils.writeYaml')
    def test_dump(self, mock_write_yaml, mock_file, serialization_probe):
        """Test dump method calls writeYaml correctly"""
        serialization_probe.dump()
        mock_write_yaml.assert_called_once_with("Probe", serialization_probe, Probe)

    def test_to_json(self, serialization_probe):
        """Test JSON serialization"""
        with patch('python_magnetgeo.deserialize.serialize_instance') as mock_serialize:
            mock_serialize.return_value = {"test": "data"}
            
            json_str = serialization_probe.to_json()
            
            mock_serialize.assert_called_once_with(serialization_probe)
            assert '"test": "data"' in json_str

    @patch('builtins.open', new_callable=mock_open)
    def test_write_to_json(self, mock_file, serialization_probe):
        """Test writing to JSON file"""
        with patch.object(serialization_probe, 'to_json', return_value='{"test": "data"}'):
            serialization_probe.write_to_json()
            
            mock_file.assert_called_once_with("serial_probe.json", "w")
            mock_file().write.assert_called_once_with('{"test": "data"}')


class TestProbeClassMethods:
    """Test Probe class methods"""

    def test_from_dict_valid(self):
        """Test creating Probe from valid dictionary"""
        data = {
            "name": "dict_probe",
            "probe_type": "voltage_taps",
            "index": ["V1", "V2"],
            "locations": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        }
        
        probe = Probe.from_dict(data)
        
        assert probe.name == "dict_probe"
        assert probe.probe_type == "voltage_taps"
        assert probe.index == ["V1", "V2"]
        assert probe.locations == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]

    @patch('python_magnetgeo.utils.loadYaml')
    def test_from_yaml(self, mock_load_yaml):
        """Test loading from YAML file"""
        mock_probe = Probe("test", "voltage_taps", ["V1"], [[1.0, 2.0, 3.0]])
        mock_load_yaml.return_value = mock_probe
        
        result = Probe.from_yaml("test.yaml")
        
        mock_load_yaml.assert_called_once_with("Probe", "test.yaml", Probe, False)
        assert result == mock_probe

    @patch('python_magnetgeo.utils.loadJson')
    def test_from_json(self, mock_load_json):
        """Test loading from JSON file"""
        mock_probe = Probe("test", "temperature", ["T1"], [[1.0, 2.0, 3.0]])
        mock_load_json.return_value = mock_probe
        
        result = Probe.from_json("test.json")
        
        mock_load_json.assert_called_once_with("Probe", "test.json", False)
        assert result == mock_probe


class TestProbeConstructor:
    """Test Probe YAML constructor"""

    def test_probe_constructor(self):
        """Test the YAML constructor function"""
        from unittest.mock import MagicMock
        
        # Mock the loader and node
        loader = MagicMock()
        node = MagicMock()
        
        # Mock the construct_mapping method
        test_data = {
            "name": "constructor_test",
            "probe_type": "temperature",
            "index": ["T1"],
            "locations": [[1.0, 2.0, 3.0]]
        }
        loader.construct_mapping.return_value = test_data
        
        # Import and test the constructor
        from python_magnetgeo.Probe import Probe_constructor
        
        result = Probe_constructor(loader, node)
        
        assert isinstance(result, Probe)
        assert result.name == "constructor_test"
        assert result.probe_type == "temperature"


class TestProbeIntegration:
    """Integration tests with actual file I/O"""

    def test_yaml_roundtrip(self):
        """Test complete YAML save/load cycle"""
        original_probe = Probe(
            name="integration_test",
            probe_type="magnetic_field",
            index=["B1", "B2", "B3"],
            locations=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(original_probe, f)
            temp_filename = f.name
        
        try:
            # Load back from file
            with open(temp_filename, 'r') as f:
                loaded_probe = yaml.load(f, Loader=yaml.FullLoader)
            
            # Verify the loaded probe matches the original
            assert loaded_probe.name == original_probe.name
            assert loaded_probe.probe_type == original_probe.probe_type
            assert loaded_probe.index == original_probe.index
            assert loaded_probe.locations == original_probe.locations
            
        finally:
            # Clean up
            os.unlink(temp_filename)

    def test_json_roundtrip(self):
        """Test complete JSON save/load cycle"""
        original_probe = Probe(
            name="json_test",
            probe_type="voltage_taps",
            index=["V1", "V2"],
            locations=[[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]
        )
        
        # Convert to JSON and back
        json_str = original_probe.to_json()
        
        # Parse JSON (this would normally go through deserialize.py)
        json_data = json.loads(json_str)
        
        # Verify JSON structure
        assert json_data["name"] == "json_test"
        assert json_data["probe_type"] == "voltage_taps"
        assert json_data["index"] == ["V1", "V2"]
        assert json_data["locations"] == [[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]


if __name__ == "__main__":
    pytest.main([__file__])
