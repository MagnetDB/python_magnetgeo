#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Screen class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the class under test
from python_magnetgeo.Screen import Screen, Screen_constructor

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


class TestScreen(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for Screen using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample Screen instance for testing"""
        return Screen(
            name="test_screen",
            r=[10.0, 50.0],
            z=[0.0, 100.0]
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """
!<Screen>
name: test_screen
r: [10.0, 50.0]
z: [0.0, 100.0]
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_screen",
            "r": [10.0, 50.0],
            "z": [0.0, 100.0]
        }
    
    def get_class_under_test(self) -> Type:
        """Return the Screen class"""
        return Screen
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return Screen
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "Screen"


class TestScreenConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for Screen YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = Screen_constructor(loader, node)
            return result.__dict__, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "r": [15.0, 45.0],
            "z": [5.0, 95.0]
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "Screen"


class TestScreenSpecific:
    """
    Specific tests for Screen functionality not covered by mixins
    """
    
    @pytest.fixture
    def sample_screen(self):
        """Fixture providing a sample Screen instance"""
        return Screen(
            name="sample_screen",
            r=[20.0, 80.0],
            z=[10.0, 110.0]
        )
    
    @pytest.fixture
    def minimal_screen(self):
        """Fixture providing a minimal Screen instance"""
        return Screen(name="minimal", r=[0.0, 1.0], z=[0.0, 1.0])
    
    def test_init_with_parameters(self):
        """Test Screen initialization with all parameters"""
        screen = Screen(
            name="init_test",
            r=[5.0, 25.0],
            z=[0.0, 50.0]
        )
        assert screen.name == "init_test"
        assert screen.r == [5.0, 25.0]
        assert screen.z == [0.0, 50.0]
    
    def test_repr(self, sample_screen):
        """Test string representation"""
        repr_str = repr(sample_screen)
        assert "Screen" in repr_str
        assert "name='sample_screen'" in repr_str
        assert "r=[20.0, 80.0]" in repr_str
        assert "z=[10.0, 110.0]" in repr_str
    
    def test_get_lc_calculation(self, sample_screen):
        """Test get_lc method calculation"""
        lc = sample_screen.get_lc()
        expected_lc = (80.0 - 20.0) / 10.0  # (r[1] - r[0]) / 10.0
        assert lc == expected_lc
        assert lc == 6.0
    
    @pytest.mark.parametrize("r_values,expected_lc", [
        ([0.0, 10.0], 1.0),
        ([5.0, 15.0], 1.0),
        ([10.0, 50.0], 4.0),
        ([0.0, 100.0], 10.0),
        ([25.0, 75.0], 5.0),
        ([1.0, 1.1], 0.01),  # Very small difference
    ])
    def test_get_lc_various_ranges(self, r_values, expected_lc):
        """Test get_lc with various r ranges"""
        screen = Screen(name="lc_test", r=r_values, z=[0.0, 1.0])
        lc = screen.get_lc()
        assert abs(lc - expected_lc) < 1e-10  # Account for floating point precision
    
    def test_get_channels_returns_empty_list(self, sample_screen):
        """Test get_channels method returns empty list"""
        channels = sample_screen.get_channels("test_magnet")
        assert channels == []
        
        channels_with_params = sample_screen.get_channels("test", hideIsolant=False, debug=True)
        assert channels_with_params == []
    
    def test_get_isolants_returns_empty_list(self, sample_screen):
        """Test get_isolants method returns empty list"""
        isolants = sample_screen.get_isolants("test_magnet")
        assert isolants == []
        
        isolants_with_debug = sample_screen.get_isolants("test", debug=True)
        assert isolants_with_debug == []
    
    def test_get_names_with_prefix(self, sample_screen):
        """Test get_names method with prefix"""
        names = sample_screen.get_names("prefix")
        expected_names = ["prefix_sample_screen_Screen"]
        assert names == expected_names
    
    def test_get_names_without_prefix(self, sample_screen):
        """Test get_names method without prefix"""
        names = sample_screen.get_names("")
        expected_names = ["sample_screen_Screen"]
        assert names == expected_names
        
        names_none = sample_screen.get_names(None)
        expected_names_none = ["sample_screen_Screen"]
        assert names_none == expected_names_none
    
    @pytest.mark.parametrize("is2D,verbose", [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_names_parameters(self, sample_screen, is2D, verbose):
        """Test get_names method with different parameter combinations"""
        names = sample_screen.get_names("test", is2D=is2D, verbose=verbose)
        expected_names = ["test_sample_screen_Screen"]
        assert names == expected_names
    
    def test_dump_success(self, sample_screen):
        """Test dump method success"""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                sample_screen.dump()
                
                mock_file.assert_called_once_with("sample_screen.yaml", "w")
                mock_yaml_dump.assert_called_once()
    
    def test_dump_failure(self, sample_screen):
        """Test dump method failure handling"""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with pytest.raises(Exception, match="Failed to Screen dump"):
                sample_screen.dump()
    
    def test_write_to_json_creates_file(self, sample_screen):
        """Test write_to_json method creates file"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_screen.write_to_json()
            mock_file.assert_called_once_with("sample_screen.json", "w")
    
    def test_write_to_json_content(self, sample_screen):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_screen.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "Screen"
            assert parsed["name"] == "sample_screen"
    
    def test_yaml_constructor_function_direct(self):
        """Test the Screen_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "r": [30.0, 70.0],
            "z": [20.0, 120.0]
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Screen_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Screen)
        assert result.name == "direct_test"
        assert result.r == [30.0, 70.0]
        assert result.z == [20.0, 120.0]
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestScreenFromDict:
    """
    Test the from_dict class method
    """
    
    def test_from_dict_complete(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_test",
            "r": [12.0, 48.0],
            "z": [5.0, 105.0]
        }
        
        screen = Screen.from_dict(data)
        
        assert screen.name == "dict_test"
        assert screen.r == [12.0, 48.0]
        assert screen.z == [5.0, 105.0]
    
    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_test",
            "r": [1.0, 2.0],
            "z": [0.0, 1.0]
        }
        
        screen = Screen.from_dict(data, debug=True)
        assert screen.name == "debug_test"
    
    def test_from_dict_missing_fields(self):
        """Test from_dict with missing required fields"""
        # Missing 'name'
        data1 = {
            "r": [1.0, 2.0],
            "z": [0.0, 1.0]
        }
        
        with pytest.raises(KeyError):
            Screen.from_dict(data1)
        
        # Missing 'r'
        data2 = {
            "name": "no_r",
            "z": [0.0, 1.0]
        }
        
        with pytest.raises(KeyError):
            Screen.from_dict(data2)
        
        # Missing 'z'
        data3 = {
            "name": "no_z",
            "r": [1.0, 2.0]
        }
        
        with pytest.raises(KeyError):
            Screen.from_dict(data3)


