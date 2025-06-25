#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for OuterCurrentLead class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the class under test
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead, OuterCurrentLead_constructor

# Import test utilities
from .test_utils_common import (
    BaseSerializationTestMixin,
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_json_structure,
    assert_instance_attributes,
    parametrize_basic_values,
    temp_yaml_file,
    temp_json_file,
    validate_geometric_data,
    validate_angle_data,
    time_function_execution,
    assert_performance_within_limits
)


class TestOuterCurrentLead(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for OuterCurrentLead using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample OuterCurrentLead instance for testing"""
        return OuterCurrentLead(
            name="test_outer_lead",
            r=[150.0, 200.0],  # Outer radius range
            h=300.0,           # Height
            bar=[25.0, 30.0, 15.0, 250.0],  # Bar configuration [R, DX, DY, L]
            support=[10.0, 20.0, 45.0, 0.0]  # Support configuration [DX0, DZ, Angle, Angle_Zero]
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """!<OuterCurrentLead>
name: test_outer_lead
r: [150.0, 200.0]
h: 300.0
bar: [25.0, 30.0, 15.0, 250.0]
support: [10.0, 20.0, 45.0, 0.0]
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_outer_lead",
            "r": [150.0, 200.0],
            "h": 300.0,
            "bar": [25.0, 30.0, 15.0, 250.0],
            "support": [10.0, 20.0, 45.0, 0.0]
        }
    
    def get_class_under_test(self) -> Type:
        """Return the OuterCurrentLead class"""
        return OuterCurrentLead
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return OuterCurrentLead
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "OuterCurrentLead"


class TestOuterCurrentLeadConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for OuterCurrentLead YAML constructor
    Note: Original constructor has a bug (infinite recursion), tests intended behavior
    """
    
    def get_constructor_function(self):
        """Return a corrected YAML constructor function"""
        def wrapper(loader, node):
            result = OuterCurrentLead_constructor(loader, node)
            return result.__dict__, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "r": [120.0, 180.0],
            "h": 350.0,
            "bar": [20.0, 25.0, 12.0, 300.0],
            "support": [8.0, 15.0, 30.0, 90.0]
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "OuterCurrentLead"


class TestOuterCurrentLeadInitialization:
    """
    Test OuterCurrentLead initialization and basic properties
    """
    
    @pytest.fixture
    def sample_outer_lead(self):
        """Fixture providing a sample OuterCurrentLead instance"""
        return OuterCurrentLead(
            name="sample_outer",
            r=[100.0, 150.0],
            h=400.0,
            bar=[30.0, 40.0, 20.0, 350.0],
            support=[12.0, 25.0, 60.0, 30.0]
        )
    
    @pytest.fixture
    def minimal_outer_lead(self):
        """Fixture providing a minimal OuterCurrentLead instance"""
        return OuterCurrentLead(name="minimal")
    
    def test_init_with_all_parameters(self):
        """Test OuterCurrentLead initialization with all parameters"""
        lead = OuterCurrentLead(
            name="full_outer_lead",
            r=[80.0, 120.0],
            h=250.0,
            bar=[20.0, 25.0, 10.0, 200.0],
            support=[5.0, 15.0, 90.0, 45.0]
        )
        assert lead.name == "full_outer_lead"
        assert lead.r == [80.0, 120.0]
        assert lead.h == 250.0
        assert lead.bar == [20.0, 25.0, 10.0, 200.0]
        assert lead.support == [5.0, 15.0, 90.0, 45.0]
    
    def test_init_with_defaults(self):
        """Test OuterCurrentLead initialization with default values"""
        lead = OuterCurrentLead(name="default_outer")
        assert lead.name == "default_outer"
        assert lead.r == []      # Default empty list
        assert lead.h == 0.0     # Default value
        assert lead.bar == []    # Default empty list
        assert lead.support == [] # Default empty list
    
    @pytest.mark.parametrize("name,r,h,expected_valid", [
        ("valid_lead", [100.0, 150.0], 200.0, True),
        ("zero_height", [100.0, 150.0], 0.0, True),
        ("negative_height", [100.0, 150.0], -10.0, True),  # Negative allowed for flexibility
        ("single_radius", [120.0], 200.0, True),  # Single radius allowed
        ("empty_name", [100.0, 150.0], 200.0, True),  # Empty name allowed
        ("empty_radius", [], 200.0, True),  # Empty radius list allowed
    ])
    def test_init_parameter_validation(self, name, r, h, expected_valid):
        """Test initialization with various parameter combinations"""
        if expected_valid:
            lead = OuterCurrentLead(name=name, r=r, h=h)
            assert lead.name == name
            assert lead.r == r
            assert lead.h == h
        else:
            with pytest.raises((ValueError, TypeError)):
                OuterCurrentLead(name=name, r=r, h=h)
    
    def test_repr(self, sample_outer_lead):
        """Test string representation"""
        repr_str = repr(sample_outer_lead)
        assert "OuterCurrentLead" in repr_str
        assert "name='sample_outer'" in repr_str
        assert "r=[100.0, 150.0]" in repr_str
        assert "h=400.0" in repr_str
        assert "bar=[30.0, 40.0, 20.0, 350.0]" in repr_str
        assert "support=[12.0, 25.0, 60.0, 30.0]" in repr_str
    
    def test_attribute_types(self, sample_outer_lead):
        """Test that attributes have correct types"""
        assert isinstance(sample_outer_lead.name, str)
        assert isinstance(sample_outer_lead.r, list)
        assert isinstance(sample_outer_lead.h, (int, float))
        assert isinstance(sample_outer_lead.bar, list)
        assert isinstance(sample_outer_lead.support, list)


class TestOuterCurrentLeadSerialization:
    """
    Test serialization methods (dump, to_json, write_to_json)
    """
    
    @pytest.fixture
    def serialization_lead(self):
        """Lead instance for serialization testing"""
        return OuterCurrentLead(
            name="serialize_test",
            r=[140.0, 190.0],
            h=380.0,
            bar=[32.0, 38.0, 18.0, 320.0],
            support=[14.0, 28.0, 50.0, 25.0]
        )
    
    def test_dump_success(self, serialization_lead):
        """Test dump method success"""
        with patch("python_magnetgeo.utils.writeYaml") as mock_write_yaml:
            serialization_lead.dump()
            mock_write_yaml.assert_called_once_with(
                "OuterCurrentLead", serialization_lead, OuterCurrentLead
            )
    
    def test_dump_failure(self, serialization_lead):
        """Test dump method failure handling"""
        with patch("python_magnetgeo.utils.writeYaml", side_effect=Exception("YAML error")):
            with pytest.raises(Exception, match="YAML error"):
                serialization_lead.dump()
    
    def test_to_json_structure(self, serialization_lead):
        """Test to_json returns properly structured JSON"""
        json_str = serialization_lead.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["__classname__"] == "OuterCurrentLead"
        assert parsed["name"] == "serialize_test"
        assert parsed["r"] == [140.0, 190.0]
        assert parsed["h"] == 380.0
        assert parsed["bar"] == [32.0, 38.0, 18.0, 320.0]
        assert parsed["support"] == [14.0, 28.0, 50.0, 25.0]
    
    def test_write_to_json_success(self, serialization_lead):
        """Test write_to_json method success"""
        with patch("builtins.open", mock_open()) as mock_file:
            serialization_lead.write_to_json()
            mock_file.assert_called_once_with("serialize_test.json", "w")
    
    def test_write_to_json_failure(self, serialization_lead):
        """Test write_to_json method failure handling"""
        with patch("builtins.open", side_effect=IOError("File error")):
            with pytest.raises(Exception, match="Failed to write to serialize_test.json"):
                serialization_lead.write_to_json()
    
    def test_write_to_json_content(self, serialization_lead):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            serialization_lead.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "OuterCurrentLead"
            assert parsed["name"] == "serialize_test"


class TestOuterCurrentLeadDeserialization:
    """
    Test deserialization methods (from_yaml, from_json, from_dict)
    """
    
    def test_from_dict_complete(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_test",
            "r": [110.0, 160.0],
            "h": 380.0,
            "bar": [28.0, 35.0, 18.0, 320.0],
            "support": [9.0, 22.0, 50.0, 20.0]
        }
        
        lead = OuterCurrentLead.from_dict(data)
        
        assert lead.name == "dict_test"
        assert lead.r == [110.0, 160.0]
        assert lead.h == 380.0
        assert lead.bar == [28.0, 35.0, 18.0, 320.0]
        assert lead.support == [9.0, 22.0, 50.0, 20.0]
    
    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_test",
            "r": [50.0, 70.0],
            "h": 100.0,
            "bar": [10.0, 12.0, 6.0, 80.0],
            "support": [3.0, 8.0, 30.0, 0.0]
        }
        
        lead = OuterCurrentLead.from_dict(data, debug=True)
        assert lead.name == "debug_test"
    
    def test_from_dict_missing_fields(self):
        """Test from_dict with missing required fields"""
        # Missing 'name'
        data1 = {
            "r": [50.0, 70.0],
            "h": 100.0,
            "bar": [10.0, 12.0, 6.0, 80.0],
            "support": [3.0, 8.0, 30.0, 0.0]
        }
        
        with pytest.raises(KeyError):
            OuterCurrentLead.from_dict(data1)
    
    def test_from_yaml_integration(self):
        """Test from_yaml integration"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load_yaml:
            mock_lead = Mock(spec=OuterCurrentLead)
            mock_load_yaml.return_value = mock_lead
            
            result = OuterCurrentLead.from_yaml("test.yaml", debug=True)
            
            mock_load_yaml.assert_called_once_with("OuterCurrentLead", "test.yaml", OuterCurrentLead, True)
            assert result == mock_lead
    
    def test_from_json_integration(self):
        """Test from_json integration"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load_json:
            mock_lead = Mock(spec=OuterCurrentLead)
            mock_load_json.return_value = mock_lead
            
            result = OuterCurrentLead.from_json("test.json", debug=False)
            
            mock_load_json.assert_called_once_with("OuterCurrentLead", "test.json", False)
            assert result == mock_lead


class TestOuterCurrentLeadBarConfiguration:
    """
    Test bar configuration functionality
    Based on documentation: [R, DX, DY, L] - rectangle cut by disk
    """
    
    @pytest.mark.parametrize("bar,description", [
        ([25.0, 30.0, 15.0, 250.0], "standard_bar"),
        ([20.0, 25.0, 10.0, 200.0], "compact_bar"),
        ([35.0, 40.0, 20.0, 300.0], "large_bar"),
        ([], "no_bar"),
        ([30.0], "incomplete_bar"),
        ([30.0, 35.0], "partial_bar"),
        ([30.0, 35.0, 18.0], "missing_length"),
    ])
    def test_various_bar_configurations(self, bar, description):
        """Test OuterCurrentLead with various bar configurations"""
        lead = OuterCurrentLead(
            name=f"bar_{description}",
            r=[100.0, 150.0],
            h=300.0,
            bar=bar
        )
        assert lead.bar == bar
        assert description in lead.name
    
    def test_bar_parameters_structure(self):
        """Test bar parameters according to documentation"""
        # Based on docstring: [R, DX, DY, L]
        # R: disk radius for cutting rectangle
        # DX, DY: rectangle dimensions  
        # L: prism length
        bar = [25.0, 30.0, 15.0, 250.0]
        lead = OuterCurrentLead(
            name="bar_params",
            r=[150.0, 200.0],
            bar=bar
        )
        
        assert len(lead.bar) == 4
        assert lead.bar[0] == 25.0  # R (disk radius)
        assert lead.bar[1] == 30.0  # DX (rectangle width)
        assert lead.bar[2] == 15.0  # DY (rectangle height)
        assert lead.bar[3] == 250.0 # L (prism length)
    
    def test_bar_geometry_constraints(self):
        """Test geometric constraints for bar configuration"""
        r = [100.0, 150.0]
        bar = [20.0, 30.0, 15.0, 200.0]
        
        lead = OuterCurrentLead(name="bar_geometry", r=r, h=300.0, bar=bar)
        
        # Validate bar parameters if complete
        if len(lead.bar) >= 4:
            # All bar dimensions should be positive
            assert all(dim >= 0 for dim in lead.bar)
            
            # Bar disk radius should be reasonable
            if len(lead.r) >= 2:
                assert lead.bar[0] <= lead.r[1]  # Bar radius <= outer radius (typical)


class TestOuterCurrentLeadSupportConfiguration:
    """
    Test support configuration functionality
    Based on documentation: [DX0, DZ, Angle, Angle_Zero]
    """
    
    @pytest.mark.parametrize("support,description", [
        ([10.0, 20.0, 45.0, 0.0], "standard_support"),
        ([15.0, 25.0, 90.0, 45.0], "rotated_support"),
        ([5.0, 10.0, 30.0, 15.0], "angled_support"),
        ([0.0, 0.0, 0.0, 0.0], "zero_support"),
        ([], "no_support"),
        ([12.0, 18.0], "incomplete_support"),
        ([12.0, 18.0, 60.0], "missing_angle_zero"),
    ])
    def test_various_support_configurations(self, support, description):
        """Test OuterCurrentLead with various support configurations"""
        lead = OuterCurrentLead(
            name=f"support_{description}",
            r=[100.0, 150.0],
            h=300.0,
            support=support
        )
        assert lead.support == support
        assert description in lead.name
    
    def test_support_parameters_structure(self):
        """Test support parameters according to documentation"""
        # Based on docstring: [DX0, DZ, Angle, Angle_Zero]
        support = [10.0, 20.0, 45.0, 0.0]
        lead = OuterCurrentLead(
            name="support_params",
            r=[150.0, 200.0],
            support=support
        )
        
        assert len(lead.support) == 4
        assert lead.support[0] == 10.0  # DX0
        assert lead.support[1] == 20.0  # DZ (vertical offset)
        assert lead.support[2] == 45.0  # Angle
        assert lead.support[3] == 0.0   # Angle_Zero (reference angle)
    
    def test_support_angular_values(self):
        """Test support with various angular configurations"""
        angle_configs = [
            ([10.0, 15.0, 0.0, 0.0], "aligned"),
            ([10.0, 15.0, 90.0, 0.0], "perpendicular"),
            ([10.0, 15.0, 180.0, 90.0], "opposite"),
            ([10.0, 15.0, 360.0, 0.0], "full_circle"),
            ([10.0, 15.0, 45.0, 315.0], "diagonal"),
        ]
        
        for support, description in angle_configs:
            lead = OuterCurrentLead(
                name=f"angles_{description}",
                r=[100.0, 150.0],
                support=support
            )
            assert lead.support[2] == support[2]  # Angle
            assert lead.support[3] == support[3]  # Angle_Zero
            
            # Validate angles if complete support configuration
            if len(lead.support) >= 4:
                validate_angle_data([lead.support[2], lead.support[3]], 
                                   allow_negative=True, max_angle=360.0)


class TestOuterCurrentLeadGeometry:
    """
    Test geometric aspects of OuterCurrentLead
    """
    
    @pytest.fixture
    def geometric_lead(self):
        """Fixture with realistic OuterCurrentLead geometry"""
        return OuterCurrentLead(
            name="geometric_test",
            r=[120.0, 180.0],
            h=350.0,
            bar=[30.0, 40.0, 20.0, 300.0],
            support=[15.0, 25.0, 60.0, 30.0]
        )
    
    def test_radius_validation(self, geometric_lead):
        """Test radius parameters"""
        if len(geometric_lead.r) >= 2:
            assert geometric_lead.r[0] <= geometric_lead.r[1]  # Inner <= Outer
            assert all(r >= 0 for r in geometric_lead.r)  # Non-negative values
        elif len(geometric_lead.r) == 1:
            assert geometric_lead.r[0] >= 0  # Single radius non-negative
    
    def test_height_validation(self, geometric_lead):
        """Test height parameter"""
        assert isinstance(geometric_lead.h, (int, float))
        assert geometric_lead.h >= 0  # Non-negative height
    
    def test_bar_to_lead_relationship(self, geometric_lead):
        """Test bar geometry fits within lead geometry"""
        if len(geometric_lead.bar) >= 4:
            bar_length = geometric_lead.bar[3]  # L parameter
            lead_height = geometric_lead.h
            
            # Bar length should be reasonable relative to lead height
            # Allow some flexibility for engineering designs
            if lead_height > 0:
                assert bar_length <= lead_height * 1.2  # Allow 20% overhang


class TestOuterCurrentLeadYAMLConstructor:
    """
    Test YAML constructor functionality
    Note: Original constructor has a bug (infinite recursion)
    """
    
    def test_yaml_constructor_function_direct(self):
        """Test the OuterCurrentLead_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "r": [120.0, 180.0],
            "h": 350.0,
            "bar": [20.0, 25.0, 12.0, 300.0],
            "support": [8.0, 15.0, 30.0, 90.0]
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = OuterCurrentLead_constructor(mock_loader, mock_node)
        
        assert isinstance(result, OuterCurrentLead)
        assert result.name == "direct_test"
        assert result.r == [120.0, 180.0]
        assert result.h == 350.0
        assert result.bar == [20.0, 25.0, 12.0, 300.0]
        assert result.support == [8.0, 15.0, 30.0, 90.0]
        mock_loader.construct_mapping.assert_called_once_with(mock_node)
    
    def test_constructor_missing_required_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'name' field
        incomplete_data = {
            "r": [100.0, 150.0],
            "h": 200.0,
            "bar": [20.0, 25.0, 12.0, 180.0],
            "support": [8.0, 15.0, 30.0, 0.0]
        }
        mock_loader.construct_mapping.return_value = incomplete_data
        
        with pytest.raises(KeyError):
            OuterCurrentLead_constructor(mock_loader, mock_node)
    
    def test_constructor_with_extra_fields(self):
        """Test constructor handles extra fields gracefully"""
        mock_loader = Mock()
        mock_node = Mock()
        
        data_with_extras = {
            "name": "extra_fields_test",
            "r": [100.0, 150.0],
            "h": 200.0,
            "bar": [20.0, 25.0, 12.0, 180.0],
            "support": [8.0, 15.0, 30.0, 0.0],
            "extra_field": "should_be_ignored",
            "another_extra": {"nested": "data"}
        }
        mock_loader.construct_mapping.return_value = data_with_extras
        
        # Should work fine, ignoring extra fields
        result = OuterCurrentLead_constructor(mock_loader, mock_node)
        assert isinstance(result, OuterCurrentLead)
        assert result.name == "extra_fields_test"
        assert not hasattr(result, "extra_field")
        assert not hasattr(result, "another_extra")


