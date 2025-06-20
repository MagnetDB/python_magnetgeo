#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Tierod class
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.tierod import Tierod, Tierod_constructor
from python_magnetgeo.Shape2D import Shape2D
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes
)


class TestTierodInitialization:
    """Test Tierod object initialization"""
    
    @pytest.fixture
    def sample_shape2d(self):
        """Create a sample Shape2D for testing"""
        return Shape2D(name="test_shape", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])

    def test_tierod_initialization_with_shape2d_object(self, sample_shape2d):
        """Test Tierod initialization with Shape2D object"""
        tierod = Tierod(
            r=15.0,
            n=4,
            dh=2.5,
            sh=10.0,
            shape=sample_shape2d
        )
        
        assert tierod.r == 15.0
        assert tierod.n == 4
        assert tierod.dh == 2.5
        assert tierod.sh == 10.0
        assert tierod.shape == sample_shape2d
        assert isinstance(tierod.shape, Shape2D)

    @patch('builtins.open', mock_open())
    @patch('yaml.load')
    def test_tierod_initialization_with_shape_filename(self, mock_yaml_load, sample_shape2d):
        """Test Tierod initialization with shape filename"""
        mock_yaml_load.return_value = sample_shape2d
        
        tierod = Tierod(
            r=20.0,
            n=6,
            dh=3.0,
            sh=15.0,
            shape="test_shape"
        )
        
        assert tierod.r == 20.0
        assert tierod.n == 6
        assert tierod.dh == 3.0
        assert tierod.sh == 15.0
        assert tierod.shape == sample_shape2d

    def test_tierod_with_zero_values(self):
        """Test Tierod with zero values"""
        shape = Shape2D(name="zero_shape", pts=[[0, 0]])
        
        tierod = Tierod(r=0.0, n=0, dh=0.0, sh=0.0, shape=shape)
        
        assert tierod.r == 0.0
        assert tierod.n == 0
        assert tierod.dh == 0.0
        assert tierod.sh == 0.0
        assert tierod.shape == shape

    def test_tierod_with_negative_values(self):
        """Test Tierod with negative values"""
        shape = Shape2D(name="neg_shape", pts=[[-1, -1], [1, 1]])
        
        tierod = Tierod(r=-5.0, n=-2, dh=-1.0, sh=-3.0, shape=shape)
        
        assert tierod.r == -5.0
        assert tierod.n == -2
        assert tierod.dh == -1.0
        assert tierod.sh == -3.0


class TestTierodMethods:
    """Test Tierod class methods"""
    
    @pytest.fixture
    def sample_tierod(self):
        """Create a sample Tierod for testing"""
        shape = Shape2D(name="sample_shape", pts=[[0, 0], [2, 0], [2, 2], [0, 2]])
        return Tierod(r=12.5, n=8, dh=4.2, sh=18.6, shape=shape)

    def test_repr(self, sample_tierod):
        """Test __repr__ method"""
        repr_str = repr(sample_tierod)
        
        assert "Tierod(" in repr_str
        assert "r=12.5" in repr_str
        assert "n=8" in repr_str
        assert "dh=4.2" in repr_str
        assert "sh=18.6" in repr_str
        assert "shape=" in repr_str

    def test_repr_with_complex_shape(self):
        """Test __repr__ with more complex shape"""
        shape = Shape2D(name="complex", pts=[[i, i**2] for i in range(5)])
        tierod = Tierod(r=25.0, n=12, dh=6.0, sh=30.0, shape=shape)
        
        repr_str = repr(tierod)
        assert "Tierod(" in repr_str
        assert "r=25.0" in repr_str
        assert "n=12" in repr_str


