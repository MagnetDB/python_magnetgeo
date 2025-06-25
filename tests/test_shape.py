#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Shape class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the class under test
from python_magnetgeo.Shape import Shape, Shape_constructor

# Import test utilities
from .test_utils_common import (
    BaseSerializationTestMixin,
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_json_structure,
    assert_instance_attributes,
    validate_angle_data,
    parametrize_basic_values,
    temp_yaml_file,
    temp_json_file
)


class TestShape(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for Shape using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample Shape instance for testing"""
        return Shape(
            name="test_shape",
            profile="rectangular",
            length=[10.0, 15.0],
            angle=[45.0, 90.0],
            onturns=[1, 3],
            position="ABOVE"
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """
!<Shape>
name: test_shape
profile: rectangular
length: [10.0, 15.0]
angle: [45.0, 90.0]
onturns: [1, 3]
position: ABOVE
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_shape",
            "profile": "rectangular",
            "length": [10.0, 15.0],
            "angle": [45.0, 90.0],
            "onturns": [1, 3],
            "position": "ABOVE"
        }
    
    def get_class_under_test(self) -> Type:
        """Return the Shape class"""
        return Shape
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return Shape
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "Shape"


class TestShapeConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for Shape YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = Shape_constructor(loader, node)
            return result.__dict__, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "profile": "circular",
            "length": [20.0],
            "angle": [180.0],
            "onturns": [2],
            "position": "BELOW"
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "Shape"


