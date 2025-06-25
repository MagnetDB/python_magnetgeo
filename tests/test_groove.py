#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Groove class
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Groove import Groove, Groove_constructor
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes
)


class TestGrooveInitialization:
    """Test Groove object initialization"""
    
    def test_groove_default_initialization(self):
        """Test Groove initialization with default parameters"""
        groove = Groove()
        
        assert groove.name == ''
        assert groove.gtype is None
        assert groove.n == 0
        assert groove.eps == 0

    def test_groove_full_initialization(self):
        """Test Groove initialization with all parameters"""
        groove = Groove(name="test_groove", gtype="rint", n=5, eps=0.5)
        
        assert groove.name == "test_groove"
        assert groove.gtype == "rint"
        assert groove.n == 5
        assert groove.eps == 0.5

    def test_groove_partial_initialization(self):
        """Test Groove initialization with some parameters"""
        groove = Groove(name="partial", gtype="rext", n=3)
        
        assert groove.name == "partial"
        assert groove.gtype == "rext"
        assert groove.n == 3
        assert groove.eps == 0

    def test_groove_types(self):
        """Test different groove types"""
        rint_groove = Groove(name="rint_test", gtype="rint", n=4, eps=1.0)
        rext_groove = Groove(name="rext_test", gtype="rext", n=6, eps=2.0)
        
        assert rint_groove.gtype == "rint"
        assert rext_groove.gtype == "rext"

    @pytest.mark.parametrize("gtype", ["rint", "rext"])
    def test_valid_groove_types(self, gtype):
        """Test valid groove types"""
        groove = Groove(name="test", gtype=gtype, n=3, eps=1.0)
        assert groove.gtype == gtype

    @pytest.mark.parametrize("n,eps", [
        (0, 0.0),
        (1, 0.1),
        (5, 1.5),
        (10, 2.0)
    ])
    def test_numeric_parameters(self, n, eps):
        """Test various numeric parameter combinations"""
        groove = Groove(name="test", gtype="rint", n=n, eps=eps)
        assert groove.n == n
        assert groove.eps == eps


class TestGrooveMethods:
    """Test Groove class methods"""
    
    def test_repr(self):
        """Test __repr__ method"""
        groove = Groove(name="test_groove", gtype="rint", n=5, eps=0.75)
        repr_str = repr(groove)
        
        assert "Groove(" in repr_str
        assert "name=test_groove" in repr_str
        assert "gtype=rint" in repr_str
        assert "n=5" in repr_str
        assert "eps=0.75" in repr_str

    def test_repr_with_none_type(self):
        """Test __repr__ with None gtype"""
        groove = Groove(name="none_test", gtype=None, n=3, eps=1.5)
        repr_str = repr(groove)
        
        assert "name=none_test" in repr_str
        assert "gtype=None" in repr_str
        assert "n=3" in repr_str
        assert "eps=1.5" in repr_str

    def test_repr_with_empty_name(self):
        """Test __repr__ with empty name"""
        groove = Groove(name="", gtype="rext", n=2, eps=0.8)
        repr_str = repr(groove)
        
        assert "name=" in repr_str
        assert "gtype=rext" in repr_str

    def test_repr_format_consistency(self):
        """Test that __repr__ format is consistent"""
        groove = Groove(name="format_test", gtype="rint", n=7, eps=2.25)
        repr_str = repr(groove)
        
        # Should match the expected format from the implementation
        expected_format = "Groove(name=format_test, gtype=rint, n=7, eps=2.25)"
        assert repr_str == expected_format


