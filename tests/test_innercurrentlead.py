#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for InnerCurrentLead class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the class under test
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead, InnerCurrentLead_constructor

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


class TestInnerCurrentLead(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for InnerCurrentLead using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample InnerCurrentLead instance for testing"""
        return InnerCurrentLead(
            name="test_inner_lead",
            r=[19.3, 24.2],  # Inner/outer radius in mm
            h=480.0,         # Height in mm
            holes=[123, 12, 90, 60, 45, 3],  # Hole configuration
            support=[24.2, 0],  # Support configuration
            fillet=True
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """!<InnerCurrentLead>
name: test_inner_lead
r: [19.3, 24.2]
h: 480.0
holes: [123, 12, 90, 60, 45, 3]
support: [24.2, 0]
fillet: true
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_inner_lead",
            "r": [19.3, 24.2],
            "h": 480.0,
            "holes": [123, 12, 90, 60, 45, 3],
            "support": [24.2, 0],
            "fillet": True
        }
    
    def get_class_under_test(self) -> Type:
        """Return the InnerCurrentLead class"""
        return InnerCurrentLead
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return InnerCurrentLead
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "InnerCurrentLead"


class TestInnerCurrentLeadConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for InnerCurrentLead YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = InnerCurrentLead_constructor(loader, node)
            return result.__dict__, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "r": [20.0, 25.0],
            "h": 500.0,
            "holes": [100, 10, 0, 90, 0, 4],
            "support": [25.0, 5.0],
            "fillet": False
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "InnerCurrentLead"


class TestInnerCurrentLeadInitialization:
    """
    Test InnerCurrentLead initialization and basic properties
    """
    
    @pytest.fixture
    def sample_inner_lead(self):
        """Fixture providing a sample InnerCurrentLead instance"""
        return InnerCurrentLead(
            name="sample_lead",
            r=[15.0, 20.0],
            h=400.0,
            holes=[80, 8, 45, 30, 0, 6],
            support=[20.0, 2.0],
            fillet=False
        )
    
    @pytest.fixture
    def minimal_inner_lead(self):
        """Fixture providing a minimal InnerCurrentLead instance"""
        return InnerCurrentLead(name="minimal", r=[1.0, 2.0])
    
    def test_init_with_all_parameters(self):
        """Test InnerCurrentLead initialization with all parameters"""
        lead = InnerCurrentLead(
            name="full_lead",
            r=[10.0, 15.0],
            h=300.0,
            holes=[50, 5, 0, 60, 30, 8],
            support=[15.0, 1.0],
            fillet=True
        )
        assert lead.name == "full_lead"
        assert lead.r == [10.0, 15.0]
        assert lead.h == 300.0
        assert lead.holes == [50, 5, 0, 60, 30, 8]
        assert lead.support == [15.0, 1.0]
        assert lead.fillet is True
    
    def test_init_with_defaults(self):
        """Test InnerCurrentLead initialization with default values"""
        lead = InnerCurrentLead(name="default_lead", r=[5.0, 8.0])
        assert lead.name == "default_lead"
        assert lead.r == [5.0, 8.0]
        assert lead.h == 0.0      # Default value
        assert lead.holes == []   # Default value
        assert lead.support == [] # Default value
        assert lead.fillet is False  # Default value
    
    @pytest.mark.parametrize("name,r,h,expected_valid", [
        ("valid_lead", [10.0, 20.0], 100.0, True),
        ("zero_height", [10.0, 20.0], 0.0, True),
        ("negative_height", [10.0, 20.0], -10.0, True),  # Negative allowed for flexibility
        ("single_radius", [15.0], 100.0, True),  # Single radius allowed
        ("", [10.0, 20.0], 100.0, True),  # Empty name allowed
    ])
    def test_init_parameter_validation(self, name, r, h, expected_valid):
        """Test initialization with various parameter combinations"""
        if expected_valid:
            lead = InnerCurrentLead(name=name, r=r, h=h)
            assert lead.name == name
            assert lead.r == r
            assert lead.h == h
        else:
            with pytest.raises((ValueError, TypeError)):
                InnerCurrentLead(name=name, r=r, h=h)
    
    def test_repr(self, sample_inner_lead):
        """Test string representation"""
        repr_str = repr(sample_inner_lead)
        assert "InnerCurrentLead" in repr_str
        assert "name='sample_lead'" in repr_str
        assert "r=[15.0, 20.0]" in repr_str
        assert "h=400.0" in repr_str
        assert "holes=[80, 8, 45, 30, 0, 6]" in repr_str
        assert "support=[20.0, 2.0]" in repr_str
        assert "fillet=False" in repr_str
    
    def test_attribute_types(self, sample_inner_lead):
        """Test that attributes have correct types"""
        assert isinstance(sample_inner_lead.name, str)
        assert isinstance(sample_inner_lead.r, list)
        assert isinstance(sample_inner_lead.h, (int, float))
        assert isinstance(sample_inner_lead.holes, list)
        assert isinstance(sample_inner_lead.support, list)
        assert isinstance(sample_inner_lead.fillet, bool)