class TestShapeSpecific:
    """
    Specific tests for Shape functionality not covered by mixins
    """
    
    @pytest.fixture
    def sample_shape(self):
        """Fixture providing a sample Shape instance"""
        return Shape(
            name="sample_cut",
            profile="trapezoidal",
            length=[12.0, 8.0, 15.0],
            angle=[60.0, 120.0, 180.0],
            onturns=[1, 2, 4],
            position="ALTERNATE"
        )
    
    @pytest.fixture
    def minimal_shape(self):
        """Fixture providing a Shape with minimal required parameters"""
        return Shape(name="minimal", profile="basic")
    
    @pytest.fixture
    def default_shape(self):
        """Fixture providing a Shape with default values"""
        return Shape(name="default", profile="default_profile")
    
    def test_init_minimal_required(self):
        """Test Shape initialization with minimal required parameters"""
        shape = Shape(name="test", profile="test_profile")
        assert shape.name == "test"
        assert shape.profile == "test_profile"
        assert shape.length == [0.0]  # Default value
        assert shape.angle == [0.0]   # Default value
        assert shape.onturns == [1]   # Default value
        assert shape.position == "ABOVE"  # Default value
    
    def test_init_with_all_parameters(self):
        """Test Shape initialization with all parameters"""
        shape = Shape(
            name="full_shape",
            profile="custom_profile",
            length=[5.0, 10.0, 15.0],
            angle=[30.0, 60.0, 90.0],
            onturns=[1, 2, 3],
            position="BELOW"
        )
        assert shape.name == "full_shape"
        assert shape.profile == "custom_profile"
        assert shape.length == [5.0, 10.0, 15.0]
        assert shape.angle == [30.0, 60.0, 90.0]
        assert shape.onturns == [1, 2, 3]
        assert shape.position == "BELOW"
    
    @pytest.mark.parametrize("position", ["ABOVE", "BELOW", "ALTERNATE"])
    def test_valid_positions(self, position):
        """Test Shape with valid position values"""
        shape = Shape(name="pos_test", profile="test", position=position)
        assert shape.position == position
    
    @pytest.mark.parametrize("position", ["above", "below", "alternate", "MIDDLE", "TOP", "BOTTOM"])
    def test_custom_positions(self, position):
        """Test Shape with custom position values (should accept any string)"""
        shape = Shape(name="custom_pos", profile="test", position=position)
        assert shape.position == position
    
    def test_repr(self, sample_shape):
        """Test string representation"""
        repr_str = repr(sample_shape)
        assert "Shape" in repr_str
        assert "name='sample_cut'" in repr_str
        assert "profile='trapezoidal'" in repr_str
        assert "length=[12.0, 8.0, 15.0]" in repr_str
        assert "angle=[60.0, 120.0, 180.0]" in repr_str
        assert "onturns=[1, 2, 4]" in repr_str
        assert "position='ALTERNATE'" in repr_str
    
    def test_repr_with_defaults(self, default_shape):
        """Test string representation with default values"""
        repr_str = repr(default_shape)
        assert "length=[0.0]" in repr_str
        assert "angle=[0.0]" in repr_str
        assert "onturns=[1]" in repr_str
        assert "position='ABOVE'" in repr_str
    
    def test_yaml_constructor_function_direct(self):
        """Test the Shape_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "profile": "direct_profile",
            "length": [25.0, 30.0],
            "angle": [45.0, 135.0],
            "onturns": [1, 3],
            "position": "BELOW"
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Shape_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Shape)
        assert result.name == "direct_test"
        assert result.profile == "direct_profile"
        assert result.length == [25.0, 30.0]
        assert result.angle == [45.0, 135.0]
        assert result.onturns == [1, 3]
        assert result.position == "BELOW"
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestShapeDataValidation:
    """
    Test Shape with various data types and validation scenarios
    """
    
    @pytest.mark.parametrize("length_input", [
        [0.0],
        [1.0],
        [5.0, 10.0],
        [1.0, 2.0, 3.0, 4.0, 5.0],
        [0.1, 0.2, 0.3],
        [100.0, 200.0, 300.0]
    ])
    def test_various_length_values(self, length_input):
        """Test Shape with various length values"""
        shape = Shape(name="length_test", profile="test", length=length_input)
        assert shape.length == length_input
        validate_angle_data(shape.length, allow_negative=False)
    
    @pytest.mark.parametrize("angle_input", [
        [0.0],
        [45.0],
        [90.0, 180.0],
        [30.0, 60.0, 90.0, 120.0],
        [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
        [360.0],  # Full circle
        [-45.0, 45.0],  # Negative angles
    ])
    def test_various_angle_values(self, angle_input):
        """Test Shape with various angle values"""
        shape = Shape(name="angle_test", profile="test", angle=angle_input)
        assert shape.angle == angle_input
        validate_angle_data(shape.angle, allow_negative=True, max_angle=360.0)
    
    @pytest.mark.parametrize("onturns_input", [
        [1],
        [1, 2],
        [1, 2, 3, 4, 5],
        [0],  # Edge case: turn 0
        [10, 20, 30],  # Large turn numbers
    ])
    def test_various_onturns_values(self, onturns_input):
        """Test Shape with various onturns values"""
        shape = Shape(name="turns_test", profile="test", onturns=onturns_input)
        assert shape.onturns == onturns_input
        
        # Validate that all are integers
        for turn in shape.onturns:
            assert isinstance(turn, int)
    
    @pytest.mark.parametrize("profile_name", [
        "rectangular",
        "circular",
        "trapezoidal",
        "triangular",
        "custom_profile_123",
        "profile-with-dashes",
        "profile_with_underscores",
        "UPPERCASE_PROFILE",
        "MixedCaseProfile",
        "",  # Empty profile
    ])
    def test_various_profile_names(self, profile_name):
        """Test Shape with various profile names"""
        shape = Shape(name="profile_test", profile=profile_name)
        assert shape.profile == profile_name
    
    def test_mismatched_list_lengths(self):
        """Test Shape with mismatched list lengths (should be allowed)"""
        shape = Shape(
            name="mismatched",
            profile="test",
            length=[10.0, 20.0, 30.0],  # 3 elements
            angle=[45.0, 90.0],         # 2 elements
            onturns=[1]                 # 1 element
        )
        # Should create successfully - implementation decides how to handle
        assert len(shape.length) == 3
        assert len(shape.angle) == 2
        assert len(shape.onturns) == 1
    
    def test_empty_lists(self):
        """Test Shape with empty lists"""
        shape = Shape(
            name="empty_lists",
            profile="test",
            length=[],
            angle=[],
            onturns=[]
        )
        assert shape.length == []
        assert shape.angle == []
        assert shape.onturns == []
    
    def test_single_value_lists(self):
        """Test Shape with single-value lists"""
        shape = Shape(
            name="single_values",
            profile="test",
            length=[42.0],
            angle=[90.0],
            onturns=[5]
        )
        assert shape.length == [42.0]
        assert shape.angle == [90.0]
        assert shape.onturns == [5]




class TestShapeIntegration:
    """
    Integration tests for Shape
    """
    
    def test_yaml_roundtrip_structure(self, temp_yaml_file):
        """Test YAML structure for Shape"""
        shape = Shape(
            name="yaml_test",
            profile="yaml_profile",
            length=[10.0, 20.0],
            angle=[45.0, 90.0],
            onturns=[1, 2],
            position="ALTERNATE"
        )
        
        yaml_content = f"""!<Shape>