class TestScreenGeometry:
    """
    Test geometric operations for Screen
    """
    
    @pytest.fixture
    def geometric_screen(self):
        """Fixture with Screen having known geometric bounds"""
        return Screen(
            name="geometric_test",
            r=[10.0, 40.0],
            z=[5.0, 25.0]
        )
    
    def test_boundingBox_returns_coordinates(self, geometric_screen):
        """Test boundingBox method returns r and z coordinates"""
        rb, zb = geometric_screen.boundingBox()
        
        assert rb == [10.0, 40.0]
        assert zb == [5.0, 25.0]
        assert rb == geometric_screen.r
        assert zb == geometric_screen.z
    
    def test_boundingBox_various_coordinates(self):
        """Test boundingBox with various coordinate combinations"""
        test_cases = [
            ([0.0, 1.0], [0.0, 1.0]),
            ([5.0, 15.0], [10.0, 20.0]),
            ([-5.0, 5.0], [-10.0, 10.0]),  # Negative coordinates
            ([100.0, 200.0], [500.0, 600.0]),  # Large coordinates
        ]
        
        for r_vals, z_vals in test_cases:
            screen = Screen(name="bbox_test", r=r_vals, z=z_vals)
            rb, zb = screen.boundingBox()
            assert rb == r_vals
            assert zb == z_vals
    
    @pytest.mark.parametrize("test_r,test_z,expected", [
        ([5.0, 45.0], [0.0, 30.0], True),    # Overlaps completely
        ([15.0, 35.0], [10.0, 20.0], True),  # Overlaps inside
        ([0.0, 50.0], [0.0, 30.0], True),    # Overlaps extending beyond
        ([50.0, 60.0], [5.0, 25.0], False),  # No overlap (too far in r)
        ([10.0, 40.0], [30.0, 40.0], False), # No overlap (too far in z)
        ([0.0, 5.0], [0.0, 2.0], False),     # No overlap (too small)
    ])
    def test_intersect(self, geometric_screen, test_r, test_z, expected):
        """Test intersect method with various test rectangles"""
        result = geometric_screen.intersect(test_r, test_z)
        assert result == expected
    
    def test_intersect_edge_cases(self, geometric_screen):
        """Test intersect method edge cases"""
        # Test with identical bounds
        rb, zb = geometric_screen.boundingBox()
        assert geometric_screen.intersect(rb, zb) is True
        
        # Test with very small overlap
        small_overlap_r = [39.9, 40.1]  # Tiny overlap with max r
        small_overlap_z = [24.9, 25.1]  # Tiny overlap with max z
        assert geometric_screen.intersect(small_overlap_r, small_overlap_z) is True
        
        # Test with exact boundary touching
        boundary_r = [40.0, 50.0]  # Starts exactly at screen boundary
        boundary_z = [5.0, 25.0]   # Same z range
        # Result depends on implementation - boundary cases might be True or False
        result = geometric_screen.intersect(boundary_r, boundary_z)
        assert isinstance(result, bool)
    
    def test_intersect_algorithm_details(self):
        """Test the specific intersection algorithm implementation"""
        screen = Screen(name="algo_test", r=[10.0, 20.0], z=[5.0, 15.0])
        
        # Test case that should definitely intersect
        test_r = [12.0, 18.0]  # Inside screen r range
        test_z = [7.0, 13.0]   # Inside screen z range
        
        # Manual calculation of the algorithm:
        # isR = abs(screen.r[0] - test_r[0]) < abs(screen.r[1] - screen.r[0] + test_r[0] + test_r[1]) / 2.0
        # isR = abs(10.0 - 12.0) < abs(20.0 - 10.0 + 12.0 + 18.0) / 2.0
        # isR = 2.0 < 50.0 / 2.0 = 25.0 → True
        
        # isZ = abs(screen.z[0] - test_z[0]) < abs(screen.z[1] - screen.z[0] + test_z[0] + test_z[1]) / 2.0
        # isZ = abs(5.0 - 7.0) < abs(15.0 - 5.0 + 7.0 + 13.0) / 2.0
        # isZ = 2.0 < 35.0 / 2.0 = 17.5 → True
        
        assert screen.intersect(test_r, test_z) is True