class TestOuterCurrentLeadErrorHandling:
    """
    Test error handling and edge cases
    """
    
    def test_serialization_errors(self):
        """Test serialization error handling"""
        lead = OuterCurrentLead(name="error_test", r=[100.0, 120.0])
        
        # Test to_json serialization error
        with patch("python_magnetgeo.deserialize.serialize_instance", 
                   side_effect=TypeError("Serialization error")):
            with pytest.raises(TypeError):
                lead.to_json()
    
    def test_file_operation_errors(self):
        """Test file operation error handling"""
        lead = OuterCurrentLead(name="file_error_test", r=[100.0, 120.0])
        
        # Test dump error
        with patch("python_magnetgeo.utils.writeYaml", 
                   side_effect=PermissionError("No permission")):
            with pytest.raises(PermissionError):
                lead.dump()
        
        # Test write_to_json error
        with patch("builtins.open", side_effect=IOError("Write error")):
            with pytest.raises(Exception, match="Failed to write to file_error_test.json"):
                lead.write_to_json()
    
    def test_deserialization_errors(self):
        """Test deserialization error handling"""
        # Test from_json with invalid JSON
        # Note: loadJson wraps JSONDecodeError in a generic Exception
        with patch("builtins.open", mock_open(read_data="{ invalid json")):
            with pytest.raises(Exception, match="Failed to load OuterCurrentLead data"):
                OuterCurrentLead.from_json("invalid.json")
        
        # Test from_yaml with file not found
        with pytest.raises(Exception):  # The actual exception depends on utils.loadYaml implementation
            OuterCurrentLead.from_yaml("nonexistent.yaml")