class TestInnerCurrentLeadSerialization:
    """
    Test serialization methods (dump, to_json, write_to_json)
    """
    
    @pytest.fixture
    def serialization_lead(self):
        """Lead instance for serialization testing"""
        return InnerCurrentLead(
            name="serialize_test",
            r=[18.0, 23.0],
            h=450.0,
            holes=[110, 10, 45, 50, 30, 4],
            support=[23.0, 2.0],
            fillet=True
        )
    
    def test_dump_success(self, serialization_lead):
        """Test dump method success"""
        with patch("python_magnetgeo.utils.writeYaml") as mock_write_yaml:
            serialization_lead.dump()
            mock_write_yaml.assert_called_once_with(
                "InnerCurrentLead", serialization_lead, InnerCurrentLead
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
        
        assert parsed["__classname__"] == "InnerCurrentLead"
        assert parsed["name"] == "serialize_test"
        assert parsed["r"] == [18.0, 23.0]
        assert parsed["h"] == 450.0
        assert parsed["holes"] == [110, 10, 45, 50, 30, 4]
        assert parsed["support"] == [23.0, 2.0]
        assert parsed["fillet"] is True
    
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
            assert parsed["__classname__"] == "InnerCurrentLead"
            assert parsed["name"] == "serialize_test"


class TestInnerCurrentLeadDeserialization:
    """
    Test deserialization methods (from_yaml, from_json, from_dict)
    """
    
    def test_from_dict_complete(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_test",
            "r": [16.0, 22.0],
            "h": 450.0,
            "holes": [90, 9, 30, 40, 15, 7],
            "support": [22.0, 1.5],
            "fillet": True
        }
        
        lead = InnerCurrentLead.from_dict(data)
        
        assert lead.name == "dict_test"
        assert lead.r == [16.0, 22.0]
        assert lead.h == 450.0
        assert lead.holes == [90, 9, 30, 40, 15, 7]
        assert lead.support == [22.0, 1.5]
        assert lead.fillet is True
    
    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_test",
            "r": [1.0, 2.0],
            "h": 10.0,
            "holes": [],
            "support": [],
            "fillet": False
        }
        
        lead = InnerCurrentLead.from_dict(data, debug=True)
        assert lead.name == "debug_test"
    
    def test_from_dict_missing_fields(self):
        """Test from_dict with missing required fields"""
        # Missing 'name'
        data1 = {
            "r": [1.0, 2.0],
            "h": 10.0,
            "holes": [],
            "support": [],
            "fillet": False
        }
        
        with pytest.raises(KeyError):
            InnerCurrentLead.from_dict(data1)
        
        # Missing 'r'
        data2 = {
            "name": "no_r",
            "h": 10.0,
            "holes": [],
            "support": [],
            "fillet": False
        }
        
        with pytest.raises(KeyError):
            InnerCurrentLead.from_dict(data2)
    
    def test_from_yaml_integration(self):
        """Test from_yaml integration"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load_yaml:
            mock_lead = Mock(spec=InnerCurrentLead)
            mock_load_yaml.return_value = mock_lead
            
            result = InnerCurrentLead.from_yaml("test.yaml", debug=True)
            
            mock_load_yaml.assert_called_once_with("InnerCurrentLead", "test.yaml", InnerCurrentLead, True)
            assert result == mock_lead
    
    def test_from_json_integration(self):
        """Test from_json integration"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load_json:
            mock_lead = Mock(spec=InnerCurrentLead)
            mock_load_json.return_value = mock_lead
            
            result = InnerCurrentLead.from_json("test.json", debug=False)
            
            mock_load_json.assert_called_once_with("InnerCurrentLead", "test.json", False)
            assert result == mock_lead


