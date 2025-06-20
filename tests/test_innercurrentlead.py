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
    temp_json_file
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
        return """
!<InnerCurrentLead>
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


class TestInnerCurrentLeadSpecific:
    """
    Specific tests for InnerCurrentLead functionality not covered by mixins
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
    
    def test_dump_success(self, sample_inner_lead):
        """Test dump method success"""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                sample_inner_lead.dump()
                
                mock_file.assert_called_once_with("sample_lead.yaml", "w")
                mock_yaml_dump.assert_called_once()
    
    def test_dump_failure(self, sample_inner_lead):
        """Test dump method failure handling"""
        with patch("yaml.dump", side_effect=Exception("YAML error")):
            with pytest.raises(Exception, match="Failed to dump InnerCurrentLead data"):
                sample_inner_lead.dump()
    
    def test_write_to_json_success(self, sample_inner_lead):
        """Test write_to_json method success"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_inner_lead.write_to_json()
            mock_file.assert_called_once_with("sample_lead.json", "w")
    
    def test_write_to_json_failure(self, sample_inner_lead):
        """Test write_to_json method failure handling"""
        with patch("builtins.open", side_effect=IOError("File error")):
            with pytest.raises(Exception, match="Failed to write to sample_lead.json"):
                sample_inner_lead.write_to_json()
    
    def test_write_to_json_content(self, sample_inner_lead):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_inner_lead.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "InnerCurrentLead"
            assert parsed["name"] == "sample_lead"
    
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


class TestInnerCurrentLeadFromDict:
    """
    Test the from_dict class method
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