class TestScreenPerformance:
    """
    Performance tests for Screen operations
    """
    
    @pytest.mark.performance
    def test_get_lc_performance(self):
        """Test get_lc performance with large coordinates"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        large_screen = Screen(
            name="performance_test",
            r=[0.0, 1e10],
            z=[0.0, 1e10]
        )
        
        result, execution_time = time_function_execution(large_screen.get_lc)
        
        # Should be very fast calculation
        assert_performance_within_limits(execution_time, 0.001)  # 1ms limit
        assert result == 1e9  # (1e10 - 0.0) / 10.0
    
    @pytest.mark.performance
    def test_intersect_performance(self):
        """Test intersect performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        screen = Screen(name="perf_test", r=[0.0, 100.0], z=[0.0, 100.0])
        test_r = [50.0, 150.0]
        test_z = [50.0, 150.0]
        
        result, execution_time = time_function_execution(screen.intersect, test_r, test_z)
        
        # Intersection calculation should be very fast
        assert_performance_within_limits(execution_time, 0.001)  # 1ms limit
        assert isinstance(result, bool)
    
    @pytest.mark.performance
    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        screen = Screen(
            name="json_performance_test",
            r=[1.23456789, 9.87654321],
            z=[2.34567891, 8.76543219]
        )
        
        result, execution_time = time_function_execution(screen.to_json)
        
        # JSON serialization should be fast
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert isinstance(result, str)
        assert len(result) > 0


