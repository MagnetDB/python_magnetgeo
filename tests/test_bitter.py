#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Bitter class (Updated with factored approach)
"""

import pytest
import json
import yaml
import tempfile
import os
import math
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Bitter import Bitter, Bitter_constructor
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo.tierod import Tierod
from python_magnetgeo.Shape2D import Shape2D
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_geometric_data
)


class TestBitterInitialization:
    """Test Bitter object initialization"""
    
    @pytest.fixture
    def sample_modelaxi(self):
        """Create a sample ModelAxi for testing"""
        return ModelAxi(
            name="bitter_axi",
            h=20.0,
            turns=[3.0, 2.5, 4.0],
            pitch=[6.0, 6.0, 6.0]
        )
    
    @pytest.fixture
    def sample_cooling_slits(self):
        """Create sample cooling slits for testing"""
        shape = Shape2D(name="slit_shape", pts=[[0, 0], [1, 0], [1, 0.5], [0, 0.5]])
        return [
            CoolingSlit(r=15.0, angle=0.0, n=8, dh=2.0, sh=8.0, shape=shape),
            CoolingSlit(r=25.0, angle=30.0, n=12, dh=3.0, sh=12.0, shape=shape)
        ]
    
    @pytest.fixture
    def sample_tierod(self):
        """Create a sample Tierod for testing"""
        shape = Shape2D(name="tierod_shape", pts=[[0, 0], [2, 0], [2, 2], [0, 2]])
        return Tierod(r=35.0, n=6, dh=4.0, sh=16.0, shape=shape)

    def test_bitter_basic_initialization(self, sample_modelaxi, sample_cooling_slits, sample_tierod):
        """Test Bitter initialization with all parameters"""
        bitter = Bitter(
            name="test_bitter",
            r=[10.0, 30.0],
            z=[0.0, 100.0],
            odd=True,
            modelaxi=sample_modelaxi,
            coolingslits=sample_cooling_slits,
            tierod=sample_tierod,
            innerbore=5.0,
            outerbore=35.0
        )
        
        assert bitter.name == "test_bitter"
        assert bitter.r == [10.0, 30.0]
        assert bitter.z == [0.0, 100.0]
        assert bitter.odd is True
        assert bitter.modelaxi == sample_modelaxi
        assert bitter.coolingslits == sample_cooling_slits
        assert bitter.tierod == sample_tierod
        assert bitter.innerbore == 5.0
        assert bitter.outerbore == 35.0

    def test_bitter_with_empty_cooling_slits(self, sample_modelaxi, sample_tierod):
        """Test Bitter initialization with empty cooling slits"""
        bitter = Bitter(
            name="no_slits_bitter",
            r=[10.0, 20.0],
            z=[0.0, 50.0],
            odd=False,
            modelaxi=sample_modelaxi,
            coolingslits=None,
            tierod=sample_tierod,
            innerbore=8.0,
            outerbore=25.0
        )
        
        assert bitter.coolingslits == []
        assert len(bitter.coolingslits) == 0

    def test_bitter_with_none_cooling_slits(self, sample_modelaxi, sample_tierod):
        """Test Bitter initialization with None cooling slits"""
        bitter = Bitter(
            name="none_slits_bitter",
            r=[15.0, 25.0],
            z=[5.0, 45.0],
            odd=True,
            modelaxi=sample_modelaxi,
            coolingslits=None,
            tierod=sample_tierod,
            innerbore=10.0,
            outerbore=30.0
        )
        
        assert bitter.coolingslits == []

    def test_bitter_minimal_initialization(self, sample_modelaxi, sample_tierod):
        """Test Bitter with minimal parameters"""
        bitter = Bitter(
            name="minimal_bitter",
            r=[0.0, 10.0],
            z=[0.0, 20.0],
            odd=False,
            modelaxi=sample_modelaxi,
            coolingslits=[],
            tierod=sample_tierod,
            innerbore=0.0,
            outerbore=15.0
        )
        
        assert bitter.name == "minimal_bitter"
        assert bitter.coolingslits == []
        assert bitter.innerbore == 0.0
        assert bitter.outerbore == 15.0


class TestBitterMethods:
    """Test Bitter class methods"""
    
    @pytest.fixture
    def sample_bitter(self):
        """Create a comprehensive sample Bitter for testing"""
        modelaxi = ModelAxi(name="test_axi", h=15.0, turns=[2.0, 3.0], pitch=[5.0, 5.0])
        
        shape = Shape2D(name="slit_shape", pts=[[0, 0], [1, 0], [1, 0.5], [0, 0.5]])
        cooling_slits = [
            CoolingSlit(r=20.0, angle=0.0, n=6, dh=2.5, sh=10.0, shape=shape),
            CoolingSlit(r=30.0, angle=45.0, n=8, dh=3.0, sh=12.0, shape=shape)
        ]
        
        tierod_shape = Shape2D(name="tierod_shape", pts=[[0, 0], [2, 2]])
        tierod = Tierod(r=40.0, n=4, dh=4.0, sh=16.0, shape=tierod_shape)
        
        return Bitter(
            name="comprehensive_bitter",
            r=[15.0, 35.0],
            z=[0.0, 80.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=cooling_slits,
            tierod=tierod,
            innerbore=10.0,
            outerbore=40.0
        )

    def test_equivalent_eps(self, sample_bitter):
        """Test equivalent_eps method"""
        # eps = n * sh / (2 * pi * r)
        # For first slit: eps = 6 * 10.0 / (2 * pi * 20.0)
        expected_eps_0 = 6 * 10.0 / (2 * math.pi * 20.0)
        actual_eps_0 = sample_bitter.equivalent_eps(0)
        assert abs(actual_eps_0 - expected_eps_0) < 1e-10
        
        # For second slit: eps = 8 * 12.0 / (2 * pi * 30.0)
        expected_eps_1 = 8 * 12.0 / (2 * math.pi * 30.0)
        actual_eps_1 = sample_bitter.equivalent_eps(1)
        assert abs(actual_eps_1 - expected_eps_1) < 1e-10

    def test_get_channels(self, sample_bitter):
        """Test get_channels method"""
        channels = sample_bitter.get_channels("test")
        
        # Should have n_slits + 2 channels (one before, one after each slit, plus final)
        # With 2 cooling slits: Slit0, Slit1, Slit2, Slit3
        expected_channels = ["test_Slit0", "test_Slit1", "test_Slit2", "test_Slit3"]
        assert channels == expected_channels

    def test_get_channels_no_prefix(self, sample_bitter):
        """Test get_channels with no prefix"""
        channels = sample_bitter.get_channels("")
        
        expected_channels = ["Slit0", "Slit1", "Slit2", "Slit3"]
        assert channels == expected_channels

    def test_get_channels_no_cooling_slits(self):
        """Test get_channels with no cooling slits"""
        modelaxi = ModelAxi(name="no_slit_axi", h=10.0, turns=[1.0], pitch=[5.0])
        tierod_shape = Shape2D(name="tierod", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=20.0, n=2, dh=2.0, sh=8.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="no_slits",
            r=[5.0, 15.0],
            z=[0.0, 30.0],
            odd=False,
            modelaxi=modelaxi,
            coolingslits=[],
            tierod=tierod,
            innerbore=0.0,
            outerbore=20.0
        )
        
        channels = bitter.get_channels("test")
        expected_channels = ["test_Slit0", "test_Slit1"]  # Just start and end
        assert channels == expected_channels

    def test_get_lc_with_cooling_slits(self, sample_bitter):
        """Test get_lc method with cooling slits"""
        lc = sample_bitter.get_lc()
        
        # Should be min(dr) / 5.0 where dr is distance between consecutive radii
        # r = [15.0, 35.0], cooling slits at r = [20.0, 30.0]
        # dr = [20.0-15.0, 30.0-20.0, 35.0-30.0] = [5.0, 10.0, 5.0]
        # min(dr) = 5.0, so lc = 5.0 / 5.0 = 1.0
        assert lc == 1.0

    def test_get_lc_no_cooling_slits(self):
        """Test get_lc method without cooling slits"""
        modelaxi = ModelAxi(name="no_slit_axi", h=10.0, turns=[1.0], pitch=[5.0])
        tierod_shape = Shape2D(name="tierod", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=20.0, n=2, dh=2.0, sh=8.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="no_slits",
            r=[10.0, 30.0],
            z=[0.0, 40.0],
            odd=False,
            modelaxi=modelaxi,
            coolingslits=[],
            tierod=tierod,
            innerbore=5.0,
            outerbore=35.0
        )
        
        # lc = (r[1] - r[0]) / 10.0 = (30.0 - 10.0) / 10.0 = 2.0
        assert bitter.get_lc() == 2.0

    def test_get_isolants(self, sample_bitter):
        """Test get_isolants method"""
        isolants = sample_bitter.get_isolants("test")
        # Currently returns empty list according to implementation
        assert isolants == []

    def test_get_names_2d(self, sample_bitter):
        """Test get_names method for 2D case"""
        names = sample_bitter.get_names("test", is2D=True)
        
        # Should include sections for each turn plus potential HP/BP sections
        # With 2 turns in modelaxi, expecting B1 and B2 sections
        # Each section should have Slit0, Slit1, Slit2, Slit3 (4 slits total with 2 cooling slits)
        assert len(names) > 0
        assert all("test_B" in name and "Slit" in name for name in names)

    def test_get_names_3d(self, sample_bitter):
        """Test get_names method for 3D case"""
        names = sample_bitter.get_names("test", is2D=False)
        
        expected_names = ["test_B", "test_Kapton"]
        assert names == expected_names

    def test_get_nturns(self, sample_bitter):
        """Test get_Nturns method"""
        # ModelAxi has turns [2.0, 3.0], so total = 5.0
        assert sample_bitter.get_Nturns() == 5.0

    def test_bounding_box(self, sample_bitter):
        """Test boundingBox method"""
        rb, zb = sample_bitter.boundingBox()
        
        assert rb == sample_bitter.r
        assert zb == sample_bitter.z

    def test_intersect_collision(self, sample_bitter):
        """Test intersect method with collision"""
        # Test with overlapping rectangle
        r = [20.0, 30.0]  # Overlaps with bitter bounds [15.0, 35.0]
        z = [10.0, 70.0]  # Overlaps with bitter bounds [0.0, 80.0]
        
        result = sample_bitter.intersect(r, z)
        assert result is True

    def test_intersect_no_collision(self, sample_bitter):
        """Test intersect method without collision"""
        # Test with non-overlapping rectangle
        r = [100.0, 110.0]  # Far from bitter bounds
        z = [200.0, 210.0]
        
        result = sample_bitter.intersect(r, z)
        assert result is False

    def test_get_params(self, sample_bitter):
        """Test get_params method"""
        params = sample_bitter.get_params()
        
        # Should return (nslits, Dh, Sh, Zh, filling_factor)
        assert len(params) == 5
        
        nslits, Dh, Sh, Zh, filling_factor = params
        
        # Should have 2 cooling slits
        assert nslits == 2
        
        # Dh should have 4 elements: [inner channel, slit1, slit2, outer channel]
        assert len(Dh) == 4
        
        # Sh should have 4 elements
        assert len(Sh) == 4
        
        # Zh should include all z positions
        assert len(Zh) > 0
        
        # Filling factor should have 4 elements
        assert len(filling_factor) == 4

    def test_repr(self, sample_bitter):
        """Test __repr__ method"""
        repr_str = repr(sample_bitter)
        
        assert "Bitter(" in repr_str
        assert "name='comprehensive_bitter'" in repr_str
        assert "r=[15.0, 35.0]" in repr_str
        assert "z=[0.0, 80.0]" in repr_str
        assert "odd=True" in repr_str


class TestBitterSerialization(BaseSerializationTestMixin):
    """Test Bitter serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Bitter instance"""
        modelaxi = ModelAxi(name="test_axi", h=10.0, turns=[2.0], pitch=[5.0])
        
        shape = Shape2D(name="test_shape", pts=[[0, 0], [1, 1]])
        cooling_slit = CoolingSlit(r=20.0, angle=0.0, n=4, dh=2.0, sh=8.0, shape=shape)
        
        tierod = Tierod(r=30.0, n=6, dh=3.0, sh=12.0, shape=shape)
        
        return Bitter(
            name="test_bitter",
            r=[10.0, 25.0],
            z=[0.0, 50.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=[cooling_slit],
            tierod=tierod,
            innerbore=5.0,
            outerbore=30.0
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
<!Bitter>
name: yaml_bitter
r: [12.0, 28.0]
z: [5.0, 55.0]
odd: false
modelaxi: !<ModelAxi>
  name: yaml_axi
  h: 12.0
  turns: [1.5, 2.5]
  pitch: [4.0, 4.0]
coolingslits: []
tierod: !<Tierod>
  r: 35.0
  n: 8
  dh: 4.0
  sh: 16.0
  shape: !Shape2D
    name: yaml_tierod_shape
    pts: [[0, 0], [2, 2]]
innerbore: 8.0
outerbore: 32.0
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_bitter",
            "r": [10.0, 25.0],
            "z": [0.0, 50.0],
            "odd": True,
            "innerbore": 5.0,
            "outerbore": 30.0
        }
    
    def get_class_under_test(self):
        """Return Bitter class"""
        return Bitter

    def test_json_includes_complex_objects(self):
        """Test that JSON serialization includes complex nested objects"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "modelaxi" in parsed
        assert "coolingslits" in parsed
        assert "tierod" in parsed
        assert isinstance(parsed["coolingslits"], list)

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to Bitter dump"):
            instance.dump()

    def test_write_to_json_method(self):
        """Test write_to_json method"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.write_to_json()
            mock_file.assert_called_once_with("test_bitter.json", "w")


class TestBitterYAMLConstructor(BaseYAMLConstructorTestMixin):
    """Test Bitter YAML constructor using common test mixin"""
    
    def get_constructor_function(self):
        """Return the Bitter constructor function"""
        return Bitter_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        modelaxi = ModelAxi(name="constructor_axi", h=8.0, turns=[1.0], pitch=[4.0])
        
        shape = Shape2D(name="constructor_shape", pts=[[0, 0], [1, 1]])
        cooling_slit = CoolingSlit(r=18.0, angle=30.0, n=6, dh=2.5, sh=10.0, shape=shape)
        tierod = Tierod(r=25.0, n=4, dh=3.5, sh=14.0, shape=shape)
        
        return {
            "name": "constructor_bitter",
            "r": [8.0, 22.0],
            "z": [2.0, 42.0],
            "odd": False,
            "modelaxi": modelaxi,
            "coolingslits": [cooling_slit],
            "tierod": tierod,
            "innerbore": 4.0,
            "outerbore": 26.0
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "Bitter"


class TestBitterYAMLTag(BaseYAMLTagTestMixin):
    """Test Bitter YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Bitter class"""
        return Bitter
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Bitter"


class TestBitterFromDict:
    """Test Bitter.from_dict class method"""
    
    def test_from_dict_complete_data(self):
        """Test from_dict with complete data"""
        modelaxi = ModelAxi(name="dict_axi", h=15.0, turns=[2.0, 3.0], pitch=[6.0, 6.0])
        
        shape = Shape2D(name="dict_shape", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])
        cooling_slit = CoolingSlit(r=25.0, angle=45.0, n=8, dh=3.0, sh=12.0, shape=shape)
        tierod = Tierod(r=35.0, n=6, dh=4.0, sh=16.0, shape=shape)
        
        data = {
            "name": "dict_bitter",
            "r": [15.0, 30.0],
            "z": [5.0, 65.0],
            "odd": True,
            "modelaxi": modelaxi,
            "coolingslits": [cooling_slit],
            "tierod": tierod,
            "innerbore": 10.0,
            "outerbore": 35.0
        }
        
        bitter = Bitter.from_dict(data)
        
        assert bitter.name == "dict_bitter"
        assert bitter.r == [15.0, 30.0]
        assert bitter.z == [5.0, 65.0]
        assert bitter.odd is True
        assert bitter.modelaxi == modelaxi
        assert bitter.coolingslits == [cooling_slit]
        assert bitter.tierod == tierod
        assert bitter.innerbore == 10.0
        assert bitter.outerbore == 35.0

    def test_from_dict_missing_bore_fields(self):
        """Test from_dict with missing innerbore/outerbore fields"""
        modelaxi = ModelAxi(name="minimal_axi", h=10.0, turns=[1.0], pitch=[5.0])
        tierod_shape = Shape2D(name="minimal_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=20.0, n=4, dh=2.0, sh=8.0, shape=tierod_shape)
        
        data = {
            "name": "minimal_bitter",
            "r": [5.0, 15.0],
            "z": [0.0, 30.0],
            "odd": False,
            "modelaxi": modelaxi,
            "coolingslits": [],
            "tierod": tierod
        }
        
        bitter = Bitter.from_dict(data)
        assert bitter.innerbore == 0
        assert bitter.outerbore == 0


class TestBitterComplexCalculations:
    """Test complex calculation methods in Bitter"""
    
    def test_equivalent_eps_edge_cases(self):
        """Test equivalent_eps with edge case values"""
        modelaxi = ModelAxi(name="edge_axi", h=5.0, turns=[1.0], pitch=[3.0])
        tierod_shape = Shape2D(name="edge_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=2, dh=1.0, sh=4.0, shape=tierod_shape)
        
        # Create slit with very small values
        shape = Shape2D(name="small_slit", pts=[[0, 0], [0.1, 0.1]])
        small_slit = CoolingSlit(r=1e-3, angle=0.0, n=1, dh=1e-6, sh=1e-9, shape=shape)
        
        bitter = Bitter(
            name="edge_bitter",
            r=[1e-4, 1e-2],
            z=[0.0, 1e-2],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=[small_slit],
            tierod=tierod,
            innerbore=1e-5,
            outerbore=1e-1
        )
        
        eps = bitter.equivalent_eps(0)
        # eps = n * sh / (2 * pi * r) = 1 * 1e-9 / (2 * pi * 1e-3)
        expected = 1e-9 / (2 * math.pi * 1e-3)
        assert abs(eps - expected) < 1e-15

    def test_get_params_complex_scenario(self):
        """Test get_params with complex bitter configuration"""
        modelaxi = ModelAxi(name="complex_axi", h=25.0, turns=[1.5, 2.0, 1.0], pitch=[4.0, 5.0, 3.0])
        
        # Multiple cooling slits with different properties
        shape1 = Shape2D(name="slit1", pts=[[0, 0], [1, 0], [1, 0.8], [0, 0.8]])
        shape2 = Shape2D(name="slit2", pts=[[0, 0], [1.5, 0], [1.5, 1.2], [0, 1.2]])
        shape3 = Shape2D(name="slit3", pts=[[0, 0], [0.8, 0], [0.8, 0.6], [0, 0.6]])
        
        cooling_slits = [
            CoolingSlit(r=18.0, angle=0.0, n=6, dh=2.0, sh=8.0, shape=shape1),
            CoolingSlit(r=28.0, angle=60.0, n=8, dh=2.5, sh=10.0, shape=shape2),
            CoolingSlit(r=38.0, angle=120.0, n=10, dh=3.0, sh=12.0, shape=shape3)
        ]
        
        tierod_shape = Shape2D(name="complex_tierod", pts=[[0, 0], [3, 3]])
        tierod = Tierod(r=45.0, n=12, dh=5.0, sh=20.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="complex_bitter",
            r=[15.0, 42.0],
            z=[-5.0, 95.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=cooling_slits,
            tierod=tierod,
            innerbore=12.0,
            outerbore=48.0
        )
        
        params = bitter.get_params()
        nslits, Dh, Sh, Zh, filling_factor = params
        
        # Should have 3 cooling slits
        assert nslits == 3
        
        # Should have 5 hydraulic diameter values: [inner, slit1, slit2, slit3, outer]
        assert len(Dh) == 5
        
        # Verify first and last Dh calculations
        expected_dh_first = 2 * (15.0 - 12.0)  # 2 * (r[0] - innerbore)
        assert Dh[0] == expected_dh_first
        
        expected_dh_last = 2 * (48.0 - 42.0)  # 2 * (outerbore - r[1])
        assert Dh[-1] == expected_dh_last
        
        # Should have corresponding Sh values
        assert len(Sh) == 5
        
        # Should have filling factors
        assert len(filling_factor) == 5
        
        # Zh should include all relevant z positions
        assert len(Zh) > 3  # At least start, sections, end


class TestBitterIntegration:
    """Integration tests for Bitter class"""
    
    @patch("python_magnetgeo.hcuts.create_cut")
    def test_create_cut_method(self, mock_create_cut):
        """Test create_cut method"""
        modelaxi = ModelAxi(name="cut_axi", h=10.0, turns=[2.0], pitch=[5.0])
        tierod_shape = Shape2D(name="cut_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=20.0, n=4, dh=2.0, sh=8.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="cut_bitter",
            r=[8.0, 18.0],
            z=[0.0, 40.0],
            odd=False,
            modelaxi=modelaxi,
            coolingslits=[],
            tierod=tierod,
            innerbore=5.0,
            outerbore=22.0
        )
        
        bitter.create_cut("SALOME")
        
        mock_create_cut.assert_called_once_with(bitter, "SALOME", "cut_bitter")

    def test_bitter_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        modelaxi = ModelAxi(name="roundtrip_axi", h=12.0, turns=[1.0, 2.0], pitch=[4.0, 6.0])
        
        shape = Shape2D(name="roundtrip_shape", pts=[[0, 0], [1.5, 0], [1.5, 1], [0, 1]])
        cooling_slit = CoolingSlit(r=22.0, angle=90.0, n=6, dh=2.8, sh=11.2, shape=shape)
        tierod = Tierod(r=32.0, n=8, dh=3.6, sh=14.4, shape=shape)
        
        original_bitter = Bitter(
            name="roundtrip_bitter",
            r=[18.0, 28.0],
            z=[8.0, 68.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=[cooling_slit],
            tierod=tierod,
            innerbore=15.0,
            outerbore=35.0
        )
        
        # Test JSON serialization
        json_str = original_bitter.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Bitter"
        assert parsed_json["name"] == "roundtrip_bitter"
        assert parsed_json["r"] == [18.0, 28.0]
        assert parsed_json["z"] == [8.0, 68.0]
        assert parsed_json["odd"] is True
        assert "modelaxi" in parsed_json
        assert "coolingslits" in parsed_json
        assert "tierod" in parsed_json


class TestBitterPerformance:
    """Performance tests for Bitter class"""
    
    def test_large_cooling_slits_performance(self):
        """Test Bitter performance with many cooling slits"""
        modelaxi = ModelAxi(name="perf_axi", h=30.0, turns=[5.0], pitch=[10.0])
        
        # Create many cooling slits
        shape = Shape2D(name="perf_shape", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])
        cooling_slits = []
        for i in range(50):
            slit = CoolingSlit(
                r=20.0 + i * 2.0,
                angle=i * 7.2,  # 7.2 degrees apart
                n=4 + i % 6,
                dh=2.0 + i * 0.1,
                sh=8.0 + i * 0.4,
                shape=shape
            )
            cooling_slits.append(slit)
        
        tierod = Tierod(r=150.0, n=20, dh=8.0, sh=32.0, shape=shape)
        
        bitter = Bitter(
            name="performance_bitter",
            r=[15.0, 120.0],
            z=[0.0, 200.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=cooling_slits,
            tierod=tierod,
            innerbore=10.0,
            outerbore=125.0
        )
        
        # Test that operations still work with many slits
        channels = bitter.get_channels("perf")
        assert len(channels) == 52  # 50 slits + 2 end channels
        
        lc = bitter.get_lc()
        assert isinstance(lc, float)
        assert lc > 0
        
        # Test get_params with many slits
        params = bitter.get_params()
        nslits, Dh, Sh, Zh, filling_factor = params
        assert nslits == 50
        assert len(Dh) == 52  # nslits + 2
        assert len(Sh) == 52
        assert len(filling_factor) == 52


class TestBitterErrorHandling:
    """Test error handling in Bitter class"""
    
    def test_equivalent_eps_index_error(self):
        """Test equivalent_eps with invalid index"""
        modelaxi = ModelAxi(name="error_axi", h=5.0, turns=[1.0], pitch=[3.0])
        tierod_shape = Shape2D(name="error_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=10.0, n=2, dh=1.0, sh=4.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="error_bitter",
            r=[5.0, 15.0],
            z=[0.0, 20.0],
            odd=False,
            modelaxi=modelaxi,
            coolingslits=[],  # Empty list
            tierod=tierod,
            innerbore=2.0,
            outerbore=18.0
        )
        
        # Should raise IndexError for invalid slit index
        with pytest.raises(IndexError):
            bitter.equivalent_eps(0)  # No cooling slits available

    def test_intersect_edge_cases(self):
        """Test intersect method with edge cases"""
        modelaxi = ModelAxi(name="intersect_axi", h=8.0, turns=[1.0], pitch=[4.0])
        tierod_shape = Shape2D(name="intersect_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(r=15.0, n=3, dh=2.0, sh=6.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="intersect_bitter",
            r=[10.0, 20.0],
            z=[5.0, 25.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=[],
            tierod=tierod,
            innerbore=8.0,
            outerbore=22.0
        )
        
        # Test with identical rectangles (should intersect)
        result = bitter.intersect([10.0, 20.0], [5.0, 25.0])
        assert result is True
        
        # Test with zero-sized rectangles
        result = bitter.intersect([15.0, 15.0], [15.0, 15.0])
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])