#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Shape2D class and factory functions
"""

import pytest
import json
import yaml
import tempfile
import os
import math
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Shape2D import (
    Shape2D, Shape_constructor, 
    create_circle, create_rectangle, create_angularslit
)
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_geometric_data
)


class TestShape2DInitialization:
    """Test Shape2D object initialization"""
    
    def test_shape2d_basic_initialization(self):
        """Test Shape2D initialization with basic parameters"""
        pts = [[0, 0], [1, 0], [1, 1], [0, 1]]
        shape = Shape2D(name="square", pts=pts)
        
        assert shape.name == "square"
        assert shape.pts == pts

    def test_shape2d_with_empty_points(self):
        """Test Shape2D with empty points list"""
        shape = Shape2D(name="empty", pts=[])
        
        assert shape.name == "empty"
        assert shape.pts == []
        assert len(shape.pts) == 0

    def test_shape2d_with_single_point(self):
        """Test Shape2D with single point"""
        pts = [[1.5, 2.5]]
        shape = Shape2D(name="point", pts=pts)
        
        assert shape.name == "point"
        assert shape.pts == pts
        assert len(shape.pts) == 1

    def test_shape2d_with_complex_geometry(self):
        """Test Shape2D with complex geometry"""
        # Create a more complex shape (pentagon)
        pts = [[1, 0], [0.309, 0.951], [-0.809, 0.588], [-0.809, -0.588], [0.309, -0.951]]
        shape = Shape2D(name="pentagon", pts=pts)
        
        assert shape.name == "pentagon"
        assert shape.pts == pts
        assert len(shape.pts) == 5

    def test_shape2d_with_float_coordinates(self):
        """Test Shape2D with floating point coordinates"""
        pts = [[0.1, 0.2], [1.5, 0.7], [2.3, 1.9], [0.8, 2.1]]
        shape = Shape2D(name="float_shape", pts=pts)
        
        assert shape.name == "float_shape"
        assert shape.pts == pts
        
        # Verify all coordinates are preserved
        for i, (x, y) in enumerate(pts):
            assert shape.pts[i][0] == x
            assert shape.pts[i][1] == y


class TestShape2DMethods:
    """Test Shape2D class methods"""
    
    @pytest.fixture
    def sample_shape(self):
        """Create a sample Shape2D for testing"""
        pts = [[0, 0], [2, 0], [2, 2], [0, 2]]
        return Shape2D(name="test_square", pts=pts)

    def test_repr(self, sample_shape):
        """Test __repr__ method"""
        repr_str = repr(sample_shape)
        
        assert "Shape2D(" in repr_str
        assert "name='test_square'" in repr_str
        assert "pts=" in repr_str
        assert "[[0, 0], [2, 0], [2, 2], [0, 2]]" in repr_str

    def test_repr_with_long_points_list(self):
        """Test __repr__ with many points"""
        pts = [[i, i**2] for i in range(50)]
        shape = Shape2D(name="many_points", pts=pts)
        
        repr_str = repr(shape)
        assert "Shape2D(" in repr_str
        assert "name='many_points'" in repr_str
        # The full points list should be included
        assert "pts=" in repr_str


class TestShape2DSerialization(BaseSerializationTestMixin):
    """Test Shape2D serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Shape2D instance"""
        pts = [[0, 0], [3, 0], [3, 3], [0, 3]]
        return Shape2D(name="test_shape", pts=pts)
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
<!Shape2D>
name: yaml_shape
pts: [[0, 0], [1, 0], [1, 1], [0, 1]]
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_shape",
            "pts": [[0, 0], [3, 0], [3, 3], [0, 3]]
        }
    
    def get_class_under_test(self):
        """Return Shape2D class"""
        return Shape2D

    def test_json_with_complex_points(self):
        """Test JSON serialization with complex point data"""
        pts = [[i, math.sin(i)] for i in range(10)]
        shape = Shape2D(name="sine_wave", pts=pts)
        
        json_str = shape.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["name"] == "sine_wave"
        assert len(parsed["pts"]) == 10
        assert parsed["pts"][0] == [0, 0.0]  # sin(0) = 0

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        shape = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to Shape2D dump"):
            shape.dump("error_file")


class TestShape2DYAMLConstructor(BaseYAMLConstructorTestMixin):
    """Test Shape2D YAML constructor using common test mixin"""
    
    def get_constructor_function(self):
        """Return the Shape2D constructor function"""
        return Shape_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        return {
            "name": "constructor_shape",
            "pts": [[0, 0], [2, 2], [0, 2]]
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "Shape2D"


class TestShape2DYAMLTag(BaseYAMLTagTestMixin):
    """Test Shape2D YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Shape2D class"""
        return Shape2D
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Shape2D"


class TestShape2DFactoryFunctions:
    """Test Shape2D factory functions"""
    
    def test_create_circle_basic(self):
        """Test create_circle with basic parameters"""
        circle = create_circle(r=5.0, n=8)
        
        assert isinstance(circle, Shape2D)
        assert circle.name == "circle-10.0-mm"  # 2*r
        assert len(circle.pts) == 8
        
        # Verify points are on circle
        for x, y in circle.pts:
            distance = math.sqrt(x**2 + y**2)
            assert abs(distance - 5.0) < 1e-10

    def test_create_circle_default_points(self):
        """Test create_circle with default number of points"""
        circle = create_circle(r=3.0)
        
        assert len(circle.pts) == 20  # default n=20
        assert circle.name == "circle-6.0-mm"

    def test_create_circle_many_points(self):
        """Test create_circle with many points"""
        circle = create_circle(r=2.0, n=100)
        
        assert len(circle.pts) == 100
        
        # Verify circle properties
        for x, y in circle.pts:
            distance = math.sqrt(x**2 + y**2)
            assert abs(distance - 2.0) < 1e-10

    def test_create_circle_edge_cases(self):
        """Test create_circle edge cases"""
        # Very small radius
        small_circle = create_circle(r=1e-6, n=4)
        assert len(small_circle.pts) == 4
        
        # Large radius
        large_circle = create_circle(r=1000.0, n=6)
        assert len(large_circle.pts) == 6

    def test_create_circle_invalid_n(self):
        """Test create_circle with invalid n parameter"""
        with pytest.raises(RuntimeError, match="n got -5, expect a positive integer"):
            create_circle(r=5.0, n=-5)

    def test_create_rectangle_basic(self):
        """Test create_rectangle with basic parameters"""
        rect = create_rectangle(x=1.0, y=2.0, dx=3.0, dy=4.0)
        
        assert isinstance(rect, Shape2D)
        assert rect.name == "rectangle-3.0-4.0-mm"
        assert len(rect.pts) == 4
        
        # Verify rectangle corners
        expected_pts = [[1.0, 2.0], [4.0, 2.0], [4.0, 6.0], [1.0, 6.0]]
        assert rect.pts == expected_pts

    def test_create_rectangle_with_fillet(self):
        """Test create_rectangle with fillet parameter"""
        rect = create_rectangle(x=0.0, y=0.0, dx=4.0, dy=2.0, fillet=2)
        
        assert isinstance(rect, Shape2D)
        assert len(rect.pts) > 4  # Should have more points due to fillet

    def test_create_rectangle_zero_fillet(self):
        """Test create_rectangle with zero fillet"""
        rect = create_rectangle(x=2.0, y=3.0, dx=5.0, dy=6.0, fillet=0)
        
        assert len(rect.pts) == 4  # Standard rectangle
        expected_pts = [[2.0, 3.0], [7.0, 3.0], [7.0, 9.0], [2.0, 9.0]]
        assert rect.pts == expected_pts

    def test_create_rectangle_invalid_fillet(self):
        """Test create_rectangle with invalid fillet parameter"""
        with pytest.raises(RuntimeError, match="fillet got -3, expect a positive integer"):
            create_rectangle(x=0.0, y=0.0, dx=2.0, dy=2.0, fillet=-3)

    def test_create_angularslit_basic(self):
        """Test create_angularslit with basic parameters"""
        slit = create_angularslit(x=10.0, angle=math.pi/4, dx=2.0, n=5)
        
        assert isinstance(slit, Shape2D)
        assert slit.name == f"angularslit-2.0-{math.pi/4}-mm"
        assert len(slit.pts) >= 10  # Should have at least 2*n points

    def test_create_angularslit_with_fillet(self):
        """Test create_angularslit with fillet parameter"""
        slit = create_angularslit(x=8.0, angle=math.pi/6, dx=1.5, n=4, fillet=2)
        
        assert isinstance(slit, Shape2D)
        assert len(slit.pts) > 8  # Should have more points due to fillet

    def test_create_angularslit_zero_fillet(self):
        """Test create_angularslit with zero fillet"""
        slit = create_angularslit(x=6.0, angle=math.pi/3, dx=1.0, n=3, fillet=0)
        
        assert isinstance(slit, Shape2D)
        assert len(slit.pts) == 6  # 2*n points

    def test_create_angularslit_invalid_parameters(self):
        """Test create_angularslit with invalid parameters"""
        with pytest.raises(RuntimeError, match="fillet got -1, expect a positive integer"):
            create_angularslit(x=5.0, angle=math.pi/4, dx=1.0, n=5, fillet=-1)
        
        with pytest.raises(RuntimeError, match="n got -2, expect a positive integer"):
            create_angularslit(x=5.0, angle=math.pi/4, dx=1.0, n=-2, fillet=0)

    def test_factory_function_names(self):
        """Test that factory functions generate appropriate names"""
        circle = create_circle(r=7.5)
        rect = create_rectangle(x=0, y=0, dx=10, dy=20)
        slit = create_angularslit(x=15, angle=math.pi/2, dx=3)
        
        assert "circle" in circle.name
        assert "15.0" in circle.name  # 2*r
        
        assert "rectangle" in rect.name
        assert "10" in rect.name and "20" in rect.name
        
        assert "angularslit" in slit.name
        assert "3" in slit.name


class TestShape2DGeometry:
    """Test geometric properties and operations"""
    
    def test_shape_point_modification(self):
        """Test modifying shape points after creation"""
        pts = [[0, 0], [1, 1]]
        shape = Shape2D(name="modifiable", pts=pts)
        
        # Modify points
        shape.pts.append([2, 2])
        assert len(shape.pts) == 3
        
        # Modify existing point
        shape.pts[0] = [0.5, 0.5]
        assert shape.pts[0] == [0.5, 0.5]

    def test_shape_name_modification(self):
        """Test modifying shape name after creation"""
        shape = Shape2D(name="original", pts=[[0, 0]])
        
        shape.name = "modified"
        assert shape.name == "modified"

    def test_complex_geometric_calculations(self):
        """Test shapes for geometric calculations"""
        # Regular hexagon
        n = 6
        r = 10.0
        hexagon_pts = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            hexagon_pts.append([x, y])
        
        hexagon = Shape2D(name="hexagon", pts=hexagon_pts)
        
        # Verify hexagon properties
        assert len(hexagon.pts) == 6
        
        # All points should be at distance r from origin
        for x, y in hexagon.pts:
            distance = math.sqrt(x**2 + y**2)
            assert abs(distance - r) < 1e-10

    def test_shape_coordinate_precision(self):
        """Test coordinate precision preservation"""
        # Use high precision coordinates
        precision_pts = [
            [1.123456789012345, 2.987654321098765],
            [3.141592653589793, 2.718281828459045]
        ]
        
        shape = Shape2D(name="precision", pts=precision_pts)
        
        # Verify precision is preserved
        assert shape.pts[0][0] == 1.123456789012345
        assert shape.pts[0][1] == 2.987654321098765
        assert shape.pts[1][0] == 3.141592653589793
        assert shape.pts[1][1] == 2.718281828459045


class TestShape2DIntegration:
    """Integration tests for Shape2D class"""
    
    def test_shape2d_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_pts = [[1, 2], [3, 4], [5, 6]]
        original_shape = Shape2D(name="roundtrip_test", pts=original_pts)
        
        # Test JSON roundtrip data
        json_str = original_shape.to_json()
        parsed_data = json.loads(json_str)
        
        assert parsed_data["__classname__"] == "Shape2D"
        assert parsed_data["name"] == "roundtrip_test"
        assert parsed_data["pts"] == original_pts

    def test_multiple_shapes_interaction(self):
        """Test creating and managing multiple shapes"""
        shapes = [
            create_circle(r=i+1, n=8) for i in range(5)
        ]
        
        # Verify each shape is independent
        for i, shape in enumerate(shapes):
            expected_name = f"circle-{2*(i+1)}.0-mm"
            assert shape.name == expected_name
            assert len(shape.pts) == 8

    def test_shape_collection_operations(self):
        """Test operations on collections of shapes"""
        # Create various shapes
        shapes = [
            create_circle(r=5.0),
            create_rectangle(x=0, y=0, dx=10, dy=10),
            create_angularslit(x=15, angle=math.pi/4, dx=2),
            Shape2D(name="custom", pts=[[0, 0], [10, 10]])
        ]
        
        # Test filtering by name pattern
        circles = [s for s in shapes if "circle" in s.name]
        assert len(circles) == 1
        
        rectangles = [s for s in shapes if "rectangle" in s.name]
        assert len(rectangles) == 1
        
        # Test mapping operations
        point_counts = [len(s.pts) for s in shapes]
        assert len(point_counts) == 4
        assert all(count >= 0 for count in point_counts)

    def test_factory_functions_integration(self):
        """Test integration between different factory functions"""
        # Create shapes with consistent sizing
        radius = 5.0
        
        circle = create_circle(r=radius, n=16)
        # Create rectangle that circumscribes the circle
        rect = create_rectangle(x=-radius, y=-radius, dx=2*radius, dy=2*radius)
        
        # Basic geometric consistency checks
        assert len(circle.pts) == 16
        assert len(rect.pts) == 4
        
        # Rectangle should contain circle (basic check)
        for x, y in circle.pts:
            assert -radius <= x <= radius
            assert -radius <= y <= radius


class TestShape2DPerformance:
    """Performance tests for Shape2D class"""
    
    def test_large_point_set_handling(self):
        """Test Shape2D performance with large point sets"""
        # Create shape with many points
        large_pts = [[i, i**2 % 1000] for i in range(10000)]
        large_shape = Shape2D(name="large_shape", pts=large_pts)
        
        assert len(large_shape.pts) == 10000
        assert large_shape.name == "large_shape"
        
        # Test that operations still work
        repr_str = repr(large_shape)
        assert len(repr_str) > 0
        
        json_str = large_shape.to_json()
        assert len(json_str) > 0

    def test_circle_generation_performance(self):
        """Test performance of circle generation with many points"""
        large_circle = create_circle(r=100.0, n=10000)
        
        assert len(large_circle.pts) == 10000
        
        # Verify geometric properties still hold
        sample_points = large_circle.pts[::1000]  # Sample every 1000th point
        for x, y in sample_points:
            distance = math.sqrt(x**2 + y**2)
            assert abs(distance - 100.0) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])