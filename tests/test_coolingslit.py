#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the CoolingSlit class
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.coolingslit import CoolingSlit, CoolingSlit_constructor
from python_magnetgeo.Shape2D import Shape2D
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_geometric_data,
    validate_angle_data
)


class TestCoolingSlitInitialization:
    """Test CoolingSlit object initialization"""
    
    @pytest.fixture
    def sample_shape2d(self):
        """Create a sample Shape2D for testing"""
        return Shape2D(name="slit_shape", pts=[[0, 0], [1, 0], [1, 0.5], [0, 0.5]])

    def test_coolingslit_basic_initialization(self, sample_shape2d):
        """Test CoolingSlit initialization with all parameters"""
        slit = CoolingSlit(
            r=25.0,
            angle=45.0,
            n=8,
            dh=3.5,
            sh=12.0,
            shape=sample_shape2d
        )
        
        assert slit.r == 25.0
        assert slit.angle == 45.0
        assert slit.n == 8
        assert slit.dh == 3.5
        assert slit.sh == 12.0
        assert slit.shape == sample_shape2d
        assert isinstance(slit.shape, Shape2D)

    def test_coolingslit_with_zero_values(self, sample_shape2d):
        """Test CoolingSlit with zero values"""
        slit = CoolingSlit(
            name="test", 
            r=0.0,
            angle=0.0,
            n=0,
            dh=0.0,
            sh=0.0,
            shape=sample_shape2d
        )
        
        assert slit.r == 0.0
        assert slit.angle == 0.0
        assert slit.n == 0
        assert slit.dh == 0.0
        assert slit.sh == 0.0

    def test_coolingslit_with_negative_values(self, sample_shape2d):
        """Test CoolingSlit with negative values"""
        slit = CoolingSlit(
            name="test", 
            r=-10.0,
            angle=-30.0,
            n=-5,
            dh=-2.0,
            sh=-8.0,
            shape=sample_shape2d
        )
        
        assert slit.r == -10.0
        assert slit.angle == -30.0
        assert slit.n == -5
        assert slit.dh == -2.0
        assert slit.sh == -8.0

    def test_coolingslit_with_large_values(self, sample_shape2d):
        """Test CoolingSlit with large values"""
        slit = CoolingSlit(
            name="test", 
            r=1000.0,
            angle=720.0,  # Multiple rotations
            n=999,
            dh=100.0,
            sh=5000.0,
            shape=sample_shape2d
        )
        
        assert slit.r == 1000.0
        assert slit.angle == 720.0
        assert slit.n == 999
        assert slit.dh == 100.0
        assert slit.sh == 5000.0

    def test_coolingslit_with_float_integer_mix(self, sample_shape2d):
        """Test CoolingSlit with mixed float and integer types"""
        slit = CoolingSlit(
            name="test", 
            r=15,      # int
            angle=30.5,  # float
            n=6,       # int
            dh=2.75,   # float
            sh=11,     # int
            shape=sample_shape2d
        )
        
        assert slit.r == 15
        assert slit.angle == 30.5
        assert slit.n == 6
        assert slit.dh == 2.75
        assert slit.sh == 11


class TestCoolingSlitMethods:
    """Test CoolingSlit class methods"""
    
    @pytest.fixture
    def sample_coolingslit(self):
        """Create a sample CoolingSlit for testing"""
        shape = Shape2D(name="test_slit", pts=[[0, 0], [2, 0], [2, 1], [0, 1]])
        return CoolingSlit(name="test", r=20.0, angle=60.0, n=12, dh=4.0, sh=16.0, shape=shape)

    def test_repr(self, sample_coolingslit):
        """Test __repr__ method"""
        repr_str = repr(sample_coolingslit)
        
        assert "CoolingSlit(" in repr_str
        assert "r=20.0" in repr_str
        assert "angle=60.0" in repr_str
        assert "n=12" in repr_str
        assert "dh=4.0" in repr_str
        assert "sh=16.0" in repr_str
        assert "shape=" in repr_str

    def test_repr_with_complex_shape(self):
        """Test __repr__ with complex shape"""
        complex_shape = Shape2D(name="complex", pts=[[i, i**2] for i in range(10)])
        slit = CoolingSlit(name="test", r=35.0, angle=90.0, n=16, dh=5.5, sh=22.0, shape=complex_shape)
        
        repr_str = repr(slit)
        assert "CoolingSlit(" in repr_str
        assert "r=35.0" in repr_str
        assert "angle=90.0" in repr_str

    def test_repr_precision(self):
        """Test __repr__ with high precision values"""
        shape = Shape2D(name="precision", pts=[[0, 0], [1, 1]])
        slit = CoolingSlit(
            name="test", 
            r=12.123456789,
            angle=45.987654321,
            n=7,
            dh=3.141592653,
            sh=2.718281828,
            shape=shape
        )
        
        repr_str = repr(slit)
        assert "r=12.123456789" in repr_str
        assert "angle=45.987654321" in repr_str


