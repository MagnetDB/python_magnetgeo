#!/usr/bin/env python3
"""
Test suite for Tierod API breaking changes
"""

import pytest
import tempfile
import yaml
from python_magnetgeo.tierod import Tierod
from python_magnetgeo.validation import ValidationError

class TestTierodBreakingChanges:
    
    def test_enhanced_validation(self):
        """Test that new validation catches invalid inputs"""
        
        # Valid case should work
        tierod = Tierod(
            name="test_tierod",
            r=12.5,
            n=8, 
            dh=10.0,
            sh=5.0,
            shape=None
        )
        assert tierod.name == "test_tierod"
        
        # Invalid name should raise ValidationError
        with pytest.raises(ValidationError, match="Name must be a non-empty string"):
            Tierod(name="", r=12.5, n=8, dh=10.0, sh=5.0, shape=None)
        
        # Invalid types should raise ValidationError  
        with pytest.raises(ValidationError):
            Tierod(name="test", r="invalid", n=8, dh=10.0, sh=5.0, shape=None)
    
    def test_yaml_format_compatibility(self):
        """Test that new YAML format loads correctly"""
        
        # Test new format with type annotation
        yaml_content = """
!<Tierod>
name: "TR-H1"
r: 12.5
n: 8
dh: 10.0
sh: 5.0
shape: null
"""
        
        data = yaml.safe_load(yaml_content)
        # This should work with new format
        tierod = Tierod.from_dict(data['!<Tierod>'])
        assert tierod.name == "TR-H1"
        assert tierod.r == 12.5
        assert tierod.n == 8
    
    def test_nested_shape_handling(self):
        """Test enhanced nested object handling"""
        
        # Test with shape reference (string)
        data = {
            'name': 'test_tierod',
            'r': 12.5,
            'n': 8,
            'dh': 10.0,
            'sh': 5.0,
            'shape': 'shape_reference'
        }
        
        tierod = Tierod.from_dict(data)
        assert tierod.shape == 'shape_reference'
        
        # Test with inline shape object (dict)
        data_with_inline_shape = {
            'name': 'test_tierod',
            'r': 12.5,
            'n': 8, 
            'dh': 10.0,
            'sh': 5.0,
            'shape': {
                'name': 'inline_shape',
                'profile': 'rectangular',
                'length': 15
            }
        }
        
        # This should create a Shape object automatically
        tierod = Tierod.from_dict(data_with_inline_shape)
        # Shape should be created from dict (implementation depends on Shape class)
    
    def test_inherited_serialization_methods(self):
        """Test that all serialization methods work via inheritance"""
        
        tierod = Tierod(
            name="test_tierod",
            r=12.5,
            n=8,
            dh=10.0, 
            sh=5.0,
            shape=None
        )
        
        # Test JSON serialization
        json_str = tierod.to_json()
        assert "test_tierod" in json_str
        assert "12.5" in json_str
        
        # Test JSON file writing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tierod.write_to_json(f.name)
            # File should exist and contain correct data
            with open(f.name, 'r') as rf:
                content = rf.read()
                assert "test_tierod" in content

if __name__ == "__main__":
    pytest.main([__file__])