class TestOuterCurrentLeadUseCases:
    """
    Test realistic use cases for OuterCurrentLead
    """
    
    def test_standard_10kA_outer_lead(self):
        """Test standard 10kA outer current lead configuration"""
        standard_lead = OuterCurrentLead(
            name="standard_outer_10kA",
            r=[150.0, 200.0],   # Standard outer dimensions
            h=300.0,            # 30cm height
            bar=[25.0, 35.0, 18.0, 280.0],  # Standard bar
            support=[12.0, 25.0, 45.0, 0.0]  # 45° angled support
        )
        
        assert standard_lead.name == "standard_outer_10kA"
        assert standard_lead.r == [150.0, 200.0]
        assert standard_lead.h == 300.0
        
        # Verify bar fits within lead
        if len(standard_lead.bar) >= 4 and len(standard_lead.r) >= 2:
            assert standard_lead.bar[0] <= standard_lead.r[1]  # Bar radius <= outer radius
            assert standard_lead.bar[3] <= standard_lead.h * 1.1  # Bar length <= lead height (with margin)
    
    def test_high_current_20kA_outer_lead(self):
        """Test high current 20kA outer current lead"""
        high_current = OuterCurrentLead(
            name="high_current_outer_20kA",
            r=[200.0, 300.0],   # Larger for higher current
            h=400.0,            # Taller for heat dissipation
            bar=[40.0, 50.0, 25.0, 350.0],  # Larger bar
            support=[20.0, 35.0, 30.0, 15.0]  # Robust support
        )
        
        # Should have larger cross-sectional area than standard
        import math
        if len(high_current.r) >= 2:
            area = math.pi * (high_current.r[1]**2 - high_current.r[0]**2)
            standard_area = math.pi * (200.0**2 - 150.0**2)
            assert area > standard_area
        
        # Larger bar dimensions
        if len(high_current.bar) >= 4:
            assert high_current.bar[1] >= 35.0  # DX should be larger
            assert high_current.bar[2] >= 18.0  # DY should be larger
    
    def test_compact_5kA_outer_lead(self):
        """Test compact 5kA outer current lead for space constraints"""
        compact = OuterCurrentLead(
            name="compact_outer_5kA",
            r=[100.0, 130.0],   # Smaller dimensions
            h=200.0,            # Shorter
            bar=[15.0, 20.0, 10.0, 180.0],  # Compact bar
            support=[8.0, 15.0, 60.0, 30.0]  # Minimal support
        )
        
        assert compact.r[1] < 200.0  # Smaller than standard
        assert compact.h < 300.0     # Shorter than standard
        if len(compact.bar) >= 4:
            assert compact.bar[1] < 35.0 # Compact bar width
            assert compact.bar[2] < 18.0 # Compact bar height