class TestInnerCurrentLeadHoleConfiguration:
    """
    Test hole configuration functionality
    Based on docstring: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
    """
    
    @pytest.mark.parametrize("holes,description", [
        ([123, 12, 90, 60, 45, 3], "standard_configuration"),
        ([100, 10, 0, 90, 0, 4], "aligned_holes"),
        ([50, 5, 45, 30, 15, 8], "angled_holes"),
        ([80, 8, 180, 45, 90, 6], "rotated_holes"),
        ([], "no_holes"),
        ([200, 20, 0, 0, 0, 1], "single_hole"),
    ])
    def test_various_hole_configurations(self, holes, description):
        """Test InnerCurrentLead with various hole configurations"""
        lead = InnerCurrentLead(
            name=f"holes_{description}",
            r=[10.0, 15.0],
            h=100.0,
            holes=holes
        )
        assert lead.holes == holes
        assert lead.name == f"holes_{description}"
    
    def test_hole_parameters_structure(self):
        """Test hole parameters follow documented structure"""
        # Based on docstring: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
        holes = [123, 12, 90, 60, 45, 3]
        lead = InnerCurrentLead(
            name="hole_params",
            r=[19.3, 24.2],
            h=480.0,
            holes=holes
        )
        
        assert len(lead.holes) == 6
        assert lead.holes[0] == 123  # H_Holes (hole height)
        assert lead.holes[1] == 12   # Shift_from_Top
        assert lead.holes[2] == 90   # Angle_Zero (reference angle)
        assert lead.holes[3] == 60   # Angle (angular spacing)
        assert lead.holes[4] == 45   # Angular_Position
        assert lead.holes[5] == 3    # N_Holes (number of holes)
    
    def test_hole_angular_parameters(self):
        """Test hole angular parameters are reasonable"""
        holes = [100, 10, 0, 90, 45, 4]
        lead = InnerCurrentLead(name="angles", r=[10.0, 15.0], holes=holes)
        
        # Validate angle parameters if holes list is complete
        if len(lead.holes) >= 6:
            validate_angle_data([lead.holes[2], lead.holes[3], lead.holes[4]])
    
    @pytest.mark.parametrize("n_holes,angle_spacing,expected_valid", [
        (3, 120, True),   # 3 holes, 120° apart = 360°
        (4, 90, True),    # 4 holes, 90° apart = 360°
        (6, 60, True),    # 6 holes, 60° apart = 360°
        (8, 45, True),    # 8 holes, 45° apart = 360°
        (12, 30, True),   # 12 holes, 30° apart = 360°
        (0, 0, True),     # No holes
        (1, 0, True),     # Single hole
    ])
    def test_hole_count_angle_relationship(self, n_holes, angle_spacing, expected_valid):
        """Test relationship between number of holes and angular spacing"""
        holes = [100, 10, 0, angle_spacing, 0, n_holes]
        if expected_valid:
            lead = InnerCurrentLead(name="hole_test", r=[10.0, 15.0], holes=holes)
            assert lead.holes[5] == n_holes
            assert lead.holes[3] == angle_spacing
        else:
            # Could add validation logic here if needed
            pass


class TestInnerCurrentLeadSupportConfiguration:
    """
    Test support configuration functionality
    """
    
    @pytest.mark.parametrize("support,description", [
        ([24.2, 0], "flush_support"),
        ([25.0, 5.0], "offset_support"),
        ([20.0, -2.0], "negative_offset"),
        ([30.0, 10.0], "large_offset"),
        ([], "no_support"),
        ([15.0], "incomplete_support"),
    ])
    def test_various_support_configurations(self, support, description):
        """Test InnerCurrentLead with various support configurations"""
        lead = InnerCurrentLead(
            name=f"support_{description}",
            r=[10.0, 20.0],
            h=100.0,
            support=support
        )
        assert lead.support == support
    
    def test_support_parameters_structure(self):
        """Test support parameters follow documented structure"""
        # Based on docstring: [R2, DZ]
        support = [24.2, 0]
        lead = InnerCurrentLead(
            name="support_params",
            r=[19.3, 24.2],
            support=support
        )
        
        assert len(lead.support) == 2
        assert lead.support[0] == 24.2  # R2 (support radius)
        assert lead.support[1] == 0     # DZ (vertical offset)
    
    def test_support_radius_relationships(self):
        """Test support radius relationships with main geometry"""
        r = [19.3, 24.2]
        
        test_cases = [
            ([24.2, 0], "equal_to_outer"),
            ([30.0, 0], "larger_than_outer"),
            ([20.0, 0], "between_radii"),
            ([15.0, 0], "smaller_than_inner"),
        ]
        
        for support, description in test_cases:
            lead = InnerCurrentLead(name=description, r=r, support=support)
            assert lead.support[0] == support[0]