name: {shape.name}
profile: {shape.profile}
length: {shape.length}
angle: {shape.angle}
onturns: {shape.onturns}
position: {shape.position}
"""
        temp_yaml_file.write(yaml_content)
        temp_yaml_file.flush()
        
        with open(temp_yaml_file.name, 'r') as f:
            content = f.read()
            assert "!<Shape>" in content
            assert shape.name in content
            assert shape.profile in content
            assert shape.position in content
    
    def test_json_serialization_completeness(self):
        """Test complete JSON serialization"""
        shape = Shape(
            name="json_complete",
            profile="json_profile",
            length=[5.0, 10.0, 15.0],
            angle=[30.0, 60.0, 90.0],
            onturns=[1, 3, 5],
            position="BELOW"
        )
        
        json_str = shape.to_json()
        parsed = json.loads(json_str)
        
        # Verify all fields are present
        expected_keys = {"__classname__", "name", "profile", "length", "angle", "onturns", "position"}
        assert set(parsed.keys()) == expected_keys
        
        # Verify values are preserved
        assert parsed["__classname__"] == "Shape"
        assert parsed["name"] == "json_complete"
        assert parsed["profile"] == "json_profile"
        assert parsed["length"] == [5.0, 10.0, 15.0]
        assert parsed["angle"] == [30.0, 60.0, 90.0]
        assert parsed["onturns"] == [1, 3, 5]
        assert parsed["position"] == "BELOW"
    
    def test_constructor_integration_comprehensive(self):
        """Test Shape_constructor with comprehensive data"""
        comprehensive_data = {
            "name": "comprehensive_shape",
            "profile": "comprehensive_profile",
            "length": [1.0, 2.0, 3.0, 4.0, 5.0],
            "angle": [0.0, 72.0, 144.0, 216.0, 288.0],  # Pentagon angles
            "onturns": [1, 2, 3, 4, 5],
            "position": "ALTERNATE"
        }
        
        mock_loader = Mock()
        mock_node = Mock()
        mock_loader.construct_mapping.return_value = comprehensive_data
        
        result = Shape_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Shape)
        assert result.name == "comprehensive_shape"
        assert result.profile == "comprehensive_profile"
        assert result.length == [1.0, 2.0, 3.0, 4.0, 5.0]
        assert result.angle == [0.0, 72.0, 144.0, 216.0, 288.0]
        assert result.onturns == [1, 2, 3, 4, 5]
        assert result.position == "ALTERNATE"


class TestShapePerformance:
    """
    Performance tests for Shape operations
    """
    
    @pytest.mark.performance
    def test_large_data_performance(self):
        """Test Shape performance with large datasets"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        # Create large datasets
        large_length = [float(i) for i in range(1000)]
        large_angle = [float(i * 0.36) for i in range(1000)]
        large_onturns = list(range(1, 1001))
        
        def create_large_shape():
            return Shape(
                name="performance_test",
                profile="large_profile",
                length=large_length,
                angle=large_angle,
                onturns=large_onturns
            )
        
        result, execution_time = time_function_execution(create_large_shape)
        
        # Should handle large datasets efficiently
        assert_performance_within_limits(execution_time, 0.05)  # 50ms limit
        assert len(result.length) == 1000
        assert len(result.angle) == 1000
        assert len(result.onturns) == 1000
    
    @pytest.mark.performance
    def test_json_serialization_large_data(self):
        """Test JSON serialization performance with large data"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        shape = Shape(
            name="large_json_test",
            profile="large_profile",
            length=[float(i) for i in range(500)],
            angle=[float(i * 0.72) for i in range(500)],
            onturns=list(range(1, 501))
        )
        
        result, execution_time = time_function_execution(shape.to_json)
        
        # JSON serialization should be reasonably fast even with large data
        assert_performance_within_limits(execution_time, 0.1)  # 100ms limit
        assert isinstance(result, str)
        assert len(result) > 1000  # Should be substantial JSON
    
    @pytest.mark.performance
    def test_repr_performance_large_data(self):
        """Test repr performance with large data"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        shape = Shape(
            name="x" * 100,  # Long name
            profile="y" * 100,  # Long profile
            length=[1.0] * 100,
            angle=[45.0] * 100,
            onturns=list(range(100))
        )
        
        result, execution_time = time_function_execution(repr, shape)
        
        # Repr should be fast even with large data
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert "Shape" in result
        assert len(result) > 100