@pytest.mark.performance
class TestOuterCurrentLeadPerformance:
    """
    Performance tests for OuterCurrentLead operations
    """
    
    def test_initialization_performance(self):
        """Test OuterCurrentLead initialization performance"""
        def create_lead():
            return OuterCurrentLead(
                name="performance_test",
                r=[150.0, 200.0],
                h=300.0,
                bar=[25.0, 30.0, 15.0, 250.0],
                support=[10.0, 20.0, 45.0, 0.0]
            )
        
        result, execution_time = time_function_execution(create_lead)
        
        assert_performance_within_limits(execution_time, 0.001)  # 1ms limit
        assert result.name == "performance_test"
    
    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        lead = OuterCurrentLead(
            name="json_performance",
            r=[150.0, 200.0],
            h=300.0,
            bar=[25.0, 30.0, 15.0, 250.0] * 100,  # Large bar array
            support=[10.0, 20.0, 45.0, 0.0]
        )
        
        result, execution_time = time_function_execution(lead.to_json)
        
        assert_performance_within_limits(execution_time, 0.05)  # 50ms limit
        assert isinstance(result, str)
        assert len(result) > 100
    
    def test_repr_performance(self):
        """Test repr performance"""
        lead = OuterCurrentLead(
            name="x" * 1000,  # Long name
            r=[100.0, 200.0],
            h=300.0,
            bar=[25.0, 30.0, 15.0, 250.0],
            support=[10.0, 20.0, 45.0, 0.0]
        )
        
        result, execution_time = time_function_execution(repr, lead)
        
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert "OuterCurrentLead" in result


class TestOuterCurrentLeadIntegration:
    """
    Integration tests combining multiple features
    """
    
    def test_full_workflow_yaml(self):
        """Test complete YAML workflow"""
        # Create instance
        original_lead = OuterCurrentLead(
            name="integration_yaml_test",
            r=[140.0, 190.0],
            h=380.0,
            bar=[32.0, 38.0, 18.0, 320.0],
            support=[14.0, 28.0, 50.0, 25.0]
        )
        
        # Test serialization
        with patch("python_magnetgeo.utils.writeYaml") as mock_write:
            original_lead.dump()
            mock_write.assert_called_once()
        
        # Test deserialization
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_load.return_value = original_lead
            loaded_lead = OuterCurrentLead.from_yaml("test.yaml")
            assert loaded_lead.name == original_lead.name
    
    def test_full_workflow_json(self):
        """Test complete JSON workflow"""
        original_lead = OuterCurrentLead(
            name="integration_json_test",
            r=[130.0, 180.0],
            h=360.0,
            bar=[28.0, 35.0, 16.0, 310.0],
            support=[12.0, 24.0, 40.0, 20.0]
        )
        
        # Test JSON serialization
        json_str = original_lead.to_json()
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["__classname__"] == "OuterCurrentLead"
        assert parsed["name"] == "integration_json_test"
        
        # Test file writing
        with patch("builtins.open", mock_open()) as mock_file:
            original_lead.write_to_json()
            mock_file.assert_called_once_with("integration_json_test.json", "w")
    
    def test_dict_roundtrip(self):
        """Test dictionary conversion roundtrip"""
        original_data = {
            "name": "roundtrip_test",
            "r": [120.0, 170.0],
            "h": 320.0,
            "bar": [26.0, 32.0, 16.0, 290.0],
            "support": [11.0, 23.0, 55.0, 10.0]
        }
        
        # Create from dict
        lead = OuterCurrentLead.from_dict(original_data)
        
        # Verify all attributes match
        assert lead.name == original_data["name"]
        assert lead.r == original_data["r"]
        assert lead.h == original_data["h"]
        assert lead.bar == original_data["bar"]
        assert lead.support == original_data["support"]


