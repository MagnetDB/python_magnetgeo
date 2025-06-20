#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Model3D class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the class under test
from python_magnetgeo.Model3D import Model3D, Model3D_constructor

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


class TestModel3D(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for Model3D using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample Model3D instance for testing"""
        return Model3D(
            cad="test_model.step",
            with_shapes=True,
            with_channels=False
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """
!<Model3D>
cad: test_model.step
with_shapes: true
with_channels: false
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "cad": "test_model.step",
            "with_shapes": True,
            "with_channels": False
        }
    
    def get_class_under_test(self) -> Type:
        """Return the Model3D class"""
        return Model3D
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return Model3D
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "Model3D"


class TestModel3DConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for Model3D YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = Model3D_constructor(loader, node)
            return result.__dict__, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "cad": "constructor_test.step",
            "with_shapes": True,
            "with_channels": True
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "Model3D"


class TestModel3DSpecific:
    """
    Specific tests for Model3D functionality not covered by mixins
    """
    
    @pytest.fixture
    def sample_model3d(self):
        """Fixture providing a sample Model3D instance"""
        return Model3D(
            cad="sample_model.step",
            with_shapes=True,
            with_channels=False
        )
    
    @pytest.fixture
    def default_model3d(self):
        """Fixture providing a Model3D with default values"""
        return Model3D(cad="default.step")
    
    def test_init_required_parameter(self):
        """Test Model3D initialization with required cad parameter"""
        model = Model3D(cad="required.step")
        assert model.cad == "required.step"
        assert model.with_shapes is False  # Default value
        assert model.with_channels is False  # Default value
    
    def test_init_with_all_parameters(self):
        """Test Model3D initialization with all parameters"""
        model = Model3D(
            cad="full_model.step",
            with_shapes=True,
            with_channels=True
        )
        assert model.cad == "full_model.step"
        assert model.with_shapes is True
        assert model.with_channels is True
    
    @pytest.mark.parametrize("with_shapes,with_channels", [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_init_boolean_combinations(self, with_shapes, with_channels):
        """Test Model3D with different boolean combinations"""
        model = Model3D(
            cad="test.step",
            with_shapes=with_shapes,
            with_channels=with_channels
        )
        assert model.with_shapes == with_shapes
        assert model.with_channels == with_channels
    
    def test_repr(self, sample_model3d):
        """Test string representation"""
        repr_str = repr(sample_model3d)
        assert "Model3D" in repr_str
        assert "cad='sample_model.step'" in repr_str
        assert "with_shapes=True" in repr_str
        assert "with_channels=False" in repr_str
    
    def test_repr_all_false(self):
        """Test string representation with all boolean flags False"""
        model = Model3D(cad="minimal.step", with_shapes=False, with_channels=False)
        repr_str = repr(model)
        assert "with_shapes=False" in repr_str
        assert "with_channels=False" in repr_str
    
    def test_write_to_json_with_name(self, sample_model3d):
        """Test write_to_json method with custom name"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_model3d.write_to_json(name="custom_name")
            mock_file.assert_called_once_with("custom_name.json", "w")
    
    def test_write_to_json_empty_name(self, sample_model3d):
        """Test write_to_json method with empty name"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_model3d.write_to_json(name="")
            mock_file.assert_called_once_with(".json", "w")
    
    def test_write_to_json_content(self, sample_model3d):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_model3d.write_to_json(name="test_output")
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "Model3D"
            assert parsed["cad"] == "sample_model.step"
            assert parsed["with_shapes"] is True
            assert parsed["with_channels"] is False
    
    def test_yaml_constructor_function_direct(self):
        """Test the Model3D_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "cad": "direct_test.step",
            "with_shapes": True,
            "with_channels": False
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Model3D_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Model3D)
        assert result.cad == "direct_test.step"
        assert result.with_shapes is True
        assert result.with_channels is False
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestModel3DFileFormats:
    """
    Test Model3D with different CAD file formats
    """
    
    @pytest.mark.parametrize("file_extension", [
        ".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".ply"
    ])
    def test_common_cad_formats(self, file_extension):
        """Test Model3D with common CAD file formats"""
        filename = f"model{file_extension}"
        model = Model3D(cad=filename)
        assert model.cad == filename
        assert filename in repr(model)
    
    @pytest.mark.parametrize("filename", [
        "model.STEP",  # Uppercase
        "model.Step",  # Mixed case
        "complex_model_v2.step",  # Complex name
        "model with spaces.step",  # Spaces
        "модель.step",  # Unicode
        "model-v1.0.step",  # Version numbers
        "model_final_FINAL.step",  # Common naming pattern
    ])
    def test_various_filenames(self, filename):
        """Test Model3D with various filename patterns"""
        model = Model3D(cad=filename)
        assert model.cad == filename
    
    def test_empty_filename(self):
        """Test Model3D with empty filename"""
        model = Model3D(cad="")
        assert model.cad == ""
    
    def test_very_long_filename(self):
        """Test Model3D with very long filename"""
        long_name = "very_" * 50 + "long_filename.step"
        model = Model3D(cad=long_name)
        assert model.cad == long_name


class TestModel3DEdgeCases:
    """
    Test edge cases and special scenarios for Model3D
    """
    
    def test_special_characters_in_cad_filename(self):
        """Test Model3D with special characters in CAD filename"""
        special_chars = "model!@#$%^&*()_+-=[]{}|;':\",./<>?.step"
        model = Model3D(cad=special_chars)
        assert model.cad == special_chars
    
    def test_path_separators_in_filename(self):
        """Test Model3D with path separators in filename"""
        path_filename = "/path/to/model.step"
        model = Model3D(cad=path_filename)
        assert model.cad == path_filename
        
        windows_path = "C:\\path\\to\\model.step"
        model_win = Model3D(cad=windows_path)
        assert model_win.cad == windows_path
    
    def test_none_values_handling(self):
        """Test Model3D behavior with None-like inputs"""
        # Note: The constructor requires cad as str, so we test string "None"
        model = Model3D(cad="None")
        assert model.cad == "None"
    
    def test_boolean_flag_combinations_comprehensive(self):
        """Test all combinations of boolean flags with edge cases"""
        test_cases = [
            (True, True, "both_true"),
            (True, False, "shapes_only"),
            (False, True, "channels_only"),
            (False, False, "neither"),
        ]
        
        for with_shapes, with_channels, description in test_cases:
            model = Model3D(
                cad=f"{description}.step",
                with_shapes=with_shapes,
                with_channels=with_channels
            )
            assert model.with_shapes == with_shapes
            assert model.with_channels == with_channels
            assert description in model.cad


class TestModel3DIntegration:
    """
    Integration tests for Model3D
    """
    
    def test_yaml_content_structure(self, temp_yaml_file):
        """Test YAML content structure for Model3D"""
        model = Model3D(
            cad="integration_test.step",
            with_shapes=True,
            with_channels=False
        )
        
        # Write YAML content
        yaml_content = f"""!<Model3D>
cad: {model.cad}
with_shapes: {str(model.with_shapes).lower()}
with_channels: {str(model.with_channels).lower()}
"""
        temp_yaml_file.write(yaml_content)
        temp_yaml_file.flush()
        
        # Test loading structure
        with open(temp_yaml_file.name, 'r') as f:
            content = f.read()
            assert "!<Model3D>" in content
            assert model.cad in content
            assert "with_shapes: true" in content
            assert "with_channels: false" in content
    
    def test_json_serialization_completeness(self):
        """Test that JSON serialization preserves all data"""
        model = Model3D(
            cad="completeness_test.step",
            with_shapes=True,
            with_channels=True
        )
        
        json_str = model.to_json()
        parsed = json.loads(json_str)
        
        # Verify all attributes are present
        expected_keys = {"__classname__", "cad", "with_shapes", "with_channels"}
        assert set(parsed.keys()) == expected_keys
        
        # Verify values are correct
        assert parsed["__classname__"] == "Model3D"
        assert parsed["cad"] == "completeness_test.step"
        assert parsed["with_shapes"] is True
        assert parsed["with_channels"] is True
    
    def test_write_to_json_file_handling(self):
        """Test write_to_json with various file handling scenarios"""
        model = Model3D(cad="file_test.step")
        
        # Test successful write
        with patch("builtins.open", mock_open()) as mock_file:
            model.write_to_json("success_test")
            mock_file.assert_called_once_with("success_test.json", "w")
            
            # Verify write was called
            handle = mock_file.return_value
            assert handle.write.called
    
    def test_constructor_with_yaml_integration(self):
        """Test Model3D_constructor integration with YAML loading"""
        yaml_data = {
            "cad": "yaml_integration.step",
            "with_shapes": False,
            "with_channels": True
        }
        
        mock_loader = Mock()
        mock_node = Mock()
        mock_loader.construct_mapping.return_value = yaml_data
        
        result = Model3D_constructor(mock_loader, mock_node)
        
        # Verify proper construction
        assert isinstance(result, Model3D)
        assert result.cad == "yaml_integration.step"
        assert result.with_shapes is False
        assert result.with_channels is True


class TestModel3DPerformance:
    """
    Performance tests for Model3D operations
    """
    
    @pytest.mark.performance
    def test_large_filename_performance(self):
        """Test Model3D performance with very large filenames"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        # Create very long filename
        large_filename = "x" * 10000 + ".step"
        
        def create_model():
            return Model3D(cad=large_filename)
        
        result, execution_time = time_function_execution(create_model)
        
        # Should handle large filenames quickly
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert result.cad == large_filename
    
    @pytest.mark.performance
    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        model = Model3D(
            cad="performance_test.step",
            with_shapes=True,
            with_channels=True
        )
        
        result, execution_time = time_function_execution(model.to_json)
        
        # JSON serialization should be fast
        assert_performance_within_limits(execution_time, 0.01)  # 10ms limit
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.performance
    def test_repr_performance(self):
        """Test repr performance with large data"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        model = Model3D(cad="x" * 1000 + ".step")
        
        result, execution_time = time_function_execution(repr, model)
        
        # Repr should be fast even with large data
        assert_performance_within_limits(execution_time, 0.005)  # 5ms limit
        assert "Model3D" in result


class TestModel3DErrorHandling:
    """
    Test error handling and robustness for Model3D
    """
    
    def test_write_to_json_file_error(self):
        """Test write_to_json error handling"""
        model = Model3D(cad="error_test.step")
        
        # Simulate file write error
        with patch("builtins.open", side_effect=PermissionError("No permission")):
            with pytest.raises(PermissionError):
                model.write_to_json("no_permission")
    
    def test_to_json_with_serialization_error(self):
        """Test to_json with potential serialization issues"""
        model = Model3D(cad="serialization_test.step")
        
        # Mock serialize_instance to raise an error
        with patch("python_magnetgeo.deserialize.serialize_instance", side_effect=ValueError("Serialization error")):
            with pytest.raises(ValueError):
                model.to_json()
    
    def test_constructor_missing_fields(self):
        """Test constructor with missing required fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Missing 'cad' field
        incomplete_data = {
            "with_shapes": True,
            "with_channels": False
        }
        mock_loader.construct_mapping.return_value = incomplete_data
        
        with pytest.raises(KeyError):
            Model3D_constructor(mock_loader, mock_node)
    
    def test_constructor_extra_fields(self):
        """Test constructor with extra fields (should be ignored)"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Extra fields that don't exist in Model3D
        data_with_extras = {
            "cad": "extra_fields_test.step",
            "with_shapes": True,
            "with_channels": False,
            "extra_field": "should_be_ignored",
            "another_extra": 42
        }
        mock_loader.construct_mapping.return_value = data_with_extras
        
        # Should work fine, ignoring extra fields
        result = Model3D_constructor(mock_loader, mock_node)
        assert isinstance(result, Model3D)
        assert result.cad == "extra_fields_test.step"
        assert not hasattr(result, "extra_field")
        assert not hasattr(result, "another_extra")


class TestModel3DCompatibility:
    """
    Test Model3D compatibility with different data types and formats
    """
    
    @pytest.mark.parametrize("boolean_input,expected", [
        ("true", "true"),  # String representation
        ("false", "false"),
        ("True", "True"),
        ("False", "False"),
        ("1", "1"),
        ("0", "0"),
    ])
    def test_string_boolean_representation(self, boolean_input, expected):
        """Test how Model3D handles string representations of booleans"""
        # Note: This tests the cad field with boolean-like strings
        model = Model3D(cad=f"model_{boolean_input}.step")
        assert f"model_{expected}.step" in model.cad
    
    def test_unicode_support(self):
        """Test Model3D with Unicode characters"""
        unicode_filename = "модель_测试_🤖.step"
        model = Model3D(cad=unicode_filename)
        assert model.cad == unicode_filename
        
        # Test in repr
        repr_str = repr(model)
        assert unicode_filename in repr_str
        
        # Test in JSON
        json_str = model.to_json()
        parsed = json.loads(json_str)
        assert parsed["cad"] == unicode_filename
    
    def test_json_special_characters_escaping(self):
        """Test JSON serialization properly escapes special characters"""
        special_cad = 'model"with\\quotes/and\nspecial\tchars.step'
        model = Model3D(cad=special_cad)
        
        json_str = model.to_json()
        parsed = json.loads(json_str)  # Should not raise exception
        assert parsed["cad"] == special_cad
    
    def test_comparison_operations(self):
        """Test Model3D instances comparison (implicit equality)"""
        model1 = Model3D(cad="same.step", with_shapes=True, with_channels=False)
        model2 = Model3D(cad="same.step", with_shapes=True, with_channels=False)
        model3 = Model3D(cad="different.step", with_shapes=True, with_channels=False)
        
        # Test that identical models have same string representation
        assert repr(model1) == repr(model2)
        assert repr(model1) != repr(model3)
        
        # Test that JSON serialization is consistent
        assert model1.to_json() == model2.to_json()
        assert model1.to_json() != model3.to_json()