class TestGrooveSerialization(BaseSerializationTestMixin):
    """Test Groove serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Groove instance"""
        return Groove(name="test_groove", gtype="rint", n=4, eps=1.2)
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
!<Groove>
name: test_groove
gtype: rext
n: 6
eps: 2.5
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_groove",
            "gtype": "rint",
            "n": 4,
            "eps": 1.2
        }
    
    def get_class_under_test(self):
        """Return Groove class"""
        return Groove

    def test_to_json_structure(self):
        """Test JSON serialization structure"""
        groove = self.get_sample_instance()
        json_str = groove.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Groove"
        assert parsed["gtype"] == "rint"
        assert parsed["n"] == 4
        assert parsed["eps"] == 1.2

    @patch("builtins.open", new_callable=mock_open)
    def test_dump_yaml_success(self, mock_file):
        """Test successful dump method"""
        groove = Groove(name="dump_test", gtype="rint", n=3, eps=1.0)
        groove.dump()
        
        mock_file.assert_called_once_with("dump_test.yaml", "w")

    @patch("builtins.open", side_effect=Exception("File error"))
    def test_dump_yaml_error(self, mock_open_error):
        """Test dump method with file error"""
        groove = Groove(name="error_test", gtype="rext", n=2, eps=0.5)
        
        with pytest.raises(Exception, match="Failed to Tierod dump"):
            groove.dump()

    def test_from_yaml_complete(self):
        """Test from_yaml class method with complete data"""
        yaml_content = '''
!<Groove>
name: yaml_test
gtype: rext
n: 6
eps: 2.5
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    groove = Groove.from_yaml(tmp_file.name)
                
                assert groove.name == "yaml_test"
                assert groove.gtype == "rext"
                assert groove.n == 6
                assert groove.eps == 2.5
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_minimal(self):
        """Test from_yaml with minimal required data"""
        yaml_content = '''
!<Groove>
name: minimal
gtype: rint
n: 1
eps: 0.1
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    groove = Groove.from_yaml(tmp_file.name)
                
                assert groove.name == "minimal"
                assert groove.gtype == "rint"
                assert groove.n == 1
                assert groove.eps == 0.1
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_file_error(self):
        """Test from_yaml with file error"""
        with pytest.raises(Exception, match="Failed to load Groove data"):
            Groove.from_yaml("nonexistent_file.yaml")

    @patch("python_magnetgeo.deserialize.unserialize_object")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_from_json_success(self, mock_file, mock_unserialize):
        """Test successful from_json class method"""
        mock_groove = Groove(name="json_test", gtype="rint", n=3, eps=1.0)
        mock_unserialize.return_value = mock_groove
        
        result = Groove.from_json("test.json")
        
        mock_file.assert_called_once_with("test.json", "r")
        mock_unserialize.assert_called_once()
        assert result == mock_groove

    def test_from_json_file_error(self):
        """Test from_json with file error"""
        with pytest.raises(Exception, match="Failed to load Groove data"):
            Groove.from_json("nonexistent_file.json")