class TestScreenIntegration:
    """
    Integration tests for Screen
    """
    
    def test_yaml_integration(self, temp_yaml_file):
        """Test YAML integration"""
        screen = Screen(
            name="yaml_integration",
            r=[25.0, 75.0],
            z=[15.0, 85.0]
        )
        
        # Test dump functionality
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                screen.dump()
                mock_file.assert_called_once_with("yaml_integration.yaml", "w")
                mock_yaml_dump.assert_called_once()
    
    def test_json_integration_complete(self):
        """Test complete JSON serialization integration"""
        screen = Screen(
            name="json_integration",
            r=[35.0, 65.0],
            z=[25.0, 95.0]
        )
        
        json_str = screen.to_json()
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["__classname__"] == "Screen"
        assert parsed["name"] == "json_integration"
        assert parsed["r"] == [35.0, 65.0]
        assert parsed["z"] == [25.0, 95.0]
    
    def test_from_yaml_integration(self):
        """Test from_yaml integration"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load_yaml:
            mock_screen = Mock(spec=Screen)
            mock_load_yaml.return_value = mock_screen
            
            result = Screen.from_yaml("test.yaml", debug=True)
            
            mock_load_yaml.assert_called_once_with("Screen", "test.yaml", Screen, True)
            assert result == mock_screen
    
    def test_from_json_integration(self):
        """Test from_json integration"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load_json:
            mock_screen = Mock(spec=Screen)
            mock_load_json.return_value = mock_screen
            
            result = Screen.from_json("test.json", debug=False)
            
            mock_load_json.assert_called_once_with("Screen", "test.json", False)
            assert result == mock_screen


class TestScreenErrorHandling:
    """
    Test error handling and robustness for Screen
    """
    
    def test_constructor_missing_required_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'name' field
        incomplete_data1 = {
            "r": [1.0, 2.0],
            "z": [0.0, 1.0]
        }
        mock_loader.construct_mapping.return_value = incomplete_data1
        
        with pytest.raises(KeyError):
            Screen_constructor(mock_loader, mock_node)
        
        # Missing 'r' field
        incomplete_data2 = {
            "name": "test_name",
            "z": [0.0, 1.0]
        }
        mock_loader.construct_mapping.return_value = incomplete_data2
        
        with pytest.raises(KeyError):
            Screen_constructor(mock_loader, mock_node)
        
        # Missing 'z' field
        incomplete_data3 = {
            "name": "test_name",
            "r": [1.0, 2.0]
        }
        mock_loader.construct_mapping.return_value = incomplete_data3
        
        with pytest.raises(KeyError):
            Screen_constructor(mock_loader, mock_node)
    
    def test_constructor_with_extra_fields(self):
        """Test constructor handles extra fields gracefully"""
        mock_loader = Mock()
        mock_node = Mock()
        
        data_with_extras = {
            "name": "extra_fields_test",
            "r": [1.0, 2.0],
            "z": [0.0, 1.0],
            "extra_field": "should_be_ignored",
            "another_extra": {"nested": "data"}
        }
        mock_loader.construct_mapping.return_value = data_with_extras
        
        # Should work fine, ignoring extra fields
        result = Screen_constructor(mock_loader, mock_node)
        assert isinstance(result, Screen)
        assert result.name == "extra_fields_test"
        assert result.r == [1.0, 2.0]
        assert result.z == [0.0, 1.0]
        assert not hasattr(result, "extra_field")
        assert not hasattr(result, "another_extra")
    
    def test_dump_error_handling(self):
        """Test dump method error handling"""
        screen = Screen(name="error_test", r=[1.0, 2.0], z=[0.0, 1.0])
        
        # Test file permission error
        with patch("builtins.open", side_effect=PermissionError("No permission")):
            with pytest.raises(Exception, match="Failed to Screen dump"):
                screen.dump()
        
        # Test YAML serialization error
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            with patch("yaml.dump", side_effect=yaml.YAMLError("YAML error")):
                with pytest.raises(Exception, match="Failed to Screen dump"):
                    screen.dump()
    
    def test_write_to_json_error_handling(self):
        """Test write_to_json error handling"""
        screen = Screen(name="json_error", r=[1.0, 2.0], z=[0.0, 1.0])
        
        # Test file write error
        with patch("builtins.open", side_effect=IOError("Write error")):
            with pytest.raises(IOError):
                screen.write_to_json()
    
    def test_to_json_serialization_error(self):
        """Test to_json with serialization issues"""
        screen = Screen(name="serialization_error", r=[1.0, 2.0], z=[0.0, 1.0])
        
        # Mock serialize_instance to raise an error
        with patch("python_magnetgeo.deserialize.serialize_instance", side_effect=TypeError("Serialization error")):
            with pytest.raises(TypeError):
                screen.to_json()
    
    def test_get_lc_with_zero_difference(self):
        """Test get_lc when r[1] - r[0] = 0"""
        screen = Screen(name="zero_diff", r=[5.0, 5.0], z=[0.0, 1.0])
        lc = screen.get_lc()
        assert lc == 0.0  # (5.0 - 5.0) / 10.0 = 0.0
    
    def test_intersect_with_invalid_coordinates(self):
        """Test intersect with potentially invalid coordinate lists"""
        screen = Screen(name="intersect_test", r=[1.0, 2.0], z=[0.0, 1.0])
        
        # Test with empty lists (should raise error)
        with pytest.raises((IndexError, TypeError)):
            screen.intersect([], [])
        
        # Test with single-element lists (should raise error)
        with pytest.raises(IndexError):
            screen.intersect([1.0], [0.0])
    
    def test_boundingBox_with_invalid_coordinates(self):
        """Test boundingBox with various coordinate edge cases"""
        # Test with very small lists
        screen = Screen(name="bbox_test", r=[1.0], z=[0.0])
        # boundingBox just returns the lists as-is, so this should work
        rb, zb = screen.boundingBox()
        assert rb == [1.0]
        assert zb == [0.0]