class TestOuterCurrentLeadDocumentation:
    """
    Test that OuterCurrentLead behavior matches its documentation
    """
    
    def test_documented_attributes_exist(self):
        """Test all documented attributes exist and have correct types"""
        lead = OuterCurrentLead(
            name="doc_test",
            r=[150.0, 200.0],
            h=300.0,
            bar=[25.0, 30.0, 15.0, 250.0],
            support=[10.0, 20.0, 45.0, 0.0]
        )
        
        # Verify all documented attributes exist
        assert hasattr(lead, "name")
        assert hasattr(lead, "r")
        assert hasattr(lead, "h")
        assert hasattr(lead, "bar")
        assert hasattr(lead, "support")
        
        # Verify types
        assert isinstance(lead.name, str)
        assert isinstance(lead.r, list)
        assert isinstance(lead.h, (int, float))
        assert isinstance(lead.bar, list)
        assert isinstance(lead.support, list)
    
    def test_yaml_tag_matches_class_name(self):
        """Test YAML tag matches class name"""
        assert OuterCurrentLead.yaml_tag == "OuterCurrentLead"
    
    def test_bar_structure_documentation(self):
        """Test bar structure matches documentation"""
        # Documentation: [R, DX, DY, L]
        # R: disk radius for cutting rectangle
        # DX, DY: rectangle dimensions
        # L: prism length along Oz
        bar = [25.0, 30.0, 15.0, 250.0]
        lead = OuterCurrentLead(name="bar_doc", r=[150.0, 200.0], bar=bar)
        
        assert len(lead.bar) == 4
        # All parameters should be numeric
        for param in lead.bar:
            assert isinstance(param, (int, float))
    
    def test_support_structure_documentation(self):
        """Test support structure matches documentation"""
        # Documentation: [DX0, DZ, Angle, Angle_Zero]
        support = [10.0, 20.0, 45.0, 0.0]
        lead = OuterCurrentLead(name="support_doc", r=[150.0, 200.0], support=support)
        
        assert len(lead.support) == 4
        # All parameters should be numeric
        for param in lead.support:
            assert isinstance(param, (int, float))
    
    def test_serialization_methods_documented(self):
        """Test all documented serialization methods work"""
        lead = OuterCurrentLead(
            name="serialize_doc",
            r=[100.0, 150.0],
            h=200.0,
            bar=[20.0, 25.0, 12.0, 180.0],
            support=[8.0, 15.0, 30.0, 0.0]
        )
        
        # YAML methods
        assert hasattr(lead, "dump")
        assert callable(lead.dump)
        
        # JSON methods
        assert hasattr(lead, "to_json")
        assert callable(lead.to_json)
        assert hasattr(lead, "write_to_json")
        assert callable(lead.write_to_json)
        
        # Class methods
        assert hasattr(OuterCurrentLead, "from_yaml")
        assert callable(OuterCurrentLead.from_yaml)
        assert hasattr(OuterCurrentLead, "from_json")
        assert callable(OuterCurrentLead.from_json)
        assert hasattr(OuterCurrentLead, "from_dict")
        assert callable(OuterCurrentLead.from_dict)
        
        # Test JSON serialization works
        json_str = lead.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "OuterCurrentLead"
        assert parsed["name"] == "serialize_doc"


@pytest.mark.parametrize("bar_config,expected_description", [
    ([20.0, 25.0, 12.0, 200.0], "standard_rectangular_bar"),
    ([30.0, 35.0, 18.0, 300.0], "large_rectangular_bar"),
    ([15.0, 20.0, 8.0, 150.0], "compact_rectangular_bar"),
    ([25.0, 50.0, 10.0, 250.0], "wide_thin_bar"),
    ([25.0, 15.0, 30.0, 250.0], "narrow_thick_bar"),
    ([], "no_bar"),
])
class TestOuterCurrentLeadParameterizedBar:
    """
    Parametrized tests for different bar configurations
    """
    
    def test_bar_configuration_validity(self, bar_config, expected_description):
        """Test various bar configurations are handled correctly"""
        lead = OuterCurrentLead(
            name=f"bar_{expected_description}",
            r=[100.0, 150.0],
            h=350.0,
            bar=bar_config
        )
        
        assert lead.bar == bar_config
        assert expected_description in lead.name
        
        # If bar is specified with full 4 parameters, validate geometric relationships
        if len(bar_config) == 4:
            disk_radius = bar_config[0]
            rect_width = bar_config[1]
            rect_height = bar_config[2]
            prism_length = bar_config[3]
            
            # All dimensions should be non-negative
            assert disk_radius >= 0
            assert rect_width >= 0
            assert rect_height >= 0
            assert prism_length >= 0
            
            # Prism length should fit within lead height (with some tolerance)
            if lead.h > 0:
                assert prism_length <= lead.h * 1.5  # Allow engineering tolerance


@pytest.mark.parametrize("support_config,expected_relationship", [
    ([8.0, 0.0, 0.0, 0.0], "flush_aligned_support"),
    ([8.0, 5.0, 45.0, 0.0], "offset_angled_support"), 
    ([8.0, -3.0, 90.0, 45.0], "negative_offset_perpendicular"),
    ([0.0, 0.0, 0.0, 0.0], "zero_support"),
    ([15.0, 10.0, 180.0, 90.0], "opposite_oriented_support"),
    ([12.0, 8.0, 360.0, 0.0], "full_rotation_support"),
])
class TestOuterCurrentLeadParameterizedSupport:
    """
    Parametrized tests for different support configurations
    """
    
    def test_support_configuration_validity(self, support_config, expected_relationship):
        """Test various support configurations are handled correctly"""
        lead = OuterCurrentLead(
            name=f"support_{expected_relationship}",
            r=[100.0, 150.0],
            h=300.0,
            support=support_config
        )
        
        assert lead.support == support_config
        
        if len(support_config) >= 4:
            dx0 = support_config[0]
            dz = support_config[1]
            angle = support_config[2]
            angle_zero = support_config[3]
            
            # Validate DX0 is non-negative
            assert dx0 >= 0
            
            # DZ can be positive, negative, or zero (offset)
            assert isinstance(dz, (int, float))
            
            # Angles should be reasonable (allowing full range including negative)
            assert abs(angle) <= 360
            assert abs(angle_zero) <= 360


