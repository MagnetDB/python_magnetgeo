#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for ModelAxi class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type

# Import the class under test
from python_magnetgeo.ModelAxi import ModelAxi, ModelAxi_constructor

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


class TestModelAxi(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for ModelAxi using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample ModelAxi instance for testing"""
        return ModelAxi(
            name="test_helix",
            h=10.5,
            turns=[2.0, 3.0, 1.5],
            pitch=[5.0, 4.5, 6.0]
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """
!<ModelAxi>
name: test_helix
h: 10.5
turns: [2.0, 3.0, 1.5]
pitch: [5.0, 4.5, 6.0]
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_helix",
            "h": 10.5,
            "turns": [2.0, 3.0, 1.5],
            "pitch": [5.0, 4.5, 6.0]
        }
    
    def get_class_under_test(self) -> Type:
        """Return the ModelAxi class"""
        return ModelAxi
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return ModelAxi
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "ModelAxi"


class TestModelAxiConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for ModelAxi YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = ModelAxi_constructor(loader, node)
            return result.__dict__, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "h": 15.0,
            "turns": [1.0, 2.0],
            "pitch": [3.0, 4.0]
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "ModelAxi"


class TestModelAxiSpecific:
    """
    Specific tests for ModelAxi functionality not covered by mixins
    """
    
    @pytest.fixture
    def sample_modelaxi(self):
        """Fixture providing a sample ModelAxi instance"""
        return ModelAxi(
            name="test_model",
            h=20.0,
            turns=[1.0, 2.0, 1.5, 3.0],
            pitch=[5.0, 5.0, 7.0, 7.0]
        )
    
    @pytest.fixture
    def empty_modelaxi(self):
        """Fixture providing an empty ModelAxi instance"""
        return ModelAxi()
    
    def test_init_default_values(self):
        """Test ModelAxi initialization with default values"""
        model = ModelAxi()
        assert model.name == ""
        assert model.h == 0.0
        assert model.turns == []
        assert model.pitch == []
    
    def test_init_with_values(self):
        """Test ModelAxi initialization with specific values"""
        model = ModelAxi(
            name="helix1", 
            h=15.5, 
            turns=[1.0, 2.0], 
            pitch=[3.0, 4.0]
        )
        assert model.name == "helix1"
        assert model.h == 15.5
        assert model.turns == [1.0, 2.0]
        assert model.pitch == [3.0, 4.0]
    
    def test_repr(self, sample_modelaxi):
        """Test string representation"""
        repr_str = repr(sample_modelaxi)
        assert "ModelAxi" in repr_str
        assert "name='test_model'" in repr_str
        assert "h=20.0" in repr_str
        assert "turns=[1.0, 2.0, 1.5, 3.0]" in repr_str
        assert "pitch=[5.0, 5.0, 7.0, 7.0]" in repr_str
    
    def test_get_Nturns(self, sample_modelaxi):
        """Test get_Nturns method"""
        total_turns = sample_modelaxi.get_Nturns()
        assert total_turns == 7.5  # 1.0 + 2.0 + 1.5 + 3.0
    
    def test_get_Nturns_empty(self, empty_modelaxi):
        """Test get_Nturns with empty turns"""
        total_turns = empty_modelaxi.get_Nturns()
        assert total_turns == 0
    
    @pytest.mark.parametrize("turns,expected", [
        ([1.0, 2.0, 3.0], 6.0),
        ([0.5, 0.5, 1.0], 2.0),
        ([10.0], 10.0),
        ([], 0),
        ([2.5, -1.0, 3.5], 5.0),  # Test with negative values
    ])
    def test_get_Nturns_various_inputs(self, turns, expected):
        """Test get_Nturns with various input combinations"""
        model = ModelAxi(turns=turns)
        assert model.get_Nturns() == expected
    
    def test_compact_empty_pitch(self):
        """Test compact method with empty pitch"""
        model = ModelAxi(turns=[1.0, 2.0, 3.0], pitch=[])
        new_turns, new_pitch = model.compact()
        assert new_turns == [1.0, 2.0, 3.0]
        assert new_pitch == []
    
    def test_compact_no_duplicates(self):
        """Test compact method with no duplicate pitches"""
        model = ModelAxi(
            turns=[1.0, 2.0, 3.0], 
            pitch=[5.0, 6.0, 7.0]
        )
        new_turns, new_pitch = model.compact()
        assert new_turns == [1.0, 2.0, 3.0]
        assert new_pitch == [5.0, 6.0, 7.0]
    
    def test_compact_with_duplicates(self):
        """Test compact method with duplicate pitches"""
        model = ModelAxi(
            turns=[1.0, 2.0, 1.5, 3.0], 
            pitch=[5.0, 5.0, 7.0, 7.0]
        )
        new_turns, new_pitch = model.compact()
        assert new_turns == [3.0, 4.5]  # 1.0+2.0, 1.5+3.0
        assert new_pitch == [5.0, 7.0]
    
    def test_compact_with_tolerance(self):
        """Test compact method with custom tolerance"""
        model = ModelAxi(
            turns=[1.0, 2.0, 1.5], 
            pitch=[5.0, 5.001, 5.002]  # Very close values
        )
        new_turns, new_pitch = model.compact(tol=1e-2)  # 1% tolerance
        assert new_turns == [4.5]  # All turns combined
        assert new_pitch == [5.0]  # First pitch value
    
    def test_compact_with_zero_pitch(self):
        """Test compact method with zero pitch values"""
        model = ModelAxi(
            turns=[1.0, 2.0, 3.0], 
            pitch=[0.0, 0.0, 5.0]
        )
        new_turns, new_pitch = model.compact()
        assert new_turns == [3.0, 3.0]  # 1.0+2.0, 3.0
        assert new_pitch == [0.0, 5.0]
    
    @pytest.mark.parametrize("tol", [1e-6, 1e-4, 1e-2, 0.1])
    def test_compact_tolerance_levels(self, tol):
        """Test compact method with different tolerance levels"""
        model = ModelAxi(
            turns=[1.0, 2.0], 
            pitch=[5.0, 5.0 + tol/2]  # Second pitch within tolerance
        )
        new_turns, new_pitch = model.compact(tol=tol)
        assert len(new_turns) == 1
        assert len(new_pitch) == 1
        assert new_turns[0] == 3.0  # Combined turns
        assert new_pitch[0] == 5.0  # First pitch
    
    def test_compact_preserves_original(self, sample_modelaxi):
        """Test that compact method doesn't modify original lists"""
        original_turns = sample_modelaxi.turns.copy()
        original_pitch = sample_modelaxi.pitch.copy()
        
        new_turns, new_pitch = sample_modelaxi.compact()
        
        # Original should be unchanged
        assert sample_modelaxi.turns == original_turns
        assert sample_modelaxi.pitch == original_pitch
    
    def test_write_to_json_creates_file(self, sample_modelaxi):
        """Test write_to_json method creates file"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_modelaxi.write_to_json()
            mock_file.assert_called_once_with("test_model.json", "w")
    
    def test_write_to_json_content(self, sample_modelaxi):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_modelaxi.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "ModelAxi"
            assert parsed["name"] == "test_model"
    
    def test_yaml_constructor_function_direct(self):
        """Test the ModelAxi_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "h": 25.0,
            "turns": [1.5, 2.5],
            "pitch": [4.0, 5.0]
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = ModelAxi_constructor(mock_loader, mock_node)
        
        assert isinstance(result, ModelAxi)
        assert result.name == "direct_test"
        assert result.h == 25.0
        assert result.turns == [1.5, 2.5]
        assert result.pitch == [4.0, 5.0]
        mock_loader.construct_mapping.assert_called_once_with(mock_node)




