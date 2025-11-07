# File: new-tests/test_core_classes.py
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


class TestHelix:
    """Test Helix class - core magnet component"""

    def test_helix_initialization(self, sample_modelaxi, sample_model3d, sample_shape):
        """Test Helix object creation with all parameters"""
        helix = Helix(
            name="init_helix",
            r=[10.0, 20.0],
            z=[0.0, 80.0],
            cutwidth=1.5,
            odd=False,
            dble=True,
            modelaxi=sample_modelaxi,
            model3d=sample_model3d,
            shape=sample_shape
        )
        
        assert helix.name == "init_helix"
        assert helix.r == [10.0, 20.0]
        assert helix.z == [0.0, 80.0]
        assert helix.cutwidth == 1.5
        assert helix.odd is False
        assert helix.dble is True
        assert helix.modelaxi == sample_modelaxi
        assert helix.model3d == sample_model3d
        assert helix.shape == sample_shape

    def test_helix_bounding_box(self, sample_helix):
        """Test boundingBox returns correct r,z bounds"""
        rb, zb = sample_helix.boundingBox()
        
        assert isinstance(rb, list)
        assert isinstance(zb, list)
        assert len(rb) == 2
        assert len(zb) == 2
        assert rb == sample_helix.r
        assert zb == sample_helix.z

    def test_helix_intersection_detection(self, sample_helix):
        """Test intersect method for collision detection"""
        # Test overlapping rectangle
        overlap_result = sample_helix.intersect([18.0, 22.0], [25.0, 75.0])
        assert overlap_result is True
        
        # Test non-overlapping rectangle
        no_overlap_result = sample_helix.intersect([30.0, 40.0], [120.0, 130.0])
        assert no_overlap_result is False

    def test_helix_get_type(self, sample_helix):
        """Test get_type method returns correct magnet type"""
        magnet_type = sample_helix.get_type()
        assert isinstance(magnet_type, str)
        assert len(magnet_type) > 0

    def test_helix_insulators(self, sample_helix):
        """Test insulators method returns material and count"""
        material, count = sample_helix.insulators()
        assert isinstance(material, str)
        assert isinstance(count, (int, float))
        assert count >= 0

    def test_helix_serialization(self, sample_helix):
        """Test JSON serialization preserves all data"""
        json_str = sample_helix.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["__classname__"] == "Helix"
        assert parsed["name"] == "test_helix"
        assert parsed["r"] == [15.0, 25.0]
        assert parsed["z"] == [0.0, 100.0]
        assert parsed["cutwidth"] == 2.0
        assert parsed["odd"] is True
        assert parsed["dble"] is False


class TestRing:
    """Test Ring class - magnet ring component"""

    def test_ring_initialization(self):
        """Test Ring object creation"""
        ring = Ring(
            name="init_ring",
            r=[8.0, 8.1, 31.9, 32.0],
            z=[20.0, 30.0],
            n=8,
            angle=45.0,
            bpside=True,
            fillets=False
        )
        
        assert ring.name == "init_ring"
        assert ring.r == [8.0, 8.1, 31.9, 32.0]
        assert ring.z == [20.0, 30.0]
        assert ring.n == 8
        assert ring.angle == 45.0

    def test_ring_height_calculation(self, sample_ring):
        """Test height calculation for ring geometry"""
        height = sample_ring.z[1] - sample_ring.z[0]
        assert height == 10.0  # 55.0 - 45.0

    def test_ring_serialization(self, sample_ring):
        """Test JSON serialization"""
        json_str = sample_ring.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["__classname__"] == "Ring"
        assert parsed["name"] == "test_ring"
        assert parsed["r"] == [12.0, 12.1, 27.9, 28.0]
        assert parsed["z"] == [45.0, 55.0]

class TestSupra:
    """Test Supra class - superconducting magnet"""

    def test_supra_initialization(self):
        """Test Supra object creation with all parameters"""
        supra = Supra(
            name="init_supra",
            r=[25.0, 45.0],
            z=[15.0, 85.0],
            n=8,
            struct=None  # Empty to avoid file loading
        )
        
        assert supra.name == "init_supra"
        assert supra.r == [25.0, 45.0]
        assert supra.z == [15.0, 85.0]
        assert supra.n == 8
        assert supra.struct == None

    def test_supra_detail_levels(self, sample_supra):
        """Test set_Detail method with valid levels"""
        from python_magnetgeo.Supra import DetailLevel
        valid_details = ["None", "dblpancake", "pancake", "tape"]
        
        for detail in valid_details:
            sample_supra.set_Detail(detail)
            assert sample_supra.detail == DetailLevel[detail.upper()]

    def test_supra_detail_invalid(self, sample_supra):
        """Test set_Detail raises exception for invalid levels"""
        with pytest.raises(Exception):
            sample_supra.set_Detail("invalid_detail")

    def test_supra_get_nturns(self, sample_supra):
        """Test get_Nturns method"""
        turns = sample_supra.get_Nturns()
        # When struct is empty, should return n value
        assert turns == sample_supra.n

    def test_supra_get_lc(self, sample_supra):
        """Test characteristic length calculation"""
        lc = sample_supra.get_lc()
        expected_lc = (sample_supra.r[1] - sample_supra.r[0]) / 5.0
        assert lc == expected_lc

    def test_supra_serialization(self, sample_supra):
        """Test JSON serialization"""
        json_str = sample_supra.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["__classname__"] == "Supra"
        assert parsed["name"] == "test_supra"
        assert parsed["n"] == 5
        assert parsed["struct"] == None


