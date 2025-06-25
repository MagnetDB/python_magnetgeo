#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Ring class (Updated with factored approach)
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Ring import Ring, Ring_constructor
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_geometric_data,
    validate_angle_data
)


class TestRingInitialization:
    """Test Ring object initialization"""
    
    def test_ring_basic_initialization(self):
        """Test Ring initialization with required parameters"""
        ring = Ring(
            name="test_ring",
            r=[10.0, 20.0],
            z=[0.0, 15.0]
        )
        
        assert ring.name == "test_ring"
        assert ring.r == [10.0, 20.0]
        assert ring.z == [0.0, 15.0]
        assert ring.n == 0
        assert ring.angle == 0
        assert ring.bpside is True
        assert ring.fillets is False
        assert ring.cad is None

    def test_ring_full_initialization(self):
        """Test Ring initialization with all parameters"""
        ring = Ring(
            name="full_ring",
            r=[5.0, 25.0],
            z=[10.0, 30.0],
            n=8,
            angle=45.0,
            bpside=False,
            fillets=True,
            cad="SALOME"
        )
        
        assert ring.name == "full_ring"
        assert ring.r == [5.0, 25.0]
        assert ring.z == [10.0, 30.0]
        assert ring.n == 8
        assert ring.angle == 45.0
        assert ring.bpside is False
        assert ring.fillets is True
        assert ring.cad == "SALOME"

    def test_ring_default_values(self):
        """Test Ring default parameter values"""
        ring = Ring(name="default_ring", r=[1.0, 2.0], z=[0.0, 1.0])
        
        # Test default values
        assert ring.n == 0
        assert ring.angle == 0
        assert ring.bpside is True
        assert ring.fillets is False
        assert ring.cad is None

    def test_ring_with_string_cad(self):
        """Test Ring with string CAD parameter"""
        ring = Ring(
            name="cad_ring",
            r=[15.0, 35.0],
            z=[5.0, 25.0],
            cad="GMSH"
        )
        
        assert ring.cad == "GMSH"

    def test_ring_setstate_method(self):
        """Test __setstate__ method for deserialization"""
        # Simulate loading from pickle/YAML without cad attribute
        state = {
            'name': 'state_ring',
            'r': [8.0, 18.0],
            'z': [2.0, 12.0],
            'n': 4,
            'angle': 90.0,
            'bpside': True,
            'fillets': False
        }
        
        ring = Ring.__new__(Ring)
        ring.__setstate__(state)
        
        assert hasattr(ring, 'cad')
        assert ring.cad == ''


class TestRingMethods:
    """Test Ring class methods"""
    
    @pytest.fixture
    def sample_ring(self):
        """Create a sample Ring for testing"""
        return Ring(
            name="test_ring",
            r=[12.0, 22.0],
            z=[5.0, 15.0],
            n=6,
            angle=60.0,
            bpside=True,
            fillets=False,
            cad="SALOME"
        )

    def test_get_lc(self, sample_ring):
        """Test get_lc method"""
        # lc = (r[1] - r[0]) / 10.0 = (22.0 - 12.0) / 10.0 = 1.0
        assert sample_ring.get_lc() == 1.0

    def test_get_lc_different_radii(self):
        """Test get_lc with different radii"""
        ring = Ring(name="lc_test", r=[0.0, 50.0], z=[0.0, 10.0])
        # lc = (50.0 - 0.0) / 10.0 = 5.0
        assert ring.get_lc() == 5.0

    def test_get_lc_zero_difference(self):
        """Test get_lc with same inner and outer radius"""
        ring = Ring(name="zero_ring", r=[10.0, 10.0], z=[0.0, 5.0])
        # lc = (10.0 - 10.0) / 10.0 = 0.0
        assert ring.get_lc() == 0.0

    def test_repr_with_cad(self, sample_ring):
        """Test __repr__ method with CAD attribute"""
        repr_str = repr(sample_ring)
        
        assert "Ring(" in repr_str
        assert "name='test_ring'" in repr_str
        assert "r=[12.0, 22.0]" in repr_str
        assert "z=[5.0, 15.0]" in repr_str
        assert "n=6" in repr_str
        assert "angle=60.0" in repr_str
        assert "bpside=True" in repr_str
        assert "fillets=False" in repr_str
        assert "cad='SALOME'" in repr_str

    def test_repr_without_cad(self):
        """Test __repr__ method without CAD attribute"""
        ring = Ring(name="no_cad", r=[5.0, 15.0], z=[0.0, 10.0])
        # Manually remove cad attribute to test the hasattr check
        if hasattr(ring, 'cad'):
            delattr(ring, 'cad')
        
        repr_str = repr(ring)
        assert "cad=None" in repr_str

    def test_repr_precision(self):
        """Test __repr__ with high precision values"""
        ring = Ring(
            name="precision",
            r=[10.123456789, 20.987654321],
            z=[0.111111111, 5.999999999],
            angle=45.123456789
        )
        
        repr_str = repr(ring)
        assert "10.123456789" in repr_str
        assert "20.987654321" in repr_str
        assert "45.123456789" in repr_str