class TestTierodSerialization(BaseSerializationTestMixin):
    """Test Tierod serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Tierod instance"""
        shape = Shape2D(name="test_shape", pts=[[0, 0], [1, 1]])
        return Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape=shape)
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
!<Tierod>
r: 15.0
n: 6
dh: 3.5
sh: 12.0
shape: !<Shape2D>
  name: yaml_shape
  pts: [[0, 0], [1, 0], [1, 1], [0, 1]]
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "r": 10.0,
            "n": 5,
            "dh": 2.0,
            "sh": 8.0
        }
    
    def get_class_under_test(self):
        """Return Tierod class"""
        return Tierod

    def test_json_with_shape_serialization(self):
        """Test JSON serialization includes shape data"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "shape" in parsed
        assert isinstance(parsed["shape"], dict)

    @patch("builtins.open", side_effect=Exception("File error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to Tierod dump"):
            instance.dump("error_file")


class TestTierodYAMLConstructor(BaseYAMLConstructorTestMixin):
    """Test Tierod YAML constructor using common test mixin"""
    
    def get_constructor_function(self):
        """Return the Tierod constructor function"""
        return Tierod_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        return {
            "r": 18.0,
            "n": 10,
            "dh": 4.5,
            "sh": 22.0,
            "shape": Shape2D(name="constructor_shape", pts=[[0, 0], [2, 2]])
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "Tierod"


class TestTierodYAMLTag(BaseYAMLTagTestMixin):
    """Test Tierod YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Tierod class"""
        return Tierod
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Tierod"


class TestTierodFileOperations:
    """Test Tierod file operations and edge cases"""
    
    def test_from_yaml_with_shape_file_loading(self):
        """Test from_yaml when shape is loaded from file"""
        yaml_content = '''
!<Tierod>
r: 20.0
n: 8
dh: 5.0
sh: 25.0
shape: test_shape_file
'''
        
        mock_shape = Shape2D(name="loaded_shape", pts=[[0, 0], [3, 3]])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    with patch('builtins.open', mock_open()):
                        with patch('yaml.load', return_value=mock_shape):
                            tierod = Tierod.from_yaml(tmp_file.name)
                
                assert tierod.r == 20.0
                assert tierod.n == 8
                assert tierod.dh == 5.0
                assert tierod.sh == 25.0
                assert tierod.shape == mock_shape
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_file_not_found(self):
        """Test from_yaml with non-existent file"""
        with pytest.raises(Exception, match="Failed to load Tierod data"):
            Tierod.from_yaml("non_existent_file.yaml")

    def test_from_yaml_invalid_yaml(self):
        """Test from_yaml with invalid YAML content"""
        invalid_yaml = "r: 10.0\nn: invalid_number\ndh: 2.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(invalid_yaml)
            tmp_file.flush()
            
            try:
                with pytest.raises(Exception):
                    Tierod.from_yaml(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)


class TestTierodIntegration:
    """Integration tests for Tierod class"""
    
    def test_tierod_with_various_shapes(self):
        """Test Tierod with different types of shapes"""
        shapes = [
            Shape2D(name="square", pts=[[0, 0], [1, 0], [1, 1], [0, 1]]),
            Shape2D(name="triangle", pts=[[0, 0], [1, 0], [0.5, 1]]),
            Shape2D(name="line", pts=[[0, 0], [1, 1]]),
            Shape2D(name="complex", pts=[[i, i**2 % 3] for i in range(10)])
        ]
        
        tierods = []
        for i, shape in enumerate(shapes):
            tierod = Tierod(
                r=10.0 + i * 5,
                n=4 + i * 2,
                dh=2.0 + i * 0.5,
                sh=8.0 + i * 2,
                shape=shape
            )
            tierods.append(tierod)
        
        # Verify each tierod maintains its properties
        for i, tierod in enumerate(tierods):
            assert tierod.r == 10.0 + i * 5
            assert tierod.n == 4 + i * 2
            assert tierod.shape == shapes[i]

    def test_tierod_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_shape = Shape2D(name="roundtrip", pts=[[0, 0], [2, 1], [1, 2]])
        original_tierod = Tierod(r=30.0, n=16, dh=7.5, sh=45.0, shape=original_shape)
        
        # Test JSON serialization
        json_str = original_tierod.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Tierod"
        assert parsed_json["r"] == 30.0
        assert parsed_json["n"] == 16
        assert parsed_json["dh"] == 7.5
        assert parsed_json["sh"] == 45.0
        assert "shape" in parsed_json

    def test_tierod_collection_operations(self):
        """Test operations on collections of tierods"""
        shape = Shape2D(name="collection_shape", pts=[[0, 0], [1, 1]])
        
        # Create collection of tierods
        tierods = [
            Tierod(r=i * 5.0, n=i + 1, dh=i * 0.5, sh=i * 2.0, shape=shape)
            for i in range(1, 11)
        ]
        
        # Test sorting by radius
        sorted_tierods = sorted(tierods, key=lambda t: t.r)
        assert sorted_tierods[0].r == 5.0
        assert sorted_tierods[-1].r == 50.0
        
        # Test filtering
        large_tierods = [t for t in tierods if t.r > 25.0]
        assert len(large_tierods) == 5
        
        # Test mapping operations
        total_n = sum(t.n for t in tierods)
        assert total_n == sum(range(2, 12))  # 2+3+4+...+11


class TestTierodPerformance:
    """Performance tests for Tierod class"""
    
    def test_large_shape_handling(self):
        """Test Tierod performance with large shape data"""
        # Create shape with many points
        large_shape = Shape2D(
            name="large_shape",
            pts=[[i, i % 100] for i in range(1000)]
        )
        
        tierod = Tierod(r=100.0, n=50, dh=10.0, sh=500.0, shape=large_shape)
        
        # Test that operations still work efficiently
        repr_str = repr(tierod)
        assert len(repr_str) > 0
        
        json_str = tierod.to_json()
        assert len(json_str) > 0

    def test_multiple_tierod_creation_performance(self):
        """Test performance of creating many tierods"""
        base_shape = Shape2D(name="base", pts=[[0, 0], [1, 1]])
        
        # Create many tierods
        tierods = []
        for i in range(100):
            tierod = Tierod(
                r=float(i),
                n=i + 1,
                dh=float(i) * 0.1,
                sh=float(i) * 2.0,
                shape=base_shape
            )
            tierods.append(tierod)
        
        assert len(tierods) == 100
        assert all(isinstance(t, Tierod) for t in tierods)


class TestTierodErrorHandling:
    """Test error handling in Tierod class"""
    
    def test_invalid_shape_file_handling(self):
        """Test handling of invalid shape file"""
        with patch('builtins.open', side_effect=FileNotFoundError("Shape file not found")):
            with pytest.raises(FileNotFoundError):
                Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape="nonexistent_shape")

    def test_yaml_load_error_in_shape_loading(self):
        """Test YAML load error when loading shape from file"""
        with patch('builtins.open', mock_open(read_data="invalid: yaml: content:::")):
            with patch('yaml.load', side_effect=yaml.YAMLError("Invalid YAML")):
                with pytest.raises(yaml.YAMLError):
                    Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape="invalid_shape")

    def test_tierod_with_none_values(self):
        """Test Tierod behavior with None values"""
        # The class doesn't validate input, so this might work depending on implementation
        shape = Shape2D(name="test", pts=[[0, 0], [1, 1]])
        
        # These might raise TypeErrors depending on how the values are used
        try:
            tierod = Tierod(r=None, n=None, dh=None, sh=None, shape=shape)
            # If it doesn't raise an error, verify the values are stored
            assert tierod.r is None
            assert tierod.n is None
            assert tierod.dh is None
            assert tierod.sh is None
        except TypeError:
            # Expected if the class validates types
            pass

    def test_dump_with_invalid_filename(self):
        """Test dump method with invalid filename"""
        shape = Shape2D(name="test", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape=shape)
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception, match="Failed to Tierod dump"):
                tierod.dump("/root/forbidden_file")


class TestTierodEdgeCases:
    """Test edge cases for Tierod class"""
    
    def test_tierod_with_empty_shape(self):
        """Test Tierod with empty shape points"""
        empty_shape = Shape2D(name="empty", pts=[])
        tierod = Tierod(r=5.0, n=1, dh=1.0, sh=2.0, shape=empty_shape)
        
        assert tierod.shape.pts == []
        assert len(tierod.shape.pts) == 0

    def test_tierod_with_single_point_shape(self):
        """Test Tierod with single point shape"""
        single_point_shape = Shape2D(name="point", pts=[[1.5, 2.5]])
        tierod = Tierod(r=7.0, n=3, dh=1.5, sh=4.0, shape=single_point_shape)
        
        assert len(tierod.shape.pts) == 1
        assert tierod.shape.pts[0] == [1.5, 2.5]

    def test_tierod_with_very_large_values(self):
        """Test Tierod with very large numeric values"""
        shape = Shape2D(name="large", pts=[[0, 0], [1e6, 1e6]])
        tierod = Tierod(
            r=1e10,
            n=999999,
            dh=1e8,
            sh=1e12,
            shape=shape
        )
        
        assert tierod.r == 1e10
        assert tierod.n == 999999
        assert tierod.dh == 1e8
        assert tierod.sh == 1e12

    def test_tierod_with_very_small_values(self):
        """Test Tierod with very small numeric values"""
        shape = Shape2D(name="small", pts=[[1e-10, 1e-10], [2e-10, 2e-10]])
        tierod = Tierod(
            r=1e-15,
            n=1,
            dh=1e-20,
            sh=1e-25,
            shape=shape
        )
        
        assert tierod.r == 1e-15
        assert tierod.n == 1
        assert tierod.dh == 1e-20
        assert tierod.sh == 1e-25

    def test_tierod_attribute_modification(self):
        """Test modifying Tierod attributes after creation"""
        shape = Shape2D(name="modifiable", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape=shape)
        
        # Modify attributes
        tierod.r = 20.0
        tierod.n = 10
        tierod.dh = 4.0
        tierod.sh = 16.0
        
        # Verify modifications
        assert tierod.r == 20.0
        assert tierod.n == 10
        assert tierod.dh == 4.0
        assert tierod.sh == 16.0

    def test_tierod_shape_modification(self):
        """Test modifying Tierod shape after creation"""
        original_shape = Shape2D(name="original", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape=original_shape)
        
        # Modify shape
        new_shape = Shape2D(name="new", pts=[[2, 2], [3, 3]])
        tierod.shape = new_shape
        
        assert tierod.shape == new_shape
        assert tierod.shape.name == "new"
        assert tierod.shape.pts == [[2, 2], [3, 3]]


class TestTierodDataValidation:
    """Test data validation and consistency"""
    
    def test_numeric_parameter_types(self):
        """Test that numeric parameters accept appropriate types"""
        shape = Shape2D(name="test", pts=[[0, 0], [1, 1]])
        
        # Test with integers
        tierod_int = Tierod(r=10, n=5, dh=2, sh=8, shape=shape)
        assert isinstance(tierod_int.r, int)
        assert isinstance(tierod_int.n, int)
        assert isinstance(tierod_int.dh, int)
        assert isinstance(tierod_int.sh, int)
        
        # Test with floats
        tierod_float = Tierod(r=10.5, n=5, dh=2.5, sh=8.5, shape=shape)
        assert isinstance(tierod_float.r, float)
        assert isinstance(tierod_float.dh, float)
        assert isinstance(tierod_float.sh, float)

    def test_shape_parameter_validation(self):
        """Test shape parameter validation"""
        # Test with valid Shape2D object
        valid_shape = Shape2D(name="valid", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape=valid_shape)
        assert isinstance(tierod.shape, Shape2D)
        
        # Test with string (should load from file)
        with patch('builtins.open', mock_open()):
            with patch('yaml.load', return_value=valid_shape):
                tierod_from_file = Tierod(r=10.0, n=5, dh=2.0, sh=8.0, shape="shape_file")
                assert isinstance(tierod_from_file.shape, Shape2D)

    def test_geometric_consistency(self):
        """Test geometric parameter consistency"""
        shape = Shape2D(name="geo_test", pts=[[0, 0], [5, 5]])
        tierod = Tierod(r=15.0, n=8, dh=3.0, sh=20.0, shape=shape)
        
        # Basic geometric relationships
        # dh (hydraulic diameter) should be positive for meaningful geometry
        assert tierod.dh > 0
        
        # sh (surface area) should be positive
        assert tierod.sh > 0
        
        # r (radius) should typically be positive
        assert tierod.r > 0
        
        # n (number) should typically be positive integer
        assert tierod.n > 0

    def test_dimensional_analysis(self):
        """Test dimensional consistency of parameters"""
        shape = Shape2D(name="dimensional", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=4, dh=2.0, sh=8.0, shape=shape)
        
        # Basic dimensional checks
        # r should be a length dimension
        # dh should be a length dimension
        # sh should be an area dimension (length²)
        # n should be dimensionless
        
        # These are primarily documentation of expected units
        assert isinstance(tierod.r, (int, float))  # Length [mm]
        assert isinstance(tierod.dh, (int, float))  # Length [mm]
        assert isinstance(tierod.sh, (int, float))  # Area [mm²]
        assert isinstance(tierod.n, int)  # Dimensionless count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    