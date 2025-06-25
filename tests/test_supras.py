#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Supras class using test_utils_common mixins
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
            outerbore=40.0
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
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_supras",
            "innerbore": 5.0,
            "outerbore": 40.0
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
            "outerbore": 50.0
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
            outerbore=40.0
        )
    
    @pytest.fixture
    def empty_supras(self):
        """Fixture providing an empty Supras instance"""
        return Supras(
            name="empty_system",
            magnets=[],
            innerbore=0.0,
            outerbore=10.0
        )
    
    def test_init_with_parameters(self, sample_supra_objects):
        """Test Supras initialization with all parameters"""
        supras = Supras(
            name="init_test",
            magnets=sample_supra_objects,
            innerbore=7.5,
            outerbore=45.0
        )
        assert supras.name == "init_test"
        assert supras.magnets == sample_supra_objects
        assert supras.innerbore == 7.5
        assert supras.outerbore == 45.0
    
    def test_init_empty_magnets(self):
        """Test Supras initialization with empty magnets list"""
        supras = Supras(
            name="empty_test",
            magnets=[],
            innerbore=1.0,
            outerbore=2.0
        )
        assert supras.name == "empty_test"
        assert supras.magnets == []
        assert supras.innerbore == 1.0
        assert supras.outerbore == 2.0
    
    def test_repr(self, sample_supras):
        """Test string representation"""
        repr_str = repr(sample_supras)
        assert "Supras" in repr_str
        assert "name='sample_system'" in repr_str
        assert "innerbore=5.0" in repr_str
        assert "outerbore=40.0" in repr_str
        assert "magnets=" in repr_str
    
    def test_update_string_magnets(self):
        """Test update method converts string magnets to objects"""
        supras = Supras(
            name="update_test",
            magnets=["supra1", "supra2"],  # String representations
            innerbore=5.0,
            outerbore=10.0
        )
        
        # Initially should be strings
        assert all(isinstance(item, str) for item in supras.magnets)
        
        # Mock the loading of magnets
        mock_supra1 = Mock()
        mock_supra1.name = "supra1"
        mock_supra2 = Mock()
        mock_supra2.name = "supra2"

        with patch('python_magnetgeo.utils.loadList', return_value=[mock_supra1, mock_supra2]) as mock_load:
            supras.update()

            # After update, should be actual Supra objects
            assert supras.magnets == [mock_supra1, mock_supra2]
            mock_load.assert_called_once_with(
                "magnets",
                ["supra1", "supra2"],
                [None, Supra],
                {"Supra": Supra.from_dict}
            )
    
    def test_update_no_string_magnets(self, sample_supras):
        """Test update method with already loaded magnets"""
        original_magnets = sample_supras.magnets.copy()
        
        with patch('python_magnetgeo.utils.check_objects') as mock_check:
            with patch('python_magnetgeo.utils.loadList') as mock_load:
                mock_check.return_value = False  # No strings present
                
                sample_supras.update()
                
                # loadList should not be called since magnets are already objects
                mock_check.assert_called_once_with(sample_supras.magnets, str)
                mock_load.assert_not_called()
                assert sample_supras.magnets == original_magnets
    
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
    
    def test_get_names_empty_magnets(self, empty_supras):
        """Test get_names method with empty magnets list"""
        names = empty_supras.get_names("prefix")
        assert names == []
    
    def test_get_names_no_prefix(self, sample_supras):
        """Test get_names method without prefix"""
        # Mock the get_names method on Supra objects
        for i, magnet in enumerate(sample_supras.magnets):
            magnet.get_names = Mock(return_value=[f"name_{i}"])
        
        names = sample_supras.get_names("")
        
        # Should call get_names on each magnet with just magnet name
        for magnet in sample_supras.magnets:
            magnet.get_names.assert_called_once_with(magnet.name, False, False)
    
    @pytest.mark.parametrize("is2D,verbose", [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_names_parameters(self, sample_supras, is2D, verbose):
        """Test get_names method with different parameter combinations"""
        # Mock the get_names method on Supra objects
        for magnet in sample_supras.magnets:
            magnet.get_names = Mock(return_value=["test_name"])
        
        names = sample_supras.get_names("test", is2D=is2D, verbose=verbose)
        
        # Verify parameters are passed correctly
        for magnet in sample_supras.magnets:
            magnet.get_names.assert_called_once_with(f"test_{magnet.name}", is2D, verbose)
    
    def test_dump_success(self, sample_supras):
        """Test dump method success"""
        with patch('python_magnetgeo.utils.writeYaml') as mock_write_yaml:
            sample_supras.dump()
            mock_write_yaml.assert_called_once_with("Supras", sample_supras, Supras)
    
    def test_dump_failure(self, sample_supras):
        """Test dump method failure handling"""
        with patch('python_magnetgeo.utils.writeYaml', side_effect=Exception("Write error")):
            with pytest.raises(Exception, match="Write error"):
                sample_supras.dump()
    
    def test_write_to_json_typo_fix(self, sample_supras):
        """Test write_to_json method (note: has .son typo in original)"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_supras.write_to_json()
            
            # Note: original code has typo - uses .son instead of .json
            mock_file.assert_called_once_with("sample_system.son", "w")
    
    def test_write_to_json_content(self, sample_supras):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_supras.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "Supras"
            assert parsed["name"] == "sample_system"
    
    def test_yaml_constructor_function_direct(self):
        """Test the Supras_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "magnets": ["magnet1", "magnet2"],
            "innerbore": 15.0,
            "outerbore": 60.0
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Supras_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Supras)
        assert result.name == "direct_test"
        assert result.magnets == ["magnet1", "magnet2"]
        assert result.innerbore == 15.0
        assert result.outerbore == 60.0
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestSuprasFromDict:
    """
    Test the from_dict class method
    """
    
    def test_from_dict_all_fields(self):
        """Test from_dict with all fields present"""
        data = {
            "name": "dict_test",
            "magnets": ["magnet1", "magnet2"],
            "innerbore": 12.0,
            "outerbore": 48.0
        }
        
        supras = Supras.from_dict(data)
        
        assert supras.name == "dict_test"
        assert supras.magnets == ["magnet1", "magnet2"]
        assert supras.innerbore == 12.0
        assert supras.outerbore == 48.0
    
    def test_from_dict_missing_optional_fields(self):
        """Test from_dict with missing optional fields (innerbore, outerbore)"""
        data = {
            "name": "minimal_dict_test",
            "magnets": ["magnet1"]
        }
        
        supras = Supras.from_dict(data)
        
        assert supras.name == "minimal_dict_test"
        assert supras.magnets == ["magnet1"]
        assert supras.innerbore == 0  # Default value
        assert supras.outerbore == 0  # Default value
    
    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_test",
            "magnets": [],
            "innerbore": 5.0,
            "outerbore": 10.0
        }
        
        supras = Supras.from_dict(data, debug=True)
        assert supras.name == "debug_test"
    
    def test_from_dict_missing_required_fields(self):
        """Test from_dict with missing required fields"""
        # Missing 'name'
        data1 = {
            "magnets": ["magnet1"],
            "innerbore": 5.0,
            "outerbore": 10.0
        }
        
        with pytest.raises(KeyError):
            Supras.from_dict(data1)
        
        # Missing 'magnets'
        data2 = {
            "name": "no_magnets",
            "innerbore": 5.0,
            "outerbore": 10.0
        }
        
        with pytest.raises(KeyError):
            Supras.from_dict(data2)


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
            outerbore=35.0
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
            outerbore=25.0
        )
    
    def test_constructor_missing_required_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'name' field
        incomplete_data1 = {
            "magnets": ["magnet1"],
            "innerbore": 5.0,
            "outerbore": 10.0
        }
        mock_loader.construct_mapping.return_value = incomplete_data1
        
        with pytest.raises(KeyError):
            Supras_constructor(mock_loader, mock_node)
        
        # Missing 'magnets' field
        incomplete_data2 = {
            "name": "test_name",
            "innerbore": 5.0,
            "outerbore": 10.0
        }
        mock_loader.construct_mapping.return_value = incomplete_data2
        
        with pytest.raises(KeyError):
            Supras_constructor(mock_loader, mock_node)
    
    def test_constructor_with_extra_fields(self):
        """Test constructor handles extra fields gracefully"""
        mock_loader = Mock()
        mock_node = Mock()
        
        data_with_extras = {
            "name": "extra_fields_test",
            "magnets": ["magnet1"],
            "innerbore": 5.0,
            "outerbore": 10.0,
            "extra_field": "should_be_ignored",
            "another_extra": {"nested": "data"},
            "list_extra": [1, 2, 3]
        }
        mock_loader.construct_mapping.return_value = data_with_extras
        
        # Should work fine, ignoring extra fields
        result = Supras_constructor(mock_loader, mock_node)
        assert isinstance(result, Supras)
        assert result.name == "extra_fields_test"
        assert result.magnets == ["magnet1"]
        assert not hasattr(result, "extra_field")
        assert not hasattr(result, "another_extra")
        assert not hasattr(result, "list_extra")
    
    def test_dump_error_handling(self, sample_supras_for_errors):
        """Test dump method error handling"""
        # Test file permission error
        with patch('python_magnetgeo.utils.writeYaml', side_effect=PermissionError("No permission")):
            with pytest.raises(Exception):
                sample_supras_for_errors.dump()
        
        # Test general error
        with patch('python_magnetgeo.utils.writeYaml', side_effect=Exception("General error")):
            with pytest.raises(Exception):
                sample_supras_for_errors.dump()
    
    def test_write_to_json_error_handling(self, sample_supras_for_errors):
        """Test write_to_json error handling"""
        # Test file write error
        with patch("builtins.open", side_effect=IOError("Write error")):
            with pytest.raises(IOError):
                sample_supras_for_errors.write_to_json()
    
    def test_to_json_serialization_error(self, sample_supras_for_errors):
        """Test to_json with serialization issues"""
        # Mock serialize_instance to raise an error
        with patch("python_magnetgeo.deserialize.serialize_instance", side_effect=TypeError("Serialization error")):
            with pytest.raises(TypeError):
                sample_supras_for_errors.to_json()
    
    def test_update_with_load_error(self):
        """Test update method with loadList error"""
        supras = Supras(
            name="update_error",
            magnets=["string_magnet"],  # String that needs loading
            innerbore=0.0,
            outerbore=1.0
        )
        
        # Mock loadList to raise an error
        with patch('python_magnetgeo.utils.loadList', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError, match="File not found"):
                supras.update()
    
    def test_get_names_with_magnet_error(self):
        """Test get_names when individual magnet raises error"""
        error_magnet = Mock(spec=Supra)
        error_magnet.name = "error_magnet"
        error_magnet.get_names = Mock(side_effect=Exception("Magnet error"))
        
        good_magnet = Mock(spec=Supra)
        good_magnet.name = "good_magnet"
        good_magnet.get_names = Mock(return_value=["good_name"])
        
        supras = Supras(
            name="mixed_error",
            magnets=[good_magnet, error_magnet],
            innerbore=0.0,
            outerbore=1.0
        )
        
        # Should propagate the error from individual magnet
        with pytest.raises(Exception, match="Magnet error"):
            supras.get_names("test")
    
    def test_boundingBox_with_invalid_magnets(self):
        """Test boundingBox with magnets that have invalid geometry"""
        invalid_magnet = Mock(spec=Supra)
        invalid_magnet.r = None  # Invalid geometry
        invalid_magnet.z = [0.0, 1.0]
        
        supras = Supras(
            name="invalid_geometry",
            magnets=[invalid_magnet],
            innerbore=0.0,
            outerbore=1.0
        )
        
        # Should handle gracefully or raise appropriate error
        with pytest.raises((TypeError, AttributeError)):
            supras.boundingBox()


