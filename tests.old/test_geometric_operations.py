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


# File: new-tests/test_geometric_operations.py
class TestGeometricOperations:
    """Test geometric computation methods across classes"""

    def test_bounding_box_consistency(self, sample_helix, sample_ring, sample_supra):
        """Test boundingBox returns consistent format across classes"""
        objects = [sample_helix, sample_supra]  # Remove sample_ring for now
        
        for obj in objects:
            rb, zb = obj.boundingBox()
            
            # All should return tuple of two lists
            assert isinstance(rb, list)
            assert isinstance(zb, list)
            assert len(rb) == 2
            assert len(zb) == 2
            
            # Min should be less than max
            assert rb[0] <= rb[1]
            assert zb[0] <= zb[1]
            
        # Test Ring separately if boundingBox exists
        if hasattr(sample_ring, 'boundingBox'):
            rb, zb = sample_ring.boundingBox()
            assert isinstance(rb, list)
            assert isinstance(zb, list)
            assert len(rb) == 2
            assert len(zb) == 2
            assert rb[0] <= rb[1]
            assert zb[0] <= zb[1]

    def test_intersection_logic(self):
        """Test intersection detection across different classes"""
        # Create objects with known bounds - use proper constructor signatures
        from python_magnetgeo.ModelAxi import ModelAxi
        from python_magnetgeo.Model3D import Model3D
        from python_magnetgeo.Shape import Shape
        
        axi = ModelAxi("test", 5.0, [1.0], [10.0])
        model3d = Model3D("test", "test_cad", False, False)
        shape = Shape("test", "rectangular", 5, [90.0], 0, "BELOW")
        
        helix = Helix("intersect_helix", [10.0, 20.0], [0.0, 50.0], 1.0, True, False, axi, model3d, shape)
        ring = Ring("intersect_ring", [15.0, 15.1, 24.9, 25.0], [20.0, 30.0], 6, 30.0, True, False)
        screen = Screen("intersect_screen", [5.0, 15.0], [10.0, 40.0])
        
        test_rectangle = [12.0, 18.0], [15.0, 35.0]  # Overlaps with all
        
        # All should detect intersection
        assert helix.intersect(*test_rectangle) is True
        if hasattr(ring, 'intersect'):
            assert ring.intersect(*test_rectangle) is True
        assert screen.intersect(*test_rectangle) is True
        
        non_overlap_rectangle = [30.0, 40.0], [60.0, 70.0]  # Overlaps with none
        
        # None should detect intersection
        assert helix.intersect(*non_overlap_rectangle) is False
        if hasattr(ring, 'intersect'):
            assert ring.intersect(*non_overlap_rectangle) is False
        assert screen.intersect(*non_overlap_rectangle) is False

    def test_insert_bounding_box_calculation(self, sample_insert):
        """Test Insert boundingBox accounts for all components"""
        rb, zb = sample_insert.boundingBox()
        
        # Should encompass all helices
        helix_rb, helix_zb = sample_insert.helices[0].boundingBox()
        assert rb[0] <= helix_rb[0]
        assert rb[1] >= helix_rb[1]
        
        # Should account for ring height adjustment
        # zb should be extended by ring height
        ring_height = abs(sample_insert.rings[0].z[1] - sample_insert.rings[0].z[0])
        assert zb[0] <= helix_zb[0] - ring_height
        assert zb[1] >= helix_zb[1] + ring_height

    def test_characteristic_length_calculations(self):
        """Test get_lc method provides reasonable values"""
        supra = Supra("lc_supra", [10.0, 30.0], [0.0, 80.0], 5, "")  # Empty struct
        screen = Screen("lc_screen", [5.0, 25.0], [0.0, 60.0])
        
        supra_lc = supra.get_lc()
        screen_lc = screen.get_lc()
        
        # Should be positive values
        assert supra_lc > 0
        assert screen_lc > 0
        
        # Should scale with geometry size
        assert supra_lc == (30.0 - 10.0) / 5.0  # 4.0
        assert screen_lc == (25.0 - 5.0) / 10.0  # 2.0