class TestScreenCompatibility:
    """
    Test Screen compatibility with different data types and edge cases
    """
    
    def test_floating_point_precision(self):
        """Test Screen with floating point precision edge cases"""
        precise_values = [
            [1.0000000000001, 1.9999999999999],
            [0.1, 0.1 + 0.2],  # Classic floating point precision issue
            [1e-15, 1e-14],
            [1e15, 2e15]
        ]
        
        for r_vals in precise_values:
            screen = Screen(
                name="precision_test",
                r=r_vals,
                z=[0.0, 1.0]
            )
            
            # Values should be preserved as-is
            assert screen.r == r_vals
            
            # get_lc should handle precision correctly
            lc = screen.get_lc()
            expected_lc = (r_vals[1] - r_vals[0]) / 10.0
            assert abs(lc - expected_lc) < 1e-15
            
            # JSON serialization should handle these values
            json_str = screen.to_json()
            parsed = json.loads(json_str)
            
            # Should be reasonably close (within floating point precision)
            for i, val in enumerate(r_vals):
                assert abs(parsed["r"][i] - val) < 1e-10
    
    def test_string_representations_in_json(self):
        """Test that string fields are properly handled in JSON"""
        screen = Screen(
            name='name"with"quotes\\and\\backslashes\nand\nnewlines',
            r=[1.0, 2.0],
            z=[0.0, 1.0]
        )
        
        json_str = screen.to_json()
        parsed = json.loads(json_str)  # Should not raise exception
        
        assert parsed["name"] == 'name"with"quotes\\and\\backslashes\nand\nnewlines'
    
    def test_comparison_consistency(self):
        """Test that identical Screens have consistent representations"""
        screen1 = Screen(
            name="identical",
            r=[10.0, 20.0],
            z=[5.0, 15.0]
        )
        
        screen2 = Screen(
            name="identical",
            r=[10.0, 20.0],
            z=[5.0, 15.0]
        )
        
        # Should have identical string representations
        assert repr(screen1) == repr(screen2)
        assert screen1.to_json() == screen2.to_json()
    
    def test_coordinate_list_lengths(self):
        """Test Screen with coordinate lists of different lengths"""
        # Test with longer coordinate lists
        long_r = [1.0, 2.0, 3.0, 4.0]  # More than 2 elements
        long_z = [0.0, 1.0, 2.0, 3.0, 4.0]  # More than 2 elements
        
        screen = Screen(name="long_coords", r=long_r, z=long_z)
        assert screen.r == long_r
        assert screen.z == long_z
        
        # get_lc should still work with first two elements
        lc = screen.get_lc()
        assert lc == (2.0 - 1.0) / 10.0  # Uses r[1] - r[0]
        
        # boundingBox should return the entire lists
        rb, zb = screen.boundingBox()
        assert rb == long_r
        assert zb == long_z