class TestShapeErrorHandling:
    """
    Test error handling and robustness for Shape
    """
    
    def test_constructor_missing_required_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'name' field
        incomplete_data = {
            "profile": "test_profile",
            "length": [10.0],
            "angle": [45.0],
            "onturns": [1],
            "position": "ABOVE"
        }
        mock_loader.construct_mapping.return_value = incomplete_data
        
        with pytest.raises(KeyError):
            Shape_constructor(mock_loader, mock_node)
        
        # Missing 'profile' field
        incomplete_data2 = {
            "name": "test_name",
            "length": [10.0],
            "angle": [45.0],
            "onturns": [1],
            "position": "ABOVE"
        }
        mock_loader.construct_mapping.return_value = incomplete_data2
        
        with pytest.raises(KeyError):
            Shape_constructor(mock_loader, mock_node)
    
    def test_constructor_with_extra_fields(self):
        """Test constructor with extra fields (should be ignored)"""
        mock_loader = Mock()
        mock_node = Mock()
        
        data_with_extras = {
            "name": "extra_fields_test",
            "profile": "test_profile",
            "length": [10.0],
            "angle": [45.0],
            "onturns": [1],
            "position": "ABOVE",
            "extra_field": "should_be_ignored",
            "another_extra": [1, 2, 3],
            "yet_another": {"nested": "data"}
        }
        mock_loader.construct_mapping.return_value = data_with_extras
        
        # Should work fine, ignoring extra fields
        result = Shape_constructor(mock_loader, mock_node)
        assert isinstance(result, Shape)
        assert result.name == "extra_fields_test"
        assert result.profile == "test_profile"
        assert not hasattr(result, "extra_field")
        assert not hasattr(result, "another_extra")
        assert not hasattr(result, "yet_another")
    
    def test_json_serialization_with_problematic_data(self):
        """Test JSON serialization with potentially problematic data"""
        # Test with very large numbers
        shape = Shape(
            name="problematic",
            profile="test",
            length=[1e100, 1e-100],  # Very large and very small
            angle=[float('nan')],    # This might cause issues
            onturns=[2**31 - 1]      # Large integer
        )
        
        # Should handle gracefully or raise appropriate exception
        try:
            json_str = shape.to_json()
            # If it succeeds, should be valid JSON
            parsed = json.loads(json_str)
            assert parsed["name"] == "problematic"
        except (ValueError, OverflowError, TypeError) as e:
            # Acceptable to fail with these exceptions for problematic data
            assert isinstance(e, (ValueError, OverflowError, TypeError))
    
    def test_from_yaml_error_handling(self):
        """Test from_yaml error handling"""
        # Test with non-existent file
        with pytest.raises(Exception):  # Could be FileNotFoundError or other
            Shape.from_yaml("nonexistent_file.yaml")
    
    def test_from_json_error_handling(self):
        """Test from_json error handling"""
        # Test with non-existent file
        with pytest.raises(Exception):  # Could be FileNotFoundError or other
            Shape.from_json("nonexistent_file.json")


