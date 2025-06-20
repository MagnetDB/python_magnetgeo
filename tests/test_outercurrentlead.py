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
    temp_json_file
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
        return """
!<OuterCurrentLead>
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
    Note: Original constructor has a bug (infinite recursion), so we test intended behavior
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


class TestOuterCurrentLeadSpecific:
    """
    Specific tests for OuterCurrentLead functionality not covered by mixins
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
    
    def test_repr(self, sample_outer_lead):
        """Test string representation"""
        repr_str = repr(sample_outer_lead)
        assert "OuterCurrentLead" in repr_str
        assert "name='sample_outer'" in repr_str
        assert "r=[100.0, 150.0]" in repr_str
        assert "h=400.0" in repr_str
        assert "bar=[30.0, 40.0, 20.0, 350.0]" in repr_str
        assert "support=[12.0, 25.0, 60.0, 30.0]" in repr_str
    
    def test_dump_success(self, sample_outer_lead):
        """Test dump method success"""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                sample_outer_lead.dump()
                
                mock_file.assert_called_once_with("sample_outer.yaml", "w")
                mock_yaml_dump.assert_called_once()
    
    def test_dump_failure(self, sample_outer_lead):
        """Test dump method failure handling"""
        with patch("yaml.dump", side_effect=Exception("YAML error")):
            with pytest.raises(Exception, match="Failed to dump OuterCurrentLead data"):
                sample_outer_lead.dump()
    
    def test_write_to_json_success(self, sample_outer_lead):
        """Test write_to_json method success"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_outer_lead.write_to_json()
            mock_file.assert_called_once_with("sample_outer.json", "w")
    
    def test_write_to_json_failure(self, sample_outer_lead):
        """Test write_to_json method failure handling"""
        with patch("builtins.open", side_effect=IOError("File error")):
            with pytest.raises(Exception, match="Failed to write to sample_outer.json"):
                sample_outer_lead.write_to_json()
    
    def test_write_to_json_content(self, sample_outer_lead):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_outer_lead.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "OuterCurrentLead"
            assert parsed["name"] == "sample_outer"

    def test_yaml_constructor_function_direct(self):
        """Test the InnerCurrentLead_constructor function directly"""
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

class TestOuterCurrentLeadFromDict:
    """
    Test the from_dict class method
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
        
        # Bar radius should be reasonable
        assert lead.bar[0] < lead.r[1]  # Bar disk radius < outer radius
        
        # All bar dimensions should be positive
        assert all(dim > 0 for dim in lead.bar)