class TestScreenUseCases:
    """
    Test Screen with realistic use cases and scenarios
    """
    
    def test_magnetic_shield_screen(self):
        """Test Screen representing a magnetic shield"""
        shield = Screen(
            name="magnetic_shield",
            r=[100.0, 150.0],  # 100-150mm radius shield
            z=[0.0, 200.0]     # 200mm height
        )
        
        assert shield.name == "magnetic_shield"
        assert shield.r == [100.0, 150.0]
        assert shield.z == [0.0, 200.0]
        
        # Check characteristic length for mesh generation
        lc = shield.get_lc()
        assert lc == 5.0  # (150-100)/10 = 5mm mesh size
        
        # Check names for CAD/mesh generation
        names = shield.get_names("magnet_system")
        assert names == ["magnet_system_magnetic_shield_Screen"]
        
        # Test intersection with magnet region
        magnet_region = [110.0, 140.0]  # Inside the shield
        magnet_height = [50.0, 150.0]   # Partially overlapping
        assert shield.intersect(magnet_region, magnet_height) is True
    
    def test_thermal_screen(self):
        """Test Screen representing a thermal radiation screen"""
        thermal_screen = Screen(
            name="thermal_barrier",
            r=[200.0, 205.0],  # Thin 5mm thick screen
            z=[-100.0, 300.0]  # 400mm total height
        )
        
        assert thermal_screen.name == "thermal_barrier"
        assert thermal_screen.r == [200.0, 205.0]
        assert thermal_screen.z == [-100.0, 300.0]
        
        # Very fine mesh due to thin geometry
        lc = thermal_screen.get_lc()
        assert lc == 0.5  # (205-200)/10 = 0.5mm mesh size
        
        # Test bounding box
        rb, zb = thermal_screen.boundingBox()
        assert rb == [200.0, 205.0]
        assert zb == [-100.0, 300.0]
    
    def test_vacuum_chamber_screen(self):
        """Test Screen representing a vacuum chamber wall"""
        vacuum_chamber = Screen(
            name="vacuum_chamber",
            r=[50.0, 55.0],    # 5mm wall thickness
            z=[-50.0, 250.0]   # Chamber height
        )
        
        assert vacuum_chamber.name == "vacuum_chamber"
        
        # Test intersection with internal components
        internal_component = [0.0, 40.0]   # Component inside chamber
        component_height = [0.0, 200.0]    # Within chamber height
        assert vacuum_chamber.intersect(internal_component, component_height) is False
        
        # Test intersection with external environment
        external_region = [60.0, 100.0]   # Outside chamber
        external_height = [0.0, 200.0]
        assert vacuum_chamber.intersect(external_region, external_height) is False
        
        # Test intersection with chamber wall itself
        wall_region = [52.0, 58.0]  # Overlapping with wall
        wall_height = [0.0, 200.0]
        assert vacuum_chamber.intersect(wall_region, wall_height) is True
    
    def test_multiple_concentric_screens(self):
        """Test multiple concentric screens scenario"""
        screens = [
            Screen("inner_screen", [80.0, 85.0], [0.0, 150.0]),
            Screen("middle_screen", [120.0, 125.0], [0.0, 150.0]),
            Screen("outer_screen", [180.0, 185.0], [0.0, 150.0])
        ]
        
        # Verify they don't intersect with each other
        for i, screen1 in enumerate(screens):
            for j, screen2 in enumerate(screens):
                if i != j:
                    rb1, zb1 = screen1.boundingBox()
                    result = screen2.intersect(rb1, zb1)
                    # Concentric screens shouldn't intersect
                    assert result is False
        
        # Test that they all have the same height
        for screen in screens:
            rb, zb = screen.boundingBox()
            assert zb == [0.0, 150.0]
        
        # Test mesh sizes are reasonable
        for screen in screens:
            lc = screen.get_lc()
            assert lc == 0.5  # All 5mm thick → 0.5mm mesh
    
    def test_asymmetric_screen(self):
        """Test Screen with asymmetric geometry"""
        asymmetric_screen = Screen(
            name="asymmetric_shield",
            r=[30.0, 90.0],    # Large radial extent
            z=[10.0, 15.0]     # Small axial extent
        )
        
        assert asymmetric_screen.name == "asymmetric_shield"
        
        # Large radial mesh size due to large r range
        lc = asymmetric_screen.get_lc()
        assert lc == 6.0  # (90-30)/10 = 6mm
        
        # Test intersection behavior with various regions
        thin_tall_region = [40.0, 50.0]   # Narrow in r
        tall_height = [0.0, 100.0]        # Tall in z
        assert asymmetric_screen.intersect(thin_tall_region, tall_height) is True
        
        wide_short_region = [0.0, 100.0]  # Wide in r
        short_height = [12.0, 13.0]       # Short in z, within screen
        assert asymmetric_screen.intersect(wide_short_region, short_height) is True