class TestShapeCompatibility:
    """
    Test Shape compatibility with different data types and edge cases
    """
    
    def test_mixed_numeric_types(self):
        """Test Shape with mixed numeric types (int, float)"""
        shape = Shape(
            name="mixed_types",
            profile="test",
            length=[1, 2.0, 3, 4.5],  # Mix of int and float
            angle=[45, 90.0, 135, 180.5],  # Mix of int and float
            onturns=[1, 2, 3, 4]  # All int (as expected)
        )
        
        # All should be converted to appropriate types
        assert shape.length == [1, 2.0, 3, 4.5]
        assert shape.angle == [45, 90.0, 135, 180.5]
        assert shape.onturns == [1, 2, 3, 4]
    
    def test_string_representations_in_json(self):
        """Test that string fields are properly quoted in JSON"""
        shape = Shape(
            name='name"with"quotes',
            profile="profile\\with\\backslashes",
            position="position\nwith\nnewlines"
        )
        
        json_str = shape.to_json()
        parsed = json.loads(json_str)  # Should not raise exception
        
        assert parsed["name"] == 'name"with"quotes'
        assert parsed["profile"] == "profile\\with\\backslashes"
        assert parsed["position"] == "position\nwith\nnewlines"
    
    def test_comparison_consistency(self):
        """Test that identical shapes have consistent representations"""
        shape1 = Shape(
            name="identical",
            profile="same_profile",
            length=[10.0, 20.0],
            angle=[45.0, 90.0],
            onturns=[1, 2],
            position="ABOVE"
        )
        
        shape2 = Shape(
            name="identical",
            profile="same_profile",
            length=[10.0, 20.0],
            angle=[45.0, 90.0],
            onturns=[1, 2],
            position="ABOVE"
        )
        
        # Should have identical string representations
        assert repr(shape1) == repr(shape2)
        assert shape1.to_json() == shape2.to_json()
    
    def test_floating_point_precision(self):
        """Test Shape with floating point precision edge cases"""
        precise_values = [
            1.0000000000001,
            1.9999999999999,
            0.1 + 0.2,  # Classic floating point precision issue
            1e-15,
            1e15
        ]
        
        shape = Shape(
            name="precision_test",
            profile="test",
            length=precise_values,
            angle=precise_values
        )
        
        # Values should be preserved as-is
        assert shape.length == precise_values
        assert shape.angle == precise_values
        
        # JSON serialization should handle these values
        json_str = shape.to_json()
        parsed = json.loads(json_str)
        
        # Should be reasonably close (within floating point precision)
        for i, val in enumerate(precise_values):
            assert abs(parsed["length"][i] - val) < 1e-10
            assert abs(parsed["angle"][i] - val) < 1e-10


class TestShapeUseCases:
    """
    Test Shape with realistic use cases and scenarios
    """
    
    def test_rectangular_cut_scenario(self):
        """Test Shape configured for rectangular cuts"""
        rect_cut = Shape(
            name="rectangular_channel",
            profile="rectangular",
            length=[10.0, 10.0, 10.0, 10.0],  # 4 identical cuts
            angle=[0.0, 90.0, 180.0, 270.0],   # Evenly spaced around
            onturns=[1, 1, 1, 1],              # All on first turn
            position="ABOVE"
        )
        
        assert rect_cut.name == "rectangular_channel"
        assert rect_cut.profile == "rectangular"
        assert len(rect_cut.length) == 4
        assert len(rect_cut.angle) == 4
        assert len(rect_cut.onturns) == 4
        assert rect_cut.position == "ABOVE"
        
        # Verify angles are properly distributed
        assert rect_cut.angle == [0.0, 90.0, 180.0, 270.0]
    
    def test_spiral_cut_scenario(self):
        """Test Shape configured for spiral cuts"""
        spiral_cut = Shape(
            name="spiral_cooling",
            profile="trapezoidal",
            length=[15.0, 12.0, 10.0, 8.0, 6.0],  # Decreasing length
            angle=[0.0, 72.0, 144.0, 216.0, 288.0], # Pentagon pattern
            onturns=[1, 2, 3, 4, 5],                # Different turns
            position="ALTERNATE"
        )
        
        assert spiral_cut.name == "spiral_cooling"
        assert spiral_cut.profile == "trapezoidal"
        assert len(spiral_cut.length) == 5
        assert len(spiral_cut.angle) == 5
        assert len(spiral_cut.onturns) == 5
        assert spiral_cut.position == "ALTERNATE"
        
        # Verify spiral pattern
        assert spiral_cut.length == [15.0, 12.0, 10.0, 8.0, 6.0]
        assert spiral_cut.onturns == [1, 2, 3, 4, 5]
    
    def test_micro_channel_scenario(self):
        """Test Shape configured for micro-channels"""
        micro_channels = Shape(
            name="micro_cooling_channels",
            profile="circular",
            length=[0.5] * 20,  # 20 small identical channels
            angle=[i * 18.0 for i in range(20)],  # Every 18 degrees (360/20)
            onturns=[1] * 20,   # All on same turn
            position="BELOW"
        )
        
        assert micro_channels.name == "micro_cooling_channels"
        assert micro_channels.profile == "circular"
        assert len(micro_channels.length) == 20
        assert len(micro_channels.angle) == 20
        assert len(micro_channels.onturns) == 20
        assert all(length == 0.5 for length in micro_channels.length)
        assert all(turn == 1 for turn in micro_channels.onturns)
        assert micro_channels.position == "BELOW"
    
    def test_asymmetric_cut_scenario(self):
        """Test Shape with asymmetric cutting pattern"""
        asymmetric_cut = Shape(
            name="asymmetric_stress_relief",
            profile="triangular",
            length=[20.0, 15.0, 25.0],  # Different lengths
            angle=[30.0, 150.0, 270.0], # Asymmetric placement
            onturns=[1, 3, 5],          # Odd turns only
            position="ALTERNATE"
        )
        
        assert asymmetric_cut.name == "asymmetric_stress_relief"
        assert asymmetric_cut.profile == "triangular"
        assert asymmetric_cut.length == [20.0, 15.0, 25.0]
        assert asymmetric_cut.angle == [30.0, 150.0, 270.0]
        assert asymmetric_cut.onturns == [1, 3, 5]
        assert asymmetric_cut.position == "ALTERNATE"
    
    def test_single_cut_scenario(self):
        """Test Shape with single cut configuration"""
        single_cut = Shape(
            name="single_access_port",
            profile="rectangular",
            length=[30.0],
            angle=[0.0],
            onturns=[1],
            position="ABOVE"
        )
        
        assert single_cut.name == "single_access_port"
        assert single_cut.profile == "rectangular"
        assert single_cut.length == [30.0]
        assert single_cut.angle == [0.0]
        assert single_cut.onturns == [1]
        assert single_cut.position == "ABOVE"