class TestSuprasCompatibility:
    """
    Test Supras compatibility with different data types and edge cases
    """
    
    def test_floating_point_precision(self):
        """Test Supras with floating point precision edge cases"""
        precise_values = [
            1.0000000000001,
            1.9999999999999,
            0.1 + 0.2,  # Classic floating point precision issue
            1e-15,
            1e15
        ]
        
        for inner, outer in zip(precise_values, precise_values[1:]):
            supras = Supras(
                name="precision_test",
                magnets=[],
                innerbore=inner,
                outerbore=outer
            )
            
            # Values should be preserved as-is
            assert supras.innerbore == inner
            assert supras.outerbore == outer
            
            # JSON serialization should handle these values
            json_str = supras.to_json()
            parsed = json.loads(json_str)
            
            # Should be reasonably close (within floating point precision)
            assert abs(parsed["innerbore"] - inner) < 1e-10
            assert abs(parsed["outerbore"] - outer) < 1e-10
    
    def test_mixed_numeric_types(self):
        """Test Supras with mixed numeric types (int, float)"""
        supras = Supras(
            name="mixed_types",
            magnets=[],
            innerbore=5,      # int
            outerbore=10.5    # float
        )
        
        assert supras.innerbore == 5
        assert supras.outerbore == 10.5
        assert type(supras.innerbore) == int
        assert type(supras.outerbore) == float
    
    def test_string_representations_in_json(self):
        """Test that string fields are properly handled in JSON"""
        supras = Supras(
            name='name"with"quotes\\and\\backslashes\nand\nnewlines',
            magnets=[],
            innerbore=1.0,
            outerbore=2.0
        )
        
        json_str = supras.to_json()
        parsed = json.loads(json_str)  # Should not raise exception
        
        assert parsed["name"] == 'name"with"quotes\\and\\backslashes\nand\nnewlines'
    
    def test_comparison_consistency(self):
        """Test that identical Supras have consistent representations"""
        supra1 = Supra(name="test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        supra2 = Supra(name="test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        supras1 = Supras(
            name="identical",
            magnets=[supra1],
            innerbore=0.5,
            outerbore=2.5
        )
        
        supras2 = Supras(
            name="identical",
            magnets=[supra2],
            innerbore=0.5,
            outerbore=2.5
        )
        
        # Should have identical string representations
        assert repr(supras1) == repr(supras2)


class TestSuprasUseCases:
    """
    Test Supras with realistic use cases and scenarios
    """
    
    def test_single_supra_system(self):
        """Test Supras system with a single superconducting magnet"""
        supra = Supra(
            name="main_coil",
            r=[50.0, 150.0],  # 50mm to 150mm radius
            z=[0.0, 200.0],   # 200mm height
            n=100,            # 100 turns
            struct="main_coil_structure"
        )
        
        system = Supras(
            name="single_coil_system",
            magnets=[supra],
            innerbore=45.0,    # 5mm clearance inside
            outerbore=155.0    # 5mm clearance outside
        )
        
        assert system.name == "single_coil_system"
        assert len(system.magnets) == 1
        assert system.innerbore < system.magnets[0].r[0]  # Inner bore smaller than inner radius
        assert system.outerbore > system.magnets[0].r[1]  # Outer bore larger than outer radius
        
        # Test bounding box
        rb, zb = system.boundingBox()
        assert rb == [50.0, 150.0]
        assert zb == [0.0, 200.0]
    
    def test_multi_coil_system(self):
        """Test Supras system with multiple superconducting coils"""
        # Create a stack of coils
        coils = []
        for i in range(3):
            coil = Supra(
                name=f"coil_{i+1}",
                r=[60.0 + i*10, 140.0 - i*5],  # Varying radii
                z=[i*220.0, (i+1)*220.0 - 20.0],  # Stacked vertically
                n=50 + i*25,  # Varying turn count
                struct=f"coil_{i+1}_structure"
            )
            coils.append(coil)
        
        system = Supras(
            name="multi_coil_system",
            magnets=coils,
            innerbore=55.0,
            outerbore=145.0
        )
        
        assert system.name == "multi_coil_system"
        assert len(system.magnets) == 3
        
        # Test overall bounding box
        rb, zb = system.boundingBox()
        assert rb == [60.0, 140.0]  # Min r from coil_1, max r from coil_1
        assert zb == [0.0, 640.0]   # From first coil start to last coil end
        
        # Test intersection with various regions
        assert system.intersect([50.0, 150.0], [-10.0, 650.0]) is True  # Overlaps entire system
        assert system.intersect([200.0, 250.0], [0.0, 100.0]) is False  # Too far in r
    
    def test_nested_coil_system(self):
        """Test Supras system with nested coils"""
        inner_coil = Supra(
            name="inner_coil",
            r=[30.0, 70.0],
            z=[50.0, 150.0],
            n=200,
            struct="inner_structure"
        )
        
        outer_coil = Supra(
            name="outer_coil", 
            r=[80.0, 120.0],
            z=[0.0, 200.0],
            n=150,
            struct="outer_structure"
        )
        
        system = Supras(
            name="nested_system",
            magnets=[inner_coil, outer_coil],
            innerbore=25.0,
            outerbore=125.0
        )
        
        # Verify nested structure
        assert inner_coil.r[1] < outer_coil.r[0]  # Inner coil inside outer coil
        
        # Test bounding box encompasses both
        rb, zb = system.boundingBox()
        assert rb == [30.0, 120.0]
        assert zb == [0.0, 200.0]
        
        # Test intersection detection
        assert system.intersect([25.0, 125.0], [-10.0, 210.0]) is True  # Full system
        assert system.intersect([40.0, 60.0], [60.0, 140.0]) is True   # Inner coil only
        assert system.intersect([90.0, 110.0], [10.0, 190.0]) is True  # Outer coil only
    
    def test_complex_magnet_arrangement(self):
        """Test Supras with complex magnet arrangement"""
        # Simulate a realistic magnet system with various coil types
        magnets = [
            Supra("background_coil", [200.0, 400.0], [-500.0, 500.0], 500, "bg_struct"),
            Supra("gradient_coil_1", [150.0, 180.0], [-100.0, -50.0], 50, "grad_struct"),
            Supra("gradient_coil_2", [150.0, 180.0], [50.0, 100.0], 50, "grad_struct"),
            Supra("shim_coil_1", [120.0, 140.0], [-25.0, 25.0], 25, "shim_struct"),
            Supra("correction_coil", [450.0, 500.0], [-200.0, 200.0], 100, "corr_struct")
        ]
        
        system = Supras(
            name="complex_magnet_system",
            magnets=magnets,
            innerbore=100.0,
            outerbore=520.0
        )
        
        assert len(system.magnets) == 5
        
        # Test overall system bounds
        rb, zb = system.boundingBox()
        assert rb == [120.0, 500.0]  # From shim to correction coil
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
    
    def test_documented_attributes(self):
        """Test that Supras has all documented attributes"""
        supra = Supra(name="doc_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        supras = Supras(
            name="documentation_test",
            magnets=[supra],
            innerbore=0.5,
            outerbore=2.5
        )
        
        # Verify all documented attributes exist
        assert hasattr(supras, "name")
        assert hasattr(supras, "magnets")
        assert hasattr(supras, "innerbore")
        assert hasattr(supras, "outerbore")
        
        # Verify types match documentation
        assert isinstance(supras.name, str)
        assert isinstance(supras.magnets, list)
        assert isinstance(supras.innerbore, (int, float))
        assert isinstance(supras.outerbore, (int, float))
    
    def test_yaml_tag_matches_class_name(self):
        """Test that YAML tag matches class name"""
        assert Supras.yaml_tag == "Supras"
    
    def test_geometric_operations_documented(self):
        """Test that geometric operations work as documented"""
        supra1 = Supra(name="geo1", r=[10.0, 20.0], z=[0.0, 10.0], n=1, struct="")
        supra2 = Supra(name="geo2", r=[15.0, 25.0], z=[5.0, 15.0], n=1, struct="")
        
        supras = Supras(name="geo_test", magnets=[supra1, supra2], innerbore=5.0, outerbore=30.0)
        
        # boundingBox should return overall bounds
        rb, zb = supras.boundingBox()
        assert isinstance(rb, list) and len(rb) == 2
        assert isinstance(zb, list) and len(zb) == 2
        assert rb[0] <= rb[1]  # Min <= Max
        assert zb[0] <= zb[1]  # Min <= Max
        
        # intersect should return boolean
        result = supras.intersect([12.0, 18.0], [2.0, 8.0])
        assert isinstance(result, bool)
    
    def test_documented_methods_exist(self):
        """Test that all documented methods exist"""
        supras = Supras(name="method_test", magnets=[], innerbore=1.0, outerbore=2.0)
        
        # Test all documented methods exist
        documented_methods = [
            'update',
            'get_channels',
            'get_isolants',
            'get_names',
            'dump',
            'to_json',
            'write_to_json',
            'from_dict',
            'from_yaml',
            'from_json',
            'boundingBox',
            'intersect'
        ]
        
        for method_name in documented_methods:
            assert hasattr(supras, method_name), f"Missing method: {method_name}"
            assert callable(getattr(supras, method_name)), f"Method {method_name} is not callable"
    
    def test_serialization_interface_compliance(self):
        """Test that serialization interface works as documented"""
        supra = Supra(name="serial_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        supras = Supras(name="serial_test_system", magnets=[supra], innerbore=0.5, outerbore=2.5)
        
        # Test to_json returns valid JSON string
        json_str = supras.to_json()
        assert isinstance(json_str, str)
        
        # Should be parseable JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "__classname__" in parsed
        assert parsed["__classname__"] == "Supras"
        
        # Test from_dict works
        data = {
            "name": "from_dict_test",
            "magnets": ["magnet1"],
            "innerbore": 2.0,
            "outerbore": 3.0
        }
        
        new_supras = Supras.from_dict(data)
        assert isinstance(new_supras, Supras)
        assert new_supras.name == "from_dict_test"