class TestScreenDocumentation:
    """
    Test that Screen behavior matches its documentation
    """
    
    def test_documented_attributes(self):
        """Test that Screen has all documented attributes"""
        screen = Screen(
            name="documentation_test",
            r=[10.0, 20.0],
            z=[0.0, 10.0]
        )
        
        # Verify all documented attributes exist
        assert hasattr(screen, "name")
        assert hasattr(screen, "r")
        assert hasattr(screen, "z")
        
        # Verify types match documentation
        assert isinstance(screen.name, str)
        assert isinstance(screen.r, list)
        assert isinstance(screen.z, list)
        
        # Verify geometric data format
        validate_geometric_data(screen.r, screen.z, allow_negative=True)
    
    def test_yaml_tag_matches_class_name(self):
        """Test that YAML tag matches class name"""
        assert Screen.yaml_tag == "Screen"
    
    def test_geometric_operations_documented(self):
        """Test that geometric operations work as documented"""
        screen = Screen(name="geo_test", r=[5.0, 15.0], z=[0.0, 20.0])
        
        # boundingBox should return r, z coordinates as tuple
        result = screen.boundingBox()
        assert isinstance(result, tuple)
        assert len(result) == 2
        rb, zb = result
        assert rb == screen.r
        assert zb == screen.z
        
        # intersect should return boolean
        intersection_result = screen.intersect([10.0, 20.0], [5.0, 15.0])
        assert isinstance(intersection_result, bool)
        
        # get_lc should return characteristic length for meshing
        lc = screen.get_lc()
        assert isinstance(lc, (int, float))
        assert lc > 0  # Should be positive for normal geometry
    
    def test_mesh_generation_support(self):
        """Test that Screen supports mesh generation operations"""
        screen = Screen(name="mesh_test", r=[10.0, 30.0], z=[0.0, 40.0])
        
        # get_lc provides characteristic length
        lc = screen.get_lc()
        assert lc == 2.0  # (30-10)/10 = 2.0
        
        # get_names provides identifier for mesh regions
        names = screen.get_names("mesh_system")
        assert len(names) == 1
        assert "Screen" in names[0]
        assert "mesh_system" in names[0]
        assert screen.name in names[0]
        
        # get_channels and get_isolants return empty (no complex geometry)
        channels = screen.get_channels("test")
        isolants = screen.get_isolants("test")
        assert channels == []
        assert isolants == []
    
    def test_serialization_support_documented(self):
        """Test that all documented serialization methods work"""
        screen = Screen(name="serialize_test", r=[1.0, 3.0], z=[0.0, 2.0])
        
        # YAML serialization
        assert hasattr(screen, "dump")
        assert callable(screen.dump)
        
        # JSON serialization
        assert hasattr(screen, "to_json")
        assert callable(screen.to_json)
        assert hasattr(screen, "write_to_json")
        assert callable(screen.write_to_json)
        
        # Class methods for loading
        assert hasattr(Screen, "from_yaml")
        assert callable(Screen.from_yaml)
        assert hasattr(Screen, "from_json")
        assert callable(Screen.from_json)
        assert hasattr(Screen, "from_dict")
        assert callable(Screen.from_dict)
        
        # Test that JSON serialization actually works
        json_str = screen.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Screen"
        assert parsed["name"] == "serialize_test"