class TestShapeDocumentation:
    """
    Test that Shape behavior matches its documentation
    """
    
    def test_documented_parameters(self):
        """Test that Shape accepts all documented parameters"""
        # Based on the docstring in the Shape class
        documented_shape = Shape(
            name="documented_test",
            profile="profile_name",  # Name of the cut profile
            length=[10.0, 15.0],     # Angular length in degrees
            angle=[45.0, 135.0],     # Angle between consecutive shapes
            onturns=[1, 2],          # Which turns to add cuts
            position="ABOVE"         # ABOVE|BELOW|ALTERNATE
        )
        
        assert documented_shape.name == "documented_test"
        assert documented_shape.profile == "profile_name"
        assert documented_shape.length == [10.0, 15.0]
        assert documented_shape.angle == [45.0, 135.0]
        assert documented_shape.onturns == [1, 2]
        assert documented_shape.position == "ABOVE"
    
    def test_position_values_documented(self):
        """Test documented position values"""
        valid_positions = ["ABOVE", "BELOW", "ALTERNATE"]
        
        for position in valid_positions:
            shape = Shape(name="pos_test", profile="test", position=position)
            assert shape.position == position
    
    def test_angle_as_degrees(self):
        """Test that angles are treated as degrees (as documented)"""
        shape = Shape(
            name="degree_test",
            profile="test",
            angle=[0.0, 90.0, 180.0, 270.0, 360.0]  # Full circle in degrees
        )
        
        assert shape.angle == [0.0, 90.0, 180.0, 270.0, 360.0]
        
        # JSON should preserve degree values
        json_str = shape.to_json()
        parsed = json.loads(json_str)
        assert parsed["angle"] == [0.0, 90.0, 180.0, 270.0, 360.0]
    
    def test_length_as_angular_degrees(self):
        """Test that length represents angular length in degrees"""
        shape = Shape(
            name="angular_length_test",
            profile="test",
            length=[5.0, 10.0, 15.0, 30.0, 45.0, 60.0, 90.0]  # Various angular lengths
        )
        
        assert shape.length == [5.0, 10.0, 15.0, 30.0, 45.0, 60.0, 90.0]
        
        # All values should be reasonable for angular measurements
        for length in shape.length:
            assert 0.0 <= length <= 360.0  # Reasonable range for angular length
