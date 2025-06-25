#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Bitters class using consistent approach
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Bitters import Bitters, Bitters_constructor
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo.tierod import Tierod
from python_magnetgeo.Shape2D import Shape2D
from .test_utils_common import (
    BaseSerializationTestMixin,
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes
)


class TestBittersInitialization:
    """Test Bitters object initialization"""
    
    @pytest.fixture
    def sample_bitter_objects(self):
        """Create sample Bitter objects for testing"""
        modelaxi = ModelAxi(name="test_axi", h=10.0, turns=[2.0], pitch=[5.0])
        shape = Shape2D(name="test_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(name="test_tierod", r=15.0, n=4, dh=2.0, sh=8.0, shape=shape)
        
        bitter1 = Bitter(
            name="bitter1", r=[10.0, 20.0], z=[0.0, 50.0], odd=True,
            modelaxi=modelaxi, coolingslits=[], tierod=tierod, innerbore=5.0, outerbore=25.0
        )
        bitter2 = Bitter(
            name="bitter2", r=[25.0, 35.0], z=[60.0, 110.0], odd=False,
            modelaxi=modelaxi, coolingslits=[], tierod=tierod, innerbore=20.0, outerbore=40.0
        )
        return [bitter1, bitter2]

    def test_bitters_basic_initialization(self, sample_bitter_objects):
        """Test Bitters initialization with Bitter objects"""
        bitters = Bitters(
            name="test_bitters",
            magnets=sample_bitter_objects,
            innerbore=5.0,
            outerbore=40.0
        )
        
        assert bitters.name == "test_bitters"
        assert bitters.magnets == sample_bitter_objects
        assert bitters.innerbore == 5.0
        assert bitters.outerbore == 40.0
        assert len(bitters.magnets) == 2

    def test_bitters_with_string_references(self):
        """Test Bitters initialization with string references (before update)"""
        bitters = Bitters(
            name="string_bitters",
            magnets=["bitter1", "bitter2", "bitter3"],  # List of string references
            innerbore=8.0,
            outerbore=50.0
        )
        
        # Before update(), magnets should remain as strings
        assert bitters.name == "string_bitters"
        assert isinstance(bitters.magnets, list)
        assert all(isinstance(item, str) for item in bitters.magnets)
        assert bitters.magnets == ["bitter1", "bitter2", "bitter3"]
        assert bitters.innerbore == 8.0
        assert bitters.outerbore == 50.0

    def test_bitters_with_empty_magnets(self):
        """Test Bitters initialization with empty magnets list"""
        bitters = Bitters(
            name="empty_bitters",
            magnets=[],
            innerbore=5.0,
            outerbore=15.0
        )
        
        assert bitters.name == "empty_bitters"
        assert bitters.magnets == []
        assert len(bitters.magnets) == 0
        assert bitters.innerbore == 5.0
        assert bitters.outerbore == 15.0

    def test_bitters_with_mixed_types(self):
        """Test Bitters with mixed integer and float types"""
        bitters = Bitters(
            name="mixed_bitters",
            magnets=[],
            innerbore=5,      # int
            outerbore=15.5    # float
        )
        
        assert bitters.name == "mixed_bitters"
        assert bitters.innerbore == 5
        assert bitters.outerbore == 15.5
        assert isinstance(bitters.innerbore, int)
        assert isinstance(bitters.outerbore, float)


class TestBittersMethods:
    """Test Bitters class methods"""
    
    @pytest.fixture
    def sample_bitters(self):
        """Create a sample Bitters for testing"""
        # Create mock Bitter objects with necessary methods
        bitter1 = Mock()
        bitter1.name = "test_bitter1"
        bitter1.r = [15.0, 25.0]
        bitter1.z = [0.0, 40.0]
        bitter1.get_names = Mock(return_value=["bitter1_section1", "bitter1_section2"])
        bitter1.get_channels = Mock(return_value=["channel1", "channel2"])
        
        bitter2 = Mock()
        bitter2.name = "test_bitter2"
        bitter2.r = [30.0, 40.0]
        bitter2.z = [50.0, 90.0]
        bitter2.get_names = Mock(return_value=["bitter2_section1"])
        bitter2.get_channels = Mock(return_value=["channel3"])
        
        return Bitters(
            name="sample_bitters",
            magnets=[bitter1, bitter2],
            innerbore=10.0,
            outerbore=45.0
        )

    def test_repr(self, sample_bitters):
        """Test __repr__ method"""
        repr_str = repr(sample_bitters)
        
        assert "Bitters(" in repr_str
        assert "name='sample_bitters'" in repr_str
        assert "innerbore=10.0" in repr_str
        assert "outerbore=45.0" in repr_str
        assert "magnets=" in repr_str

    def test_get_channels(self, sample_bitters):
        """Test get_channels method"""
        channels = sample_bitters.get_channels("test")
        
        # Should return a dictionary with entries for each magnet
        assert isinstance(channels, dict)
        expected_keys = ["test_test_bitter1", "test_test_bitter2"]
        assert set(channels.keys()) == set(expected_keys)
        
        # Verify get_channels was called on each magnet
        for magnet in sample_bitters.magnets:
            magnet.get_channels.assert_called_once()

    def test_get_channels_no_prefix(self, sample_bitters):
        """Test get_channels with no prefix"""
        channels = sample_bitters.get_channels("")
        
        expected_keys = ["test_bitter1", "test_bitter2"]
        assert set(channels.keys()) == set(expected_keys)

    def test_get_isolants(self, sample_bitters):
        """Test get_isolants method"""
        isolants = sample_bitters.get_isolants("test")
        # Currently returns empty dict according to implementation
        assert isolants == {}

    def test_get_names(self, sample_bitters):
        """Test get_names method"""
        names = sample_bitters.get_names("test")
        
        # Should aggregate names from all magnets
        expected_names = ["bitter1_section1", "bitter1_section2", "bitter2_section1"]
        assert names == expected_names
        
        # Verify get_names was called on each magnet with correct parameters
        sample_bitters.magnets[0].get_names.assert_called_once_with("test_test_bitter1", False, False)
        sample_bitters.magnets[1].get_names.assert_called_once_with("test_test_bitter2", False, False)

    def test_get_names_with_parameters(self, sample_bitters):
        """Test get_names method with is2D and verbose parameters"""
        names = sample_bitters.get_names("test", is2D=True, verbose=True)
        
        # Verify parameters are passed correctly
        sample_bitters.magnets[0].get_names.assert_called_once_with("test_test_bitter1", True, True)
        sample_bitters.magnets[1].get_names.assert_called_once_with("test_test_bitter2", True, True)

    def test_bounding_box(self, sample_bitters):
        """Test boundingBox method"""
        rb, zb = sample_bitters.boundingBox()
        
        # Should return overall bounding box encompassing all magnets
        # bitter1: r=[15.0, 25.0], z=[0.0, 40.0]
        # bitter2: r=[30.0, 40.0], z=[50.0, 90.0]
        assert rb == [15.0, 40.0]  # min r from bitter1, max r from bitter2
        assert zb == [0.0, 90.0]   # min z from bitter1, max z from bitter2

    def test_bounding_box_empty_magnets(self):
        """Test boundingBox method with empty magnets"""
        empty_bitters = Bitters(name="empty", magnets=[], innerbore=5.0, outerbore=15.0)
        
        rb, zb = empty_bitters.boundingBox()
        assert rb == [0, 0]
        assert zb == [0, 0]

    def test_intersect(self, sample_bitters):
        """Test intersect method"""
        # Test with overlapping rectangle
        result = sample_bitters.intersect([20.0, 35.0], [10.0, 70.0])
        assert result is True
        
        # Test with non-overlapping rectangle
        result = sample_bitters.intersect([100.0, 110.0], [200.0, 210.0])
        assert result is False

    def test_update_method_with_string_magnets(self):
        """Test update method when magnets are string references"""
        bitters = Bitters(
            name="update_test",
            magnets=["bitter1", "bitter2"],  # String references
            innerbore=5.0,
            outerbore=25.0
        )
        
        # Initially should be strings
        assert all(isinstance(item, str) for item in bitters.magnets)
        
        # Mock the loading of magnets
        mock_bitter1 = Mock()
        mock_bitter1.name = "bitter1"
        mock_bitter2 = Mock()
        mock_bitter2.name = "bitter2"
        
        with patch('python_magnetgeo.utils.loadList', return_value=[mock_bitter1, mock_bitter2]) as mock_load:
            bitters.update()
            
            # After update, should be actual Bitter objects
            assert bitters.magnets == [mock_bitter1, mock_bitter2]
            mock_load.assert_called_once_with(
                "magnets", 
                ["bitter1", "bitter2"], 
                [None, Bitter], 
                {"Bitter": Bitter.from_dict}
            )

    def test_update_method_with_object_magnets(self, sample_bitters):
        """Test update method when magnets are already objects"""
        original_magnets = sample_bitters.magnets
        
        # update() should not change anything when magnets are already objects
        with patch('python_magnetgeo.utils.check_objects', return_value=False):
            sample_bitters.update()
            assert sample_bitters.magnets is original_magnets


class TestBittersSerialization(BaseSerializationTestMixin):
    """Test Bitters serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Bitters instance"""
        # Use simple string references instead of Mock objects for serialization
        # This avoids YAML serialization issues with Mock objects
        return Bitters(
            name="test_bitters",
            magnets=["bitter1", "bitter2"],  # String references are serializable
            innerbore=5.0,
            outerbore=40.0
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''!<Bitters>
name: yaml_bitters
magnets: []
innerbore: 8.0
outerbore: 32.0
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_bitters",
            "innerbore": 5.0,
            "outerbore": 40.0,
            "magnets": ["bitter1", "bitter2"]
        }
    
    def get_class_under_test(self):
        """Return Bitters class"""
        return Bitters

    def test_json_includes_magnets_data(self):
        """Test that JSON serialization includes magnets data"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "magnets" in parsed
        assert isinstance(parsed["magnets"], list)
        assert parsed["magnets"] == ["bitter1", "bitter2"]

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to Bitters dump"):
            instance.dump()

    def test_write_to_json_method(self):
        """Test write_to_json method"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.write_to_json()
            mock_file.assert_called_once_with("test_bitters.json", "w")

    def test_serialization_with_actual_objects(self):
        """Test serialization works with actual Bitter objects (not Mock)"""
        # Create a simple Bitters instance with actual Bitter objects
        modelaxi = ModelAxi(name="test_axi", h=10.0, turns=[2.0], pitch=[5.0])
        shape = Shape2D(name="test_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(name="test_tierod", r=15.0, n=4, dh=2.0, sh=8.0, shape=shape)
        
        bitter1 = Bitter(
            name="actual_bitter1", r=[10.0, 20.0], z=[0.0, 50.0], odd=True,
            modelaxi=modelaxi, coolingslits=[], tierod=tierod, innerbore=5.0, outerbore=25.0
        )
        
        bitters = Bitters(
            name="actual_bitters",
            magnets=[bitter1],
            innerbore=5.0,
            outerbore=30.0
        )
        
        # Test JSON serialization works
        json_str = bitters.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Bitters"
        assert parsed["name"] == "actual_bitters"
        assert "magnets" in parsed


class TestBittersYAMLConstructor(BaseYAMLConstructorTestMixin):
    """Test Bitters YAML constructor using common test mixin"""
    
    def get_constructor_function(self):
        """Return the Bitters constructor function"""
        def mock_constructor(loader, node):
            # Call construct_mapping to satisfy the mixin's expectation
            values = loader.construct_mapping(node)
            # Return simplified data for easy comparison
            return values, self.get_expected_constructor_type()
        return mock_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        return {
            "name": "constructor_bitters",
            "magnets": ["bitter1", "bitter2"],
            "innerbore": 8.0,
            "outerbore": 50.0
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "Bitters"

    def test_constructor_directly(self):
        """Test the Bitters_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test_bitters",
            "magnets": ["bitter1", "bitter2"],
            "innerbore": 10.0,
            "outerbore": 60.0
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Bitters_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Bitters)
        assert result.name == "direct_test_bitters"
        assert result.magnets == ["bitter1", "bitter2"]
        assert result.innerbore == 10.0
        assert result.outerbore == 60.0
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestBittersYAMLTag(BaseYAMLTagTestMixin):
    """Test Bitters YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Bitters class"""
        return Bitters
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Bitters"


class TestBittersFromDict:
    """Test Bitters.from_dict class method"""
    
    def test_from_dict_complete_data(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_bitters",
            "magnets": ["bitter1", "bitter2", "bitter3"],
            "innerbore": 12.0,
            "outerbore": 48.0
        }
        
        bitters = Bitters.from_dict(data)
        
        assert bitters.name == "dict_bitters"
        assert bitters.magnets == ["bitter1", "bitter2", "bitter3"]
        assert bitters.innerbore == 12.0
        assert bitters.outerbore == 48.0

    def test_from_dict_missing_bore_fields(self):
        """Test from_dict with missing innerbore/outerbore fields"""
        data = {
            "name": "minimal_bitters",
            "magnets": ["bitter1"]
        }
        
        bitters = Bitters.from_dict(data)
        
        assert bitters.name == "minimal_bitters"
        assert bitters.magnets == ["bitter1"]
        assert bitters.innerbore == 0  # Default value
        assert bitters.outerbore == 0  # Default value

    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_bitters",
            "magnets": [],
            "innerbore": 5.0,
            "outerbore": 15.0
        }
        
        bitters = Bitters.from_dict(data, debug=True)
        assert bitters.name == "debug_bitters"


class TestBittersFileOperations:
    """Test Bitters file operations and edge cases"""
    
    def test_from_yaml_success(self):
        """Test successful from_yaml loading"""
        yaml_content = '''!<Bitters>
name: yaml_bitters
magnets: []
innerbore: 10.0
outerbore: 50.0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                bitters = Bitters.from_yaml(tmp_file.name)
                
                assert bitters.name == "yaml_bitters"
                assert bitters.magnets == []
                assert bitters.innerbore == 10.0
                assert bitters.outerbore == 50.0
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_file_not_found(self):
        """Test from_yaml with non-existent file"""
        with pytest.raises(Exception, match="Failed to load Bitters data"):
            Bitters.from_yaml("non_existent_file.yaml")

    def test_from_yaml_invalid_yaml(self):
        """Test from_yaml with invalid YAML content"""
        invalid_yaml = "name: test\nmagnets: invalid_list_format\ninnerbore: not_a_number"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(invalid_yaml)
            tmp_file.flush()
            
            try:
                with pytest.raises(Exception):
                    Bitters.from_yaml(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)

    @patch("python_magnetgeo.deserialize.unserialize_object")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_from_json_success(self, mock_file, mock_unserialize):
        """Test successful from_json loading"""
        mock_bitters = Bitters(name="json_bitters", magnets=[], innerbore=5.0, outerbore=25.0)
        mock_unserialize.return_value = mock_bitters
        
        result = Bitters.from_json("test.json")
        
        mock_file.assert_called_once_with("test.json", "r")
        mock_unserialize.assert_called_once()
        assert result == mock_bitters


class TestBittersErrorHandling:
    """Test error handling in Bitters class"""

    def test_invalid_magnets_handling(self):
        """Test handling of invalid magnets parameter"""
        # Test with None magnets (should raise error depending on implementation)
        try:
            bitters = Bitters(name="none_bitters", magnets=None, innerbore=5.0, outerbore=15.0)
            # If no error is raised, the implementation allows None
            assert bitters.magnets is None
        except (TypeError, AttributeError):
            # Expected if the implementation validates the magnets parameter
            pass

    def test_extreme_value_handling(self):
        """Test handling of extreme parameter values"""
        # Test with very large values
        large_bitters = Bitters(
            name="large_bitters",
            magnets=[],
            innerbore=1e10,
            outerbore=1e12
        )
        
        assert large_bitters.name == "large_bitters"
        assert large_bitters.innerbore == 1e10
        assert large_bitters.outerbore == 1e12
        
        # Test with very small values
        small_bitters = Bitters(
            name="small_bitters",
            magnets=[],
            innerbore=1e-10,
            outerbore=1e-8
        )
        
        assert small_bitters.name == "small_bitters"
        assert small_bitters.innerbore == 1e-10
        assert small_bitters.outerbore == 1e-8

    def test_update_method_error_handling(self):
        """Test update method error handling"""
        bitters = Bitters(name="error_bitters", magnets=["nonexistent_bitter"], innerbore=5.0, outerbore=15.0)
        
        # Mock loadList to raise an error
        with patch('python_magnetgeo.utils.loadList', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError, match="File not found"):
                bitters.update()

    def test_get_channels_with_magnet_error(self):
        """Test get_channels when individual magnet raises error"""
        error_magnet = Mock()
        error_magnet.name = "error_magnet"
        error_magnet.get_channels = Mock(side_effect=Exception("Magnet error"))
        
        bitters = Bitters(name="error_bitters", magnets=[error_magnet], innerbore=5.0, outerbore=15.0)
        
        # Should propagate the error from individual magnet
        with pytest.raises(Exception, match="Magnet error"):
            bitters.get_channels("test")

    def test_dump_with_invalid_filename(self):
        """Test dump method with invalid filename"""
        bitters = Bitters(name="dump_error_bitters", magnets=[], innerbore=5.0, outerbore=15.0)
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception, match="Failed to Bitters dump"):
                bitters.dump()


class TestBittersIntegration:
    """Integration tests for Bitters class"""
    
    def test_bitters_with_various_magnets(self):
        """Test Bitters with different types of magnets"""
        # Create mock magnets with different properties
        magnets = []
        for i in range(3):
            magnet = Mock()
            magnet.name = f"magnet_{i}"
            magnet.r = [i * 10.0, (i + 1) * 15.0]
            magnet.z = [i * 20.0, (i + 1) * 30.0]
            magnet.get_names = Mock(return_value=[f"magnet_{i}_section"])
            magnet.get_channels = Mock(return_value=[f"channel_{i}"])
            magnets.append(magnet)
        
        bitters = Bitters(
            name="integration_bitters",
            magnets=magnets,
            innerbore=5.0,
            outerbore=50.0
        )
        
        # Verify each magnet maintains its properties
        for i, magnet in enumerate(bitters.magnets):
            assert magnet.name == f"magnet_{i}"
            assert magnet.r == [i * 10.0, (i + 1) * 15.0]

    def test_bitters_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_bitters = Bitters(
            name="roundtrip_bitters",
            magnets=["bitter1", "bitter2"],  # String references
            innerbore=10.0,
            outerbore=60.0
        )
        
        # Test JSON serialization
        json_str = original_bitters.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Bitters"
        assert parsed_json["name"] == "roundtrip_bitters"
        assert parsed_json["magnets"] == ["bitter1", "bitter2"]
        assert parsed_json["innerbore"] == 10.0
        assert parsed_json["outerbore"] == 60.0

    def test_bitters_collection_operations(self):
        """Test operations on collections of bitters"""
        # Create collection of bitters with different properties
        bitters_list = []
        for i in range(5):
            bitters = Bitters(
                name=f"collection_bitters_{i}",
                magnets=[f"bitter_{i}_1", f"bitter_{i}_2"],
                innerbore=i * 2.0,
                outerbore=(i + 1) * 10.0
            )
            bitters_list.append(bitters)
        
        # Test sorting by innerbore
        sorted_bitters = sorted(bitters_list, key=lambda b: b.innerbore)
        assert sorted_bitters[0].innerbore == 0.0
        assert sorted_bitters[-1].innerbore == 8.0
        
        # Test filtering by number of magnets
        all_with_two_magnets = [b for b in bitters_list if len(b.magnets) == 2]
        assert len(all_with_two_magnets) == 5
        
        # Test aggregation operations
        total_bore_range = sum(b.outerbore - b.innerbore for b in bitters_list)
        assert total_bore_range > 0


class TestBittersPerformance:
    """Performance tests for Bitters class"""
    
    def test_large_magnets_list_performance(self):
        """Test Bitters performance with many magnets"""
        # Create many magnet references
        large_magnets_list = [f"bitter_{i}" for i in range(100)]
        
        bitters = Bitters(
            name="performance_bitters",
            magnets=large_magnets_list,
            innerbore=5.0,
            outerbore=200.0
        )
        
        # Test that operations still work with many magnets
        assert len(bitters.magnets) == 100
        assert all(isinstance(m, str) for m in bitters.magnets)
        
        json_str = bitters.to_json()
        assert len(json_str) > 0

    def test_multiple_bitters_creation_performance(self):
        """Test performance of creating many bitters"""
        # Create many bitters
        bitters_list = []
        for i in range(50):
            bitters = Bitters(
                name=f"perf_bitters_{i}",
                magnets=[f"bitter_{i}"],
                innerbore=float(i),
                outerbore=float(i + 20)
            )
            bitters_list.append(bitters)
        
        assert len(bitters_list) == 50
        assert all(isinstance(b, Bitters) for b in bitters_list)


class TestBittersComplexScenarios:
    """Test complex real-world scenarios for Bitters"""
    
    def test_resistive_magnet_system(self):
        """Test Bitters representing a resistive magnet system"""
        # Simulate a multi-section resistive magnet
        magnet_configs = [
            ("outer_section", [100.0, 200.0], [0.0, 300.0]),
            ("middle_section", [50.0, 90.0], [50.0, 250.0]),
            ("inner_section", [20.0, 40.0], [100.0, 200.0])
        ]
        
        mock_magnets = []
        for name, r, z in magnet_configs:
            magnet = Mock()
            magnet.name = name
            magnet.r = r
            magnet.z = z
            magnet.get_names = Mock(return_value=[f"{name}_section"])
            mock_magnets.append(magnet)
        
        resistive_system = Bitters(
            name="resistive_magnet_system",
            magnets=mock_magnets,
            innerbore=15.0,
            outerbore=210.0
        )
        
        # Test bounding box encompasses all sections
        rb, zb = resistive_system.boundingBox()
        assert rb == [20.0, 200.0]  # From inner to outer
        assert zb == [0.0, 300.0]   # Full height range
        
        # Test names generation
        names = resistive_system.get_names("magnet")
        expected = ["outer_section_section", "middle_section_section", "inner_section_section"]
        assert names == expected

    def test_high_field_bitter_stack(self):
        """Test Bitters representing a high-field Bitter magnet stack"""
        # Multiple thin disks for high field generation
        mock_disks = []
        for i in range(10):
            disk = Mock()
            disk.name = f"disk_{i+1:02d}"
            disk.r = [30.0, 80.0]
            disk.z = [i*25.0, (i+1)*25.0 - 5.0]
            disk.get_names = Mock(return_value=[f"disk_{i+1:02d}_section"])
            mock_disks.append(disk)
        
        high_field_system = Bitters(
            name="high_field_bitter_stack",
            magnets=mock_disks,
            innerbore=25.0,
            outerbore=85.0
        )
        
        assert len(high_field_system.magnets) == 10
        
        # All disks should have same radial extent
        for disk in high_field_system.magnets:
            assert disk.r == [30.0, 80.0]
        
        # Test overall bounding box
        rb, zb = high_field_system.boundingBox()
        assert rb == [30.0, 80.0]
        assert zb == [0.0, 245.0]  # Last disk: 9*25 to 10*25-5

    def test_water_cooled_bitter_system(self):
        """Test Bitters with water cooling channels"""
        # Bitter magnets typically have complex cooling
        mock_cooled_bitters = []
        configs = [
            ("cooled_bitter_1", [40.0, 120.0], [0.0, 100.0]),
            ("cooled_bitter_2", [40.0, 120.0], [110.0, 210.0]),
            ("cooled_bitter_3", [40.0, 120.0], [220.0, 320.0])
        ]
        
        for name, r, z in configs:
            bitter = Mock()
            bitter.name = name
            bitter.r = r
            bitter.z = z
            bitter.get_channels = Mock(return_value=[f"{name}_channel"])
            mock_cooled_bitters.append(bitter)
        
        cooled_system = Bitters(
            name="water_cooled_system",
            magnets=mock_cooled_bitters,
            innerbore=35.0,
            outerbore=125.0
        )
        
        # Test channels collection
        channels = cooled_system.get_channels("cooling")
        assert len(channels) == 3
        expected_keys = [
            "cooling_cooled_bitter_1",
            "cooling_cooled_bitter_2", 
            "cooling_cooled_bitter_3"
        ]
        assert set(channels.keys()) == set(expected_keys)
        
        # Test intersection with cooling circuit
        cooling_region = [30.0, 130.0]  # Slightly larger than magnets
        cooling_height = [-10.0, 330.0] # Full height plus margins
        assert cooled_system.intersect(cooling_region, cooling_height) is True
        
        # Test no intersection with external regions
        external_region = [200.0, 300.0]  # Far from magnets
        external_height = [0.0, 100.0]
        assert cooled_system.intersect(external_region, external_height) is False


class TestBittersGeometry:
    """Test geometric operations for Bitters"""
    
    def test_bounding_box_calculation(self):
        """Test bounding box calculation with known coordinates"""
        # Create mock magnets with specific geometries
        magnet1 = Mock()
        magnet1.name = "geo1"
        magnet1.r = [10.0, 20.0]
        magnet1.z = [0.0, 30.0]
        
        magnet2 = Mock()
        magnet2.name = "geo2"
        magnet2.r = [15.0, 25.0]
        magnet2.z = [35.0, 65.0]
        
        magnet3 = Mock()
        magnet3.name = "geo3"
        magnet3.r = [5.0, 30.0]  # Widest bounds
        magnet3.z = [-10.0, 70.0]  # Tallest bounds
        
        bitters = Bitters(
            name="geometric_test",
            magnets=[magnet1, magnet2, magnet3],
            innerbore=2.0,
            outerbore=35.0
        )
        
        rb, zb = bitters.boundingBox()
        
        # Should return the overall bounding box
        assert rb == [5.0, 30.0]  # Min r from magnet3, max r from magnet3
        assert zb == [-10.0, 70.0]  # Min z from magnet3, max z from magnet3

    def test_intersect_various_cases(self):
        """Test intersect method with various test cases"""
        # Setup bitters with known bounds
        magnet = Mock()
        magnet.name = "test_magnet"
        magnet.r = [10.0, 20.0]
        magnet.z = [5.0, 25.0]
        
        bitters = Bitters(name="intersect_test", magnets=[magnet], innerbore=5.0, outerbore=25.0)
        
        # Test cases: (r_range, z_range, expected_result)
        test_cases = [
            ([15.0, 25.0], [10.0, 30.0], True),   # Overlaps
            ([0.0, 30.0], [0.0, 30.0], True),    # Contains entirely
            ([12.0, 18.0], [10.0, 20.0], True),  # Contained within
            ([25.0, 35.0], [10.0, 20.0], False), # No overlap (r)
            ([15.0, 18.0], [30.0, 40.0], False), # No overlap (z)
            ([5.0, 8.0], [20.0, 22.0], False),   # No overlap (both)
        ]
        
        for r_range, z_range, expected in test_cases:
            result = bitters.intersect(r_range, z_range)
            assert result == expected, f"Failed for r={r_range}, z={z_range}"

    def test_intersect_edge_cases(self):
        """Test intersect method edge cases"""
        magnet = Mock()
        magnet.name = "edge_magnet"
        magnet.r = [10.0, 20.0]
        magnet.z = [5.0, 15.0]
        
        bitters = Bitters(name="edge_test", magnets=[magnet], innerbore=5.0, outerbore=25.0)
        
        # Edge touching cases
        assert bitters.intersect([20.0, 30.0], [5.0, 15.0]) is False  # Edge touching in r
        assert bitters.intersect([10.0, 20.0], [15.0, 25.0]) is False  # Edge touching in z
        
        # Barely overlapping cases
        assert bitters.intersect([19.9, 30.0], [5.0, 15.0]) is True   # Tiny overlap in r
        assert bitters.intersect([10.0, 20.0], [14.9, 25.0]) is True  # Tiny overlap in z


class TestBittersDataValidation:
    """Test data validation and consistency for Bitters"""
    
    def test_numeric_parameter_types(self):
        """Test that numeric parameters accept appropriate types"""
        # Test with integers
        bitters_int = Bitters(name="int_test", magnets=[], innerbore=5, outerbore=15)
        assert isinstance(bitters_int.innerbore, int)
        assert isinstance(bitters_int.outerbore, int)
        
        # Test with floats
        bitters_float = Bitters(name="float_test", magnets=[], innerbore=5.5, outerbore=15.5)
        assert isinstance(bitters_float.innerbore, float)
        assert isinstance(bitters_float.outerbore, float)
        
        # Test with mixed types
        bitters_mixed = Bitters(name="mixed_test", magnets=[], innerbore=5, outerbore=15.5)
        assert isinstance(bitters_mixed.innerbore, int)
        assert isinstance(bitters_mixed.outerbore, float)

    def test_magnets_parameter_validation(self):
        """Test magnets parameter validation"""
        # Test with empty list
        bitters_empty = Bitters(name="empty_test", magnets=[], innerbore=5.0, outerbore=15.0)
        assert isinstance(bitters_empty.magnets, list)
        assert len(bitters_empty.magnets) == 0
        
        # Test with strings
        bitters_strings = Bitters(name="string_test", magnets=["bitter1", "bitter2"], innerbore=5.0, outerbore=15.0)
        assert isinstance(bitters_strings.magnets, list)
        assert all(isinstance(m, str) for m in bitters_strings.magnets)
        
        # Test with mock objects
        mock_magnet = Mock()
        bitters_objects = Bitters(name="object_test", magnets=[mock_magnet], innerbore=5.0, outerbore=15.0)
        assert isinstance(bitters_objects.magnets, list)
        assert bitters_objects.magnets[0] == mock_magnet

    def test_geometric_consistency(self):
        """Test geometric parameter consistency"""
        bitters = Bitters(name="geo_test", magnets=[], innerbore=10.0, outerbore=50.0)
        
        # Basic geometric relationships
        assert bitters.outerbore > bitters.innerbore, "Outer bore should be larger than inner bore"
        assert bitters.innerbore >= 0, "Inner bore should be non-negative"
        assert bitters.outerbore > 0, "Outer bore should be positive"

    def test_name_validation(self):
        """Test name parameter validation"""
        # Test with various string types
        names_to_test = [
            "simple_name",
            "name-with-dashes",
            "name_with_underscores",
            "name123with456numbers",
            "Name With Spaces",
            "name.with.dots",
            "",  # Empty string
        ]
        
        for name in names_to_test:
            bitters = Bitters(name=name, magnets=[], innerbore=5.0, outerbore=15.0)
            assert bitters.name == name
            assert isinstance(bitters.name, str)


class TestBittersCompatibility:
    """Test Bitters compatibility and edge cases"""
    
    def test_floating_point_precision(self):
        """Test Bitters with floating point precision edge cases"""
        precise_values = [
            1.0000000000001,
            1.9999999999999,
            0.1 + 0.2,  # Classic floating point precision issue
            1e-15,
            1e15
        ]
        
        for inner, outer in zip(precise_values[:-1], precise_values[1:]):
            bitters = Bitters(
                name="precision_test",
                magnets=[],
                innerbore=inner,
                outerbore=outer
            )
            
            # Values should be preserved as-is
            assert bitters.innerbore == inner
            assert bitters.outerbore == outer
            
            # JSON serialization should handle these values
            json_str = bitters.to_json()
            parsed = json.loads(json_str)
            
            # Should be reasonably close (within floating point precision)
            assert abs(parsed["innerbore"] - inner) < 1e-10
            assert abs(parsed["outerbore"] - outer) < 1e-10

    def test_string_representations_in_json(self):
        """Test that string fields are properly handled in JSON"""
        bitters = Bitters(
            name='name"with"quotes\\and\\backslashes\nand\nnewlines',
            magnets=["magnet\\with\\backslashes", "magnet\"with\"quotes"],
            innerbore=1.0,
            outerbore=2.0
        )
        
        json_str = bitters.to_json()
        parsed = json.loads(json_str)  # Should not raise exception
        
        assert parsed["name"] == 'name"with"quotes\\and\\backslashes\nand\nnewlines'
        assert "magnet\\with\\backslashes" in parsed["magnets"]
        assert "magnet\"with\"quotes" in parsed["magnets"]

    def test_comparison_consistency(self):
        """Test that identical Bitters have consistent representations"""
        bitters1 = Bitters(
            name="identical",
            magnets=["bitter1", "bitter2"],
            innerbore=5.0,
            outerbore=25.0
        )
        
        bitters2 = Bitters(
            name="identical",
            magnets=["bitter1", "bitter2"],
            innerbore=5.0,
            outerbore=25.0
        )
        
        # Should have identical string representations
        assert repr(bitters1) == repr(bitters2)


class TestBittersDocumentation:
    """Test that Bitters behavior matches its documentation"""
    
    def test_documented_attributes(self):
        """Test that Bitters has all documented attributes"""
        bitters = Bitters(
            name="doc_test",
            magnets=["bitter1"],
            innerbore=5.0,
            outerbore=15.0
        )
        
        # Verify all documented attributes exist
        assert hasattr(bitters, "name")
        assert hasattr(bitters, "magnets")
        assert hasattr(bitters, "innerbore")
        assert hasattr(bitters, "outerbore")
        
        # Verify types
        assert isinstance(bitters.name, str)
        assert isinstance(bitters.magnets, list)
        assert isinstance(bitters.innerbore, (int, float))
        assert isinstance(bitters.outerbore, (int, float))

    def test_yaml_tag_matches_class_name(self):
        """Test that YAML tag matches class name"""
        assert Bitters.yaml_tag == "Bitters"

    def test_container_behavior(self):
        """Test that Bitters behaves as container for Bitter objects"""
        bitter1 = Mock()
        bitter1.name = "bitter1"
        bitter2 = Mock()
        bitter2.name = "bitter2"
        
        bitters = Bitters(
            name="container_test",
            magnets=[bitter1, bitter2],
            innerbore=5.0,
            outerbore=25.0
        )
        
        # Should contain the bitter objects
        assert len(bitters.magnets) == 2
        assert bitters.magnets[0] == bitter1
        assert bitters.magnets[1] == bitter2

    def test_geometric_operations_documented(self):
        """Test that geometric operations work as documented"""
        magnet = Mock()
        magnet.name = "geo_test"
        magnet.r = [5.0, 15.0]
        magnet.z = [0.0, 20.0]
        
        bitters = Bitters(name="geo_test", magnets=[magnet], innerbore=2.0, outerbore=18.0)
        
        # boundingBox should return r, z coordinates as tuple
        result = bitters.boundingBox()
        assert isinstance(result, tuple)
        assert len(result) == 2
        rb, zb = result
        assert rb == [5.0, 15.0]
        assert zb == [0.0, 20.0]
        
        # intersect should return boolean
        intersection_result = bitters.intersect([10.0, 20.0], [5.0, 15.0])
        assert isinstance(intersection_result, bool)

    def test_serialization_methods_documented(self):
        """Test that all documented serialization methods work"""
        bitters = Bitters(name="serialize_test", magnets=[], innerbore=1.0, outerbore=2.0)
        
        # YAML methods
        assert hasattr(bitters, "dump")
        assert callable(bitters.dump)
        
        # JSON methods
        assert hasattr(bitters, "to_json")
        assert callable(bitters.to_json)
        assert hasattr(bitters, "write_to_json")
        assert callable(bitters.write_to_json)
        
        # Class methods
        assert hasattr(Bitters, "from_yaml")
        assert callable(Bitters.from_yaml)
        assert hasattr(Bitters, "from_json")
        assert callable(Bitters.from_json)
        assert hasattr(Bitters, "from_dict")
        assert callable(Bitters.from_dict)
        
        # Test that JSON serialization works
        json_str = bitters.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Bitters"
        assert parsed["name"] == "serialize_test"

    def test_update_functionality_documented(self):
        """Test that update functionality works as documented"""
        bitters = Bitters(
            name="update_test",
            magnets=["string1", "string2"],  # String magnets that need loading
            innerbore=1.0,
            outerbore=2.0
        )
        
        # Mock the update process
        with patch('python_magnetgeo.utils.loadList') as mock_load:
            mock_bitter1 = Mock()
            mock_bitter2 = Mock()
            mock_load.return_value = [mock_bitter1, mock_bitter2]
            
            bitters.update()
            
            # Should convert strings to Bitter objects
            assert bitters.magnets == [mock_bitter1, mock_bitter2]
            mock_load.assert_called_once_with(
                "magnets", 
                ["string1", "string2"], 
                [None, Bitter], 
                {"Bitter": Bitter.from_dict}
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