class TestInnerCurrentLeadHoleConfiguration:
    """
    Test hole configuration functionality
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
    
    def test_hole_parameters_meaning(self):
        """Test that hole parameters have correct structure"""
        # Based on docstring: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
        holes = [123, 12, 90, 60, 45, 3]
        lead = InnerCurrentLead(
            name="hole_params",
            r=[19.3, 24.2],
            h=480.0,
            holes=holes
        )
        
        assert len(lead.holes) == 6
        # H_Holes (hole height)
        assert lead.holes[0] == 123
        # Shift_from_Top
        assert lead.holes[1] == 12
        # Angle_Zero (reference angle)
        assert lead.holes[2] == 90
        # Angle (angular spacing)
        assert lead.holes[3] == 60
        # Angular_Position
        assert lead.holes[4] == 45
        # N_Holes (number of holes)
        assert lead.holes[5] == 3
    
    def test_hole_configuration_edge_cases(self):
        """Test edge cases for hole configuration"""
        # Very large number of holes
        many_holes = [50, 5, 0, 360/100, 0, 100]  # 100 holes
        lead_many = InnerCurrentLead(name="many_holes", r=[10.0, 15.0], holes=many_holes)
        assert lead_many.holes[5] == 100
        
        # Zero holes
        no_holes = [0, 0, 0, 0, 0, 0]
        lead_none = InnerCurrentLead(name="no_holes", r=[10.0, 15.0], holes=no_holes)
        assert lead_none.holes[5] == 0
        
        # Non-standard hole parameters
        custom_holes = [200, 25, 45, 120, 30, 2]
        lead_custom = InnerCurrentLead(name="custom", r=[20.0, 30.0], holes=custom_holes)
        assert lead_custom.holes == custom_holes


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
    
    def test_support_parameters_meaning(self):
        """Test that support parameters have correct structure"""
        # Based on docstring: [R2, DZ]
        support = [24.2, 0]
        lead = InnerCurrentLead(
            name="support_params",
            r=[19.3, 24.2],
            support=support
        )
        
        assert len(lead.support) == 2
        # R2 (support radius)
        assert lead.support[0] == 24.2
        # DZ (vertical offset)
        assert lead.support[1] == 0
    
    def test_support_radius_relationship(self):
        """Test support radius relationship with main radius"""
        r = [19.3, 24.2]
        
        # Support radius equal to outer radius
        support_equal = [24.2, 0]
        lead_equal = InnerCurrentLead(name="equal", r=r, support=support_equal)
        assert lead_equal.support[0] == r[1]
        
        # Support radius larger than outer radius
        support_larger = [30.0, 0]
        lead_larger = InnerCurrentLead(name="larger", r=r, support=support_larger)
        assert lead_larger.support[0] > r[1]
        
        # Support radius smaller than outer radius
        support_smaller = [20.0, 0]
        lead_smaller = InnerCurrentLead(name="smaller", r=r, support=support_smaller)
        assert lead_smaller.support[0] < r[1]


class TestInnerCurrentLeadGeometry:
    """
    Test geometric aspects of InnerCurrentLead
    """
    
    @pytest.fixture
    def geometric_lead(self):
        """Fixture with InnerCurrentLead having realistic geometry"""
        return InnerCurrentLead(
            name="geometric_test",
            r=[19.3, 24.2],  # Realistic current lead dimensions
            h=480.0,         # 48cm height
            holes=[123, 12, 90, 60, 45, 3],
            support=[24.2, 0]
        )
    
    def test_radius_validation(self, geometric_lead):
        """Test radius parameters are reasonable"""
        assert len(geometric_lead.r) == 2
        assert geometric_lead.r[0] < geometric_lead.r[1]  # Inner < Outer
        assert geometric_lead.r[0] > 0  # Positive inner radius
        assert geometric_lead.r[1] > 0  # Positive outer radius
    
    def test_height_validation(self, geometric_lead):
        """Test height parameter is reasonable"""
        assert geometric_lead.h > 0  # Positive height
        assert geometric_lead.h == 480.0
    
    

class TestInnerCurrentLeadEdgeCases:
    """
    Test edge cases and special scenarios for InnerCurrentLead
    """
    
    def test_zero_dimensions(self):
        """Test InnerCurrentLead with zero dimensions"""
        zero_height = InnerCurrentLead(name="zero_h", r=[1.0, 2.0], h=0.0)
        assert zero_height.h == 0.0
        
        # Zero wall thickness (though physically unrealistic)
        zero_wall = InnerCurrentLead(name="zero_wall", r=[5.0, 5.0], h=10.0)
        assert zero_wall.r[0] == zero_wall.r[1]
    
    def test_negative_values(self):
        """Test InnerCurrentLead with negative values"""
        # Negative height (unusual but mathematically valid)
        negative_h = InnerCurrentLead(name="neg_h", r=[1.0, 2.0], h=-100.0)
        assert negative_h.h == -100.0
        
        # Negative radius values (unusual)
        negative_r = InnerCurrentLead(name="neg_r", r=[-2.0, -1.0], h=10.0)
        assert negative_r.r == [-2.0, -1.0]
    
    def test_very_large_values(self):
        """Test InnerCurrentLead with very large values"""
        large_val = 1e6
        large_lead = InnerCurrentLead(
            name="large_test",
            r=[large_val, large_val * 1.5],
            h=large_val * 2
        )
        assert large_lead.r[0] == large_val
        assert large_lead.h == large_val * 2
    
    def test_unicode_name(self):
        """Test InnerCurrentLead with Unicode name"""
        unicode_name = "内部导线_токопровод_🔌"
        unicode_lead = InnerCurrentLead(
            name=unicode_name,
            r=[1.0, 2.0],
            h=10.0
        )
        assert unicode_lead.name == unicode_name
    
    def test_special_characters_name(self):
        """Test InnerCurrentLead with special characters in name"""
        special_name = "lead!@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_lead = InnerCurrentLead(
            name=special_name,
            r=[1.0, 2.0],
            h=10.0
        )
        assert special_lead.name == special_name
    
    def test_mixed_numeric_types(self):
        """Test InnerCurrentLead with mixed numeric types (int, float)"""
        mixed_lead = InnerCurrentLead(
            name="mixed_types",
            r=[1, 2.5],      # int, float
            h=100,           # int
            holes=[50, 5, 0, 90, 0, 4],  # All int
            support=[2.5, 1] # float, int
        )
        
        assert mixed_lead.r == [1, 2.5]
        assert mixed_lead.h == 100
        assert mixed_lead.support == [2.5, 1]
    
    def test_boolean_fillet_edge_cases(self):
        """Test boolean fillet with edge cases"""
        # Explicit True/False
        true_fillet = InnerCurrentLead(name="true", r=[1.0, 2.0], fillet=True)
        false_fillet = InnerCurrentLead(name="false", r=[1.0, 2.0], fillet=False)
        
        assert true_fillet.fillet is True
        assert false_fillet.fillet is False
        
        # Test in JSON serialization
        true_json = true_fillet.to_json()
        false_json = false_fillet.to_json()
        
        assert "true" in true_json.lower()
        assert "false" in false_json.lower()


class TestInnerCurrentLeadIntegration:
    """
    Integration tests for InnerCurrentLead
    """
    
    def test_yaml_integration(self, temp_yaml_file):
        """Test YAML integration"""
        lead = InnerCurrentLead(
            name="yaml_integration",
            r=[18.0, 23.0],
            h=450.0,
            holes=[110, 10, 45, 50, 30, 4],
            support=[23.0, 2.0],
            fillet=True
        )
        
        # Test dump functionality
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                lead.dump()
                mock_file.assert_called_once_with("yaml_integration.yaml", "w")
                mock_yaml_dump.assert_called_once()
    
    def test_json_integration_complete(self):
        """Test complete JSON serialization integration"""
        lead = InnerCurrentLead(
            name="json_integration",
            r=[20.0, 26.0],
            h=500.0,
            holes=[130, 15, 60, 40, 20, 5],
            support=[26.0, 3.0],
            fillet=False
        )
        
        json_str = lead.to_json()
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["__classname__"] == "InnerCurrentLead"
        assert parsed["name"] == "json_integration"
        assert parsed["r"] == [20.0, 26.0]
        assert parsed["h"] == 500.0
        assert parsed["holes"] == [130, 15, 60, 40, 20, 5]
        assert parsed["support"] == [26.0, 3.0]
        assert parsed["fillet"] is False
    
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


class TestInnerCurrentLeadErrorHandling:
    """
    Test error handling and robustness for InnerCurrentLead
    """
    
    def test_constructor_missing_required_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'name' field
        incomplete_data1 = {
            "r": [1.0, 2.0],
            "h": 10.0,
            "holes": [],
            "support": [],
            "fillet": False
        }
        mock_loader.construct_mapping.return_value = incomplete_data1
        
        with pytest.raises(KeyError):
            InnerCurrentLead_constructor(mock_loader, mock_node)
        
        # Missing 'fillet' field
        incomplete_data2 = {
            "name": "test_name",
            "r": [1.0, 2.0],
            "h": 10.0,
            "holes": [],
            "support": []
        }
        mock_loader.construct_mapping.return_value = incomplete_data2
        
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
    
    def test_dump_file_error(self):
        """Test dump method with file errors"""
        lead = InnerCurrentLead(name="error_test", r=[1.0, 2.0])
        
        # Test file permission error
        with patch("yaml.dump", side_effect=PermissionError("No permission")):
            with pytest.raises(Exception, match="Failed to dump InnerCurrentLead data"):
                lead.dump()
    
    def test_to_json_serialization_error(self):
        """Test to_json with serialization issues"""
        lead = InnerCurrentLead(name="serialization_error", r=[1.0, 2.0])
        
        # Mock serialize_instance to raise an error
        with patch("python_magnetgeo.deserialize.serialize_instance", side_effect=TypeError("Serialization error")):
            with pytest.raises(TypeError):
                lead.to_json()
    
    def test_from_json_file_error(self):
        """Test from_json with file errors"""
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            InnerCurrentLead.from_json("nonexistent_file.json")
    
    def test_from_json_invalid_json(self):
        """Test from_json with invalid JSON content"""
        invalid_json = "{ invalid json content"
        
        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with pytest.raises(json.JSONDecodeError):
                InnerCurrentLead.from_json("invalid.json")


class TestInnerCurrentLeadUseCases:
    """
    Test InnerCurrentLead with realistic use cases and scenarios
    """
    
    def test_standard_current_lead(self):
        """Test InnerCurrentLead representing a standard current lead design"""
        standard_lead = InnerCurrentLead(
            name="standard_10kA_lead",
            r=[19.3, 24.2],   # Standard dimensions for 10kA lead
            h=480.0,          # 48cm height
            holes=[123, 12, 90, 60, 45, 3],  # 3 holes, 60° apart
            support=[24.2, 0], # Support at outer radius
            fillet=True       # Rounded edges for better current flow
        )
        
        assert standard_lead.name == "standard_10kA_lead"
        assert standard_lead.r == [19.3, 24.2]
        assert standard_lead.h == 480.0
        assert standard_lead.fillet is True
        
        # Check hole configuration
        holes = standard_lead.holes
        assert holes[5] == 3  # 3 holes
        assert holes[3] == 60  # 60° spacing
        assert holes[0] == 123  # Hole height
    
    def test_high_current_lead(self):
        """Test InnerCurrentLead for high current applications"""
        high_current_lead = InnerCurrentLead(
            name="high_current_20kA_lead",
            r=[25.0, 35.0],   # Larger dimensions for higher current
            h=600.0,          # Taller for better heat dissipation
            holes=[150, 15, 0, 45, 0, 8],  # 8 holes, 45° apart
            support=[35.0, 5.0],  # Support with offset
            fillet=True
        )
        
        # Larger cross-sectional area for higher current
        area = 3.14159 * (high_current_lead.r[1]**2 - high_current_lead.r[0]**2)
        standard_area = 3.14159 * (24.2**2 - 19.3**2)
        assert area > standard_area
        
        # More holes for better cooling
        assert high_current_lead.holes[5] == 8  # 8 holes
        assert high_current_lead.h > 480.0  # Taller
    
    def test_compact_current_lead(self):
        """Test InnerCurrentLead for space-constrained applications"""
        compact_lead = InnerCurrentLead(
            name="compact_5kA_lead",
            r=[12.0, 16.0],   # Smaller dimensions
            h=250.0,          # Shorter height
            holes=[60, 8, 45, 90, 30, 4],  # 4 holes, 90° apart
            support=[16.0, -2.0],  # Support with negative offset
            fillet=False      # Sharp edges for compact design
        )
        
        # Smaller than standard
        assert compact_lead.r[1] < 24.2
        assert compact_lead.h < 480.0
        assert compact_lead.fillet is False
        
        # Fewer holes due to size constraints
        assert compact_lead.holes[5] == 4  # 4 holes
        assert compact_lead.holes[3] == 90  # 90° spacing
    
    def test_asymmetric_current_lead(self):
        """Test InnerCurrentLead with asymmetric hole pattern"""
        asymmetric_lead = InnerCurrentLead(
            name="asymmetric_lead",
            r=[18.0, 24.0],
            h=400.0,
            holes=[100, 10, 30, 120, 45, 3],  # 3 holes, 120° apart, offset by 30°
            support=[24.0, 3.0],
            fillet=True
        )
        
        holes = asymmetric_lead.holes
        assert holes[2] == 30   # Angle offset
        assert holes[3] == 120  # 120° spacing (asymmetric)
        assert holes[4] == 45   # Angular position
        assert holes[5] == 3    # 3 holes
    
    def test_experimental_current_lead(self):
        """Test InnerCurrentLead for experimental/prototype applications"""
        experimental_lead = InnerCurrentLead(
            name="experimental_prototype",
            r=[15.0, 25.0],
            h=350.0,
            holes=[80, 5, 0, 36, 0, 10],  # 10 holes, 36° apart (fine pattern)
            support=[28.0, 8.0],  # Extended support
            fillet=False
        )
        
        # Many small holes for detailed study
        assert experimental_lead.holes[5] == 10  # 10 holes
        assert experimental_lead.holes[3] == 36  # Fine angular spacing
        
        # Extended support beyond outer radius
        assert experimental_lead.support[0] > experimental_lead.r[1]
    
    def test_maintenance_access_lead(self):
        """Test InnerCurrentLead optimized for maintenance access"""
        maintenance_lead = InnerCurrentLead(
            name="maintenance_accessible_lead",
            r=[20.0, 28.0],
            h=520.0,
            holes=[140, 20, 0, 180, 0, 2],  # 2 holes, 180° apart for access
            support=[28.0, 0],
            fillet=True
        )
        
        holes = maintenance_lead.holes
        assert holes[5] == 2    # Only 2 holes
        assert holes[3] == 180  # Opposite sides for access
        assert holes[1] == 20   # Large shift from top for access


class TestInnerCurrentLeadPerformance:
    """
    Performance tests for InnerCurrentLead operations
    """
    
    @pytest.mark.performance
    def test_large_data_performance(self):
        """Test InnerCurrentLead performance with large datasets"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
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
    
    @pytest.mark.performance
    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
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
    
    @pytest.mark.performance
    def test_repr_performance(self):
        """Test repr performance with large data"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
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


class TestInnerCurrentLeadDocumentation:
    """
    Test that InnerCurrentLead behavior matches its documentation
    """
    
    def test_documented_attributes(self):
        """Test that InnerCurrentLead has all documented attributes"""
        lead = InnerCurrentLead(
            name="documentation_test",
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
    
    def test_holes_parameter_structure(self):
        """Test holes parameter structure matches documentation"""
        # Documentation: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
        holes = [123, 12, 90, 60, 45, 3]
        lead = InnerCurrentLead(name="holes_doc", r=[19.3, 24.2], holes=holes)
        
        assert len(lead.holes) == 6
        # Each parameter should be numeric
        for param in lead.holes:
            assert isinstance(param, (int, float))
    
    def test_support_parameter_structure(self):
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
    
    def test_serialization_support_documented(self):
        """Test that all documented serialization methods work"""
        lead = InnerCurrentLead(
            name="serialize_test",
            r=[10.0, 15.0],
            h=100.0,
            holes=[50, 5, 0, 90, 0, 4],
            support=[15.0, 0],
            fillet=False
        )
        
        # YAML serialization
        assert hasattr(lead, "dump")
        assert callable(lead.dump)
        
        # JSON serialization
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
        
        # Test that JSON serialization actually works
        json_str = lead.to_json()
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "InnerCurrentLead"
        assert parsed["name"] == "serialize_test"
    
    def test_geometric_constraints_documented(self):
        """Test that geometric constraints are reasonable"""
        lead = InnerCurrentLead(
            name="constraints_test",
            r=[19.3, 24.2],
            h=480.0
        )
        
        # Radius constraints
        assert len(lead.r) == 2
        assert lead.r[0] >= 0  # Inner radius non-negative
        assert lead.r[1] > lead.r[0]  # Outer > Inner (typically)
        
        # Height should be positive for physical current leads
        assert lead.h >= 0
    
    def test_fillet_boolean_behavior(self):
        """Test fillet boolean parameter behavior"""
        # Test True
        fillet_true = InnerCurrentLead(name="fillet_true", r=[1.0, 2.0], fillet=True)
        assert fillet_true.fillet is True
        
        # Test False
        fillet_false = InnerCurrentLead(name="fillet_false", r=[1.0, 2.0], fillet=False)
        assert fillet_false.fillet is False
        
        # Test default
        fillet_default = InnerCurrentLead(name="fillet_default", r=[1.0, 2.0])
        assert fillet_default.fillet is False  # Default should be False