class TestScreen:
    """Test Screen class - geometric screen component"""

    def test_screen_initialization(self):
        """Test Screen object creation"""
        screen = Screen(
            name="init_screen",
            r=[5.0, 50.0],
            z=[0.0, 100.0]
        )
        
        assert screen.name == "init_screen"
        assert screen.r == [5.0, 50.0]
        assert screen.z == [0.0, 100.0]

    def test_screen_bounding_box(self):
        """Test boundingBox returns screen dimensions"""
        screen = Screen("bbox_screen", [10.0, 30.0], [0.0, 80.0])
        rb, zb = screen.boundingBox()
        
        assert rb == [10.0, 30.0]
        assert zb == [0.0, 80.0]

    def test_screen_intersection(self):
        """Test intersect method"""
        screen = Screen("intersect_screen", [10.0, 30.0], [20.0, 60.0])
        
        # Overlapping case
        overlap = screen.intersect([15.0, 25.0], [30.0, 50.0])
        assert overlap is True
        
        # Non-overlapping case
        no_overlap = screen.intersect([40.0, 50.0], [70.0, 80.0])
        assert no_overlap is False

    def test_screen_get_lc(self):
        """Test characteristic length calculation"""
        screen = Screen("lc_screen", [10.0, 30.0], [0.0, 40.0])
        lc = screen.get_lc()
        expected_lc = (30.0 - 10.0) / 10.0  # 2.0
        assert lc == expected_lc

    def test_screen_mesh_support(self):
        """Test mesh generation support methods"""
        screen = Screen("mesh_screen", [5.0, 25.0], [0.0, 50.0])
        
        # get_names should return screen identifiers
        names = screen.get_names("test_system")
        assert len(names) == 1
        assert "Screen" in names[0]
        assert "test_system" in names[0]
        assert screen.name in names[0]
        
        # get_channels and get_isolants should return empty for screens
        channels = screen.get_channels("test")
        isolants = screen.get_isolants("test")
        assert channels == []
        assert isolants == []


class TestProbe:
    """Test Probe class - measurement probe system"""

    def test_probe_initialization(self):
        """Test Probe object creation"""
        probe = Probe(
            name="init_probe",
            type="temperature",
            labels=[1, 2, 3],
            points=[[10.0, 0.0, 5.0], [15.0, 0.0, 10.0], [20.0, 0.0, 15.0]]
        )
        
        assert probe.name == "init_probe"
        assert probe.type == "temperature"
        assert probe.labels == [1, 2, 3]
        assert len(probe.points) == 3

    def test_probe_count(self, sample_probe):
        """Test get_probe_count method"""
        count = sample_probe.get_probe_count()
        assert count == 3

    def test_probe_by_labels(self, sample_probe):
        """Test get_probe_by_labels method"""
        probe_info = sample_probe.get_probe_by_labels("V2")
        
        assert probe_info["labels"] == "V2"
        assert probe_info["points"] == [20.0, 0.0, 50.0]
        assert probe_info["type"] == "voltage_taps"

    def test_probe_by_labels_not_found(self, sample_probe):
        """Test get_probe_by_labels with invalid labels"""
        with pytest.raises(ValueError):
            sample_probe.get_probe_by_labels("V999")

    def test_probe_points_by_type(self, sample_probe):
        """Test get_points_by_type method"""
        points = sample_probe.get_points_by_type("voltage_taps")
        assert len(points) == 3
        assert points == sample_probe.points
        
        # Test with different type
        empty_points = sample_probe.get_points_by_type("temperature")
        assert empty_points == []

    def test_probe_add_probe(self, sample_probe):
        """Test add_probe method"""
        initial_count = sample_probe.get_probe_count()
        
        sample_probe.add_probe("V4", [22.0, 0.0, 85.0])
        
        assert sample_probe.get_probe_count() == initial_count + 1
        new_probe = sample_probe.get_probe_by_labels("V4")
        assert new_probe["points"] == [22.0, 0.0, 85.0]

    def test_probe_add_invalid_location(self, sample_probe):
        """Test add_probe with invalid location coordinates"""
        with pytest.raises(ValueError):
            sample_probe.add_probe("V_bad", [10.0, 20.0])  # Only 2 coordinates

    def test_probe_serialization(self, sample_probe):
        """Test JSON serialization"""
        json_str = sample_probe.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["__classname__"] == "Probe"
        assert parsed["name"] == "test_probe"
        assert parsed["type"] == "voltage_taps"
        assert len(parsed["labels"]) == 3
        assert len(parsed["points"]) == 3