class TestOuterCurrentLeadEdgeCases:
    """
    Test edge cases and boundary conditions
    """
    
    def test_minimal_valid_configuration(self):
        """Test most minimal valid configuration"""
        minimal_lead = OuterCurrentLead(name="minimal")
        
        assert minimal_lead.name == "minimal"
        assert minimal_lead.r == []
        assert minimal_lead.h == 0.0
        assert minimal_lead.bar == []
        assert minimal_lead.support == []
    
    def test_single_radius_configuration(self):
        """Test configuration with single radius value"""
        single_r_lead = OuterCurrentLead(name="single_r", r=[120.0], h=250.0)
        
        assert len(single_r_lead.r) == 1
        assert single_r_lead.r[0] == 120.0
        assert single_r_lead.h == 250.0
    
    def test_zero_height_configuration(self):
        """Test configuration with zero height"""
        zero_height_lead = OuterCurrentLead(
            name="zero_height",
            r=[100.0, 150.0],
            h=0.0,
            bar=[25.0, 30.0, 15.0, 0.0]  # Zero length bar
        )
        
        assert zero_height_lead.h == 0.0
        if len(zero_height_lead.bar) >= 4:
            assert zero_height_lead.bar[3] == 0.0  # Zero length
    
    def test_empty_list_configurations(self):
        """Test configurations with empty lists"""
        empty_config_lead = OuterCurrentLead(
            name="empty_configs",
            r=[],
            bar=[],
            support=[]
        )
        
        assert empty_config_lead.r == []
        assert empty_config_lead.bar == []
        assert empty_config_lead.support == []
    
    def test_very_large_values(self):
        """Test with very large numerical values"""
        large_values_lead = OuterCurrentLead(
            name="large_values",
            r=[1e6, 2e6],  # Very large radii
            h=1e9,         # Very large height
            bar=[5e5, 6e5, 3e5, 8e8],  # Large bar values
            support=[4e5, 1e6, 180, 90]  # Large support values
        )
        
        assert large_values_lead.r[0] == 1e6
        assert large_values_lead.h == 1e9
        if len(large_values_lead.bar) >= 4:
            assert large_values_lead.bar[3] == 8e8
    
    def test_high_precision_values(self):
        """Test with high precision floating point values"""
        precision_lead = OuterCurrentLead(
            name="high_precision",
            r=[150.123456789012345, 200.987654321098765],
            h=300.555555555555555,
            bar=[25.111111111111111, 30.222222222222222, 
                 15.333333333333333, 250.444444444444444],
            support=[10.777777777777777, 20.888888888888888,
                     45.999999999999999, 0.000000000000001]
        )
        
        # Values should be preserved with reasonable precision
        assert abs(precision_lead.r[0] - 150.123456789012345) < 1e-14
        assert abs(precision_lead.h - 300.555555555555555) < 1e-14
    
    def test_mixed_numeric_types(self):
        """Test with mixed integer and float types"""
        mixed_types_lead = OuterCurrentLead(
            name="mixed_types",
            r=[100, 150.5],           # int and float
            h=300,                    # int
            bar=[25, 30.5, 15, 250.0],  # mixed int/float
            support=[10.0, 20, 45.5, 0]  # float and int
        )
        
        assert isinstance(mixed_types_lead.r[0], int)
        assert isinstance(mixed_types_lead.r[1], float)
        assert isinstance(mixed_types_lead.h, int)


# Custom fixtures for complex test scenarios
@pytest.fixture(scope="class")
def outer_current_lead_test_suite():
    """Class-scoped fixture providing test data for multiple test methods"""
    return {
        "standard_configs": [
            {
                "name": "test_5kA_outer",
                "r": [80.0, 120.0],
                "h": 200.0,
                "bar": [15.0, 20.0, 10.0, 180.0],
                "support": [6.0, 12.0, 30.0, 0.0]
            },
            {
                "name": "test_10kA_outer", 
                "r": [150.0, 200.0],
                "h": 300.0,
                "bar": [25.0, 30.0, 15.0, 250.0],
                "support": [10.0, 20.0, 45.0, 0.0]
            },
            {
                "name": "test_20kA_outer",
                "r": [200.0, 300.0],
                "h": 400.0,
                "bar": [40.0, 50.0, 25.0, 350.0],
                "support": [20.0, 35.0, 60.0, 30.0]
            }
        ],
        "error_configs": [
            {
                "name": "",  # Empty name
                "r": [100.0, 150.0],
                "expected_error": None  # Empty name should be allowed
            },
            {
                "name": "missing_r",
                "r": [],  # Empty radius list
                "expected_error": None  # Should be allowed for flexibility
            }
        ]
    }


class TestOuterCurrentLeadWithFixture:
    """
    Tests using the outer_current_lead_test_suite fixture
    """
    
    def test_standard_configurations(self, outer_current_lead_test_suite):
        """Test multiple standard configurations"""
        for config in outer_current_lead_test_suite["standard_configs"]:
            lead = OuterCurrentLead(**config)
            
            assert lead.name == config["name"]
            assert lead.r == config["r"]
            assert lead.h == config["h"]
            assert lead.bar == config["bar"]
            assert lead.support == config["support"]
    
    def test_error_configurations(self, outer_current_lead_test_suite):
        """Test error configurations"""
        for config in outer_current_lead_test_suite["error_configs"]:
            if config.get("expected_error"):
                with pytest.raises(config["expected_error"]):
                    OuterCurrentLead(**{k: v for k, v in config.items() 
                                       if k != "expected_error"})
            else:
                # Should succeed
                lead = OuterCurrentLead(**{k: v for k, v in config.items() 
                                         if k != "expected_error"})
                assert isinstance(lead, OuterCurrentLead)
    
    def test_scaling_relationships(self, outer_current_lead_test_suite):
        """Test scaling relationships between different current ratings"""
        configs = outer_current_lead_test_suite["standard_configs"]
        
        # Test that higher current leads have larger dimensions
        for i in range(len(configs) - 1):
            current_config = configs[i]
            next_config = configs[i + 1]
            
            current_lead = OuterCurrentLead(**current_config)
            next_lead = OuterCurrentLead(**next_config)
            
            # Higher current should generally have larger outer radius
            if len(current_lead.r) >= 2 and len(next_lead.r) >= 2:
                assert next_lead.r[1] >= current_lead.r[1]
            
            # Higher current should generally have larger height
            assert next_lead.h >= current_lead.h