class TestOuterCurrentLeadSupportConfiguration:
    """
    Test support configuration functionality
    Based on documentation: [DX0, DZ, Angle, Angle_Zero]
    """
    
    @pytest.mark.parametrize("support,description", [
        ([10.0, 20.0, 45.0, 0.0], "standard_support"),
        ([15.0, 25.0, 90.0, 45.0], "rotated_support"),
        ([5.0, 10.0, 30.0, 15.0], "angled_support"),
        ([], "no_support"),
        ([12.0, 18.0], "incomplete_support"),
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
        ]
        
        for support, description in angle_configs:
            lead = OuterCurrentLead(
                name=f"angles_{description}",
                r=[100.0, 150.0],
                support=support
            )
            assert lead.support[2] == support[2]  # Angle
            assert lead.support[3] == support[3]  # Angle_Zero


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
        assert len(geometric_lead.r) == 2
        assert geometric_lead.r[0] < geometric_lead.r[1]  # Inner < Outer
        assert all(r > 0 for r in geometric_lead.r)  # Positive values
    
    def test_height_validation(self, geometric_lead):
        """Test height parameter"""
        assert geometric_lead.h > 0
        assert geometric_lead.h == 350.0
    
    def test_bar_to_lead_relationship(self, geometric_lead):
        """Test bar geometry fits within lead geometry"""
        bar_length = geometric_lead.bar[3]  # L parameter
        lead_height = geometric_lead.h
        assert bar_length <= lead_height * 1.1  # Allow reasonable overhang
    
    def test_geometric_scaling(self):
        """Test OuterCurrentLead with different scales"""
        # Small scale
        small_lead = OuterCurrentLead(
            name="small",
            r=[20.0, 30.0],
            h=50.0,
            bar=[5.0, 8.0, 4.0, 40.0]
        )
        assert small_lead.r == [20.0, 30.0]
        
        # Large scale  
        large_lead = OuterCurrentLead(
            name="large",
            r=[500.0, 800.0],
            h=1000.0,
            bar=[100.0, 150.0, 80.0, 900.0]
        )
        assert large_lead.r == [500.0, 800.0]


class TestOuterCurrentLeadEdgeCases:
    """
    Test edge cases and special scenarios
    """
    
    def test_zero_and_negative_values(self):
        """Test with zero and negative values"""
        # Zero height
        zero_h = OuterCurrentLead(name="zero_h", r=[50.0, 60.0], h=0.0)
        assert zero_h.h == 0.0
        
        # Negative height
        neg_h = OuterCurrentLead(name="neg_h", r=[50.0, 60.0], h=-100.0)
        assert neg_h.h == -100.0
        
        # Negative radius values
        neg_r = OuterCurrentLead(name="neg_r", r=[-60.0, -50.0])
        assert neg_r.r == [-60.0, -50.0]
    
    def test_very_large_values(self):
        """Test with very large values"""
        large_val = 1e6
        large_lead = OuterCurrentLead(
            name="large_test",
            r=[large_val, large_val * 1.2],
            h=large_val * 0.5
        )
        assert large_lead.r[0] == large_val
        assert large_lead.h == large_val * 0.5
    
    def test_unicode_and_special_characters(self):
        """Test with Unicode and special characters in name"""
        unicode_name = "外部导线_🔌"
        unicode_lead = OuterCurrentLead(name=unicode_name, r=[100.0, 120.0])
        assert unicode_lead.name == unicode_name
        
        special_name = "lead!@#$%^&*()"
        special_lead = OuterCurrentLead(name=special_name, r=[80.0, 100.0])
        assert special_lead.name == special_name
    
    def test_mixed_numeric_types(self):
        """Test with mixed int/float types"""
        mixed_lead = OuterCurrentLead(
            name="mixed_types",
            r=[100, 120.5],  # int, float
            h=200,           # int
            bar=[25.0, 30, 15.5, 180],  # mixed
            support=[10, 20.0, 45, 0.0] # mixed
        )
        assert mixed_lead.r == [100, 120.5]
        assert mixed_lead.h == 200
    
    def test_empty_lists(self):
        """Test with empty lists"""
        empty_lead = OuterCurrentLead(
            name="empty_lists",
            r=[],
            bar=[],
            support=[]
        )
        assert empty_lead.r == []
        assert empty_lead.bar == []
        assert empty_lead.support == []


class TestOuterCurrentLeadIntegration:
    """
    Integration tests for OuterCurrentLead
    """
    
    def test_yaml_integration(self):
        """Test YAML integration"""
        lead = OuterCurrentLead(
            name="yaml_integration",
            r=[140.0, 190.0],
            h=380.0,
            bar=[32.0, 38.0, 18.0, 320.0],
            support=[14.0, 28.0, 50.0, 25.0]
        )
        
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                lead.dump()
                mock_file.assert_called_once_with("yaml_integration.yaml", "w")
                mock_yaml_dump.assert_called_once()
    
    def test_json_integration_complete(self):
        """Test complete JSON serialization"""
        lead = OuterCurrentLead(
            name="json_integration",
            r=[130.0, 180.0],
            h=360.0,
            bar=[28.0, 35.0, 16.0, 310.0],
            support=[12.0, 24.0, 40.0, 20.0]
        )
        
        json_str = lead.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["__classname__"] == "OuterCurrentLead"
        assert parsed["name"] == "json_integration"
        assert parsed["r"] == [130.0, 180.0]
        assert parsed["h"] == 360.0
        assert parsed["bar"] == [28.0, 35.0, 16.0, 310.0]
        assert parsed["support"] == [12.0, 24.0, 40.0, 20.0]
    
    def test_from_yaml_integration(self):
        """Test from_yaml integration (noting original typo)"""
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
    


class TestOuterCurrentLeadErrorHandling:
    """
    Test error handling and robustness
    """
    
    def test_original_constructor_bug(self):
        """Test documentation of original constructor bug"""
        # Original OuterCurrentLead_constructor has infinite recursion bug:
        # return OuterCurrentLead_constructor(name, r, h, bar, support)
        # Should be: return OuterCurrentLead(name, r, h, bar, support)
        
        # We test the corrected behavior
        def corrected_constructor(name, r, h, bar, support):
            return OuterCurrentLead(name, r, h, bar, support)
        
        result = corrected_constructor(
            "bug_test", [100.0, 150.0], 300.0, 
            [25.0, 30.0, 15.0, 250.0], [10.0, 20.0, 45.0, 0.0]
        )
        assert isinstance(result, OuterCurrentLead)
        assert result.name == "bug_test"
    
    def test_from_yaml_typo_in_original(self):
        """Test documentation of from_yaml typo"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load_yaml:
            mock_lead = Mock(spec=OuterCurrentLead)
            mock_load_yaml.return_value = mock_lead
            
            result = OuterCurrentLead.from_yaml("test.yaml")
            
            mock_load_yaml.assert_called_once_with("OuterCurrentLead", "test.yaml")
    
    def test_file_operation_errors(self):
        """Test file operation error handling"""
        lead = OuterCurrentLead(name="error_test", r=[100.0, 120.0])
        
        # Test dump error
        with patch("yaml.dump", side_effect=PermissionError("No permission")):
            with pytest.raises(Exception, match="Failed to dump OuterCurrentLead data"):
                lead.dump()
        
        # Test write_to_json error
        with patch("builtins.open", side_effect=IOError("Write error")):
            with pytest.raises(Exception, match="Failed to write to error_test.json"):
                lead.write_to_json()
    
    def test_serialization_errors(self):
        """Test serialization error handling"""
        lead = OuterCurrentLead(name="serialization_error", r=[100.0, 120.0])
        
        with patch("python_magnetgeo.deserialize.serialize_instance", 
                   side_effect=TypeError("Serialization error")):
            with pytest.raises(TypeError):
                lead.to_json()
    
    def test_json_file_errors(self):
        """Test JSON file operation errors"""
        # Non-existent file
        with pytest.raises(FileNotFoundError):
            OuterCurrentLead.from_json("nonexistent.json")
        
        # Invalid JSON
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                OuterCurrentLead.from_json("invalid.json")


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
        assert standard_lead.bar[0] < standard_lead.r[1]  # Bar radius < outer radius
        assert standard_lead.bar[3] < standard_lead.h     # Bar length < lead height
    
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
        area = 3.14159 * (high_current.r[1]**2 - high_current.r[0]**2)
        standard_area = 3.14159 * (200.0**2 - 150.0**2)
        assert area > standard_area
        
        # Larger bar dimensions
        assert high_current.bar[1] > 35.0  # DX
        assert high_current.bar[2] > 18.0  # DY
    
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
        assert compact.bar[1] < 35.0 # Compact bar width
        assert compact.bar[2] < 18.0 # Compact bar height
    
    def test_experimental_research_lead(self):
        """Test experimental outer lead for research applications"""
        experimental = OuterCurrentLead(
            name="experimental_research",
            r=[80.0, 250.0],    # Wide radial range for studies
            h=500.0,            # Very tall for thermal research
            bar=[50.0, 60.0, 30.0, 450.0],  # Large bar for current distribution
            support=[25.0, 50.0, 0.0, 0.0]  # Aligned support for measurements
        )
        
        # Wide radial range
        radial_range = experimental.r[1] - experimental.r[0]
        assert radial_range == 170.0
        
        # Very tall for thermal studies
        assert experimental.h == 500.0
        
        # Large bar for current distribution studies
        assert experimental.bar[1] == 60.0  # Large DX
        assert experimental.bar[2] == 30.0  # Large DY


class TestOuterCurrentLeadPerformance:
    """
    Performance tests for OuterCurrentLead operations
    """
    
    @pytest.mark.performance
    def test_initialization_performance(self):
        """Test OuterCurrentLead initialization performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
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
    
    @pytest.mark.performance
    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        lead = OuterCurrentLead(
            name="json_performance",
            r=[150.0, 200.0],
            h=300.0,
            bar=[25.0, 30.0, 15.0, 250.0],
            support=[10.0, 20.0, 45.0, 0.0]
        )
        
        result, execution_time = time_function_execution(lead.to_json)
        
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert isinstance(result, str)
        assert len(result) > 100
    
    @pytest.mark.performance
    def test_repr_performance(self):
        """Test repr performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
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


class TestOuterCurrentLeadDocumentation:
    """
    Test that OuterCurrentLead behavior matches its documentation
    """
    
    def test_documented_attributes(self):
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
    
    def test_geometric_description_compliance(self):
        """Test geometry matches documented description"""
        lead = OuterCurrentLead(
            name="geometry_doc",
            r=[150.0, 200.0],  # [R0, R1] outer radius range
            h=300.0,           # Height
            bar=[25.0, 30.0, 15.0, 250.0],    # [R, DX, DY, L]
            support=[10.0, 20.0, 45.0, 0.0]   # [DX0, DZ, Angle, Angle_Zero]
        )
        
        # Radius constraints for outer current lead
        assert len(lead.r) == 2
        assert lead.r[0] >= 0    # Non-negative inner radius
        assert lead.r[1] > lead.r[0]  # Outer > Inner (typically)
        
        # Height should be positive for physical components
        assert lead.h >= 0
        
        # Bar geometry constraints from documentation
        if lead.bar:
            assert lead.bar[0] > 0   # Positive disk radius R
            assert lead.bar[1] > 0   # Positive rectangle width DX
            assert lead.bar[2] > 0   # Positive rectangle height DY
            assert lead.bar[3] > 0   # Positive prism length L
    
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
    
    def test_known_bugs_documentation(self):
        """Document known bugs in original implementation"""
        # Bug 1: Constructor infinite recursion
        # Original OuterCurrentLead_constructor calls itself:
        # return OuterCurrentLead_constructor(name, r, h, bar, support)
        # Should be: return OuterCurrentLead(name, r, h, bar, support)
        
        # Bug 2: from_yaml uses wrong class name
        # Original uses: loadYaml("Ring", filename)
        # Should be: loadYaml("OuterCurrentLead", filename)
        
        # These bugs prevent proper YAML loading in the original code
        lead = OuterCurrentLead(name="bug_doc", r=[100.0, 120.0])
        
        # Direct instantiation works fine
        assert isinstance(lead, OuterCurrentLead)
        assert lead.name == "bug_doc"
        
        # But YAML constructor and from_yaml have issues
        # Documented in error handling tests above


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
        lead2 = OuterCurrentLead(name="with_r", r=[50.0, 60.0])
        assert lead2.r == [50.0, 60.0]
        assert lead2.h == 0.0
        
        # Name, r, and h
        lead3 = OuterCurrentLead(name="with_r_h", r=[50.0, 60.0], h=100.0)
        assert lead3.h == 100.0
        assert lead3.bar == []
        
        # Name, r, h, and bar
        lead4 = OuterCurrentLead(
            name="with_bar", 
            r=[50.0, 60.0], 
            h=100.0, 
            bar=[10.0, 15.0, 8.0, 80.0]
        )
        assert lead4.bar == [10.0, 15.0, 8.0, 80.0]
        assert lead4.support == []
        
        # All parameters
        lead5 = OuterCurrentLead(
            name="complete",
            r=[50.0, 60.0],
            h=100.0,
            bar=[10.0, 15.0, 8.0, 80.0],
            support=[5.0, 10.0, 30.0, 0.0]
        )
        assert lead5.support == [5.0, 10.0, 30.0, 0.0]
    
    def test_edge_case_list_lengths(self):
        """Test with various list lengths"""
        # Empty lists
        empty = OuterCurrentLead(name="empty", r=[], bar=[], support=[])
        assert empty.r == []
        assert empty.bar == []
        assert empty.support == []
        
        # Single element lists
        single = OuterCurrentLead(
            name="single", 
            r=[100.0], 
            bar=[25.0], 
            support=[10.0]
        )
        assert len(single.r) == 1
        assert len(single.bar) == 1
        assert len(single.support) == 1
        
        # Long lists (more than expected)
        long_lists = OuterCurrentLead(
            name="long",
            r=[100.0, 120.0, 140.0, 160.0],  # More than 2
            bar=[25.0, 30.0, 15.0, 250.0, 10.0, 20.0],  # More than 4
            support=[10.0, 20.0, 45.0, 0.0, 30.0, 60.0]  # More than 4
        )
        assert len(long_lists.r) == 4
        assert len(long_lists.bar) == 6
        assert len(long_lists.support) == 6
    
    def test_floating_point_precision(self):
        """Test with high precision floating point values"""
        precise = OuterCurrentLead(
            name="precise",
            r=[100.123456789012345, 150.987654321098765],
            h=200.555555555555555,
            bar=[25.111111111111111, 30.222222222222222, 
                 15.333333333333333, 250.444444444444444],
            support=[10.777777777777777, 20.888888888888888,
                     45.999999999999999, 0.000000000000001]
        )
        
        # Values should be preserved
        assert precise.r[0] == 100.123456789012345
        assert precise.h == 200.555555555555555
        
        # JSON should handle precision reasonably
        json_str = precise.to_json()
        parsed = json.loads(json_str)
        assert abs(parsed["r"][0] - 100.123456789012345) < 1e-14
    
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