class TestCoolingSlitSerialization(BaseSerializationTestMixin):
    """Test CoolingSlit serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample CoolingSlit instance"""
        shape = Shape2D(name="test_shape", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])
        return CoolingSlit(name="test", r=15.0, angle=30.0, n=6, dh=2.5, sh=10.0, shape=shape)
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
!<CoolingSlit>
name: test 
r: 18.0
angle: 45.0
n: 8
dh: 3.0
sh: 12.0
shape: !<Shape2D>
  name: yaml_slit_shape
  pts: [[0, 0], [1.5, 0], [1.5, 0.8], [0, 0.8]]
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test", 
            "r": 15.0,
            "angle": 30.0,
            "n": 6,
            "dh": 2.5,
            "sh": 10.0
        }
    
    def get_class_under_test(self):
        """Return CoolingSlit class"""
        return CoolingSlit

    def test_json_includes_shape_data(self):
        """Test that JSON serialization includes shape data"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "shape" in parsed
        assert isinstance(parsed["shape"], dict)
        assert parsed["shape"]["__classname__"] == "Shape2D"

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to CoolingSlit dump"):
            instance.dump("error_file")


class TestCoolingSlitYAMLConstructor(BaseYAMLConstructorTestMixin):
    """Test CoolingSlit YAML constructor using common test mixin"""
    
    def get_constructor_function(self):
        """Return the CoolingSlit constructor function"""
        return CoolingSlit_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        shape = Shape2D(name="constructor_shape", pts=[[0, 0], [2, 0], [2, 1.5], [0, 1.5]])
        return {
            "name": "test", 
            "r": 22.0,
            "angle": 75.0,
            "n": 10,
            "dh": 4.5,
            "sh": 18.0,
            "shape": shape
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "CoolingSlit"


class TestCoolingSlitYAMLTag(BaseYAMLTagTestMixin):
    """Test CoolingSlit YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return CoolingSlit class"""
        return CoolingSlit
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Slit"


class TestCoolingSlitFileOperations:
    """Test CoolingSlit file operations and edge cases"""
    
    def test_from_yaml_success(self):
        """Test successful from_yaml loading"""
        yaml_content = '''
!>CoolingSlit>
name: test 
r: 25.0
angle: 120.0
n: 15
dh: 5.0
sh: 20.0
shape: !<Shape2D>
  name: loaded_shape
  pts: [[0, 0], [3, 0], [3, 2], [0, 2]]
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    slit = CoolingSlit.from_yaml(tmp_file.name)
                
                assert slit.r == 25.0
                assert slit.angle == 120.0
                assert slit.n == 15
                assert slit.dh == 5.0
                assert slit.sh == 20.0
                assert isinstance(slit.shape, Shape2D)
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_file_not_found(self):
        """Test from_yaml with non-existent file"""
        with pytest.raises(Exception, match="Failed to load CoolingSlit data"):
            CoolingSlit.from_yaml("non_existent_file.yaml")

    def test_from_yaml_invalid_yaml(self):
        """Test from_yaml with invalid YAML content"""
        invalid_yaml = "r: 10.0\nangle: invalid_angle\nn: 5"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(invalid_yaml)
            tmp_file.flush()
            
            try:
                with pytest.raises(Exception):
                    CoolingSlit.from_yaml(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)

    @patch("python_magnetgeo.deserialize.unserialize_object")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_from_json_success(self, mock_file, mock_unserialize):
        """Test successful from_json loading"""
        shape = Shape2D(name="json_shape", pts=[[0, 0], [1, 1]])
        mock_slit = CoolingSlit(name="test", r=10.0, angle=45.0, n=4, dh=2.0, sh=8.0, shape=shape)
        mock_unserialize.return_value = mock_slit
        
        result = CoolingSlit.from_json("test.json")
        
        mock_file.assert_called_once_with("test.json", "r")
        mock_unserialize.assert_called_once()
        assert result == mock_slit


class TestCoolingSlitValidation:
    """Test CoolingSlit parameter validation and consistency"""
    
    def test_geometric_parameter_consistency(self):
        """Test geometric parameter consistency"""
        shape = Shape2D(name="geo_test", pts=[[0, 0], [2, 0], [2, 1], [0, 1]])
        slit = CoolingSlit(name="test", r=30.0, angle=90.0, n=12, dh=4.0, sh=16.0, shape=shape)
        
        # Basic geometric consistency checks
        assert slit.r > 0  # Radius should be positive
        assert 0 <= slit.angle <= 360  # Angle in reasonable range
        assert slit.n > 0  # Number of slits should be positive
        assert slit.dh > 0  # Hydraulic diameter should be positive
        assert slit.sh > 0  # Surface area should be positive

    def test_angle_range_validation(self):
        """Test angle parameter ranges"""
        shape = Shape2D(name="angle_test", pts=[[0, 0], [1, 1]])
        
        # Test various angle ranges
        angles_to_test = [0.0, 30.0, 45.0, 90.0, 180.0, 270.0, 360.0]
        
        for angle in angles_to_test:
            slit = CoolingSlit(name="test", r=20.0, angle=angle, n=8, dh=3.0, sh=12.0, shape=shape)
            assert slit.angle == angle

    def test_hydraulic_parameters_validation(self):
        """Test hydraulic parameter validation"""
        shape = Shape2D(name="hydraulic_test", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])
        
        # Test relationship between dh and sh
        # dh = 4 * Area / Perimeter, so for meaningful geometry both should be positive
        test_cases = [
            (1.0, 4.0),    # Small values
            (5.0, 20.0),   # Medium values
            (10.0, 40.0),  # Large values
        ]
        
        for dh, sh in test_cases:
            slit = CoolingSlit(name="test", r=25.0, angle=60.0, n=6, dh=dh, sh=sh, shape=shape)
            assert slit.dh == dh
            assert slit.sh == sh
            
            # Basic relationship check (dh should be much smaller than sh for typical geometries)
            assert slit.dh < slit.sh

    def test_integer_parameter_validation(self):
        """Test integer parameter validation"""
        shape = Shape2D(name="int_test", pts=[[0, 0], [1, 1]])
        
        # Test that n (number of slits) is handled correctly
        for n in [1, 2, 5, 10, 20, 50]:
            slit = CoolingSlit(name="test", r=20.0, angle=45.0, n=n, dh=3.0, sh=12.0, shape=shape)
            assert slit.n == n
            assert isinstance(slit.n, int)

    def test_shape_parameter_validation(self):
        """Test shape parameter validation"""
        # Test with different types of shapes
        shapes = [
            Shape2D(name="simple", pts=[[0, 0], [1, 1]]),
            Shape2D(name="empty", pts=[]),
            Shape2D(name="complex", pts=[[i, i**2] for i in range(20)])
        ]
        
        for shape in shapes:
            slit = CoolingSlit(name="test", r=15.0, angle=30.0, n=4, dh=2.0, sh=8.0, shape=shape)
            assert slit.shape == shape
            assert isinstance(slit.shape, Shape2D)


class TestCoolingSlitIntegration:
    """Integration tests for CoolingSlit class"""
    
    def test_coolingslit_in_system_context(self):
        """Test CoolingSlit as it would be used in a larger system"""
        # Create multiple cooling slits with different configurations
        slits = []
        
        for i in range(5):
            shape = Shape2D(name=f"slit_shape_{i}", pts=[[0, 0], [i+1, 0], [i+1, 1], [0, 1]])
            slit = CoolingSlit(
                name="test", 
                r=20.0 + i * 5.0,
                angle=30.0 + i * 15.0,
                n=4 + i * 2,
                dh=2.0 + i * 0.5,
                sh=8.0 + i * 2.0,
                shape=shape
            )
            slits.append(slit)
        
        # Verify each slit maintains its properties
        for i, slit in enumerate(slits):
            assert slit.r == 20.0 + i * 5.0
            assert slit.angle == 30.0 + i * 15.0
            assert slit.n == 4 + i * 2

    def test_coolingslit_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_shape = Shape2D(name="roundtrip", pts=[[0, 0], [3, 0], [3, 2], [0, 2]])
        original_slit = CoolingSlit(name="test", r=40.0, angle=135.0, n=18, dh=6.0, sh=24.0, shape=original_shape)
        
        # Test JSON serialization
        json_str = original_slit.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "CoolingSlit"
        assert parsed_json["r"] == 40.0
        assert parsed_json["angle"] == 135.0
        assert parsed_json["n"] == 18
        assert parsed_json["dh"] == 6.0
        assert parsed_json["sh"] == 24.0
        assert "shape" in parsed_json

    def test_coolingslit_collection_operations(self):
        """Test operations on collections of cooling slits"""
        shape = Shape2D(name="collection_shape", pts=[[0, 0], [2, 0], [2, 1.5], [0, 1.5]])
        
        # Create collection of slits
        slits = [
            CoolingSlit(name="test", r=i * 10.0, angle=i * 30.0, n=i + 2, dh=i * 1.0, sh=i * 4.0, shape=shape)
            for i in range(1, 11)
        ]
        
        # Test sorting by radius
        sorted_slits = sorted(slits, key=lambda s: s.r)
        assert sorted_slits[0].r == 10.0
        assert sorted_slits[-1].r == 100.0
        
        # Test filtering by angle
        slits_90_plus = [s for s in slits if s.angle >= 90.0]
        assert len(slits_90_plus) > 0
        
        # Test aggregation operations
        total_n = sum(s.n for s in slits)
        assert total_n == sum(range(3, 13))  # 3+4+5+...+12


class TestCoolingSlitPerformance:
    """Performance tests for CoolingSlit class"""
    
    def test_large_shape_handling(self):
        """Test CoolingSlit performance with large shape data"""
        # Create shape with many points
        large_shape = Shape2D(
            name="large_slit_shape",
            pts=[[i, (i % 100) / 10.0] for i in range(5000)]
        )
        
        slit = CoolingSlit(name="test", r=100.0, angle=180.0, n=50, dh=10.0, sh=200.0, shape=large_shape)
        
        # Test that operations still work efficiently
        repr_str = repr(slit)
        assert len(repr_str) > 0
        
        json_str = slit.to_json()
        assert len(json_str) > 0

    def test_multiple_coolingslit_creation_performance(self):
        """Test performance of creating many cooling slits"""
        base_shape = Shape2D(name="base", pts=[[0, 0], [2, 0], [2, 1], [0, 1]])
        
        # Create many cooling slits
        slits = []
        for i in range(200):
            slit = CoolingSlit(
                name="test", 
                r=float(i + 10),
                angle=float((i * 3) % 360),
                n=i % 20 + 1,
                dh=float(i) * 0.1 + 1.0,
                sh=float(i) * 0.4 + 4.0,
                shape=base_shape
            )
            slits.append(slit)
        
        assert len(slits) == 200
        assert all(isinstance(s, CoolingSlit) for s in slits)


class TestCoolingSlitErrorHandling:
    """Test error handling in CoolingSlit class"""
    
    def test_invalid_shape_handling(self):
        """Test handling of invalid shape parameter"""
        # Test with None shape (should raise error depending on implementation)
        try:
            slit = CoolingSlit(name="test", r=20.0, angle=45.0, n=6, dh=3.0, sh=12.0, shape=None)
            # If no error is raised, the implementation allows None
            assert slit.shape is None
        except (TypeError, AttributeError):
            # Expected if the implementation validates the shape parameter
            pass

    def test_extreme_value_handling(self):
        """Test handling of extreme parameter values"""
        shape = Shape2D(name="extreme_test", pts=[[0, 0], [1, 1]])
        
        # Test with very large values
        large_slit = CoolingSlit(
            name="test", 
            r=1e10,
            angle=1e6,  # Many rotations
            n=1000000,
            dh=1e8,
            sh=1e12,
            shape=shape
        )
        
        assert large_slit.r == 1e10
        assert large_slit.angle == 1e6
        
        # Test with very small values
        small_slit = CoolingSlit(
            name="test", 
            r=1e-10,
            angle=1e-6,
            n=1,
            dh=1e-15,
            sh=1e-20,
            shape=shape
        )
        
        assert small_slit.r == 1e-10
        assert small_slit.angle == 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])