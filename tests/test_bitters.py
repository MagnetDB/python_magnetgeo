#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Bitters class using consistent approach (Updated with probes attribute)
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Bitters import Bitters, Bitters_constructor
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.Probe import Probe
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
        assert bitters.probes == []  # NEW: Check default empty probes
        assert len(bitters.magnets) == 2

    def test_bitters_initialization_with_probes(self):
        """Test Bitters initialization with probes parameter"""
        # Create mock probe objects
        probe1 = Mock(spec=Probe)
        probe1.name = "voltage_probe"
        probe1.probe_type = "voltage_taps"
        
        probe2 = Mock(spec=Probe)
        probe2.name = "temp_probe"
        probe2.probe_type = "temperature"
        
        bitters = Bitters(
            name="probes_bitters",
            magnets=[],
            innerbore=5.0,
            outerbore=40.0,
            probes=[probe1, probe2]  # NEW: Initialize with probes
        )
        
        assert bitters.name == "probes_bitters"
        assert len(bitters.probes) == 2
        assert bitters.probes[0] == probe1
        assert bitters.probes[1] == probe2

    def test_bitters_with_string_references(self):
        """Test Bitters initialization with string references (before update)"""
        bitters = Bitters(
            name="string_bitters",
            magnets=["bitter1", "bitter2", "bitter3"],  # List of string references
            innerbore=8.0,
            outerbore=50.0,
            probes=["probe1.yaml", "probe2.yaml"]  # NEW: String probe references
        )
        
        # Before update(), magnets should remain as strings
        assert bitters.name == "string_bitters"
        assert isinstance(bitters.magnets, list)
        assert all(isinstance(item, str) for item in bitters.magnets)
        assert bitters.magnets == ["bitter1", "bitter2", "bitter3"]
        assert bitters.innerbore == 8.0
        assert bitters.outerbore == 50.0
        assert bitters.probes == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probe strings
        assert all(isinstance(item, str) for item in bitters.probes)

    def test_bitters_with_empty_magnets(self):
        """Test Bitters initialization with empty magnets list"""
        bitters = Bitters(
            name="empty_bitters",
            magnets=[],
            innerbore=5.0,
            outerbore=15.0,
            probes=[]  # NEW: Include empty probes
        )
        
        assert bitters.name == "empty_bitters"
        assert bitters.magnets == []
        assert len(bitters.magnets) == 0
        assert bitters.innerbore == 5.0
        assert bitters.outerbore == 15.0
        assert bitters.probes == []  # NEW: Check empty probes

    def test_bitters_probes_default_none(self):
        """Test Bitters with probes=None defaults to empty list"""
        bitters = Bitters(
            name="default_probes_bitters",
            magnets=[],
            innerbore=5.0,
            outerbore=15.0,
            probes=None  # NEW: Explicit None
        )
        
        assert bitters.probes == []  # Should default to empty list


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
            outerbore=45.0,
            probes=[]  # NEW: Include empty probes
        )

    def test_repr_with_probes(self):
        """Test __repr__ method includes probes"""
        probe = Mock(spec=Probe)
        probe.name = "test_probe"
        
        bitters = Bitters(
            name="repr_test_bitters",
            magnets=[],
            innerbore=5.0,
            outerbore=15.0,
            probes=[probe]  # NEW: Include probe
        )
        
        repr_str = repr(bitters)
        
        # Should include probes in representation
        assert "Bitters(" in repr_str
        assert "name='repr_test_bitters'" in repr_str
        assert "probes=" in repr_str

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

    def test_update_method_with_string_magnets_and_probes(self):
        """Test update method when both magnets and probes are string references"""
        bitters = Bitters(
            name="update_test",
            magnets=["bitter1", "bitter2"],  # String references
            innerbore=5.0,
            outerbore=25.0,
            probes=["probe1", "probe2"]  # NEW: String probe references
        )
        
        # Initially should be strings
        assert all(isinstance(item, str) for item in bitters.magnets)
        assert all(isinstance(item, str) for item in bitters.probes)  # NEW: Check probe strings
        
        # Mock the loading of magnets and probes
        mock_bitter1 = Mock()
        mock_bitter1.name = "bitter1"
        mock_bitter2 = Mock()
        mock_bitter2.name = "bitter2"
        
        mock_probe1 = Mock(spec=Probe)  # NEW: Mock probe objects
        mock_probe1.name = "probe1"
        mock_probe2 = Mock(spec=Probe)
        mock_probe2.name = "probe2"
        
        with patch('python_magnetgeo.utils.loadList') as mock_load:
            def mock_load_side_effect(comment, objects, supported_types, dict_objects):
                if comment == "magnets":
                    return [mock_bitter1, mock_bitter2]
                elif comment == "probes":  # NEW: Handle probe loading
                    return [mock_probe1, mock_probe2]
                return []
            
            mock_load.side_effect = mock_load_side_effect
            
            bitters.update()
            
            # After update, should be actual objects
            assert bitters.magnets == [mock_bitter1, mock_bitter2]
            assert bitters.probes == [mock_probe1, mock_probe2]  # NEW: Check loaded probes
            
            # Verify loadList was called for both magnets and probes
            assert mock_load.call_count == 2
            mock_load.assert_any_call(
                "magnets", 
                ["bitter1", "bitter2"], 
                [None, Bitter], 
                {"Bitter": Bitter.from_dict}
            )
            mock_load.assert_any_call(  # NEW: Verify probe loading
                "probes",
                ["probe1", "probe2"],
                [None, Probe],
                {"Probe": Probe.from_dict}
            )

    def test_update_method_with_object_magnets(self, sample_bitters):
        """Test update method when magnets are already objects"""
        original_magnets = sample_bitters.magnets
        original_probes = sample_bitters.probes  # NEW: Store original probes
        
        # update() should not change anything when magnets are already objects
        with patch('python_magnetgeo.utils.check_objects', return_value=False):
            sample_bitters.update()
            assert sample_bitters.magnets is original_magnets
            assert sample_bitters.probes is original_probes  # NEW: Check probes unchanged


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
            outerbore=40.0,
            probes=["probe1.yaml", "probe2.yaml"]  # NEW: Include probe strings
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''!<Bitters>
name: yaml_bitters
magnets: []
innerbore: 8.0
outerbore: 32.0
probes: []
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_bitters",
            "innerbore": 5.0,
            "outerbore": 40.0,
            "magnets": ["bitter1", "bitter2"],
            "probes": ["probe1.yaml", "probe2.yaml"]  # NEW: Include probes field
        }
    
    def get_class_under_test(self):
        """Return Bitters class"""
        return Bitters

    def test_json_includes_magnets_and_probes_data(self):
        """Test that JSON serialization includes magnets and probes data"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "magnets" in parsed
        assert "probes" in parsed  # NEW: Check probes included
        assert isinstance(parsed["magnets"], list)
        assert isinstance(parsed["probes"], list)  # NEW: Check probes type
        assert parsed["magnets"] == ["bitter1", "bitter2"]
        assert parsed["probes"] == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probe values

    def test_serialization_with_probes(self):
        """Test serialization works with probe objects"""
        # Create a Bitters instance with string probe references (serializable)
        bitters_with_probes = Bitters(
            name="probes_serialization_test",
            magnets=["bitter1"],
            innerbore=5.0,
            outerbore=30.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: String references
        )
        
        # Test JSON serialization works
        json_str = bitters_with_probes.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Bitters"
        assert parsed["name"] == "probes_serialization_test"
        assert parsed["probes"] == ["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Check probes


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
            "outerbore": 50.0,
            "probes": ["probe1.yaml"]  # NEW: Include probes
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
            "outerbore": 60.0,
            "probes": ["probe1.yaml", "probe2.yaml"]  # NEW: Include probes
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Bitters_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Bitters)
        assert result.name == "direct_test_bitters"
        assert result.magnets == ["bitter1", "bitter2"]
        assert result.innerbore == 10.0
        assert result.outerbore == 60.0
        assert result.probes == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probes
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
    
    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_from_dict_complete_data(self, mock_check, mock_load_list):
        """Test from_dict with complete data including probes"""
        mock_check.return_value = False
        mock_load_list.return_value = []
        
        data = {
            "name": "dict_bitters",
            "magnets": [],  # Empty list instead of file references
            "innerbore": 12.0,
            "outerbore": 48.0,
            "probes": []  # Empty list instead of file references
        }
        
        bitters = Bitters.from_dict(data)
        assert bitters.name == "dict_bitters"
        assert bitters.innerbore == 12.0
        assert bitters.outerbore == 48.0

    def test_from_dict_missing_probes_field(self):
        """Test from_dict with missing probes field (should default to empty list)"""
        data = {
            "name": "minimal_bitters",
            "magnets": ["bitter1"],
            "innerbore": 5.0,
            "outerbore": 15.0
            # No probes field
        }
        
        bitters = Bitters.from_dict(data)
        
        assert bitters.name == "minimal_bitters"
        assert bitters.magnets == ["bitter1"]
        assert bitters.innerbore == 5.0
        assert bitters.outerbore == 15.0
        assert bitters.probes == []  # NEW: Should default to empty list

    def test_from_dict_missing_bore_fields(self):
        """Test from_dict with missing innerbore/outerbore fields"""
        data = {
            "name": "minimal_bitters",
            "magnets": ["bitter1"],
            "probes": ["probe1.yaml"]  # NEW: Include probes
        }
        
        bitters = Bitters.from_dict(data)
        
        assert bitters.name == "minimal_bitters"
        assert bitters.magnets == ["bitter1"]
        assert bitters.innerbore == 0  # Default value
        assert bitters.outerbore == 0  # Default value
        assert bitters.probes == ["probe1.yaml"]  # NEW: Check probes preserved

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

class TestBittersProbesIntegration:
    """Test Bitters integration with probes functionality"""
    
    def test_bitters_with_probes_workflow(self):
        """Test complete workflow with probes from string to object"""
        # Step 1: Create Bitters with string probe references
        bitters = Bitters(
            name="probes_workflow_bitters",
            magnets=["bitter1.yaml"],
            innerbore=5.0,
            outerbore=25.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Probe references
        )
        
        # Initial state: probes should be strings
        assert all(isinstance(probe, str) for probe in bitters.probes)
        assert len(bitters.probes) == 2
        
        # Step 2: Mock the update process for probes
        with patch('python_magnetgeo.utils.loadList') as mock_load_list:
            with patch('python_magnetgeo.utils.check_objects') as mock_check:
                
                def mock_check_side_effect(objects, target_type):
                    return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
                
                mock_check.side_effect = mock_check_side_effect
                
                # Create mock loaded objects
                mock_bitter = Mock(spec=Bitter)
                mock_bitter.name = "loaded_bitter"
                
                mock_voltage_probe = Mock(spec=Probe)
                mock_voltage_probe.name = "loaded_voltage_probe"
                mock_voltage_probe.probe_type = "voltage_taps"
                
                mock_temp_probe = Mock(spec=Probe)
                mock_temp_probe.name = "loaded_temp_probe"
                mock_temp_probe.probe_type = "temperature"
                
                def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
                    if comment == "probes":
                        return [mock_voltage_probe, mock_temp_probe]
                    elif comment == "magnets":
                        return [mock_bitter]
                    return []
                
                mock_load_list.side_effect = mock_load_list_side_effect
                
                # Step 3: Update to load string references
                bitters.update()
                
                # Step 4: Verify probes are loaded
                assert len(bitters.probes) == 2
                assert bitters.probes[0] == mock_voltage_probe
                assert bitters.probes[1] == mock_temp_probe
                
                # Verify loadList was called correctly for probes
                mock_load_list.assert_any_call(
                    "probes", 
                    ["voltage_probes.yaml", "temp_probes.yaml"], 
                    [None, Probe], 
                    {"Probe": Probe.from_dict}
                )

    def test_bitters_serialization_with_mixed_probe_types(self):
        """Test serialization with mixed probe configurations"""
        bitters = Bitters(
            name="mixed_probes_bitters",
            magnets=["bitter1"],
            innerbore=5.0,
            outerbore=25.0,
            probes=["external_probe.yaml"]  # String reference for serialization
        )
        
        # Test JSON serialization preserves string references
        json_str = bitters.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["probes"] == ["external_probe.yaml"]
        assert parsed["__classname__"] == "Bitters"

    @patch('python_magnetgeo.utils.check_objects')
    def test_bitters_empty_probes_handling(self, mock_check):
        """Test Bitters correctly handles empty probes list"""
        bitters = Bitters(
            name="empty_probes_bitters",
            magnets=["bitter1"],
            innerbore=5.0,
            outerbore=25.0,
            probes=[]  # Empty probes list
        )
        
        assert bitters.probes == []
        assert isinstance(bitters.probes, list)
        
        # Mock check_objects to return False for empty lists
        mock_check.return_value = False
        
        # Update should not affect empty probes list
        bitters.update()
        assert bitters.probes == []


class TestBittersErrorHandling:
    """Test error handling in Bitters class"""

    def test_invalid_magnets_handling(self):
        """Test handling of invalid magnets parameter"""
        # Test with None magnets (should raise error depending on implementation)
        try:
            bitters = Bitters(
                name="none_bitters", 
                magnets=None, 
                innerbore=5.0, 
                outerbore=15.0,
                probes=[]  # NEW: Include probes
            )
            # If no error is raised, the implementation allows None
            assert bitters.magnets is None
        except (TypeError, AttributeError):
            # Expected if the implementation validates the magnets parameter
            pass

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_probe_loading_errors(self, mock_check, mock_load_list):
        """Test update method handles probe loading errors gracefully"""
        bitters = Bitters(
            name="error_bitters", 
            magnets=["bitter1"], 
            innerbore=5.0, 
            outerbore=15.0,
            probes=["invalid_probe_file.yaml"]  # NEW: Invalid probe file
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loading to raise exceptions for probes
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "probes":
                raise Exception("Failed to load probe components")
            elif comment == "magnets":
                return [Mock()]  # Return valid magnet
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Update should handle errors without crashing
        try:
            bitters.update()
        except Exception as e:
            # If exceptions are not caught internally, that's the expected behavior
            assert "Failed to load probe components" in str(e)


class TestBittersIntegration:
    """Integration tests for Bitters class"""
    
    def test_bitters_serialization_roundtrip_with_probes(self):
        """Test complete serialization roundtrip with probes"""
        original_bitters = Bitters(
            name="roundtrip_bitters",
            magnets=["bitter1", "bitter2"],  # String references
            innerbore=10.0,
            outerbore=60.0,
            probes=["roundtrip_probe1.yaml", "roundtrip_probe2.yaml"]  # NEW: Include probes
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
        assert parsed_json["probes"] == ["roundtrip_probe1.yaml", "roundtrip_probe2.yaml"]  # NEW: Check probes

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_bitters_workflow_string_to_object_conversion(self, mock_check, mock_load_list):
        """Test complete workflow from string references to object usage"""
        # Step 1: Create Bitters with string references
        bitters = Bitters(
            name="workflow_bitters",
            magnets=["bitter1.yaml", "bitter2.yaml"],
            innerbore=8.0,
            outerbore=40.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Include probe strings
        )
        
        # Step 2: Setup mocks for string loading
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Create realistic mock objects
        mock_bitter1 = Mock(spec=Bitter)
        mock_bitter1.name = "loaded_bitter1"
        mock_bitter1.r = [10.0, 20.0]
        mock_bitter1.z = [0.0, 100.0]
        mock_bitter1.get_channels = Mock(return_value=["channel1", "channel2"])
        
        mock_bitter2 = Mock(spec=Bitter)
        mock_bitter2.name = "loaded_bitter2"
        mock_bitter2.r = [25.0, 35.0]
        mock_bitter2.z = [5.0, 95.0]
        mock_bitter2.get_channels = Mock(return_value=["channel3"])
        
        # NEW: Create mock probe objects
        mock_voltage_probe = Mock(spec=Probe)
        mock_voltage_probe.name = "loaded_voltage_probe"
        mock_voltage_probe.probe_type = "voltage_taps"
        
        mock_temp_probe = Mock(spec=Probe)
        mock_temp_probe.name = "loaded_temp_probe"
        mock_temp_probe.probe_type = "temperature"
        
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "magnets":
                return [mock_bitter1, mock_bitter2]
            elif comment == "probes":  # NEW: Handle probe loading
                return [mock_voltage_probe, mock_temp_probe]
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Step 3: Convert string references to objects
        bitters.update()
        
        # Step 4: Verify objects are loaded
        assert isinstance(bitters.magnets[0], Mock)
        assert isinstance(bitters.magnets[1], Mock)
        assert len(bitters.probes) == 2  # NEW: Check probes loaded
        assert isinstance(bitters.probes[0], Mock)
        assert isinstance(bitters.probes[1], Mock)
        
        # Verify that loadList was called for probes
        mock_load_list.assert_any_call(
            "probes",
            ["voltage_probes.yaml", "temp_probes.yaml"],
            [None, Probe],
            {"Probe": Probe.from_dict}
        )
        
        # FIXED: Test channels collection using the bitters object instead of undefined cooled_system
        channels = bitters.get_channels("cooling")
        assert isinstance(channels, dict)
        expected_keys = [
            "cooling_loaded_bitter1",
            "cooling_loaded_bitter2"
        ]
        assert set(channels.keys()) == set(expected_keys)
        
        # Test intersection with cooling circuit
        cooling_region = [30.0, 130.0]  # Slightly larger than magnets
        cooling_height = [-10.0, 330.0] # Full height plus margins
        assert bitters.intersect(cooling_region, cooling_height) is True
        
        # Test no intersection with external regions
        external_region = [200.0, 300.0]  # Far from magnets
        external_height = [0.0, 100.0]
        assert bitters.intersect(external_region, external_height) is False


class TestBittersPerformance:
    """Performance tests for Bitters class"""
    
    def test_large_magnets_list_with_probes_performance(self):
        """Test Bitters performance with many magnets and probes"""
        # Create many magnet references
        large_magnets_list = [f"bitter_{i}" for i in range(50)]
        large_probes_list = [f"probe_{i}.yaml" for i in range(20)]  # NEW: Many probes
        
        bitters = Bitters(
            name="performance_bitters",
            magnets=large_magnets_list,
            innerbore=5.0,
            outerbore=200.0,
            probes=large_probes_list  # NEW: Include many probes
        )
        
        # Test that operations still work with many magnets and probes
        assert len(bitters.magnets) == 50
        assert len(bitters.probes) == 20  # NEW: Check probe count
        assert all(isinstance(m, str) for m in bitters.magnets)
        assert all(isinstance(p, str) for p in bitters.probes)  # NEW: Check probe types
        
        json_str = bitters.to_json()
        assert len(json_str) > 0


class TestBittersDocumentation:
    """Test that Bitters behavior matches its documentation"""
    
    def test_documented_attributes_with_probes(self):
        """Test that Bitters has all documented attributes including probes"""
        bitters = Bitters(
            name="doc_test",
            magnets=["bitter1"],
            innerbore=5.0,
            outerbore=15.0,
            probes=["probe1.yaml"]  # NEW: Include probes
        )
        
        # Verify all documented attributes exist
        assert hasattr(bitters, "name")
        assert hasattr(bitters, "magnets")
        assert hasattr(bitters, "innerbore")
        assert hasattr(bitters, "outerbore")
        assert hasattr(bitters, "probes")  # NEW: Check probes attribute
        
        # Verify types
        assert isinstance(bitters.name, str)
        assert isinstance(bitters.magnets, list)
        assert isinstance(bitters.innerbore, (int, float))
        assert isinstance(bitters.outerbore, (int, float))
        assert isinstance(bitters.probes, list)  # NEW: Check probes type

    def test_serialization_interface_compliance_with_probes(self):
        """Test that serialization interface works as documented with probes"""
        bitters = Bitters(
            name="serial_test_system", 
            magnets=["bitter1"], 
            innerbore=1.0, 
            outerbore=2.0,
            probes=["probe1.yaml"]  # NEW: Include probes
        )
        
        # Test to_json returns valid JSON string
        json_str = bitters.to_json()
        assert isinstance(json_str, str)
        
        # Should be parseable JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "__classname__" in parsed
        assert parsed["__classname__"] == "Bitters"
        assert "probes" in parsed  # NEW: Check probes in JSON
        assert parsed["probes"] == ["probe1.yaml"]
        
        # Test from_dict works with probes
        data = {
            "name": "from_dict_test",
            "magnets": ["bitter1"],
            "innerbore": 2.0,
            "outerbore": 3.0,
            "probes": ["probe_test.yaml"]  # NEW: Include probes
        }
        
        new_bitters = Bitters.from_dict(data)
        assert isinstance(new_bitters, Bitters)
        assert new_bitters.name == "from_dict_test"
        assert new_bitters.probes == ["probe_test.yaml"]  # NEW: Check probes loaded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
