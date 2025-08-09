# File: new-tests/test_yaml_constructors.py
import pytest
import json
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

# Import all classes for testing
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Screen import Screen
from python_magnetgeo.MSite import MSite
from python_magnetgeo.Probe import Probe
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D

class TestYAMLConstructors:
    """Test YAML constructor system and loading"""

    def test_yaml_tags_exist(self):
        """Test all classes have proper YAML tags"""
        classes_with_tags = [
            (Insert, "Insert"),
            (Helix, "Helix"),
            (Ring, "Ring"),
            (Supra, "Supra"),
            (Supras, "Supras"),
            (Screen, "Screen"),
            (MSite, "MSite"),
            (Probe, "Probe"),
        ]
        
        for cls, expected_tag in classes_with_tags:
            assert hasattr(cls, 'yaml_tag')
            assert cls.yaml_tag == expected_tag

    def test_yaml_constructor_registration(self):
        """Test YAML constructors are properly registered"""
        # This test verifies the constructors exist and are callable
        from python_magnetgeo.Insert import Insert_constructor
        from python_magnetgeo.Helix import Helix_constructor
        from python_magnetgeo.Ring import Ring_constructor
        from python_magnetgeo.Supra import Supra_constructor
        from python_magnetgeo.Supras import Supras_constructor
        from python_magnetgeo.Screen import Screen_constructor
        from python_magnetgeo.MSite import MSite_constructor
        from python_magnetgeo.Probe import Probe_constructor
        
        constructors = [
            Insert_constructor,
            Helix_constructor, 
            Ring_constructor,
            Supra_constructor,
            Supras_constructor,
            Screen_constructor,
            MSite_constructor,
            Probe_constructor
        ]
        
        for constructor in constructors:
            assert callable(constructor)

    def test_yaml_loading_interface(self, temp_yaml_file):
        """Test YAML loading works for simple objects"""
        # Create simple YAML content
        yaml_content = """
!<Screen>
name: yaml_test_screen
r: [5.0, 25.0]
z: [0.0, 50.0]
"""
        
        with open(temp_yaml_file, 'w') as f:
            f.write(yaml_content)
        
        # Test loading
        screen = Screen.from_yaml(temp_yaml_file)
        assert screen.name == "yaml_test_screen"
        assert screen.r == [5.0, 25.0]
        assert screen.z == [0.0, 50.0]