class TestInnerCurrentLeadGeometry:
    """
    Test geometric aspects and constraints
    """
    
    @pytest.fixture
    def geometric_lead(self):
        """Fixture with realistic geometry for validation"""
        return InnerCurrentLead(
            name="geometric_test",
            r=[19.3, 24.2],  # Realistic current lead dimensions
            h=480.0,         # 48cm height
            holes=[123, 12, 90, 60, 45, 3],
            support=[24.2, 0]
        )
    
    def test_radius_geometry_validation(self, geometric_lead):
        """Test radius geometry is reasonable"""
        assert len(geometric_lead.r) >= 1
        if len(geometric_lead.r) >= 2:
            validate_geometric_data(geometric_lead.r, [0, geometric_lead.h])
    
    def test_height_validation(self, geometric_lead):
        """Test height parameter is reasonable"""
        assert isinstance(geometric_lead.h, (int, float))
        # Height can be zero or positive for physical components
        assert geometric_lead.h >= 0
    
    def test_geometric_consistency(self, geometric_lead):
        """Test geometric consistency between parameters"""
        # If support radius is defined, check relationship with main radius
        if len(geometric_lead.support) >= 1 and len(geometric_lead.r) >= 2:
            # Support radius should be reasonable relative to main geometry
            support_radius = geometric_lead.support[0]
            outer_radius = geometric_lead.r[-1]
            # Allow support to extend beyond outer radius (common in engineering)
            assert support_radius >= 0
    
    @pytest.mark.parametrize("r,h,expected_volume_positive", [
        ([10.0, 20.0], 100.0, True),
        ([0.0, 10.0], 50.0, True),
        ([5.0, 5.0], 100.0, False),  # Zero volume (inner=outer)
        ([10.0], 100.0, None),       # Single radius - volume calculation not applicable
    ])
    def test_volume_calculations(self, r, h, expected_volume_positive):
        """Test volume-related calculations for geometric validation"""
        lead = InnerCurrentLead(name="volume_test", r=r, h=h)
        
        if expected_volume_positive is not None and len(lead.r) >= 2:
            # Calculate annular volume
            import math
            inner_radius = lead.r[0]
            outer_radius = lead.r[1]
            volume = math.pi * (outer_radius**2 - inner_radius**2) * lead.h
            
            if expected_volume_positive:
                assert volume > 0
            else:
                assert volume == 0