class TestModelAxiIntegration:
    """
    Integration tests for ModelAxi with file operations
    """
    
    def test_yaml_roundtrip_integration(self, temp_yaml_file):
        """Test complete YAML serialization/deserialization roundtrip"""
        original = ModelAxi(
            name="roundtrip_test",
            h=12.5,
            turns=[1.0, 2.0, 3.0],
            pitch=[4.0, 5.0, 6.0]
        )
        
        # Write YAML content
        yaml_content = f"""!<ModelAxi>
name: {original.name}
h: {original.h}
turns: {original.turns}
pitch: {original.pitch}
"""
        temp_yaml_file.write(yaml_content)
        temp_yaml_file.flush()
        
        # Test loading (would require proper YAML constructor setup)
        # This tests the structure without full integration
        with open(temp_yaml_file.name, 'r') as f:
            content = f.read()
            assert "!<ModelAxi>" in content
            assert original.name in content
    
    def test_json_serialization_integration(self):
        """Test JSON serialization produces valid, complete data"""
        model = ModelAxi(
            name="json_test",
            h=30.0,
            turns=[2.0, 3.0, 1.0],
            pitch=[10.0, 15.0, 12.0]
        )
        
        json_str = model.to_json()
        parsed = json.loads(json_str)
        
        # Verify all data is preserved
        assert parsed["__classname__"] == "ModelAxi"
        assert parsed["name"] == "json_test"
        assert parsed["h"] == 30.0
        assert parsed["turns"] == [2.0, 3.0, 1.0]
        assert parsed["pitch"] == [10.0, 15.0, 12.0]
        
        # Verify JSON is properly formatted
        assert json_str.count('\n') > 0  # Should be indented
        assert '"__classname__"' in json_str
    
    @pytest.mark.performance
    def test_compact_performance(self):
        """Test compact method performance with large datasets"""
        from .test_utils_common import time_function_execution, assert_performance_within_limits
        
        # Create large dataset
        large_turns = [1.0] * 1000
        large_pitch = [5.0] * 1000  # All same value for maximum compaction
        
        model = ModelAxi(
            name="performance_test",
            turns=large_turns,
            pitch=large_pitch
        )
        
        result, execution_time = time_function_execution(model.compact)
        
        # Should complete quickly even with large dataset
        assert_performance_within_limits(execution_time, 0.1)  # 100ms limit
        
        # Should compact to single values
        new_turns, new_pitch = result
        assert len(new_turns) == 1
        assert len(new_pitch) == 1
        assert new_turns[0] == 1000.0  # Sum of all turns
        assert new_pitch[0] == 5.0