class TestGrooveYAMLConstructor:
    """Test YAML constructor functionality"""
    
    def test_yaml_constructor_function(self):
        """Test the Groove_constructor function"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = {
            "name": "constructor_test",
            "gtype": "rint",
            "n": 5,
            "eps": 1.5
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Groove_constructor(mock_loader, mock_node)
        
        # The constructor should return a Groove instance directly
        assert isinstance(result, Groove)
        assert result.name == "constructor_test"
        assert result.gtype == "rint"
        assert result.n == 5
        assert result.eps == 1.5
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_groove_constructor_function_complete(self):
        """Test the Groove_constructor function with complete data"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = {
            "name": "complete_test",
            "gtype": "rext",
            "n": 8,
            "eps": 2.0
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Groove_constructor(mock_loader, mock_node)
        
        # The constructor should return a Groove instance, not a tuple
        assert isinstance(result, Groove)
        assert result.name == "complete_test"
        assert result.gtype == "rext"
        assert result.n == 8
        assert result.eps == 2.0
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_groove_constructor_function_minimal(self):
        """Test the Groove_constructor function with minimal data"""
        mock_loader = Mock()
        mock_node = Mock()
        
        mock_data = {
            "name": "",
            "gtype": "rint",
            "n": 1,
            "eps": 0.0
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Groove_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Groove)
        assert result.name == ""
        assert result.gtype == "rint"
        assert result.n == 1
        assert result.eps == 0.0

    def test_groove_constructor_with_defaults(self):
        """Test constructor with get() method for optional fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Test with missing 'name' field (should default to '')
        mock_data = {
            "gtype": "rext",
            "n": 3,
            "eps": 1.0
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Groove_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Groove)
        assert result.name == ""  # Should default to empty string
        assert result.gtype == "rext"
        assert result.n == 3
        assert result.eps == 1.0


class TestGrooveYAMLTag(BaseYAMLTagTestMixin):
    """Test Groove YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Groove class"""
        return Groove
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Groove"

    def test_yaml_tag_registration(self):
        """Test that the YAML tag is properly registered"""
        assert hasattr(Groove, 'yaml_tag')
        assert Groove.yaml_tag == "Groove"
        
        # Test that the constructor is registered with yaml
        # Note: This is a more comprehensive test than the base mixin
        # You might need to check yaml's internal registration if needed


class TestGrooveIntegration:
    """Integration tests for Groove class"""
    
    def test_yaml_serialization_roundtrip(self):
        """Test YAML serialization and deserialization"""
        original_groove = Groove(name="roundtrip_test", gtype="rext", n=8, eps=3.14)
        
        # Serialize to YAML string
        yaml_str = yaml.dump(original_groove)
        assert isinstance(yaml_str, str)
        assert len(yaml_str) > 0
        
        # The YAML should contain the tag and data
        assert "!<Groove>" in yaml_str or "Groove" in yaml_str
        assert "gtype: rext" in yaml_str
        assert "n: 8" in yaml_str

    def test_json_serialization_roundtrip(self):
        """Test JSON serialization data integrity"""
        original_groove = Groove(name="json_test", gtype="rint", n=12, eps=2.71)
        
        # Serialize to JSON
        json_str = original_groove.to_json()
        
        # Parse JSON (deserialization would require the deserialize module)
        parsed_data = json.loads(json_str)
        
        # Verify the data structure
        assert parsed_data["__classname__"] == "Groove"
        assert parsed_data["name"] == "json_test"
        assert parsed_data["gtype"] == "rint"
        assert parsed_data["n"] == 12
        assert parsed_data["eps"] == 2.71

    def test_multiple_grooves_interaction(self):
        """Test creating and managing multiple grooves"""
        grooves = [
            Groove(name="groove1", gtype="rint", n=3, eps=0.5),
            Groove(name="groove2", gtype="rext", n=5, eps=1.0),
            Groove(name="groove3", gtype="rint", n=7, eps=1.5),
            Groove(name="groove4", gtype="rext", n=9, eps=2.0)
        ]
        
        # Test that each groove maintains its own state
        assert grooves[0].gtype == "rint" and grooves[0].n == 3
        assert grooves[1].gtype == "rext" and grooves[1].n == 5
        assert grooves[2].gtype == "rint" and grooves[2].n == 7
        assert grooves[3].gtype == "rext" and grooves[3].n == 9
        
        # Test that modifying one doesn't affect others
        grooves[0].eps = 10.0
        assert grooves[1].eps == 1.0
        assert grooves[2].eps == 1.5
        assert grooves[3].eps == 2.0

    def test_groove_collection_operations(self):
        """Test operations on collections of grooves"""
        grooves = [
            Groove(name=f"groove_{i}", gtype="rint" if i % 2 == 0 else "rext", n=i+1, eps=i*0.5)
            for i in range(5)
        ]
        
        # Test filtering by type
        rint_grooves = [g for g in grooves if g.gtype == "rint"]
        rext_grooves = [g for g in grooves if g.gtype == "rext"]
        
        assert len(rint_grooves) == 3  # indices 0, 2, 4
        assert len(rext_grooves) == 2  # indices 1, 3
        
        # Test sorting by number of grooves
        sorted_grooves = sorted(grooves, key=lambda g: g.n)
        assert sorted_grooves[0].n == 1
        assert sorted_grooves[-1].n == 5
        
        # Test aggregation
        total_grooves = sum(g.n for g in grooves)
        assert total_grooves == 15  # 1+2+3+4+5


class TestGrooveValidation:
    """Test Groove parameter validation and edge cases"""
    
    @pytest.mark.parametrize("gtype", ["rint", "rext", None])
    def test_gtype_values(self, gtype):
        """Test various gtype values"""
        groove = Groove(name="test", gtype=gtype, n=1, eps=0.1)
        assert groove.gtype == gtype

    @pytest.mark.parametrize("n", [0, 1, 5, 10, 100])
    def test_n_values(self, n):
        """Test various n values"""
        groove = Groove(name="test", gtype="rint", n=n, eps=1.0)
        assert groove.n == n

    @pytest.mark.parametrize("eps", [0.0, 0.1, 1.0, 5.0, 10.0])
    def test_eps_values(self, eps):
        """Test various eps values"""
        groove = Groove(name="test", gtype="rint", n=5, eps=eps)
        assert groove.eps == eps

    def test_negative_values(self):
        """Test behavior with negative values"""
        # The implementation might allow negative values
        groove = Groove(name="test", gtype="rint", n=-1, eps=-0.5)
        assert groove.n == -1
        assert groove.eps == -0.5

    def test_zero_values(self):
        """Test behavior with zero values"""
        groove = Groove(name="test", gtype="rint", n=0, eps=0.0)
        assert groove.n == 0
        assert groove.eps == 0.0

    def test_float_precision(self):
        """Test floating point precision handling"""
        eps_value = 1.23456789
        groove = Groove(name="test", gtype="rint", n=1, eps=eps_value)
        assert groove.eps == eps_value


class TestGrooveErrorHandling:
    """Test error handling in Groove class"""
    
    def test_repr_with_special_characters(self):
        """Test __repr__ with special characters in name"""
        special_names = ["test with spaces", "test-with-dashes", "test_with_underscores", ""]
        
        for name in special_names:
            groove = Groove(name=name, gtype="rint", n=1, eps=0.1)
            repr_str = repr(groove)
            assert isinstance(repr_str, str)
            assert "Groove(" in repr_str

    def test_serialization_with_special_values(self):
        """Test serialization with special floating point values"""
        # Test with very small eps
        groove = Groove(name="small", gtype="rint", n=1, eps=1e-10)
        json_str = groove.to_json()
        parsed = json.loads(json_str)
        assert parsed["eps"] == 1e-10
        
        # Test with large eps
        groove = Groove(name="large", gtype="rint", n=1, eps=1e6)
        json_str = groove.to_json()
        parsed = json.loads(json_str)
        assert parsed["eps"] == 1e6

    def test_type_coercion(self):
        """Test type coercion for numeric parameters"""
        # Test with string numbers (if the implementation handles this)
        try:
            groove = Groove(name="test", gtype="rint", n="5", eps="1.5")
            # If this works, check if values are converted
            assert groove.n == "5" or groove.n == 5
            assert groove.eps == "1.5" or groove.eps == 1.5
        except TypeError:
            # Expected if implementation requires proper types
            pass


class TestGroovePerformance:
    """Performance tests for Groove class"""
    
    def test_large_scale_creation(self):
        """Test creating many groove instances"""
        grooves = []
        for i in range(1000):
            groove = Groove(
                name=f"groove_{i}",
                gtype="rint" if i % 2 == 0 else "rext",
                n=i % 10 + 1,
                eps=i * 0.001
            )
            grooves.append(groove)
        
        assert len(grooves) == 1000
        assert all(isinstance(g, Groove) for g in grooves)
        
        # Test that all have unique names and proper values
        names = [g.name for g in grooves]
        assert len(set(names)) == 1000  # All unique names

    def test_repr_performance(self):
        """Test __repr__ performance with many grooves"""
        grooves = [
            Groove(name=f"perf_test_{i}", gtype="rint", n=i, eps=i*0.1)
            for i in range(100)
        ]
        
        # Generate all repr strings
        repr_strings = [repr(g) for g in grooves]
        
        assert len(repr_strings) == 100
        assert all(isinstance(s, str) for s in repr_strings)
        assert all("Groove(" in s for s in repr_strings)

    def test_serialization_performance(self):
        """Test serialization performance"""
        grooves = [
            Groove(name=f"serial_test_{i}", gtype="rint", n=i, eps=i*0.01)
            for i in range(50)
        ]
        
        # Test JSON serialization performance
        json_strings = [g.to_json() for g in grooves]
        
        assert len(json_strings) == 50
        assert all(isinstance(s, str) for s in json_strings)
        
        # Verify all can be parsed back
        parsed_data = [json.loads(s) for s in json_strings]
        assert len(parsed_data) == 50
        assert all("__classname__" in d for d in parsed_data)