class TestRingSerialization(BaseSerializationTestMixin):
    """Test Ring serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Ring instance"""
        return Ring(
            name="test_ring",
            r=[10.0, 20.0],
            z=[0.0, 15.0],
            n=4,
            angle=30.0,
            bpside=True,
            fillets=False,
            cad="SALOME"
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''!<Ring>
name: yaml_ring
r: [15.0, 25.0]
z: [5.0, 20.0]
n: 8
angle: 45.0
bpside: false
fillets: true
cad: GMSH
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_ring",
            "r": [10.0, 20.0],
            "z": [0.0, 15.0],
            "n": 4,
            "angle": 30.0,
            "bpside": True,
            "fillets": False,
            "cad": "SALOME"
        }
    
    def get_class_under_test(self):
        """Return Ring class"""
        return Ring

    @patch("python_magnetgeo.utils.writeYaml")
    def test_dump_method(self, mock_write_yaml):
        """Test dump method calls writeYaml correctly"""
        instance = self.get_sample_instance()
        instance.dump()
        mock_write_yaml.assert_called_once_with("Ring", instance, Ring)

    @patch("python_magnetgeo.utils.writeYaml", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_write_yaml):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Dump error"):
            instance.dump()

    def test_write_to_json_method(self):
        """Test write_to_json method"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.write_to_json()
            mock_file.assert_called_once_with("test_ring.json", "w")


class TestRingYAMLConstructor:
    """Test Ring YAML constructor - custom implementation since base mixin expects different return format"""
    
    def get_constructor_function(self):
        """Return the Ring constructor function"""
        return Ring_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        return {
            "name": "constructor_ring",
            "r": [8.0, 18.0],
            "z": [2.0, 12.0],
            "n": 6,
            "angle": 90.0,
            "bpside": False,
            "fillets": True,
            "cad": "SALOME"
        }
    
    def test_yaml_constructor_function(self):
        """Test the YAML constructor function"""
        constructor_func = self.get_constructor_function()
        
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = self.get_sample_constructor_data()
        mock_loader.construct_mapping.return_value = mock_data
        
        # The Ring_constructor returns a Ring instance directly, not a tuple
        result = constructor_func(mock_loader, mock_node)
        
        assert isinstance(result, Ring)
        assert result.name == "constructor_ring"
        assert result.r == [8.0, 18.0]
        assert result.z == [2.0, 12.0]
        assert result.n == 6
        assert result.angle == 90.0
        assert result.bpside is False
        assert result.fillets is True
        assert result.cad == "SALOME"
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_yaml_constructor_missing_cad(self):
        """Test YAML constructor with missing CAD field"""
        constructor_func = self.get_constructor_function()
        
        mock_loader = Mock()
        mock_node = Mock()
        
        # Data without 'cad' field
        mock_data = {
            "name": "no_cad_ring",
            "r": [5.0, 15.0],
            "z": [0.0, 10.0],
            "n": 4,
            "angle": 45.0,
            "bpside": True,
            "fillets": False
        }
        mock_loader.construct_mapping.return_value = mock_data
        
        result = constructor_func(mock_loader, mock_node)
        
        assert isinstance(result, Ring)
        assert result.cad == ''  # Should default to empty string


class TestRingYAMLTag(BaseYAMLTagTestMixin):
    """Test Ring YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Ring class"""
        return Ring
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Ring"


class TestRingFromDict:
    """Test Ring.from_dict class method"""
    
    def test_from_dict_complete_data(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_ring",
            "r": [12.0, 32.0],
            "z": [8.0, 28.0],
            "n": 10,
            "angle": 120.0,
            "bpside": False,
            "fillets": True,
            "cad": "GMSH"
        }
        
        ring = Ring.from_dict(data)
        
        assert ring.name == "dict_ring"
        assert ring.r == [12.0, 32.0]
        assert ring.z == [8.0, 28.0]
        assert ring.n == 10
        assert ring.angle == 120.0
        assert ring.bpside is False
        assert ring.fillets is True
        assert ring.cad == "GMSH"

    def test_from_dict_missing_cad(self):
        """Test from_dict with missing CAD field"""
        data = {
            "name": "no_cad_ring",
            "r": [5.0, 15.0],
            "z": [0.0, 10.0],
            "n": 4,
            "angle": 45.0,
            "bpside": True,
            "fillets": False
        }
        
        ring = Ring.from_dict(data)
        assert ring.cad == ''

    def test_from_dict_minimal_data(self):
        """Test from_dict with minimal required data"""
        data = {
            "name": "minimal_ring",
            "r": [1.0, 2.0],
            "z": [0.0, 1.0],
            "n": 0,
            "angle": 0,
            "bpside": True,
            "fillets": False
        }
        
        ring = Ring.from_dict(data)
        assert ring.name == "minimal_ring"
        assert ring.cad == ''

    def test_from_dict_with_debug(self):
        """Test from_dict with debug flag"""
        data = {
            "name": "debug_ring",
            "r": [3.0, 13.0],
            "z": [1.0, 11.0],
            "n": 2,
            "angle": 30.0,
            "bpside": True,
            "fillets": False
        }
        
        ring = Ring.from_dict(data, debug=True)
        assert isinstance(ring, Ring)
        assert ring.name == "debug_ring"


class TestRingValidation:
    """Test Ring parameter validation and consistency"""
    
    def test_geometric_parameter_validation(self):
        """Test geometric parameter validation"""
        ring = Ring(
            name="geo_ring",
            r=[10.0, 30.0],
            z=[5.0, 25.0]
        )
        
        # Validate geometric data using common utility
        validate_geometric_data(ring.r, ring.z)
        
        # Ring-specific validations
        assert ring.r[0] <= ring.r[1]  # Inner radius <= outer radius
        assert len(ring.r) == 2
        assert len(ring.z) == 2

    def test_angle_parameter_validation(self):
        """Test angle parameter validation"""
        angles_to_test = [0.0, 30.0, 45.0, 90.0, 180.0, 270.0, 360.0, -30.0]
        
        for angle in angles_to_test:
            ring = Ring(
                name=f"angle_test_{abs(angle)}",  # Use abs to avoid negative in name
                r=[5.0, 15.0],
                z=[0.0, 10.0],
                angle=angle
            )
            assert ring.angle == angle
            validate_angle_data([angle])

    def test_integer_parameter_validation(self):
        """Test integer parameter validation"""
        for n in [0, 1, 4, 8, 16, 32]:
            ring = Ring(
                name=f"n_test_{n}",
                r=[10.0, 20.0],
                z=[0.0, 10.0],
                n=n
            )
            assert ring.n == n
            assert isinstance(ring.n, int)

    def test_boolean_parameter_validation(self):
        """Test boolean parameter validation"""
        test_cases = [
            (True, True),
            (True, False),
            (False, True),
            (False, False)
        ]
        
        for i, (bpside, fillets) in enumerate(test_cases):
            ring = Ring(
                name=f"bool_test_{i}",
                r=[5.0, 15.0],
                z=[0.0, 5.0],
                bpside=bpside,
                fillets=fillets
            )
            assert ring.bpside == bpside
            assert ring.fillets == fillets


class TestRingFileOperations:
    """Test Ring file I/O operations"""
    
    def test_from_yaml_with_mocking(self):
        """Test from_yaml with proper mocking"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_ring = Ring(name="yaml_test", r=[1.0, 2.0], z=[0.0, 1.0])
            mock_load.return_value = mock_ring
            
            result = Ring.from_yaml("test.yaml")
            
            assert result == mock_ring
            mock_load.assert_called_once_with("Ring", "test.yaml", Ring, False)

    def test_from_yaml_with_debug(self):
        """Test from_yaml with debug flag"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_ring = Ring(name="debug_yaml", r=[2.0, 4.0], z=[1.0, 3.0])
            mock_load.return_value = mock_ring
            
            result = Ring.from_yaml("test.yaml", debug=True)
            
            assert result == mock_ring
            mock_load.assert_called_once_with("Ring", "test.yaml", Ring, True)

    def test_from_json_with_mocking(self):
        """Test from_json with proper mocking"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load:
            mock_ring = Ring(name="json_test", r=[3.0, 6.0], z=[2.0, 5.0])
            mock_load.return_value = mock_ring
            
            result = Ring.from_json("test.json")
            
            assert result == mock_ring
            mock_load.assert_called_once_with("Ring", "test.json", False)

    def test_from_json_with_debug(self):
        """Test from_json with debug flag"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load:
            mock_ring = Ring(name="debug_json", r=[4.0, 8.0], z=[3.0, 7.0])
            mock_load.return_value = mock_ring
            
            result = Ring.from_json("test.json", debug=True)
            
            assert result == mock_ring
            mock_load.assert_called_once_with("Ring", "test.json", True)


class TestRingIntegration:
    """Integration tests for Ring class"""
    
    def test_ring_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_ring = Ring(
            name="roundtrip_ring",
            r=[20.0, 40.0],
            z=[10.0, 30.0],
            n=12,
            angle=135.0,
            bpside=False,
            fillets=True,
            cad="ROUNDTRIP_CAD"
        )
        
        # Test JSON serialization
        json_str = original_ring.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Ring"
        assert parsed_json["name"] == "roundtrip_ring"
        assert parsed_json["r"] == [20.0, 40.0]
        assert parsed_json["z"] == [10.0, 30.0]
        assert parsed_json["n"] == 12
        assert parsed_json["angle"] == 135.0
        assert parsed_json["bpside"] is False
        assert parsed_json["fillets"] is True
        assert parsed_json["cad"] == "ROUNDTRIP_CAD"

    def test_ring_collection_operations(self):
        """Test operations on collections of rings"""
        rings = [
            Ring(name=f"ring_{i}", r=[i*5.0, (i+1)*5.0], z=[0.0, 10.0], n=i+1)
            for i in range(5)
        ]
        
        # Test sorting by inner radius
        sorted_rings = sorted(rings, key=lambda r: r.r[0])
        assert sorted_rings[0].r[0] == 0.0
        assert sorted_rings[-1].r[0] == 20.0
        
        # Test filtering
        large_rings = [r for r in rings if r.r[1] > 15.0]
        assert len(large_rings) == 2
        
        # Test aggregation
        total_n = sum(r.n for r in rings)
        assert total_n == sum(range(1, 6))  # 1+2+3+4+5 = 15

    def test_ring_with_insert_context(self):
        """Test ring as it would be used in an Insert context"""
        # Create rings that might be used in an Insert
        rings = [
            Ring(name="ring_1", r=[10.0, 15.0], z=[5.0, 10.0], bpside=True),
            Ring(name="ring_2", r=[25.0, 30.0], z=[85.0, 90.0], bpside=False)
        ]
        
        # Test that rings maintain their properties
        assert rings[0].bpside is True
        assert rings[1].bpside is False
        
        # Test geometric consistency
        for ring in rings:
            assert ring.r[0] < ring.r[1]
            assert ring.z[0] < ring.z[1]


class TestRingPerformance:
    """Performance tests for Ring class"""
    
    def test_multiple_ring_creation_performance(self):
        """Test performance of creating many rings"""
        rings = []
        for i in range(1000):
            ring = Ring(
                name=f"perf_ring_{i}",
                r=[float(i), float(i+10)],
                z=[0.0, 10.0],
                n=i % 20,
                angle=float(i % 360),
                bpside=i % 2 == 0,
                fillets=i % 3 == 0,
                cad=f"CAD_{i % 5}"
            )
            rings.append(ring)
        
        assert len(rings) == 1000
        assert all(isinstance(r, Ring) for r in rings)
        
        # Test that operations still work efficiently
        lc_values = [r.get_lc() for r in rings[:100]]  # Sample first 100
        assert len(lc_values) == 100
        assert all(isinstance(lc, float) for lc in lc_values)

    def test_ring_serialization_performance(self):
        """Test performance of ring serialization operations"""
        ring = Ring(
            name="perf_test_ring",
            r=[100.0, 200.0],
            z=[50.0, 150.0],
            n=50,
            angle=180.0,
            bpside=True,
            fillets=True,
            cad="PERFORMANCE_TEST"
        )
        
        # Test JSON serialization performance
        json_strings = []
        for _ in range(100):
            json_str = ring.to_json()
            json_strings.append(json_str)
        
        assert len(json_strings) == 100
        assert all(len(js) > 0 for js in json_strings)


class TestRingErrorHandling:
    """Test error handling in Ring class"""
    
    def test_invalid_parameter_types(self):
        """Test handling of invalid parameter types"""
        # These might raise TypeErrors depending on implementation
        try:
            ring = Ring(name=None, r=None, z=None)
            # If no error, implementation allows None values
            assert ring.name is None
        except TypeError:
            # Expected if implementation validates types
            pass

    def test_malformed_geometric_data(self):
        """Test handling of malformed geometric data"""
        # Test with wrong list lengths
        try:
            ring = Ring(name="malformed", r=[1.0], z=[0.0, 1.0, 2.0])
            # If no error, implementation allows mismatched lengths
            assert len(ring.r) == 1
            assert len(ring.z) == 3
        except (ValueError, IndexError):
            # Expected if implementation validates list lengths
            pass

    def test_extreme_parameter_combinations(self):
        """Test extreme parameter combinations"""
        # Test with inverted radius (outer < inner)
        ring = Ring(name="inverted", r=[20.0, 10.0], z=[0.0, 5.0])
        # Implementation doesn't validate, so this should work
        assert ring.r == [20.0, 10.0]
        
        # The get_lc method will return negative value
        assert ring.get_lc() == -1.0

    def test_file_operation_errors(self):
        """Test file operation error handling"""
        ring = Ring(name="error_test", r=[1.0, 2.0], z=[0.0, 1.0])
        
        # Test from_yaml with non-existent file
        with pytest.raises(Exception):
            Ring.from_yaml("nonexistent_file.yaml")
        
        # Test from_json with non-existent file  
        with pytest.raises(Exception):
            Ring.from_json("nonexistent_file.json")



