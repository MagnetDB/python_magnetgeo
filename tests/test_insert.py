#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Insert class (Updated with factored approach)
"""

import pytest
import json
import yaml
import tempfile
import os
import math
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Insert import Insert, filter
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Groove import Groove
from test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_geometric_data
)


class TestFilterFunction:
    """Test the filter utility function"""
    
    def test_filter_no_duplicates(self):
        """Test filter with no duplicate values"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = filter(data)
        assert result == data
    
    def test_filter_with_duplicates(self):
        """Test filter with exact duplicates"""
        data = [1.0, 2.0, 2.0, 3.0, 4.0, 4.0, 4.0, 5.0]
        result = filter(data)
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert result == expected
    
    def test_filter_with_tolerance(self):
        """Test filter with values within tolerance"""
        data = [1.0, 2.0, 2.000001, 3.0, 4.0, 4.000001]
        result = filter(data, tol=1e-5)
        expected = [1.0, 2.0, 3.0, 4.0]
        assert result == expected
    
    def test_filter_empty_list(self):
        """Test filter with empty list"""
        result = filter([])
        assert result == []
    
    def test_filter_single_element(self):
        """Test filter with single element"""
        result = filter([1.0])
        assert result == [1.0]


class TestInsertInitialization:
    """Test Insert object initialization"""
    
    @pytest.fixture
    def sample_helix(self):
        """Create a sample Helix object for testing"""
        modelaxi = ModelAxi(name="test_axi", h=10.0, turns=[2.0, 3.0], pitch=[5.0, 5.0])
        model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="test_shape", profile="rect")
        
        return Helix(
            name="test_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
    
    @pytest.fixture
    def sample_ring(self):
        """Create a sample Ring object for testing"""
        return Ring(
            name="test_ring",
            r=[5.0, 15.0],
            z=[10.0, 20.0],
            n=6,
            angle=30.0,
            bpside=True,
            fillets=False
        )
    
    @pytest.fixture
    def sample_inner_lead(self):
        """Create a sample InnerCurrentLead object for testing"""
        return InnerCurrentLead(
            name="inner_lead",
            r=[2.0, 8.0],
            z=[0.0, 5.0]
        )
    
    @pytest.fixture
    def sample_outer_lead(self):
        """Create a sample OuterCurrentLead object for testing"""
        return OuterCurrentLead(
            name="outer_lead",
            r=[25.0, 30.0],
            z=[95.0, 105.0]
        )

    def test_insert_minimal_initialization(self):
        """Test Insert initialization with minimal parameters"""
        insert = Insert(name="test_insert")
        
        assert insert.name == "test_insert"
        assert insert.helices == []
        assert insert.rings == []
        assert insert.currentleads == []
        assert insert.hangles == []
        assert insert.rangles == []
        assert insert.innerbore == 0
        assert insert.outerbore == 0

    @patch('python_magnetgeo.utils.load')
    def test_insert_full_initialization(self, mock_load, sample_helix, sample_ring, 
                                       sample_inner_lead, sample_outer_lead):
        """Test Insert initialization with all parameters"""
        # Mock the load function to return our sample objects
        mock_load.side_effect = [
            [sample_helix],
            [sample_ring], 
            [sample_inner_lead, sample_outer_lead]
        ]
        
        insert = Insert(
            name="full_insert",
            helices=["helix_data"],
            rings=["ring_data"],
            currentleads=["lead_data1", "lead_data2"],
            hangles=[0.0, 90.0, 180.0],
            rangles=[45.0, 135.0],
            innerbore=5.0,
            outerbore=50.0
        )
        
        assert insert.name == "full_insert"
        assert len(insert.helices) == 1
        assert len(insert.rings) == 1
        assert insert.hangles == [0.0, 90.0, 180.0]
        assert insert.rangles == [45.0, 135.0]
        assert insert.innerbore == 5.0
        assert insert.outerbore == 50.0

    def test_insert_with_none_values(self):
        """Test Insert initialization with None values for optional parameters"""
        insert = Insert(
            name="none_insert",
            helices=None,
            rings=None,
            currentleads=None,
            hangles=None,
            rangles=None
        )
        
        assert insert.helices == []
        assert insert.rings == []
        assert insert.currentleads == []
        assert insert.hangles == []
        assert insert.rangles == []


class TestInsertMethods:
    """Test Insert class methods"""
    
    @pytest.fixture
    def sample_insert_with_components(self):
        """Create an Insert with sample components"""
        # Create mock helices
        helix1 = Mock(spec=Helix)
        helix1.get_names.return_value = ["H1_Cu0", "H1_Cu1", "H1_Cu2"]
        helix1.r = [10.0, 20.0]
        helix1.z = [0.0, 100.0]
        helix1.modelaxi = Mock()
        helix1.modelaxi.turns = [2.0, 3.0]
        helix1.modelaxi.h = 10.0
        helix1.modelaxi.pitch = [5.0, 5.0]
        helix1.modelaxi.compact.return_value = ([2.0, 3.0], [5.0, 5.0])
        
        helix2 = Mock(spec=Helix)
        helix2.get_names.return_value = ["H2_Cu0", "H2_Cu1"]
        helix2.r = [25.0, 35.0]
        helix2.z = [5.0, 95.0]
        helix2.modelaxi = Mock()
        helix2.modelaxi.turns = [1.5, 2.5]
        helix2.modelaxi.h = 8.0
        helix2.modelaxi.pitch = [4.0, 4.0]
        helix2.modelaxi.compact.return_value = ([1.5, 2.5], [4.0, 4.0])
        
        # Create mock rings
        ring1 = Mock(spec=Ring)
        ring1.z = [10.0, 15.0]
        ring2 = Mock(spec=Ring)
        ring2.z = [85.0, 90.0]
        
        # Create mock current leads
        inner_lead = Mock(spec=InnerCurrentLead)
        outer_lead = Mock(spec=OuterCurrentLead)
        
        insert = Insert(name="test_insert")
        insert.helices = [helix1, helix2]
        insert.rings = [ring1, ring2]
        insert.currentleads = [inner_lead, outer_lead]
        insert.innerbore = 5.0
        insert.outerbore = 40.0
        
        return insert

    def test_get_nhelices(self, sample_insert_with_components):
        """Test get_nhelices method"""
        assert sample_insert_with_components.get_nhelices() == 2

    def test_get_nhelices_empty(self):
        """Test get_nhelices with no helices"""
        insert = Insert(name="empty_insert")
        assert insert.get_nhelices() == 0

    def test_get_names_2d(self, sample_insert_with_components):
        """Test get_names method for 2D case"""
        names = sample_insert_with_components.get_names("test", is2D=True)
        
        expected_names = [
            "H1_Cu0", "H1_Cu1", "H1_Cu2",  # From helix1
            "H2_Cu0", "H2_Cu1",            # From helix2
            "test_R1", "test_R2"           # From rings
        ]
        assert names == expected_names

    def test_get_names_3d(self, sample_insert_with_components):
        """Test get_names method for 3D case"""
        names = sample_insert_with_components.get_names("test", is2D=False)
        
        expected_names = [
            "H1", "H2",        # Helices
            "test_R1", "test_R2",  # Rings
            "iL1", "oL2"       # Current leads (inner and outer)
        ]
        assert names == expected_names

    def test_get_names_no_prefix(self, sample_insert_with_components):
        """Test get_names with no prefix"""
        names = sample_insert_with_components.get_names("", is2D=False)
        
        expected_names = [
            "H1", "H2",    # Helices
            "R1", "R2",    # Rings (no prefix)
            "iL1", "oL2"   # Current leads
        ]
        assert names == expected_names

    def test_get_channels_basic(self, sample_insert_with_components):
        """Test get_channels method basic functionality"""
        channels = sample_insert_with_components.get_channels("test")
        
        # Should have NHelices + 1 channels = 3 channels
        assert len(channels) == 3
        
        # Each channel should be a list of names
        for channel in channels:
            assert isinstance(channel, list)

    def test_get_channels_hide_isolant(self, sample_insert_with_components):
        """Test get_channels with hideIsolant=True"""
        channels = sample_insert_with_components.get_channels("test", hideIsolant=True)
        
        # Check that isolant names are not included
        for channel in channels:
            for name in channel:
                assert "IrExt" not in name
                assert "IrInt" not in name
                assert "kaptonsIrExt" not in name
                assert "kaptonsIrInt" not in name

    def test_get_isolants(self, sample_insert_with_components):
        """Test get_isolants method"""
        isolants = sample_insert_with_components.get_isolants("test")
        # Currently returns empty list according to implementation
        assert isolants == []

    def test_bounding_box_with_helices(self, sample_insert_with_components):
        """Test boundingBox method with helices"""
        rb, zb = sample_insert_with_components.boundingBox()
        
        # Should be the union of all helix bounding boxes
        # helix1: r=[10.0, 20.0], z=[0.0, 100.0]
        # helix2: r=[25.0, 35.0], z=[5.0, 95.0]
        # Expected: r=[10.0, 35.0], z=[0.0, 100.0] + ring adjustments
        assert rb[0] == 10.0  # min r
        assert rb[1] == 35.0  # max r
        
        # Z bounds should be adjusted by ring dimensions
        assert zb[0] <= 0.0   # Should be reduced by ring height
        assert zb[1] >= 100.0 # Should be increased by ring height

    def test_bounding_box_empty_insert(self):
        """Test boundingBox with empty insert"""
        insert = Insert(name="empty_insert")
        rb, zb = insert.boundingBox()
        
        # Should return [0, 0] for both r and z
        assert rb == [0, 0]
        assert zb == [0, 0]

    def test_intersect_collision(self, sample_insert_with_components):
        """Test intersect method with collision"""
        # Test with overlapping rectangle
        r = [15.0, 30.0]  # Overlaps with insert bounds
        z = [10.0, 90.0]
        
        result = sample_insert_with_components.intersect(r, z)
        assert result is True

    def test_intersect_no_collision(self, sample_insert_with_components):
        """Test intersect method without collision"""
        # Test with non-overlapping rectangle
        r = [100.0, 110.0]  # Far from insert bounds
        z = [200.0, 210.0]
        
        result = sample_insert_with_components.intersect(r, z)
        assert result is False

    def test_get_params(self, sample_insert_with_components):
        """Test get_params method"""
        params = sample_insert_with_components.get_params()
        
        # Should return tuple with 9 elements
        assert len(params) == 9
        
        Nhelices, Nrings, NChannels, Nsections, R1, R2, Dh, Sh, Zc = params
        
        assert Nhelices == 2
        assert Nrings == 2
        assert NChannels == 3  # Nhelices + 1
        assert len(R1) == 2
        assert len(R2) == 2
        assert len(Dh) == 3  # NChannels
        assert len(Sh) == 3  # NChannels
        assert len(Zc) == 3  # NChannels


class TestInsertSerialization(BaseSerializationTestMixin):
    """Test Insert serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Insert instance"""
        return Insert(
            name="test_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[0.0, 90.0],
            rangles=[45.0],
            innerbore=5.0,
            outerbore=50.0
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
<!Insert>
name: yaml_insert
helices: []
rings: []
currentleads: []
hangles: [0.0, 180.0]
rangles: [90.0]
innerbore: 10.0
outerbore: 60.0
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_insert",
            "hangles": [0.0, 90.0],
            "rangles": [45.0],
            "innerbore": 5.0,
            "outerbore": 50.0
        }
    
    def get_class_under_test(self):
        """Return Insert class"""
        return Insert

    def test_json_includes_component_lists(self):
        """Test that JSON serialization includes component lists"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "helices" in parsed
        assert "rings" in parsed
        assert "currentleads" in parsed
        assert isinstance(parsed["helices"], list)
        assert isinstance(parsed["rings"], list)
        assert isinstance(parsed["currentleads"], list)

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling - should not raise exception"""
        instance = self.get_sample_instance()
        
        # Should handle exception internally without raising
        instance.dump()  # Should not raise

    def test_write_to_json_method(self):
        """Test write_to_json method"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.write_to_json()
            mock_file.assert_called_once_with("test_insert.json", "w")


class TestInsertYAMLTag(BaseYAMLTagTestMixin):
    """Test Insert YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Insert class"""
        return Insert
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Insert"


class TestInsertFromDict:
    """Test Insert.from_dict class method"""
    
    def test_from_dict_complete_data(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_insert",
            "helices": [],
            "rings": [],
            "currentleads": [],
            "hangles": [0.0, 120.0, 240.0],
            "rangles": [60.0, 180.0, 300.0],
            "innerbore": 8.0,
            "outerbore": 48.0
        }
        
        insert = Insert.from_dict(data)
        
        assert insert.name == "dict_insert"
        assert insert.helices == []
        assert insert.rings == []
        assert insert.currentleads == []
        assert insert.hangles == [0.0, 120.0, 240.0]
        assert insert.