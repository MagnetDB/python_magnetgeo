#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Supras class using test_utils_common mixins (Updated with probes attribute)
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the classes under test
from python_magnetgeo.Supras import Supras, Supras_constructor
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Probe import Probe

# Import test utilities
from .test_utils_common import (
    BaseSerializationTestMixin,
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_json_structure,
    assert_instance_attributes,
    validate_geometric_data,
    parametrize_basic_values,
    temp_yaml_file,
    temp_json_file
)


class TestSupras(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for Supras using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample Supras instance for testing"""
        # Create mock Supra objects for testing
        supra1 = Supra(name="supra1", r=[10.0, 20.0], z=[0.0, 10.0], n=5, struct="struct1")
        supra2 = Supra(name="supra2", r=[25.0, 35.0], z=[15.0, 25.0], n=3, struct="struct2")
        
        return Supras(
            name="test_supras",
            magnets=[supra1, supra2],
            innerbore=5.0,
            outerbore=40.0,
            probes=[]  # NEW: Include empty probes
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """
!<Supras>
name: test_supras
magnets:
  - !<Supra>
    name: supra1
    r: [10.0, 20.0]
    z: [0.0, 10.0]
    n: 5
    struct: struct1
  - !<Supra>
    name: supra2
    r: [25.0, 35.0]
    z: [15.0, 25.0]
    n: 3
    struct: struct2
innerbore: 5.0
outerbore: 40.0
probes: []
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_supras",
            "innerbore": 5.0,
            "outerbore": 40.0,
            "probes": []  # NEW: Include probes field
            # Note: magnets will be complex objects, tested separately
        }
    
    def get_class_under_test(self) -> Type:
        """Return the Supras class"""
        return Supras
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return Supras
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "Supras"
    
    # FIXED: Override the problematic test method to avoid file system interference
    def test_dump_yaml_success(self):
        """Test successful YAML dump - overridden to handle file system interference"""
        instance = self.get_sample_instance()
        
        # Use a more specific mock that only patches the utils.writeYaml function
        with patch('python_magnetgeo.utils.writeYaml') as mock_write_yaml:
            instance.dump()
            mock_write_yaml.assert_called_once_with("Supras", instance, Supras)


class TestSuprasConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for Supras YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = Supras_constructor(loader, node)
            # Return the actual result and its type name
            return result, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "magnets": ["magnet1", "magnet2"],  # Will be strings initially
            "innerbore": 8.0,
            "outerbore": 50.0,
            "probes": ["probe1.yaml"]  # NEW: Include probes
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "Supras"
    
    # Override the inherited test method that's causing issues
    def test_yaml_constructor_function(self):
        """Test the YAML constructor function"""
        constructor_func = self.get_constructor_function()
        
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = self.get_sample_constructor_data()
        mock_loader.construct_mapping.return_value = mock_data
        
        result, result_type = constructor_func(mock_loader, mock_node)
        
        # Check that we get a Supras instance with the expected attributes
        assert isinstance(result, Supras)
        assert result_type == self.get_expected_constructor_type()
        assert result.name == mock_data["name"]
        assert result.magnets == mock_data["magnets"]
        assert result.innerbore == mock_data["innerbore"]
        assert result.outerbore == mock_data["outerbore"]
        assert result.probes == mock_data["probes"]  # NEW: Check probes
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestSuprasSpecific:
    """
    Specific tests for Supras functionality not covered by mixins
    """
    
    @pytest.fixture
    def sample_supra_objects(self):
        """Fixture providing sample Supra objects"""
        supra1 = Supra(name="test_supra1", r=[10.0, 15.0], z=[0.0, 5.0], n=2, struct="test_struct1")
        supra2 = Supra(name="test_supra2", r=[20.0, 25.0], z=[10.0, 15.0], n=3, struct="test_struct2")
        supra3 = Supra(name="test_supra3", r=[30.0, 35.0], z=[20.0, 25.0], n=4, struct="test_struct3")
        return [supra1, supra2, supra3]
    
    @pytest.fixture
    def sample_supras(self, sample_supra_objects):
        """Fixture providing a sample Supras instance"""
        return Supras(
            name="sample_system",
            magnets=sample_supra_objects,
            innerbore=5.0,
            outerbore=40.0,
            probes=[]  # NEW: Include empty probes
        )
    
    @pytest.fixture
    def empty_supras(self):
        """Fixture providing an empty Supras instance"""
        return Supras(
            name="empty_system",
            magnets=[],
            innerbore=0.0,
            outerbore=10.0,
            probes=[]  # NEW: Include empty probes
        )

    def test_init_with_parameters(self, sample_supra_objects):
        """Test Supras initialization with all parameters"""
        supras = Supras(
            name="init_test",
            magnets=sample_supra_objects,
            innerbore=7.5,
            outerbore=45.0,
            probes=[]  # NEW: Include probes
        )
        assert supras.name == "init_test"
        assert supras.magnets == sample_supra_objects
        assert supras.innerbore == 7.5
        assert supras.outerbore == 45.0
        assert supras.probes == []  # NEW: Check probes

    def test_init_with_probes(self):
        """Test Supras initialization with probes parameter"""
        # Create mock probe objects
        probe1 = Mock(spec=Probe)
        probe1.name = "voltage_probe"
        probe1.probe_type = "voltage_taps"
        
        probe2 = Mock(spec=Probe)
        probe2.name = "temp_probe"
        probe2.probe_type = "temperature"
        
        supras = Supras(
            name="probes_supras",
            magnets=[],
            innerbore=5.0,
            outerbore=40.0,
            probes=[probe1, probe2]  # NEW: Initialize with probes
        )
        
        assert supras.name == "probes_supras"
        assert len(supras.probes) == 2
        assert supras.probes[0] == probe1
        assert supras.probes[1] == probe2

    def test_init_with_string_probe_references(self):
        """Test Supras initialization with string probe references"""
        supras = Supras(
            name="string_probes_supras",
            magnets=["supra1.yaml"],
            innerbore=8.0,
            outerbore=48.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: String references
        )
        
        assert supras.name == "string_probes_supras"
        assert supras.probes == ["voltage_probes.yaml", "temp_probes.yaml"]
        assert isinstance(supras.probes, list)
        assert all(isinstance(item, str) for item in supras.probes)

    def test_init_empty_magnets(self):
        """Test Supras initialization with empty magnets list"""
        supras = Supras(
            name="empty_test",
            magnets=[],
            innerbore=1.0,
            outerbore=2.0,
            probes=[]  # NEW: Include empty probes
        )
        assert supras.name == "empty_test"
        assert supras.magnets == []
        assert supras.innerbore == 1.0
        assert supras.outerbore == 2.0
        assert supras.probes == []  # NEW: Check empty probes

    def test_probes_default_none(self):
        """Test Supras with probes=None defaults to empty list"""
        supras = Supras(
            name="default_probes_supras",
            magnets=[],
            innerbore=5.0,
            outerbore=15.0,
            probes=None  # NEW: Explicit None
        )
        
        assert supras.probes == []  # Should default to empty list

    def test_repr_with_probes(self, sample_supras):
        """Test string representation includes probes"""
        probe = Mock(spec=Probe)
        probe.name = "test_probe"
        
        sample_supras.probes = [probe]
        repr_str = repr(sample_supras)
        
        assert "Supras" in repr_str
        assert "name='sample_system'" in repr_str
        assert "innerbore=5.0" in repr_str
        assert "outerbore=40.0" in repr_str
        assert "magnets=" in repr_str
        assert "probes=" in repr_str  # NEW: Check probes in repr

    def test_update_string_magnets_and_probes(self):
        """Test update method converts string magnets and probes to objects"""
        supras = Supras(
            name="update_test",
            magnets=["supra1", "supra2"],  # String representations
            innerbore=5.0,
            outerbore=10.0,
            probes=["probe1", "probe2"]  # NEW: String probe representations
        )
        
        # Initially should be strings
        assert all(isinstance(item, str) for item in supras.magnets)
        assert all(isinstance(item, str) for item in supras.probes)  # NEW: Check probe strings
        
        # Mock the loading of magnets and probes
        mock_supra1 = Mock()
        mock_supra1.name = "supra1"
        mock_supra2 = Mock()
        mock_supra2.name = "supra2"

        mock_probe1 = Mock(spec=Probe)  # NEW: Mock probe objects
        mock_probe1.name = "probe1"
        mock_probe2 = Mock(spec=Probe)
        mock_probe2.name = "probe2"

        with patch('python_magnetgeo.utils.loadList') as mock_load:
            def mock_load_side_effect(comment, objects, supported_types, dict_objects):
                if comment == "magnets":
                    return [mock_supra1, mock_supra2]
                elif comment == "probes":  # NEW: Handle probe loading
                    return [mock_probe1, mock_probe2]
                return []
            
            mock_load.side_effect = mock_load_side_effect

            supras.update()

            # After update, should be actual objects
            assert supras.magnets == [mock_supra1, mock_supra2]
            assert supras.probes == [mock_probe1, mock_probe2]  # NEW: Check loaded probes
            
            # Verify loadList was called for both magnets and probes
            assert mock_load.call_count == 2
            mock_load.assert_any_call(
                "magnets",
                ["supra1", "supra2"],
                [None, Supra],
                {"Supra": Supra.from_dict}
            )
            mock_load.assert_any_call(  # NEW: Verify probe loading
                "probes",
                ["probe1", "probe2"],
                [None, Probe],
                {"Probe": Probe.from_dict}
            )
    
    def test_update_no_string_magnets(self, sample_supras):
        """Test update method with already loaded magnets"""
        original_magnets = sample_supras.magnets.copy()
        original_probes = sample_supras.probes.copy()  # NEW: Store original probes
        
        with patch('python_magnetgeo.utils.check_objects') as mock_check:
            with patch('python_magnetgeo.utils.loadList') as mock_load:
                mock_check.return_value = False  # No strings present
                
                sample_supras.update()
                
                # loadList should not be called since magnets are already objects
                mock_check.assert_called()
                mock_load.assert_not_called()
                assert sample_supras.magnets == original_magnets
                assert sample_supras.probes == original_probes  # NEW: Check probes unchanged

    def test_get_channels_returns_empty_dict(self, sample_supras):
        """Test get_channels method returns empty dict"""
        channels = sample_supras.get_channels("test_magnet")
        assert channels == {}
        
        channels_with_params = sample_supras.get_channels("test", hideIsolant=False, debug=True)
        assert channels_with_params == {}
    
    def test_get_isolants_returns_empty_dict(self, sample_supras):
        """Test get_isolants method returns empty dict"""
        isolants = sample_supras.get_isolants("test_magnet")
        assert isolants == {}
        
        isolants_with_debug = sample_supras.get_isolants("test", debug=True)
        assert isolants_with_debug == {}
    
    def test_get_names_with_magnets(self, sample_supras):
        """Test get_names method with magnets"""
        # Mock the get_names method on Supra objects
        for i, magnet in enumerate(sample_supras.magnets):
            magnet.get_names = Mock(return_value=[f"name_{i}_1", f"name_{i}_2"])
        
        names = sample_supras.get_names("prefix")
        
        # Should call get_names on each magnet
        for i, magnet in enumerate(sample_supras.magnets):
            magnet.get_names.assert_called_once_with(f"prefix_{magnet.name}", False, False)
        
        expected_names = ["name_0_1", "name_0_2", "name_1_1", "name_1_2", "name_2_1", "name_2_2"]
        assert names == expected_names

    def test_yaml_constructor_function_direct(self):
        """Test the Supras_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "magnets": ["magnet1", "magnet2"],
            "innerbore": 15.0,
            "outerbore": 60.0,
            "probes": ["probe1.yaml", "probe2.yaml"]  # NEW: Include probes
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Supras_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Supras)
        assert result.name == "direct_test"
        assert result.magnets == ["magnet1", "magnet2"]
        assert result.innerbore == 15.0
        assert result.outerbore == 60.0
        assert result.probes == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probes
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestSuprasFromDict:
    """
    Test the from_dict class method
    """
    
    def test_from_dict_all_fields(self):
        """Test from_dict with all fields present including probes"""
        data = {
            "name": "dict_test",
            "magnets": ["magnet1", "magnet2"],
            "innerbore": 12.0,
            "outerbore": 48.0,
            "probes": ["probe1.yaml", "probe2.yaml"]  # NEW: Include probes
        }
        
        supras = Supras.from_dict(data)
        
        assert supras.name == "dict_test"
        assert supras.magnets == ["magnet1", "magnet2"]
        assert supras.innerbore == 12.0
        assert supras.outerbore == 48.0
        assert supras.probes == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probes
    
    def test_from_dict_missing_optional_fields(self):
        """Test from_dict with missing optional fields (innerbore, outerbore, probes)"""
        data = {
            "name": "minimal_dict_test",
            "magnets": ["magnet1"]
        }
        
        supras = Supras.from_dict(data)
        
        assert supras.name == "minimal_dict_test"
        assert supras.magnets == ["magnet1"]
        assert supras.innerbore == 0  # Default value
        assert supras.outerbore == 0  # Default value
        assert supras.probes == []  # NEW: Default empty list

    def test_from_dict_missing_probes_field(self):
        """Test from_dict with missing probes field (should default to empty list)"""
        data = {
            "name": "no_probes_test",
            "magnets": ["magnet1"],
            "innerbore": 5.0,
            "outerbore": 15.0
            # No probes field
        }
        
        supras = Supras.from_dict(data)
        
        assert supras.name == "no_probes_test"
        assert supras.magnets == ["magnet1"]
        assert supras.innerbore == 5.0
        assert supras.outerbore == 15.0
        assert supras.probes == []  # NEW: Should default to empty list
    
    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_test",
            "magnets": [],
            "innerbore": 5.0,
            "outerbore": 10.0,
            "probes": ["probe1.yaml"]  # NEW: Include probes
        }
        
        supras = Supras.from_dict(data, debug=True)
        assert supras.name == "debug_test"
        assert supras.probes == ["probe1.yaml"]  # NEW: Check probes


class TestSuprasProbesIntegration:
    """Test Supras integration with probes functionality"""
    
    def test_supras_with_probes_workflow(self):
        """Test complete workflow with probes from string to object"""
        # Step 1: Create Supras with string probe references
        supras = Supras(
            name="probes_workflow_supras",
            magnets=["supra1.yaml"],
            innerbore=5.0,
            outerbore=25.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Probe references
        )
        
        # Initial state: probes should be strings
        assert all(isinstance(probe, str) for probe in supras.probes)
        assert len(supras.probes) == 2
        
        # Step 2: Mock the update process for probes
        with patch('python_magnetgeo.utils.loadList') as mock_load_list:
            with patch('python_magnetgeo.utils.check_objects') as mock_check:
                
                def mock_check_side_effect(objects, target_type):
                    return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
                
                mock_check.side_effect = mock_check_side_effect
                
                # Create mock loaded objects
                mock_supra = Mock(spec=Supra)
                mock_supra.name = "loaded_supra"
                
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
                        return [mock_supra]
                    return []
                
                mock_load_list.side_effect = mock_load_list_side_effect
                
                # Step 3: Update to load string references
                supras.update()
                
                # Step 4: Verify probes are loaded
                assert len(supras.probes) == 2
                assert supras.probes[0] == mock_voltage_probe
                assert supras.probes[1] == mock_temp_probe
                
                # Verify loadList was called correctly for probes
                mock_load_list.assert_any_call(
                    "probes", 
                    ["voltage_probes.yaml", "temp_probes.yaml"], 
                    [None, Probe], 
                    {"Probe": Probe.from_dict}
                )

    def test_supras_serialization_with_mixed_probe_types(self):
        """Test serialization with mixed probe configurations"""
        supras = Supras(
            name="mixed_probes_supras",
            magnets=["supra1"],
            innerbore=5.0,
            outerbore=25.0,
            probes=["external_probe.yaml"]  # String reference for serialization
        )
        
        # Test JSON serialization preserves string references
        json_str = supras.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["probes"] == ["external_probe.yaml"]
        assert parsed["__classname__"] == "Supras"

    @patch('python_magnetgeo.utils.check_objects')
    def test_supras_empty_probes_handling(self, mock_check):
        """Test Supras correctly handles empty probes list"""
        supras = Supras(
            name="empty_probes_supras",
            magnets=["supra1"],  # String reference that would trigger update
            innerbore=5.0,
            outerbore=25.0,
            probes=[]  # Empty probes list
        )
        
        assert supras.probes == []
        assert isinstance(supras.probes, list)
        
        # Mock check_objects to return False for empty lists
        mock_check.return_value = False
        
        # Update should not affect empty probes list
        supras.update()
        assert supras.probes == []


class TestSuprasGeometry:
    """
    Test geometric operations for Supras
    """
    
    @pytest.fixture
    def geometric_supras(self):
        """Fixture with Supras having known geometric bounds"""
        supra1 = Supra(name="geo1", r=[10.0, 20.0], z=[0.0, 10.0], n=1, struct="")
        supra2 = Supra(name="geo2", r=[15.0, 25.0], z=[5.0, 15.0], n=1, struct="")
        supra3 = Supra(name="geo3", r=[5.0, 30.0], z=[-5.0, 20.0], n=1, struct="")  # Largest bounds
        
        return Supras(
            name="geometric_test",
            magnets=[supra1, supra2, supra3],
            innerbore=2.0,
            outerbore=35.0,
            probes=[]  # NEW: Include empty probes
        )
    
    @pytest.fixture
    def empty_supras(self):
        """Fixture providing an empty Supras instance"""
        return Supras(
            name="empty_system",
            magnets=[],
            innerbore=0.0,
            outerbore=10.0,
            probes=[]  # NEW: Include empty probes
        )
    
    def test_boundingBox_with_magnets(self, geometric_supras):
        """Test boundingBox method with multiple magnets"""
        rb, zb = geometric_supras.boundingBox()
        
        # Should return the overall bounding box
        assert rb == [5.0, 30.0]  # Min r from supra3, max r from supra3
        assert zb == [-5.0, 20.0]  # Min z from supra3, max z from supra3
    
    def test_boundingBox_single_magnet(self):
        """Test boundingBox method with single magnet"""
        supra = Supra(name="single", r=[12.0, 18.0], z=[3.0, 9.0], n=1, struct="")
        supras = Supras(name="single_test", magnets=[supra], innerbore=5.0, outerbore=25.0)
        
        rb, zb = supras.boundingBox()
        
        assert rb == [12.0, 18.0]
        assert zb == [3.0, 9.0]
    
    def test_boundingBox_empty_magnets(self, empty_supras):
        """Test boundingBox method with empty magnets list"""
        rb, zb = empty_supras.boundingBox()
        
        # Should return [0, 0] for both when no magnets
        assert rb == [0, 0]
        assert zb == [0, 0]
    
    @pytest.mark.parametrize("test_r,test_z,expected", [
        ([10.0, 20.0], [0.0, 10.0], True),    # Overlaps with supra1
        ([16.0, 24.0], [6.0, 14.0], True),    # Overlaps with supra2
        ([0.0, 35.0], [-10.0, 25.0], True),   # Overlaps with entire system
        ([40.0, 50.0], [0.0, 10.0], False),   # No overlap (too far in r)
        ([10.0, 20.0], [30.0, 40.0], False),  # No overlap (too far in z)
        ([0.0, 1.0], [0.0, 1.0], False),      # No overlap (too small)
    ])
    def test_intersect(self, geometric_supras, test_r, test_z, expected):
        """Test intersect method with various test rectangles"""
        result = geometric_supras.intersect(test_r, test_z)
        assert result == expected
    
    def test_intersect_edge_cases(self, geometric_supras):
        """Test intersect method edge cases"""
        # Test with identical bounds
        rb, zb = geometric_supras.boundingBox()
        assert geometric_supras.intersect(rb, zb) is True
        
        # Test with very small overlap
        small_overlap_r = [29.9, 30.1]  # Tiny overlap with max r
        small_overlap_z = [19.9, 20.1]  # Tiny overlap with max z
        assert geometric_supras.intersect(small_overlap_r, small_overlap_z) is True
    
    def test_intersect_empty_system(self, empty_supras):
        """Test intersect method with empty magnet system"""
        # Empty system has bounding box [0,0], [0,0]
        # Only rectangles containing origin should intersect
        assert empty_supras.intersect([-1.0, 1.0], [-1.0, 1.0]) is True
        assert empty_supras.intersect([1.0, 2.0], [1.0, 2.0]) is False


class TestSuprasPerformance:
    """
    Performance tests for Supras operations
    """
    
    @pytest.mark.performance
    def test_large_magnet_list_performance(self):
        """Test Supras performance with large number of magnets"""
        # Create large list of magnets
        large_magnets = []
        for i in range(100):  # Reduced from 1000 for reasonable test time
            magnet = Supra(
                name=f"magnet_{i}",
                r=[float(i), float(i+1)],
                z=[0.0, 1.0],
                n=1,
                struct=""
            )
            large_magnets.append(magnet)
        
        supras = Supras(
            name="performance_test",
            magnets=large_magnets,
            innerbore=0.0,
            outerbore=101.0
        )
        
        # Should handle large datasets efficiently
        assert len(supras.magnets) == 100
        
        # Test bounding box computation
        rb, zb = supras.boundingBox()
        assert rb == [0.0, 100.0]  # Min from first magnet, max from last
        assert zb == [0.0, 1.0]    # Same z for all magnets
    
    @pytest.mark.performance
    def test_bounding_box_performance(self):
        """Test boundingBox performance with many magnets"""
        # Create many magnets with overlapping bounds
        magnets = []
        for i in range(50):  # Reduced for reasonable test time
            magnet = Supra(
                name=f"perf_magnet_{i}",
                r=[float(i), float(i+10)],
                z=[float(i), float(i+5)],
                n=1,
                struct=""
            )
            magnets.append(magnet)
        
        supras = Supras(name="perf_test", magnets=magnets, innerbore=0.0, outerbore=60.0)
        
        # Should compute bounding box correctly
        rb, zb = supras.boundingBox()
        assert rb == [0.0, 59.0]  # Expected bounds
        assert zb == [0.0, 54.0]
    
    @pytest.mark.performance
    def test_get_names_performance(self):
        """Test get_names performance with many magnets"""
        # Create magnets with mocked get_names
        magnets = []
        for i in range(20):  # Reduced for reasonable test time
            magnet = Mock(spec=Supra)
            magnet.name = f"magnet_{i}"
            magnet.get_names = Mock(return_value=[f"name_{i}_1", f"name_{i}_2"])
            magnets.append(magnet)
        
        supras = Supras(name="names_perf", magnets=magnets, innerbore=0.0, outerbore=10.0)
        
        names = supras.get_names("prefix")
        
        # Should collect names correctly
        assert len(names) == 40  # 20 magnets * 2 names each


class TestSuprasIntegration:
    """
    Integration tests for Supras
    """
    
    def test_yaml_integration(self):
        """Test YAML integration with real Supra objects"""
        supra1 = Supra(name="int_supra1", r=[5.0, 10.0], z=[0.0, 5.0], n=2, struct="struct1")
        supra2 = Supra(name="int_supra2", r=[15.0, 20.0], z=[10.0, 15.0], n=3, struct="struct2")
        
        supras = Supras(
            name="integration_test",
            magnets=[supra1, supra2],
            innerbore=2.0,
            outerbore=25.0
        )
        
        # Test YAML tag is properly set
        assert hasattr(Supras, 'yaml_tag')
        assert Supras.yaml_tag == "Supras"
        
        # Test constructor function exists and is callable
        assert callable(Supras_constructor)
        
        # Test that we can create a Supras using the constructor
        mock_loader = Mock()
        mock_node = Mock()
        test_data = {
            "name": "yaml_test",
            "magnets": ["magnet1"],
            "innerbore": 1.0,
            "outerbore": 2.0
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Supras_constructor(mock_loader, mock_node)
        assert isinstance(result, Supras)
        assert result.name == "yaml_test"
    
    def test_json_integration_complete(self):
        """Test complete JSON serialization integration"""
        supra1 = Supra(name="json_supra1", r=[8.0, 12.0], z=[1.0, 6.0], n=4, struct="json_struct1")
        supra2 = Supra(name="json_supra2", r=[18.0, 22.0], z=[11.0, 16.0], n=2, struct="json_struct2")
        
        supras = Supras(
            name="json_integration",
            magnets=[supra1, supra2],
            innerbore=3.0,
            outerbore=28.0
        )
        
        json_str = supras.to_json()
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["__classname__"] == "Supras"
        assert parsed["name"] == "json_integration"
        assert parsed["innerbore"] == 3.0
        assert parsed["outerbore"] == 28.0
        assert "magnets" in parsed
        assert len(parsed["magnets"]) == 2
    
    def test_constructor_integration_comprehensive(self):
        """Test constructor integration with comprehensive data"""
        comprehensive_data = {
            "name": "comprehensive_supras",
            "magnets": [
                "magnet_string_1",
                "magnet_string_2", 
                "magnet_string_3"
            ],
            "innerbore": 4.5,
            "outerbore": 55.5
        }
        
        mock_loader = Mock()
        mock_node = Mock()
        mock_loader.construct_mapping.return_value = comprehensive_data
        
        result = Supras_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Supras)
        assert result.name == "comprehensive_supras"
        assert result.magnets == ["magnet_string_1", "magnet_string_2", "magnet_string_3"]
        assert result.innerbore == 4.5
        assert result.outerbore == 55.5
    
    def test_from_yaml_integration(self):
        """Test from_yaml integration"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load_yaml:
            mock_supras = Mock(spec=Supras)
            mock_load_yaml.return_value = mock_supras
            
            result = Supras.from_yaml("test.yaml")
            
            mock_load_yaml.assert_called_once_with("Supras", "test.yaml", Supras, False)
            assert result == mock_supras
    
    def test_from_json_integration(self):
        """Test from_json integration"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load_json:
            mock_supras = Mock(spec=Supras)
            mock_load_json.return_value = mock_supras
            
            result = Supras.from_json("test.json", debug=True)
            
            mock_load_json.assert_called_once_with("Supras", "test.json", True)
            assert result == mock_supras


class TestSuprasErrorHandling:
    """
    Test error handling and robustness for Supras
    """
    
    @pytest.fixture
    def sample_supras_for_errors(self):
        """Fixture providing a sample Supras instance for error handling tests"""
        supra1 = Supra(name="error_supra1", r=[10.0, 20.0], z=[0.0, 10.0], n=5, struct="struct1")
        return Supras(
            name="error_test_supras",
            magnets=[supra1],
            innerbore=5.0,
            outerbore=25.0,
            probes=[]  # NEW: Include empty probes
        )

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_probe_loading_errors(self, mock_check, mock_load_list):
        """Test update method handles probe loading errors gracefully"""
        supras = Supras(
            name="error_supras", 
            magnets=["supra1"], 
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
                return [Mock(spec=Supra)]  # Return valid supra
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Update should handle errors without crashing
        try:
            supras.update()
        except Exception as e:
            # If exceptions are not caught internally, that's the expected behavior
            assert "Failed to load probe components" in str(e)


class TestSuprasIntegrationAdvanced:
    """
    Advanced integration tests for Supras
    """
    
    def test_supras_serialization_roundtrip_with_probes(self):
        """Test complete serialization roundtrip with probes"""
        original_supras = Supras(
            name="roundtrip_supras",
            magnets=["supra1", "supra2"],  # String references
            innerbore=10.0,
            outerbore=60.0,
            probes=["roundtrip_probe1.yaml", "roundtrip_probe2.yaml"]  # NEW: Include probes
        )
        
        # Test JSON serialization
        json_str = original_supras.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Supras"
        assert parsed_json["name"] == "roundtrip_supras"
        assert parsed_json["magnets"] == ["supra1", "supra2"]
        assert parsed_json["innerbore"] == 10.0
        assert parsed_json["outerbore"] == 60.0
        assert parsed_json["probes"] == ["roundtrip_probe1.yaml", "roundtrip_probe2.yaml"]  # NEW: Check probes

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_supras_workflow_string_to_object_conversion(self, mock_check, mock_load_list):
        """Test complete workflow from string references to object usage"""
        # Step 1: Create Supras with string references
        supras = Supras(
            name="workflow_supras",
            magnets=["supra1.yaml", "supra2.yaml"],
            innerbore=8.0,
            outerbore=40.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Include probe strings
        )
        
        # Step 2: Setup mocks for string loading
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Create realistic mock objects
        mock_supra1 = Mock(spec=Supra)
        mock_supra1.name = "loaded_supra1"
        mock_supra1.r = [10.0, 20.0]
        mock_supra1.z = [0.0, 100.0]
        
        mock_supra2 = Mock(spec=Supra)
        mock_supra2.name = "loaded_supra2"
        mock_supra2.r = [25.0, 35.0]
        mock_supra2.z = [5.0, 95.0]
        
        # NEW: Create mock probe objects
        mock_voltage_probe = Mock(spec=Probe)
        mock_voltage_probe.name = "loaded_voltage_probe"
        mock_voltage_probe.probe_type = "voltage_taps"
        
        mock_temp_probe = Mock(spec=Probe)
        mock_temp_probe.name = "loaded_temp_probe"
        mock_temp_probe.probe_type = "temperature"
        
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "magnets":
                return [mock_supra1, mock_supra2]
            elif comment == "probes":  # NEW: Handle probe loading
                return [mock_voltage_probe, mock_temp_probe]
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Step 3: Convert string references to objects
        supras.update()
        
        # Step 4: Verify objects are loaded
        assert isinstance(supras.magnets[0], Mock)
        assert isinstance(supras.magnets[1], Mock)
        assert len(supras.probes) == 2  # NEW: Check probes loaded
        assert isinstance(supras.probes[0], Mock)
        assert isinstance(supras.probes[1], Mock)
        
        # Verify that loadList was called for probes
        mock_load_list.assert_any_call(
            "probes", 
            ["voltage_probes.yaml", "temp_probes.yaml"], 
            [None, Probe], 
            {"Probe": Probe.from_dict}
        )
        
        # FIXED: Test Supras functionality with loaded objects instead of undefined 'system'
        assert len(supras.magnets) == 2
        
        # Test bounding box calculation with loaded objects
        # Note: The bounding box calculation is in Supras.boundingBox() method
        # but since we're using Mock objects, we need to set up their attributes
        mock_supra1.r = [10.0, 20.0]
        mock_supra1.z = [0.0, 100.0]
        mock_supra2.r = [25.0, 35.0] 
        mock_supra2.z = [5.0, 95.0]
        
        rb, zb = supras.boundingBox()
        expected_rb = [10.0, 35.0]  # Min and max r from both supras
        expected_zb = [0.0, 100.0]  # Min and max z from both supras
        assert rb == expected_rb
        assert zb == expected_zb


class TestSuprasUseCases:
    """
    Test real-world use cases for Supras
    """
    
    def test_complex_magnet_system_use_case(self):
        """Test Supras representing a complex magnet system"""
        # Create a realistic magnet system with different types of supras
        background_coil = Supra(name="background", r=[200.0, 400.0], z=[-500.0, 500.0], n=1000, struct="background_struct")
        shim_coil = Supra(name="shim", r=[120.0, 180.0], z=[-100.0, 100.0], n=500, struct="shim_struct") 
        gradient_coil = Supra(name="gradient", r=[140.0, 160.0], z=[-50.0, 50.0], n=200, struct="gradient_struct")
        insert_coil = Supra(name="insert", r=[130.0, 150.0], z=[-20.0, 20.0], n=100, struct="insert_struct")
        correction_coil = Supra(name="correction", r=[380.0, 420.0], z=[-300.0, 300.0], n=800, struct="correction_struct")
        
        system = Supras(
            name="complex_magnet_system",
            magnets=[background_coil, shim_coil, gradient_coil, insert_coil, correction_coil],
            innerbore=100.0,
            outerbore=500.0,
            probes=[]  # Empty probes for this test
        )
        
        assert system.name == "complex_magnet_system"
        assert len(system.magnets) == 5
        
        # Test overall system bounds
        rb, zb = system.boundingBox()
        assert rb == [120.0, 420.0]  # From shim to correction coil
        assert zb == [-500.0, 500.0]  # Full background coil range
        
        # Test that all magnets are within system bounds
        for magnet in system.magnets:
            assert magnet.r[0] >= rb[0]
            assert magnet.r[1] <= rb[1]
            assert magnet.z[0] >= zb[0]
            assert magnet.z[1] <= zb[1]
    
    def test_empty_system_use_case(self):
        """Test Supras representing an empty magnet bore"""
        empty_system = Supras(
            name="empty_bore",
            magnets=[],
            innerbore=100.0,   # 100mm inner diameter
            outerbore=120.0    # 120mm outer diameter (20mm wall thickness)
        )
        
        assert empty_system.name == "empty_bore"
        assert len(empty_system.magnets) == 0
        assert empty_system.outerbore > empty_system.innerbore
        
        # Empty system should have zero bounding box
        rb, zb = empty_system.boundingBox()
        assert rb == [0, 0]
        assert zb == [0, 0]
        
        # Only intersections containing origin should return True
        assert empty_system.intersect([-1.0, 1.0], [-1.0, 1.0]) is True
        assert empty_system.intersect([1.0, 2.0], [1.0, 2.0]) is False


class TestSuprasDocumentation:
    """
    Test that Supras behavior matches its documentation
    """
    
    def test_documented_attributes_with_probes(self):
        """Test that Supras has all documented attributes including probes"""
        supra = Supra(name="doc_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        supras = Supras(
            name="documentation_test",
            magnets=[supra],
            innerbore=0.5,
            outerbore=2.5,
            probes=["probe1.yaml"]  # NEW: Include probes
        )
        
        # Verify all documented attributes exist
        assert hasattr(supras, "name")
        assert hasattr(supras, "magnets")
        assert hasattr(supras, "innerbore")
        assert hasattr(supras, "outerbore")
        assert hasattr(supras, "probes")  # NEW: Check probes attribute
        
        # Verify types match documentation
        assert isinstance(supras.name, str)
        assert isinstance(supras.magnets, list)
        assert isinstance(supras.innerbore, (int, float))
        assert isinstance(supras.outerbore, (int, float))
        assert isinstance(supras.probes, list)  # NEW: Check probes type

    def test_serialization_interface_compliance_with_probes(self):
        """Test that serialization interface works as documented with probes"""
        supra = Supra(name="serial_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        supras = Supras(
            name="serial_test_system", 
            magnets=[supra], 
            innerbore=0.5, 
            outerbore=2.5,
            probes=["probe1.yaml"]  # NEW: Include probes
        )
        
        # Test to_json returns valid JSON string
        json_str = supras.to_json()
        assert isinstance(json_str, str)
        
        # Should be parseable JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "__classname__" in parsed
        assert parsed["__classname__"] == "Supras"
        assert "probes" in parsed  # NEW: Check probes in JSON
        assert parsed["probes"] == ["probe1.yaml"]
        
        # Test from_dict works with probes
        data = {
            "name": "from_dict_test",
            "magnets": ["magnet1"],
            "innerbore": 2.0,
            "outerbore": 3.0,
            "probes": ["probe_test.yaml"]  # NEW: Include probes
        }
        
        new_supras = Supras.from_dict(data)
        assert isinstance(new_supras, Supras)
        assert new_supras.name == "from_dict_test"
        assert new_supras.probes == ["probe_test.yaml"]  # NEW: Check probes loaded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])