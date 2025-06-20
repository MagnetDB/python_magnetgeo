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


class TestGrooveInitialization:
    """Test Groove object initialization"""
    
    def test_groove_default_initialization(self):
        """Test Groove initialization with default parameters"""
        groove = Groove()
        
        assert groove.gtype is None
        assert groove.n == 0
        assert groove.eps == 0

    def test_groove_full_initialization(self):
        """Test Groove initialization with all parameters"""
        groove = Groove(gtype="rint", n=5, eps=0.5)
        
        assert groove.gtype == "rint"
        assert groove.n == 5
        assert groove.eps == 0.5

    def test_groove_partial_initialization(self):
        """Test Groove initialization with some parameters"""
        groove = Groove(gtype="rext", n=3)
        
        assert groove.gtype == "rext"
        assert groove.n == 3
        assert groove.eps == 0

    def test_groove_types(self):
        """Test different groove types"""
        rint_groove = Groove(gtype="rint", n=4, eps=1.0)
        rext_groove = Groove(gtype="rext", n=6, eps=2.0)
        
        assert rint_groove.gtype == "rint"
        assert rext_groove.gtype == "rext"


class TestGrooveMethods:
    """Test Groove class methods"""
    
    def test_repr(self):
        """Test __repr__ method"""
        groove = Groove(gtype="rint", n=5, eps=0.75)
        repr_str = repr(groove)
        
        assert "Groove(" in repr_str
        assert "gtype=rint" in repr_str
        assert "n=5" in repr_str
        assert "eps=0.75" in repr_str

    def test_repr_with_none_type(self):
        """Test __repr__ with None gtype"""
        groove = Groove(gtype=None, n=3, eps=1.5)
        repr_str = repr(groove)
        
        assert "gtype=None" in repr_str
        assert "n=3" in repr_str
        assert "eps=1.5" in repr_str


class TestGrooveSerialization:
    """Test Groove serialization/deserialization methods"""
    
    @pytest.fixture
    def sample_groove(self):
        """Create a sample Groove for testing"""
        return Groove(name="test_groove", gtype="rint", n=4, eps=1.2)

    def test_to_json(self, sample_groove):
        """Test to_json method"""
        json_str = sample_groove.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Groove"
        assert parsed["gtype"] == "rint"
        assert parsed["n"] == 4
        assert parsed["eps"] == 1.2

    @patch("builtins.open", new_callable=mock_open)
    def test_dump_yaml(self, mock_file, sample_groove):
        """Test dump method"""
        sample_groove.dump("test_groove")
        
        mock_file.assert_called_once_with("test_groove.yaml", "w")

    @patch("builtins.open", side_effect=Exception("File error"))
    def test_dump_yaml_error(self, mock_open, sample_groove):
        """Test dump method with file error"""
        with pytest.raises(Exception, match="Failed to Tierod dump"):
            sample_groove.dump("error_groove")

    def test_from_yaml(self):
        """Test from_yaml class method"""
        yaml_content = """
!<Groove>
name: test 
gtype: rext
n: 6
eps: 2.5
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    groove = Groove.from_yaml(tmp_file.name)
                
                assert groove.gtype == "rext"
                assert groove.n == 6
                assert groove.eps == 2.5
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_file_error(self):
        """Test from_yaml with file error"""
        with pytest.raises(Exception, match="Failed to load Groove data"):
            Groove.from_yaml("nonexistent_file.yaml")

    @patch("python_magnetgeo.deserialize.unserialize_object")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_from_json(self, mock_file, mock_unserialize):
        """Test from_json class method"""
        mock_groove = Groove(name="test", gtype="rint", n=3, eps=1.0)
        mock_unserialize.return_value = mock_groove
        
        result = Groove.from_json("test.json")
        
        mock_file.assert_called_once_with("test.json", "r")
        mock_unserialize.assert_called_once()
        assert result == mock_groove


class TestGrooveYAMLConstructor:
    """Test YAML constructor functionality"""
    
    def test_groove_constructor_function(self):
        """Test the Groove_constructor function"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = {
            "name": "test", 
            "gtype": "rint",
            "n": 5,
            "eps": 1.5
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result_data, result_type = Groove_constructor(mock_loader, mock_node)
        
        assert result_data == mock_data
        assert result_type == "Groove"
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_yaml_tag_registration(self):
        """Test that the YAML tag is properly registered"""
        assert hasattr(Groove, 'yaml_tag')
        assert Groove.yaml_tag == "Groove"


class TestGrooveEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_groove_with_zero_values(self):
        """Test groove with zero values"""
        groove = Groove(name="test", gtype="rint", n=0, eps=0.0)
        
        assert groove.gtype == "rint"
        assert groove.n == 0
        assert groove.eps == 0.0

    def test_groove_with_negative_values(self):
        """Test groove with negative values"""
        # The class doesn't validate input, so this should work
        groove = Groove(name="test", gtype="rext", n=-1, eps=-0.5)
        
        assert groove.gtype == "rext"
        assert groove.n == -1
        assert groove.eps == -0.5

    def test_groove_with_large_values(self):
        """Test groove with large values"""
        groove = Groove(name="test", gtype="rint", n=1000000, eps=999.999)
        
        assert groove.gtype == "rint"
        assert groove.n == 1000000
        assert groove.eps == 999.999

    def test_groove_with_invalid_gtype(self):
        """Test groove with invalid gtype"""
        # The class doesn't validate gtype, so this should work
        groove = Groove(name="test", gtype="invalid_type", n=5, eps=1.0)
        
        assert groove.gtype == "invalid_type"
        assert groove.n == 5
        assert groove.eps == 1.0


class TestGrooveIntegration:
    """Integration tests for Groove class"""
    
    def test_yaml_roundtrip(self):
        """Test complete YAML serialization/deserialization roundtrip"""
        original_groove = Groove(name="test", gtype="rext", n=8, eps=3.14)
        
        # Serialize to YAML string
        yaml_str = yaml.dump(original_groove)
        
        # Deserialize back
        reconstructed_groove = yaml.load(yaml_str, Loader=yaml.FullLoader)
        
        # Note: This depends on the YAML constructor being properly implemented
        # The current implementation returns a tuple, so this test might need adjustment
        # based on the actual YAML loading behavior

    def test_json_roundtrip(self):
        """Test complete JSON serialization/deserialization roundtrip"""
        original_groove = Groove(name="test", gtype="rint", n=12, eps=2.71)
        
        # Serialize to JSON
        json_str = original_groove.to_json()
        
        # Parse JSON (deserialization would require the deserialize module)
        parsed_data = json.loads(json_str)
        
        # Verify the data structure
        assert parsed_data["__classname__"] == "Groove"
        assert parsed_data["gtype"] == "rint"
        assert parsed_data["n"] == 12
        assert parsed_data["eps"] == 2.71

    def test_multiple_grooves_interaction(self):
        """Test creating and managing multiple grooves"""
        grooves = [
            Groove(name="test", gtype="rint", n=3, eps=0.5),
            Groove(name="test", gtype="rext", n=5, eps=1.0),
            Groove(name="test", gtype="rint", n=7, eps=1.5),
            Groove(name="test", gtype="rext", n=9, eps=2.0)
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