class TestInnerCurrentLeadYAMLConstructor:
    """
    Test YAML constructor functionality
    """
    
    def test_yaml_constructor_function_direct(self):
        """Test the InnerCurrentLead_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "r": [12.0, 18.0],
            "h": 350.0,
            "holes": [75, 7, 15, 45, 60, 5],
            "support": [18.0, 3.0],
            "fillet": True
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = InnerCurrentLead_constructor(mock_loader, mock_node)
        
        assert isinstance(result, InnerCurrentLead)
        assert result.name == "direct_test"
        assert result.r == [12.0, 18.0]
        assert result.h == 350.0
        assert result.holes == [75, 7, 15, 45, 60, 5]
        assert result.support == [18.0, 3.0]
        assert result.fillet is True
        mock_loader.construct_mapping.assert_called_once_with(mock_node)
    
    def test_constructor_missing_required_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'name' field
        incomplete_data = {
            "r": [1.0, 2.0],
            "h": 10.0,
            "holes": [],
            "support": [],
            "fillet": False
        }
        mock_loader.construct_mapping.return_value = incomplete_data
        
        with pytest.raises(KeyError):
            InnerCurrentLead_constructor(mock_loader, mock_node)
    
    def test_constructor_with_extra_fields(self):
        """Test constructor handles extra fields gracefully"""
        mock_loader = Mock()
        mock_node = Mock()
        
        data_with_extras = {
            "name": "extra_fields_test",
            "r": [1.0, 2.0],
            "h": 10.0,
            "holes": [],
            "support": [],
            "fillet": False,
            "extra_field": "should_be_ignored",
            "another_extra": {"nested": "data"}
        }
        mock_loader.construct_mapping.return_value = data_with_extras
        
        # Should work fine, ignoring extra fields
        result = InnerCurrentLead_constructor(mock_loader, mock_node)
        assert isinstance(result, InnerCurrentLead)
        assert result.name == "extra_fields_test"
        assert not hasattr(result, "extra_field")
        assert not hasattr(result, "another_extra")


class TestInnerCurrentLeadErrorHandling:
    """
    Test error handling and edge cases
    """
    
    def test_serialization_errors(self):
        """Test serialization error handling"""
        lead = InnerCurrentLead(name="error_test", r=[1.0, 2.0])
        
        # Test to_json serialization error
        with patch("python_magnetgeo.deserialize.serialize_instance", 
                   side_effect=TypeError("Serialization error")):
            with pytest.raises(TypeError):
                lead.to_json()
    
    def test_file_operation_errors(self):
        """Test file operation error handling"""
        lead = InnerCurrentLead(name="file_error_test", r=[1.0, 2.0])
        
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
            with pytest.raises(Exception, match="Failed to load InnerCurrentLead data"):
                InnerCurrentLead.from_json("invalid.json")
        
        # Test from_yaml with file not found
        with pytest.raises(Exception):  # The actual exception depends on utils.loadYaml implementation
            InnerCurrentLead.from_yaml("nonexistent.yaml")


class TestInnerCurrentLeadUseCases:
    """
    Test realistic use cases and scenarios
    """
    
    def test_standard_10kA_current_lead(self):
        """Test standard 10kA current lead configuration"""
        standard_lead = InnerCurrentLead(
            name="standard_10kA_inner_lead",
            r=[19.3, 24.2],   # Standard dimensions for 10kA lead
            h=480.0,          # 48cm height
            holes=[123, 12, 90, 60, 45, 3],  # 3 holes, 60° apart
            support=[24.2, 0], # Support at outer radius
            fillet=True       # Rounded edges for better current flow
        )
        
        assert standard_lead.name == "standard_10kA_inner_lead"
        assert standard_lead.fillet is True
        
        # Check hole configuration for 3 symmetric holes
        holes = standard_lead.holes
        if len(holes) >= 6:
            assert holes[5] == 3  # 3 holes
            assert holes[3] == 60  # 60° spacing
    
    def test_high_current_20kA_lead(self):
        """Test high current 20kA inner current lead"""
        high_current_lead = InnerCurrentLead(
            name="high_current_20kA_inner",
            r=[25.0, 35.0],   # Larger dimensions for higher current
            h=600.0,          # Taller for better heat dissipation
            holes=[150, 15, 0, 45, 0, 8],  # 8 holes, 45° apart
            support=[35.0, 5.0],  # Support with offset
            fillet=True
        )
        
        # Verify larger cross-sectional area than standard
        import math
        area = math.pi * (high_current_lead.r[1]**2 - high_current_lead.r[0]**2)
        standard_area = math.pi * (24.2**2 - 19.3**2)
        assert area > standard_area
        
        # More holes for better cooling
        if len(high_current_lead.holes) >= 6:
            assert high_current_lead.holes[5] == 8  # 8 holes
        assert high_current_lead.h > 480.0  # Taller than standard
    
    def test_compact_5kA_lead(self):
        """Test compact 5kA inner current lead for space constraints"""
        compact_lead = InnerCurrentLead(
            name="compact_5kA_inner",
            r=[12.0, 16.0],   # Smaller dimensions
            h=250.0,          # Shorter height
            holes=[60, 8, 45, 90, 30, 4],  # 4 holes, 90° apart
            support=[16.0, -2.0],  # Support with negative offset
            fillet=False      # Sharp edges for compact design
        )
        
        # Verify smaller than standard
        assert compact_lead.r[1] < 24.2
        assert compact_lead.h < 480.0
        assert compact_lead.fillet is False
        
        # Fewer holes due to size constraints
        if len(compact_lead.holes) >= 6:
            assert compact_lead.holes[5] == 4  # 4 holes
            assert compact_lead.holes[3] == 90  # 90° spacing
    
    def test_experimental_research_lead(self):
        """Test experimental inner lead for research applications"""
        experimental_lead = InnerCurrentLead(
            name="experimental_research_inner",
            r=[15.0, 25.0],
            h=350.0,
            holes=[80, 5, 0, 36, 0, 10],  # 10 holes, 36° apart (fine pattern)
            support=[28.0, 8.0],  # Extended support beyond outer radius
            fillet=False
        )
        
        # Many small holes for detailed study
        if len(experimental_lead.holes) >= 6:
            assert experimental_lead.holes[5] == 10  # 10 holes
            assert experimental_lead.holes[3] == 36  # Fine angular spacing
        
        # Extended support beyond outer radius
        if len(experimental_lead.support) >= 1:
            assert experimental_lead.support[0] > experimental_lead.r[1]


@pytest.mark.performance
class TestInnerCurrentLeadPerformance:
    """
    Performance tests for InnerCurrentLead operations
    """
    
    def test_initialization_performance(self):
        """Test InnerCurrentLead initialization performance"""
        def create_lead():
            return InnerCurrentLead(
                name="performance_test",
                r=[19.3, 24.2],
                h=480.0,
                holes=[123, 12, 90, 60, 45, 3],
                support=[24.2, 0],
                fillet=True
            )
        
        result, execution_time = time_function_execution(create_lead)
        
        # Should initialize quickly
        assert_performance_within_limits(execution_time, 0.001)  # 1ms limit
        assert result.name == "performance_test"
    
    def test_large_data_performance(self):
        """Test InnerCurrentLead performance with large datasets"""
        # Create InnerCurrentLead with large hole configuration
        large_holes = [1000, 100] + [i for i in range(1000)]  # Large hole list
        large_support = [50.0 + i*0.1 for i in range(100)]    # Large support list
        
        def create_large_lead():
            return InnerCurrentLead(
                name="performance_test",
                r=[10.0, 50.0],
                h=2000.0,
                holes=large_holes,
                support=large_support,
                fillet=True
            )
        
        result, execution_time = time_function_execution(create_large_lead)
        
        # Should handle large datasets efficiently
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert len(result.holes) == len(large_holes)
        assert len(result.support) == len(large_support)
    
    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        lead = InnerCurrentLead(
            name="json_performance_test",
            r=[19.3, 24.2],
            h=480.0,
            holes=[123, 12, 90, 60, 45, 3] * 100,  # Large hole array
            support=[24.2, 0],
            fillet=True
        )
        
        result, execution_time = time_function_execution(lead.to_json)
        
        # JSON serialization should be reasonably fast
        assert_performance_within_limits(execution_time, 0.05)  # 50ms limit
        assert isinstance(result, str)
        assert len(result) > 100
    
    def test_repr_performance(self):
        """Test repr performance with large data"""
        lead = InnerCurrentLead(
            name="x" * 1000,  # Long name
            r=[1.0, 2.0],
            h=100.0,
            holes=[1] * 1000,  # Large holes list
            support=[2.0, 0],
            fillet=True
        )
        
        result, execution_time = time_function_execution(repr, lead)
        
        # Repr should be fast even with large data
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert "InnerCurrentLead" in result


class TestInnerCurrentLeadIntegration:
    """
    Integration tests combining multiple features
    """
    
    def test_full_workflow_yaml(self):
        """Test complete YAML workflow"""
        # Create instance
        original_lead = InnerCurrentLead(
            name="integration_yaml_test",
            r=[18.0, 23.0],
            h=450.0,
            holes=[110, 10, 45, 50, 30, 4],
            support=[23.0, 2.0],
            fillet=True
        )
        
        # Test serialization
        with patch("python_magnetgeo.utils.writeYaml") as mock_write:
            original_lead.dump()
            mock_write.assert_called_once()
        
        # Test deserialization
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_load.return_value = original_lead
            loaded_lead = InnerCurrentLead.from_yaml("test.yaml")
            assert loaded_lead.name == original_lead.name
    
    def test_full_workflow_json(self):
        """Test complete JSON workflow"""
        original_lead = InnerCurrentLead(
            name="integration_json_test",
            r=[20.0, 26.0],
            h=500.0,
            holes=[130, 15, 60, 40, 20, 5],
            support=[26.0, 3.0],
            fillet=False
        )
        
        # Test JSON serialization
        json_str = original_lead.to_json()
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["__classname__"] == "InnerCurrentLead"
        assert parsed["name"] == "integration_json_test"
        
        # Test file writing
        with patch("builtins.open", mock_open()) as mock_file:
            original_lead.write_to_json()
            mock_file.assert_called_once_with("integration_json_test.json", "w")
    
    def test_dict_roundtrip(self):
        """Test dictionary conversion roundtrip"""
        original_data = {
            "name": "roundtrip_test",
            "r": [15.0, 20.0],
            "h": 300.0,
            "holes": [90, 8, 30, 60, 15, 6],
            "support": [20.0, 1.0],
            "fillet": True
        }
        
        # Create from dict
        lead = InnerCurrentLead.from_dict(original_data)
        
        # Verify all attributes match
        assert lead.name == original_data["name"]
        assert lead.r == original_data["r"]
        assert lead.h == original_data["h"]
        assert lead.holes == original_data["holes"]
        assert lead.support == original_data["support"]
        assert lead.fillet == original_data["fillet"]


class TestInnerCurrentLeadDocumentation:
    """
    Test that InnerCurrentLead behavior matches its documentation
    """
    
    def test_documented_attributes_exist(self):
        """Test that all documented attributes exist and have correct types"""
        lead = InnerCurrentLead(
            name="doc_test",
            r=[19.3, 24.2],
            h=480.0,
            holes=[123, 12, 90, 60, 45, 3],
            support=[24.2, 0],
            fillet=True
        )
        
        # Verify all documented attributes exist
        assert hasattr(lead, "name")
        assert hasattr(lead, "r")
        assert hasattr(lead, "h")
        assert hasattr(lead, "holes")
        assert hasattr(lead, "support")
        assert hasattr(lead, "fillet")
        
        # Verify types match documentation
        assert isinstance(lead.name, str)
        assert isinstance(lead.r, list)
        assert isinstance(lead.h, (int, float))
        assert isinstance(lead.holes, list)
        assert isinstance(lead.support, list)
        assert isinstance(lead.fillet, bool)
    
    def test_holes_parameter_documentation(self):
        """Test holes parameter structure matches documentation"""
        # Documentation: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
        holes = [123, 12, 90, 60, 45, 3]
        lead = InnerCurrentLead(name="holes_doc", r=[19.3, 24.2], holes=holes)
        
        assert len(lead.holes) == 6
        # Each parameter should be numeric
        for param in lead.holes:
            assert isinstance(param, (int, float))
    
    def test_support_parameter_documentation(self):
        """Test support parameter structure matches documentation"""
        # Documentation: [R2, DZ]
        support = [24.2, 0]
        lead = InnerCurrentLead(name="support_doc", r=[19.3, 24.2], support=support)
        
        assert len(lead.support) == 2
        # Each parameter should be numeric
        for param in lead.support:
            assert isinstance(param, (int, float))
    
    def test_yaml_tag_matches_class_name(self):
        """Test that YAML tag matches class name"""
        assert InnerCurrentLead.yaml_tag == "InnerCurrentLead"
    
    def test_serialization_methods_documented(self):
        """Test that all documented serialization methods exist and work"""
        lead = InnerCurrentLead(
            name="serialize_test",
            r=[10.0, 15.0],
            h=100.0,
            holes=[50, 5, 0, 90, 0, 4],
            support=[15.0, 0],
            fillet=False
        )
        
        # YAML serialization methods
        assert hasattr(lead, "dump")
        assert callable(lead.dump)
        
        # JSON serialization methods
        assert hasattr(lead, "to_json")
        assert callable(lead.to_json)
        assert hasattr(lead, "write_to_json")
        assert callable(lead.write_to_json)
        
        # Class methods for loading
        assert hasattr(InnerCurrentLead, "from_yaml")
        assert callable(InnerCurrentLead.from_yaml)
        assert hasattr(InnerCurrentLead, "from_json")
        assert callable(InnerCurrentLead.from_json)
        assert hasattr(InnerCurrentLead, "from_dict")
        assert callable(InnerCurrentLead.from_dict)
        
        # Test that JSON serialization actually produces valid JSON
        json_str = lead.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "InnerCurrentLead"
        assert parsed["name"] == "serialize_test"


@pytest.mark.parametrize("holes_config,expected_description", [
    ([100, 10, 0, 120, 0, 3], "three_holes_120_degrees"),
    ([80, 8, 45, 90, 0, 4], "four_holes_90_degrees_offset"),
    ([60, 5, 0, 60, 30, 6], "six_holes_60_degrees"),
    ([120, 15, 90, 180, 0, 2], "two_holes_opposite"),
    ([], "no_holes"),
])
class TestInnerCurrentLeadParameterizedHoles:
    """
    Parametrized tests for different hole configurations
    """
    
    def test_hole_configuration_validity(self, holes_config, expected_description):
        """Test various hole configurations are handled correctly"""
        lead = InnerCurrentLead(
            name=f"holes_{expected_description}",
            r=[15.0, 20.0],
            h=200.0,
            holes=holes_config
        )
        
        assert lead.holes == holes_config
        assert expected_description in lead.name
        
        # If holes are specified with full 6 parameters, validate angular consistency
        if len(holes_config) == 6 and holes_config[5] > 1:  # More than 1 hole
            n_holes = holes_config[5]
            angle_spacing = holes_config[3]
            
            # For symmetric arrangements, n_holes * angle_spacing should be <= 360
            if n_holes > 0 and angle_spacing > 0:
                total_span = n_holes * angle_spacing
                assert total_span <= 360 or total_span == 360  # Allow exactly 360 for full coverage


@pytest.mark.parametrize("support_config,expected_relationship", [
    ([20.0, 0], "equal_to_outer"),
    ([25.0, 0], "larger_than_outer"), 
    ([15.0, 0], "smaller_than_outer"),
    ([0.0, 0], "zero_radius"),
    ([20.0, 5.0], "positive_offset"),
    ([20.0, -5.0], "negative_offset"),
])
class TestInnerCurrentLeadParameterizedSupport:
    """
    Parametrized tests for different support configurations
    """
    
    def test_support_configuration_validity(self, support_config, expected_relationship):
        """Test various support configurations are handled correctly"""
        r = [15.0, 20.0]  # Standard radius configuration
        lead = InnerCurrentLead(
            name=f"support_{expected_relationship}",
            r=r,
            h=200.0,
            support=support_config
        )
        
        assert lead.support == support_config
        
        if len(support_config) >= 2:
            support_radius = support_config[0]
            support_offset = support_config[1]
            
            # Validate support radius is non-negative
            assert support_radius >= 0
            
            # Validate relationship descriptions
            outer_radius = r[1]
            if expected_relationship == "equal_to_outer":
                assert abs(support_radius - outer_radius) < 1e-10
            elif expected_relationship == "larger_than_outer":
                assert support_radius > outer_radius
            elif expected_relationship == "smaller_than_outer":
                assert support_radius < outer_radius
            elif expected_relationship == "zero_radius":
                assert support_radius == 0.0




# Custom fixtures for complex test scenarios
@pytest.fixture(scope="class")
def current_lead_test_suite():
    """Class-scoped fixture providing test data for multiple test methods"""
    return {
        "standard_configs": [
            {
                "name": "test_1kA",
                "r": [8.0, 12.0],
                "h": 200.0,
                "holes": [60, 5, 0, 180, 0, 2],
                "support": [12.0, 0],
                "fillet": False
            },
            {
                "name": "test_5kA", 
                "r": [15.0, 20.0],
                "h": 350.0,
                "holes": [100, 8, 45, 90, 0, 4],
                "support": [20.0, 2.0],
                "fillet": True
            },
            {
                "name": "test_10kA",
                "r": [19.3, 24.2],
                "h": 480.0,
                "holes": [123, 12, 90, 60, 45, 3],
                "support": [24.2, 0],
                "fillet": True
            }
        ],
        "error_configs": [
            {
                "name": "",  # Empty name
                "r": [10.0, 15.0],
                "expected_error": None  # Empty name should be allowed
            },
            {
                "name": "missing_r",
                "r": [],  # Empty radius list
                "expected_error": None  # Should be allowed for flexibility
            }
        ]
    }


class TestInnerCurrentLeadWithFixture:
    """
    Tests using the current_lead_test_suite fixture
    """
    
    def test_standard_configurations(self, current_lead_test_suite):
        """Test multiple standard configurations"""
        for config in current_lead_test_suite["standard_configs"]:
            lead = InnerCurrentLead(**config)
            
            assert lead.name == config["name"]
            assert lead.r == config["r"]
            assert lead.h == config["h"]
            assert lead.holes == config["holes"]
            assert lead.support == config["support"]
            assert lead.fillet == config["fillet"]
    
    def test_error_configurations(self, current_lead_test_suite):
        """Test error configurations"""
        for config in current_lead_test_suite["error_configs"]:
            if config.get("expected_error"):
                with pytest.raises(config["expected_error"]):
                    InnerCurrentLead(**{k: v for k, v in config.items() 
                                       if k != "expected_error"})
            else:
                # Should succeed
                lead = InnerCurrentLead(**{k: v for k, v in config.items() 
                                         if k != "expected_error"})
                assert isinstance(lead, InnerCurrentLead)
    
