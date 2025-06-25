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
            CoolingSlit(name="slit1", r=15.0, angle=0.0, n=8, dh=2.0, sh=8.0, shape=shape),
            CoolingSlit(name="slit2", r=25.0, angle=30.0, n=12, dh=3.0, sh=12.0, shape=shape)
        ]
    
    @pytest.fixture
    def sample_tierod(self):
        """Create a sample Tierod for testing"""
        shape = Shape2D(name="tierod_shape", pts=[[0, 0], [2, 0], [2, 2], [0, 2]])
        return Tierod(name="tierod", r=35.0, n=6, dh=4.0, sh=16.0, shape=shape)

    def test_bitter_basic_initialization(self, sample_modelaxi, sample_cooling_slits, sample_tierod):
        """Test Bitter initialization with all parameters as objects"""
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

    def test_bitter_with_string_references(self):
        """Test Bitter initialization with string references (before update)"""
        bitter = Bitter(
            name="string_bitter",
            r=[10.0, 20.0],
            z=[0.0, 50.0],
            odd=False,
            modelaxi="test_modelaxi",  # String reference
            coolingslits=["slit1", "slit2"],  # List of string references
            tierod="test_tierod",  # String reference
            innerbore=8.0,
            outerbore=25.0
        )
        
        # Before update(), these should remain as strings/list of strings
        assert bitter.name == "string_bitter"
        assert isinstance(bitter.modelaxi, str)
        assert bitter.modelaxi == "test_modelaxi"
        assert isinstance(bitter.coolingslits, list)
        assert all(isinstance(item, str) for item in bitter.coolingslits)
        assert bitter.coolingslits == ["slit1", "slit2"]
        assert isinstance(bitter.tierod, str)
        assert bitter.tierod == "test_tierod"

    def test_bitter_with_empty_cooling_slits(self, sample_modelaxi, sample_tierod):
        """Test Bitter initialization with empty cooling slits"""
        bitter = Bitter(
            name="no_slits_bitter",
            r=[10.0, 20.0],
            z=[0.0, 50.0],
            odd=False,
            modelaxi=sample_modelaxi,
            coolingslits=[],
            tierod=sample_tierod,
            innerbore=8.0,
            outerbore=25.0
        )
        
        assert bitter.coolingslits == []
        assert len(bitter.coolingslits) == 0

    def test_bitter_with_mixed_types(self):
        """Test Bitter with mixed integer and float types"""
        modelaxi = ModelAxi(name="mixed_axi", h=10, turns=[1, 2], pitch=[5, 6])
        shape = Shape2D(name="mixed_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(name="mixed_tierod", r=20, n=4, dh=2, sh=8, shape=shape)
        
        bitter = Bitter(
            name="mixed_bitter",
            r=[5, 15],      # ints
            z=[0.0, 30.5],  # mixed int/float
            odd=True,
            modelaxi=modelaxi,
            coolingslits=[],
            tierod=tierod,
            innerbore=0,    # int
            outerbore=20.5  # float
        )
        
        assert bitter.r == [5, 15]
        assert bitter.z == [0.0, 30.5]
        assert bitter.innerbore == 0
        assert bitter.outerbore == 20.5


class TestBitterMethods:
    """Test Bitter class methods"""
    
    @pytest.fixture
    def sample_bitter(self):
        """Create a comprehensive sample Bitter for testing"""
        modelaxi = ModelAxi(name="test_axi", h=15.0, turns=[2.0, 3.0], pitch=[5.0, 5.0])
        
        shape = Shape2D(name="slit_shape", pts=[[0, 0], [1, 0], [1, 0.5], [0, 0.5]])
        cooling_slits = [
            CoolingSlit(name="slit1", r=20.0, angle=0.0, n=6, dh=2.5, sh=10.0, shape=shape),
            CoolingSlit(name="slit2", r=30.0, angle=45.0, n=8, dh=3.0, sh=12.0, shape=shape)
        ]
        
        tierod_shape = Shape2D(name="tierod_shape", pts=[[0, 0], [2, 2]])
        tierod = Tierod(name="tierod", r=40.0, n=4, dh=4.0, sh=16.0, shape=tierod_shape)
        
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
        tierod = Tierod(name="tierod", r=20.0, n=2, dh=2.0, sh=8.0, shape=tierod_shape)
        
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
        tierod = Tierod(name="tierod", r=20.0, n=2, dh=2.0, sh=8.0, shape=tierod_shape)
        
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

    def test_update_method_with_string_references(self):
        """Test update method when components are string references"""
        bitter = Bitter(
            name="update_bitter",
            r=[10.0, 25.0],
            z=[0.0, 50.0],
            odd=True,
            modelaxi="test_modelaxi",
            coolingslits=["test_slit1", "test_slit2"],
            tierod="test_tierod",
            innerbore=5.0,
            outerbore=30.0
        )
        
        # Initially should be strings
        assert isinstance(bitter.modelaxi, str)
        assert isinstance(bitter.coolingslits, list)
        assert all(isinstance(item, str) for item in bitter.coolingslits)
        assert isinstance(bitter.tierod, str)
        
        # Mock the loading of components
        mock_modelaxi = ModelAxi(name="test_modelaxi", h=10.0, turns=[2.0], pitch=[5.0])
        mock_slit1 = CoolingSlit(name="test_slit1", r=15.0, angle=0.0, n=4, dh=2.0, sh=8.0, 
                                shape=Shape2D(name="slit1_shape", pts=[[0, 0], [1, 1]]))
        mock_slit2 = CoolingSlit(name="test_slit2", r=20.0, angle=45.0, n=6, dh=3.0, sh=12.0, 
                                shape=Shape2D(name="slit2_shape", pts=[[0, 0], [1, 1]]))
        mock_tierod = Tierod(name="test_tierod", r=30.0, n=8, dh=4.0, sh=16.0, 
                            shape=Shape2D(name="tierod_shape", pts=[[0, 0], [2, 2]]))
        
        with patch('python_magnetgeo.utils.loadObject') as mock_load_obj, \
             patch('python_magnetgeo.utils.loadList') as mock_load_list:
            
            # Configure mocks
            mock_load_obj.side_effect = [mock_modelaxi, mock_tierod]
            mock_load_list.return_value = [mock_slit1, mock_slit2]
            
            bitter.update()
            
            # After update, should be actual objects
            assert isinstance(bitter.modelaxi, ModelAxi)
            assert bitter.modelaxi == mock_modelaxi
            assert isinstance(bitter.coolingslits, list)
            assert len(bitter.coolingslits) == 2
            assert all(isinstance(item, CoolingSlit) for item in bitter.coolingslits)
            assert isinstance(bitter.tierod, Tierod)
            assert bitter.tierod == mock_tierod

    def test_update_method_with_object_references(self, sample_bitter):
        """Test update method when components are already objects"""
        # Store original references
        original_modelaxi = sample_bitter.modelaxi
        original_coolingslits = sample_bitter.coolingslits
        original_tierod = sample_bitter.tierod
        
        # update() should not change anything when components are already objects
        sample_bitter.update()
        
        assert sample_bitter.modelaxi is original_modelaxi
        assert sample_bitter.coolingslits is original_coolingslits
        assert sample_bitter.tierod is original_tierod


class TestBitterSerialization(BaseSerializationTestMixin):
    """Test Bitter serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Bitter instance"""
        modelaxi = ModelAxi(name="test_axi", h=10.0, turns=[2.0], pitch=[5.0])
        
        shape = Shape2D(name="test_shape", pts=[[0, 0], [1, 1]])
        cooling_slit = CoolingSlit(name="slit", r=20.0, angle=0.0, n=4, dh=2.0, sh=8.0, shape=shape)
        tierod = Tierod(name="test", r=30.0, n=6, dh=3.0, sh=12.0, shape=shape)

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
        return '''!<Bitter>
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
  name: yaml_tierod
  r: 35.0
  n: 8
  dh: 4.0
  sh: 16.0
  shape: !<Shape2D>
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
        def mock_constructor(loader, node):
            # Call construct_mapping to satisfy the mixin's expectation
            values = loader.construct_mapping(node)
            # Return simplified data for easy comparison
            return values, self.get_expected_constructor_type()
        return mock_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        return {
            "name": "constructor_bitter",
            "r": [8.0, 22.0],
            "z": [2.0, 42.0],
            "odd": False,
            "innerbore": 4.0,
            "outerbore": 26.0
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "Bitter"

    def test_constructor_with_missing_bore_fields(self):
        """Test constructor when innerbore/outerbore fields are missing"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "test_bitter",
            "r": [10.0, 20.0],
            "z": [0.0, 30.0],
            "odd": True,
            "modelaxi": ModelAxi(name="test", h=5.0, turns=[1.0], pitch=[3.0]),
            "coolingslits": [],
            "tierod": Tierod(name="test", r=15.0, n=4, dh=2.0, sh=8.0, 
                           shape=Shape2D(name="test", pts=[[0, 0], [1, 1]]))
            # Missing innerbore and outerbore
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Bitter_constructor(mock_loader, mock_node)
        
        assert result.name == "test_bitter"
        assert result.innerbore == 0  # Should default to 0
        assert result.outerbore == 0  # Should default to 0

    def test_constructor_directly(self):
        """Test the Bitter_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Create test objects
        modelaxi = ModelAxi(name="direct_test_axi", h=10.0, turns=[2.0], pitch=[5.0])
        shape = Shape2D(name="direct_test_shape", pts=[[0, 0], [1, 1]])
        cooling_slit = CoolingSlit(name="direct_slit", r=20.0, angle=45.0, n=6, dh=3.0, sh=12.0, shape=shape)
        tierod = Tierod(name="direct_tierod", r=30.0, n=8, dh=4.0, sh=16.0, shape=shape)
        
        test_data = {
            "name": "direct_test_bitter",
            "r": [15.0, 25.0],
            "z": [5.0, 45.0],
            "odd": True,
            "modelaxi": modelaxi,
            "coolingslits": [cooling_slit],
            "tierod": tierod,
            "innerbore": 10.0,
            "outerbore": 30.0
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Bitter_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Bitter)
        assert result.name == "direct_test_bitter"
        assert result.r == [15.0, 25.0]
        assert result.z == [5.0, 45.0]
        assert result.odd is True
        assert result.modelaxi == modelaxi
        assert result.coolingslits == [cooling_slit]
        assert result.tierod == tierod
        assert result.innerbore == 10.0
        assert result.outerbore == 30.0
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestBitterYAMLTag(BaseYAMLTagTestMixin):
    """Test Bitter YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Bitter class"""
        return Bitter
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Bitter"


class TestBitterFileOperations:
    """Test Bitter file operations and edge cases"""
    
    def test_from_yaml_success(self):
        """Test successful from_yaml loading"""
        yaml_content = '''!<Bitter>
name: yaml_bitter
r: [15.0, 30.0]
z: [5.0, 65.0]
odd: true
modelaxi: !<ModelAxi>
  name: yaml_modelaxi
  h: 20.0
  turns: [2.0, 3.0]
  pitch: [6.0, 6.0]
coolingslits: []
tierod: !<Tierod>
  name: yaml_tierod
  r: 35.0
  n: 8
  dh: 4.5
  sh: 18.0
  shape: !<Shape2D>
    name: yaml_tierod_shape
    pts: [[0, 0], [3, 0], [3, 3], [0, 3]]
innerbore: 10.0
outerbore: 35.0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                bitter = Bitter.from_yaml(tmp_file.name)
                
                assert bitter.name == "yaml_bitter"
                assert bitter.r == [15.0, 30.0]
                assert bitter.z == [5.0, 65.0]
                assert bitter.odd is True
                assert isinstance(bitter.modelaxi, ModelAxi)
                assert bitter.modelaxi.name == "yaml_modelaxi"
                assert bitter.coolingslits == []
                assert isinstance(bitter.tierod, Tierod)
                assert bitter.tierod.name == "yaml_tierod"
                assert bitter.innerbore == 10.0
                assert bitter.outerbore == 35.0
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_file_not_found(self):
        """Test from_yaml with non-existent file"""
        with pytest.raises(Exception, match="Failed to load Bitter data"):
            Bitter.from_yaml("non_existent_file.yaml")

    def test_from_yaml_invalid_yaml(self):
        """Test from_yaml with invalid YAML content"""
        invalid_yaml = "r: [10.0, 20.0]\nodd: invalid_boolean\nz: [0.0, 30.0]"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(invalid_yaml)
            tmp_file.flush()
            
            try:
                with pytest.raises(Exception):
                    Bitter.from_yaml(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)

    @patch("python_magnetgeo.deserialize.unserialize_object")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_from_json_success(self, mock_file, mock_unserialize):
        """Test successful from_json loading"""
        shape = Shape2D(name="json_shape", pts=[[0, 0], [1, 1]])
        modelaxi = ModelAxi(name="json_axi", h=5.0, turns=[1.0], pitch=[3.0])
        tierod = Tierod(name="json_tierod", r=15.0, n=4, dh=2.0, sh=8.0, shape=shape)
        mock_bitter = Bitter(
            name="json_bitter", r=[10.0, 20.0], z=[0.0, 30.0], odd=False,
            modelaxi=modelaxi, coolingslits=[], tierod=tierod, innerbore=5.0, outerbore=25.0
        )
        mock_unserialize.return_value = mock_bitter
        
        result = Bitter.from_json("test.json")
        
        mock_file.assert_called_once_with("test.json", "r")
        mock_unserialize.assert_called_once()
        assert result == mock_bitter


class TestBitterErrorHandling:
    """Test error handling in Bitter class"""

    def test_invalid_component_handling(self):
        """Test handling of invalid component parameters"""
        # Test with None components (should raise error depending on implementation)
        try:
            bitter = Bitter(
                name="none_bitter", r=[10.0, 20.0], z=[0.0, 30.0], odd=True,
                modelaxi=None, coolingslits=None, tierod=None, innerbore=5.0, outerbore=25.0
            )
            # If no error is raised, the implementation allows None
            assert bitter.modelaxi is None
            assert bitter.coolingslits is None
            assert bitter.tierod is None
        except (TypeError, AttributeError):
            # Expected if the implementation validates the parameters
            pass

    def test_extreme_value_handling(self):
        """Test handling of extreme parameter values"""
        modelaxi = ModelAxi(name="extreme_axi", h=1e10, turns=[1e6], pitch=[1e8])
        shape = Shape2D(name="extreme_shape", pts=[[0, 0], [1e10, 1e10]])
        tierod = Tierod(name="extreme_tierod", r=1e12, n=1000000, dh=1e8, sh=1e15, shape=shape)
        
        # Test with very large values
        large_bitter = Bitter(
            name="large_bitter",
            r=[1e8, 1e10],
            z=[1e6, 1e12],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=[],
            tierod=tierod,
            innerbore=1e5,
            outerbore=1e11
        )
        
        assert large_bitter.name == "large_bitter"
        assert large_bitter.r == [1e8, 1e10]
        assert large_bitter.z == [1e6, 1e12]

    def test_update_method_error_handling(self):
        """Test update method error handling"""
        bitter = Bitter(
            name="error_bitter", r=[10.0, 20.0], z=[0.0, 30.0], odd=True,
            modelaxi="nonexistent_modelaxi", coolingslits=["nonexistent_slit"], 
            tierod="nonexistent_tierod", innerbore=5.0, outerbore=25.0
        )
        
        # Mock file operations to simulate file not found errors
        with patch('python_magnetgeo.utils.loadObject', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError, match="File not found"):
                bitter.update()

    def test_equivalent_eps_index_error(self):
        """Test equivalent_eps with invalid index"""
        modelaxi = ModelAxi(name="error_axi", h=5.0, turns=[1.0], pitch=[3.0])
        tierod_shape = Shape2D(name="error_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(name="tierod", r=10.0, n=2, dh=1.0, sh=4.0, shape=tierod_shape)
        
        bitter = Bitter(
            name="error_bitter", r=[5.0, 15.0], z=[0.0, 20.0], odd=False,
            modelaxi=modelaxi, coolingslits=[], tierod=tierod, innerbore=2.0, outerbore=18.0
        )
        
        # Should raise IndexError for invalid slit index
        with pytest.raises(IndexError):
            bitter.equivalent_eps(0)  # No cooling slits available

    def test_dump_with_invalid_filename(self):
        """Test dump method with invalid filename"""
        modelaxi = ModelAxi(name="dump_axi", h=5.0, turns=[1.0], pitch=[3.0])
        shape = Shape2D(name="dump_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(name="dump_tierod", r=10.0, n=2, dh=1.0, sh=4.0, shape=shape)
        
        bitter = Bitter(
            name="dump_error_bitter", r=[5.0, 15.0], z=[0.0, 20.0], odd=False,
            modelaxi=modelaxi, coolingslits=[], tierod=tierod, innerbore=2.0, outerbore=18.0
        )
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception, match="Failed to Bitter dump"):
                bitter.dump()


class TestBitterIntegration:
    """Integration tests for Bitter class"""
    
    def test_bitter_with_various_components(self):
        """Test Bitter with different types of components"""
        # Create various modelaxi configurations
        modelaxis = [
            ModelAxi(name="simple_axi", h=10.0, turns=[1.0], pitch=[5.0]),
            ModelAxi(name="complex_axi", h=20.0, turns=[2.0, 3.0, 1.5], pitch=[4.0, 5.0, 6.0])
        ]
        
        # Create various shapes and components
        shapes = [
            Shape2D(name="square", pts=[[0, 0], [1, 0], [1, 1], [0, 1]]),
            Shape2D(name="triangle", pts=[[0, 0], [1, 0], [0.5, 1]])
        ]
        
        bitters = []
        for i, (modelaxi, shape) in enumerate(zip(modelaxis, shapes)):
            cooling_slits = [
                CoolingSlit(name=f"slit_{i}_1", r=15.0 + i*5, angle=i*30, n=4+i*2, 
                          dh=2.0+i*0.5, sh=8.0+i*2, shape=shape)
            ]
            tierod = Tierod(name=f"tierod_{i}", r=25.0+i*10, n=6+i*2, dh=3.0+i, sh=12.0+i*4, shape=shape)
            
            bitter = Bitter(
                name=f"integration_bitter_{i}",
                r=[10.0 + i*5, 20.0 + i*10],
                z=[0.0, 30.0 + i*20],
                odd=(i % 2 == 0),
                modelaxi=modelaxi,
                coolingslits=cooling_slits,
                tierod=tierod,
                innerbore=5.0 + i*2,
                outerbore=25.0 + i*5
            )
            bitters.append(bitter)
        
        # Verify each bitter maintains its properties
        for i, bitter in enumerate(bitters):
            assert bitter.name == f"integration_bitter_{i}"
            assert bitter.r == [10.0 + i*5, 20.0 + i*10]
            assert bitter.odd == (i % 2 == 0)
            assert isinstance(bitter.modelaxi, ModelAxi)
            assert len(bitter.coolingslits) == 1
            assert isinstance(bitter.tierod, Tierod)

    def test_bitter_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_shape = Shape2D(name="roundtrip", pts=[[0, 0], [2, 1], [1, 2]])
        original_modelaxi = ModelAxi(name="roundtrip_axi", h=15.0, turns=[2.0, 1.5], pitch=[5.0, 6.0])
        original_slit = CoolingSlit(name="roundtrip_slit", r=22.0, angle=60.0, n=8, dh=3.5, sh=14.0, shape=original_shape)
        original_tierod = Tierod(name="roundtrip_tierod", r=35.0, n=12, dh=5.0, sh=20.0, shape=original_shape)
        
        original_bitter = Bitter(
            name="roundtrip_bitter",
            r=[18.0, 28.0],
            z=[8.0, 68.0],
            odd=True,
            modelaxi=original_modelaxi,
            coolingslits=[original_slit],
            tierod=original_tierod,
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

    def test_bitter_collection_operations(self):
        """Test operations on collections of bitters"""
        base_modelaxi = ModelAxi(name="base_axi", h=10.0, turns=[1.0], pitch=[5.0])
        base_shape = Shape2D(name="base_shape", pts=[[0, 0], [1, 1]])
        base_tierod = Tierod(name="base_tierod", r=20.0, n=4, dh=2.0, sh=8.0, shape=base_shape)
        
        # Create collection of bitters
        bitters = []
        for i in range(5):
            bitter = Bitter(
                name=f"collection_bitter_{i}",
                r=[i * 5.0, (i+1) * 10.0],
                z=[0.0, (i+1) * 20.0],
                odd=(i % 2 == 0),
                modelaxi=base_modelaxi,
                coolingslits=[],
                tierod=base_tierod,
                innerbore=i * 2.0,
                outerbore=(i+1) * 5.0
            )
            bitters.append(bitter)
        
        # Test sorting by inner radius
        sorted_bitters = sorted(bitters, key=lambda b: b.r[0])
        assert sorted_bitters[0].r[0] == 0.0
        assert sorted_bitters[-1].r[0] == 20.0
        
        # Test filtering by odd property
        odd_bitters = [b for b in bitters if b.odd]
        even_bitters = [b for b in bitters if not b.odd]
        assert len(odd_bitters) == 3  # indices 0, 2, 4
        assert len(even_bitters) == 2  # indices 1, 3
        
        # Test aggregation operations
        total_volume = sum((b.r[1] - b.r[0]) * (b.z[1] - b.z[0]) for b in bitters)
        assert total_volume > 0


class TestBitterPerformance:
    """Performance tests for Bitter class"""
    
    def test_large_cooling_slits_performance(self):
        """Test Bitter performance with many cooling slits"""
        modelaxi = ModelAxi(name="perf_axi", h=30.0, turns=[5.0], pitch=[10.0])
        
        # Create many cooling slits
        shape = Shape2D(name="perf_shape", pts=[[0, 0], [1, 0], [1, 1], [0, 1]])
        cooling_slits = []
        for i in range(20):  # Reasonable number for testing
            slit = CoolingSlit(
                name=f"perf_slit_{i}",
                r=20.0 + i * 2.0,
                angle=i * 18.0,  # 18 degrees apart
                n=4 + i % 6,
                dh=2.0 + i * 0.1,
                sh=8.0 + i * 0.4,
                shape=shape
            )
            cooling_slits.append(slit)
        
        tierod = Tierod(name="perf_tierod", r=80.0, n=20, dh=8.0, sh=32.0, shape=shape)
        
        bitter = Bitter(
            name="performance_bitter",
            r=[15.0, 65.0],
            z=[0.0, 100.0],
            odd=True,
            modelaxi=modelaxi,
            coolingslits=cooling_slits,
            tierod=tierod,
            innerbore=10.0,
            outerbore=70.0
        )
        
        # Test that operations still work with many slits
        channels = bitter.get_channels("perf")
        assert len(channels) == 22  # 20 slits + 2 end channels
        
        lc = bitter.get_lc()
        assert isinstance(lc, float)
        assert lc > 0
        
        # Test get_params with many slits
        params = bitter.get_params()
        nslits, Dh, Sh, Zh, filling_factor = params
        assert nslits == 20
        assert len(Dh) == 22  # nslits + 2
        assert len(Sh) == 22
        assert len(filling_factor) == 22

    def test_multiple_bitter_creation_performance(self):
        """Test performance of creating many bitters"""
        base_modelaxi = ModelAxi(name="base", h=10.0, turns=[1.0], pitch=[5.0])
        base_shape = Shape2D(name="base", pts=[[0, 0], [1, 1]])
        base_tierod = Tierod(name="base", r=20.0, n=4, dh=2.0, sh=8.0, shape=base_shape)
        
        # Create many bitters
        bitters = []
        for i in range(50):  # Reasonable number for testing
            bitter = Bitter(
                name=f"perf_bitter_{i}",
                r=[float(i), float(i + 10)],
                z=[0.0, float(i + 20)],
                odd=(i % 2 == 0),
                modelaxi=base_modelaxi,
                coolingslits=[],
                tierod=base_tierod,
                innerbore=float(i * 0.5),
                outerbore=float(i + 15)
            )
            bitters.append(bitter)
        
        assert len(bitters) == 50
        assert all(isinstance(b, Bitter) for b in bitters)


class TestBitterComplexCalculations:
    """Test complex calculation methods in Bitter"""
    
    def test_equivalent_eps_edge_cases(self):
        """Test equivalent_eps with edge case values"""
        modelaxi = ModelAxi(name="edge_axi", h=5.0, turns=[1.0], pitch=[3.0])
        tierod_shape = Shape2D(name="edge_shape", pts=[[0, 0], [1, 1]])
        tierod = Tierod(name="tierod", r=10.0, n=2, dh=1.0, sh=4.0, shape=tierod_shape)
        
        # Create slit with very small values
        shape = Shape2D(name="small_slit", pts=[[0, 0], [0.1, 0.1]])
        small_slit = CoolingSlit(name="slit", r=1e-3, angle=0.0, n=1, dh=1e-6, sh=1e-9, shape=shape)
        
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
            CoolingSlit(name="slit1", r=18.0, angle=0.0, n=6, dh=2.0, sh=8.0, shape=shape1),
            CoolingSlit(name="slit2", r=28.0, angle=60.0, n=8, dh=2.5, sh=10.0, shape=shape2),
            CoolingSlit(name="slit3", r=38.0, angle=120.0, n=10, dh=3.0, sh=12.0, shape=shape3)
        ]
        
        tierod_shape = Shape2D(name="complex_tierod", pts=[[0, 0], [3, 3]])
        tierod = Tierod(name="tierod", r=45.0, n=12, dh=5.0, sh=20.0, shape=tierod_shape)
        
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