class TestOuterCurrentLeadComplexScenarios:
    """
    Test complex scenarios and realistic engineering use cases
    """
    
    def test_thermal_analysis_configuration(self):
        """Test configuration optimized for thermal analysis"""
        thermal_lead = OuterCurrentLead(
            name="thermal_analysis_lead",
            r=[120.0, 200.0],  # Good thermal mass
            h=500.0,           # Tall for heat dissipation
            bar=[35.0, 45.0, 22.0, 450.0],  # Large cross-section for heat conduction
            support=[15.0, 30.0, 0.0, 0.0]  # Aligned for thermal measurement access
        )
        
        # Verify thermal-friendly dimensions
        if len(thermal_lead.r) >= 2:
            thermal_volume = 3.14159 * (thermal_lead.r[1]**2 - thermal_lead.r[0]**2) * thermal_lead.h
            assert thermal_volume > 1e6  # Large volume for thermal mass
        
        # Large bar cross-section for heat conduction
        if len(thermal_lead.bar) >= 3:
            bar_cross_section = thermal_lead.bar[1] * thermal_lead.bar[2]  # DX * DY
            assert bar_cross_section > 500  # Large cross-section
    
    def test_electromagnetic_analysis_configuration(self):
        """Test configuration optimized for electromagnetic analysis"""
        em_lead = OuterCurrentLead(
            name="electromagnetic_analysis_lead",
            r=[100.0, 180.0],  # Specific radius ratio for field analysis
            h=300.0,
            bar=[25.0, 60.0, 8.0, 280.0],  # Wide, thin bar for current distribution
            support=[12.0, 20.0, 90.0, 0.0]  # Perpendicular support
        )
        
        # Check radius ratio for EM analysis
        if len(em_lead.r) >= 2:
            radius_ratio = em_lead.r[1] / em_lead.r[0]
            assert 1.5 <= radius_ratio <= 2.5  # Typical range for EM analysis
        
        # Wide, thin bar for current distribution studies
        if len(em_lead.bar) >= 3:
            aspect_ratio = em_lead.bar[1] / em_lead.bar[2]  # Width / Height
            assert aspect_ratio > 5  # Wide and thin
    
    def test_mechanical_stress_configuration(self):
        """Test configuration for mechanical stress analysis"""
        stress_lead = OuterCurrentLead(
            name="mechanical_stress_lead",
            r=[150.0, 220.0],  # Thick walls for stress analysis
            h=350.0,
            bar=[30.0, 35.0, 35.0, 320.0],  # Square cross-section for uniform stress
            support=[18.0, 0.0, 45.0, 45.0]  # Diagonal support for stress distribution
        )
        
        # Check wall thickness for stress analysis
        if len(stress_lead.r) >= 2:
            wall_thickness = stress_lead.r[1] - stress_lead.r[0]
            assert wall_thickness >= 50.0  # Thick enough for stress analysis
        
        # Square bar cross-section for uniform stress distribution
        if len(stress_lead.bar) >= 3:
            width_height_diff = abs(stress_lead.bar[1] - stress_lead.bar[2])
            assert width_height_diff <= 5.0  # Nearly square


class TestOuterCurrentLeadCodeCoverage:
    """
    Additional tests to ensure complete code coverage
    """
    
    def test_all_initialization_paths(self):
        """Test all possible initialization parameter combinations"""
        # Only name (minimal)
        lead1 = OuterCurrentLead(name="minimal")
        assert lead1.name == "minimal"
        assert lead1.r == []
        assert lead1.h == 0.0
        assert lead1.bar == []
        assert lead1.support == []
        
        # Name and r
        lead2 = OuterCurrentLead(name="with_r", r=[100.0, 150.0])
        assert lead2.r == [100.0, 150.0]
        assert lead2.h == 0.0
        
        # Name, r, and h
        lead3 = OuterCurrentLead(name="with_r_h", r=[100.0, 150.0], h=200.0)
        assert lead3.h == 200.0
        assert lead3.bar == []
        
        # Name, r, h, and bar
        lead4 = OuterCurrentLead(
            name="with_bar", 
            r=[100.0, 150.0], 
            h=200.0, 
            bar=[20.0, 25.0, 12.0, 180.0]
        )
        assert lead4.bar == [20.0, 25.0, 12.0, 180.0]
        assert lead4.support == []
        
        # All parameters
        lead5 = OuterCurrentLead(
            name="complete",
            r=[100.0, 150.0],
            h=200.0,
            bar=[20.0, 25.0, 12.0, 180.0],
            support=[8.0, 15.0, 30.0, 0.0]
        )
        assert lead5.support == [8.0, 15.0, 30.0, 0.0]
    
    def test_method_chaining_possibility(self):
        """Test that methods can be called in sequence"""
        lead = OuterCurrentLead(
            name="chaining_test",
            r=[100.0, 150.0],
            h=200.0,
            bar=[20.0, 25.0, 12.0, 180.0],
            support=[8.0, 15.0, 30.0, 0.0]
        )
        
        # Test method calls don't interfere with each other
        json_str = lead.to_json()
        repr_str = repr(lead)
        
        assert isinstance(json_str, str)
        assert isinstance(repr_str, str)
        assert "OuterCurrentLead" in repr_str
        assert '"name": "chaining_test"' in json_str
    
    def test_memory_efficiency(self):
        """Test memory usage is reasonable"""
        leads = []
        
        # Create many instances
        for i in range(100):
            lead = OuterCurrentLead(
                name=f"lead_{i}",
                r=[100.0 + i, 150.0 + i],
                h=200.0 + i,
                bar=[20.0, 25.0, 12.0, 180.0],
                support=[8.0, 15.0, 30.0, 0.0]
            )
            leads.append(lead)
        
        # Verify all instances are independent
        assert len(leads) == 100
        assert leads[0].name == "lead_0"
        assert leads[99].name == "lead_99"
        assert leads[0].r[0] == 100.0
        assert leads[99].r[0] == 199.0
