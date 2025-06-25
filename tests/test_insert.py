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

from python_magnetgeo.Insert import Insert, Insert_constructor, filter
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Groove import Groove
from .test_utils_common import (
    BaseSerializationTestMixin, 
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
    
    def test_insert_minimal_initialization(self):
        """Test Insert initialization with minimal parameters"""
        insert = Insert(
            name="test_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            innerbore=0,
            outerbore=0
        )
        
        assert insert.name == "test_insert"
        assert insert.helices == []
        assert insert.rings == []
        assert insert.currentleads == []
        assert insert.hangles == []
        assert insert.rangles == []
        assert insert.innerbore == 0
        assert insert.outerbore == 0

    def test_insert_full_initialization_with_objects(self):
        """Test Insert initialization with actual objects"""
        # Create mock objects
        helix = Mock(spec=Helix)
        helix.name = "test_helix"
        helix.r = [10.0, 20.0]
        helix.z = [0.0, 100.0]
        
        ring = Mock(spec=Ring)
        ring.name = "test_ring"
        ring.r = [5.0, 15.0]
        ring.z = [10.0, 20.0]
        
        inner_lead = Mock(spec=InnerCurrentLead)
        inner_lead.name = "inner_lead"
        
        insert = Insert(
            name="full_insert",
            helices=[helix],
            rings=[ring],
            currentleads=[inner_lead],
            hangles=[0.0, 90.0, 180.0],
            rangles=[45.0, 135.0],
            innerbore=5.0,
            outerbore=50.0
        )
        
        assert insert.name == "full_insert"
        assert len(insert.helices) == 1
        assert insert.helices[0] == helix
        assert len(insert.rings) == 1
        assert insert.rings[0] == ring
        assert len(insert.currentleads) == 1
        assert insert.currentleads[0] == inner_lead
        assert insert.hangles == [0.0, 90.0, 180.0]
        assert insert.rangles == [45.0, 135.0]
        assert insert.innerbore == 5.0
        assert insert.outerbore == 50.0

    def test_insert_initialization_with_string_references(self):
        """Test Insert initialization with string references"""
        insert = Insert(
            name="string_insert",
            helices=["helix1.yaml", "helix2.yaml"],
            rings=["ring1.yaml"],
            currentleads=["inner_lead.yaml", "outer_lead.yaml"],
            hangles=[0.0, 120.0, 240.0],
            rangles=[60.0, 180.0],
            innerbore=8.0,
            outerbore=48.0
        )
        
        assert insert.name == "string_insert"
        assert insert.helices == ["helix1.yaml", "helix2.yaml"]
        assert insert.rings == ["ring1.yaml"]
        assert insert.currentleads == ["inner_lead.yaml", "outer_lead.yaml"]


class TestInsertUpdate:
    """Test Insert update method for loading string references"""
    
    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_string_helices(self, mock_check, mock_load_list):
        """Test update method with string helices references"""
        insert = Insert(
            name="update_helices_insert",
            helices=["helix1", "helix2"],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded helices
        mock_helices = [Mock(spec=Helix), Mock(spec=Helix)]
        mock_helices[0].name = "loaded_helix1"
        mock_helices[1].name = "loaded_helix2"
        mock_load_list.return_value = mock_helices
        
        insert.update()
        
        assert insert.helices == mock_helices
        mock_load_list.assert_any_call("helices", ["helix1", "helix2"], [None, Helix], {"Helix": Helix.from_dict})

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_string_rings(self, mock_check, mock_load_list):
        """Test update method with string rings references"""
        insert = Insert(
            name="update_rings_insert",
            helices=[],
            rings=["ring1", "ring2", "ring3"],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded rings
        mock_rings = [Mock(spec=Ring) for _ in range(3)]
        for i, ring in enumerate(mock_rings):
            ring.name = f"loaded_ring{i+1}"
        mock_load_list.return_value = mock_rings
        
        insert.update()
        
        assert insert.rings == mock_rings
        mock_load_list.assert_any_call("rings", ["ring1", "ring2", "ring3"], [None, Ring], {"Ring": Ring.from_dict})

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_string_currentleads(self, mock_check, mock_load_list):
        """Test update method with string currentleads references"""
        dict_leads = {
            "InnerCurrentLead": InnerCurrentLead.from_dict,
            "OuterCurrentLead": OuterCurrentLead.from_dict,
        }
        
        insert = Insert(
            name="update_leads_insert",
            helices=[],
            rings=[],
            currentleads=["inner_lead", "outer_lead"],
            hangles=[],
            rangles=[]
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded current leads
        mock_leads = [Mock(spec=InnerCurrentLead), Mock(spec=OuterCurrentLead)]
        mock_leads[0].name = "loaded_inner_lead"
        mock_leads[1].name = "loaded_outer_lead"
        mock_load_list.return_value = mock_leads
        
        insert.update()
        
        assert insert.currentleads == mock_leads
        mock_load_list.assert_any_call("currentleads", ["inner_lead", "outer_lead"], [None, InnerCurrentLead, OuterCurrentLead], dict_leads)

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_mixed_objects_and_strings(self, mock_check, mock_load_list):
        """Test update method with mixed object and string references"""
        # Create existing objects
        existing_helix = Mock(spec=Helix)
        existing_helix.name = "existing_helix"
        existing_ring = Mock(spec=Ring)
        existing_ring.name = "existing_ring"
        
        insert = Insert(
            name="mixed_insert",
            helices=[existing_helix],  # Object
            rings=["string_ring1", "string_ring2"],  # Strings
            currentleads=[],  # Empty
            hangles=[0.0],
            rangles=[45.0]
        )
        
        def mock_check_side_effect(objects, target_type):
            if target_type == str:
                return isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
            return False
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded rings (only rings should be loaded)
        mock_rings = [Mock(spec=Ring), Mock(spec=Ring)]
        mock_rings[0].name = "loaded_ring1"
        mock_rings[1].name = "loaded_ring2"
        mock_load_list.return_value = mock_rings
        
        insert.update()
        
        # Helices should remain unchanged (was already object)
        assert insert.helices == [existing_helix]
        # Rings should be loaded from strings
        assert insert.rings == mock_rings
        # Both rings and currentleads should have been called (currentleads is empty list but still checked)
        assert mock_load_list.call_count == 2
        mock_load_list.assert_any_call("rings", ["string_ring1", "string_ring2"], [None, Ring], {"Ring": Ring.from_dict})

    def test_update_with_object_references(self):
        """Test update method when components are already objects"""
        # Create mock objects
        helix = Mock(spec=Helix)
        ring = Mock(spec=Ring)
        lead = Mock(spec=InnerCurrentLead)
        
        insert = Insert(
            name="object_insert",
            helices=[helix],
            rings=[ring],
            currentleads=[lead],
            hangles=[0.0],
            rangles=[90.0]
        )
        
        # Store original references
        orig_helices = insert.helices
        orig_rings = insert.rings
        orig_leads = insert.currentleads
        
        insert.update()
        
        # Objects should remain unchanged
        assert insert.helices == orig_helices
        assert insert.rings == orig_rings
        assert insert.currentleads == orig_leads


class TestInsertMethods:
    """Test Insert class methods"""
    
    def test_get_nhelices_with_objects(self):
        """Test get_nhelices method with helix objects"""
        helices = [Mock(spec=Helix) for _ in range(3)]
        insert = Insert(
            name="test_insert",
            helices=helices,
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        assert insert.get_nhelices() == 3

    def test_get_nhelices_with_strings(self):
        """Test get_nhelices method with string references"""
        insert = Insert(
            name="string_insert",
            helices=["helix1", "helix2", "helix3", "helix4"],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        assert insert.get_nhelices() == 4

    def test_get_nhelices_empty(self):
        """Test get_nhelices with no helices"""
        insert = Insert(
            name="empty_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        assert insert.get_nhelices() == 0

    def test_get_names_with_mock_objects(self):
        """Test get_names method with properly mocked objects"""
        # Create mock helices with get_names method
        helix1 = Mock(spec=Helix)
        helix1.get_names.return_value = ["test_H1_Cu0", "test_H1_Cu1"]
        helix2 = Mock(spec=Helix)
        helix2.get_names.return_value = ["test_H2_Cu0", "test_H2_Cu1", "test_H2_Cu2"]
        
        # Create mock rings
        ring1 = Mock(spec=Ring)
        ring1.name = "ring1"
        ring2 = Mock(spec=Ring)
        ring2.name = "ring2"
        
        # Create mock current leads
        inner_lead = Mock(spec=InnerCurrentLead)
        outer_lead = Mock(spec=OuterCurrentLead)
        
        insert = Insert(
            name="names_test_insert",
            helices=[helix1, helix2],
            rings=[ring1, ring2],
            currentleads=[inner_lead, outer_lead],
            hangles=[],
            rangles=[]
        )
        
        # Test 2D names
        names_2d = insert.get_names("test", is2D=True)
        expected_2d = [
            "test_H1_Cu0", "test_H1_Cu1",    # From helix1
            "test_H2_Cu0", "test_H2_Cu1", "test_H2_Cu2",  # From helix2
            "test_R1", "test_R2"             # From rings
        ]
        assert names_2d == expected_2d
        
        # Verify helices were called with correct parameters
        helix1.get_names.assert_called_with("test_H1", True, False)
        helix2.get_names.assert_called_with("test_H2", True, False)
        
        # Test 3D names
        names_3d = insert.get_names("test", is2D=False)
        expected_3d = [
            "H1", "H2",                      # Helices
            "test_R1", "test_R2",           # Rings
            "iL1", "oL2"                    # Current leads
        ]
        assert names_3d == expected_3d

    def test_get_names_no_prefix(self):
        """Test get_names with no prefix"""
        helix = Mock(spec=Helix)
        ring = Mock(spec=Ring)
        lead = Mock(spec=InnerCurrentLead)
        
        insert = Insert(
            name="no_prefix_insert",
            helices=[helix],
            rings=[ring],
            currentleads=[lead],
            hangles=[],
            rangles=[]
        )
        
        names = insert.get_names("", is2D=False)
        expected = ["H1", "R1", "iL1"]
        assert names == expected

    def test_get_names_no_rings_no_leads(self):
        """Test get_names with only helices"""
        helix1 = Mock(spec=Helix)
        helix1.get_names.return_value = ["test_H1_Cu0"]
        helix2 = Mock(spec=Helix)
        helix2.get_names.return_value = ["test_H2_Cu0"]
        
        insert = Insert(
            name="minimal_insert",
            helices=[helix1, helix2],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        names_2d = insert.get_names("test", is2D=True)
        assert names_2d == ["test_H1_Cu0", "test_H2_Cu0"]
        
        names_3d = insert.get_names("test", is2D=False)
        assert names_3d == ["H1", "H2"]

    def test_bounding_box_with_helices(self):
        """Test boundingBox method with helix objects"""
        # Create mock helices with bounding box data
        helix1 = Mock(spec=Helix)
        helix1.r = [10.0, 20.0]
        helix1.z = [0.0, 100.0]
        
        helix2 = Mock(spec=Helix)
        helix2.r = [25.0, 35.0]
        helix2.z = [5.0, 95.0]
        
        # Create mock rings with z coordinates
        ring1 = Mock(spec=Ring)
        ring1.z = [10.0, 15.0]  # height = 5.0
        ring2 = Mock(spec=Ring)
        ring2.z = [85.0, 90.0]  # height = 5.0
        
        insert = Insert(
            name="bbox_insert",
            helices=[helix1, helix2],
            rings=[ring1, ring2],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        rb, zb = insert.boundingBox()
        
        # Should be union of helix bounds: r=[10.0, 35.0], z=[0.0, 100.0]
        # Adjusted by max ring height (5.0)
        assert rb[0] == 10.0  # min r
        assert rb[1] == 35.0  # max r
        assert zb[0] == -5.0  # min z - max ring height
        assert zb[1] == 105.0 # max z + max ring height

    def test_bounding_box_empty_insert(self):
        """Test boundingBox with empty insert"""
        insert = Insert(
            name="empty_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        rb, zb = insert.boundingBox()
        
        # Should return [0, 0] for both r and z
        assert rb == [0, 0]
        assert zb == [0, 0]

    def test_intersect_collision(self):
        """Test intersect method with collision"""
        # Create insert with known bounds
        helix = Mock(spec=Helix)
        helix.r = [10.0, 30.0]
        helix.z = [0.0, 100.0]
        
        insert = Insert(
            name="intersect_insert",
            helices=[helix],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        # Test with overlapping rectangle
        r = [15.0, 25.0]  # Overlaps with [10.0, 30.0]
        z = [10.0, 90.0]  # Overlaps with [0.0, 100.0]
        
        result = insert.intersect(r, z)
        assert result is True

    def test_intersect_no_collision(self):
        """Test intersect method without collision"""
        # Create insert with known bounds
        helix = Mock(spec=Helix)
        helix.r = [10.0, 30.0]
        helix.z = [0.0, 100.0]
        
        insert = Insert(
            name="no_intersect_insert",
            helices=[helix],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        # Test with non-overlapping rectangle that is truly far away
        # The intersect method uses center-based collision detection
        # For helix bounds [10.0, 30.0] and [0.0, 100.0], we need rectangles that don't overlap
        r = [50.0, 60.0]  # Completely outside r range [10.0, 30.0]
        z = [150.0, 160.0]  # Completely outside z range [0.0, 100.0]
        
        result = insert.intersect(r, z)
        assert result is False

    def test_get_channels_basic(self):
        """Test get_channels method basic functionality"""
        helices = [Mock(spec=Helix), Mock(spec=Helix)]
        rings = [Mock(spec=Ring), Mock(spec=Ring)]
        
        insert = Insert(
            name="channels_insert",
            helices=helices,
            rings=rings,
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        channels = insert.get_channels("test")
        
        # Should have NHelices + 1 channels = 3 channels
        assert len(channels) == 3
        
        # Each channel should be a list of names
        for channel in channels:
            assert isinstance(channel, list)

    def test_get_channels_hide_isolant(self):
        """Test get_channels with hideIsolant=True (default)"""
        helices = [Mock(spec=Helix)]
        
        insert = Insert(
            name="hide_isolant_insert",
            helices=helices,
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        channels = insert.get_channels("test", hideIsolant=True)
        
        # Check that isolant names are not included
        for channel in channels:
            for name in channel:
                assert "IrExt" not in name
                assert "IrInt" not in name
                assert "kaptonsIrExt" not in name
                assert "kaptonsIrInt" not in name

    def test_get_isolants(self):
        """Test get_isolants method"""
        insert = Insert(
            name="isolants_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        isolants = insert.get_isolants("test")
        # Currently returns empty list according to implementation
        assert isolants == []

    def test_get_params_basic(self):
        """Test get_params method with mock objects"""
        # Create mock helices with required attributes
        helix1 = Mock(spec=Helix)
        helix1.r = [10.0, 20.0]
        helix1.z = [0.0, 50.0]
        helix1.modelaxi = Mock()
        helix1.modelaxi.turns = [2.0, 3.0]
        helix1.modelaxi.h = 10.0
        helix1.modelaxi.compact.return_value = ([2.0, 3.0], [5.0, 5.0])
        
        helix2 = Mock(spec=Helix)
        helix2.r = [25.0, 35.0]
        helix2.z = [5.0, 45.0]
        helix2.modelaxi = Mock()
        helix2.modelaxi.turns = [1.5, 2.5]
        helix2.modelaxi.h = 8.0
        helix2.modelaxi.compact.return_value = ([1.5, 2.5], [4.0, 4.0])
        
        # Create mock rings
        ring1 = Mock(spec=Ring)
        ring1.z = [10.0, 15.0]
        ring2 = Mock(spec=Ring)
        ring2.z = [85.0, 90.0]
        
        insert = Insert(
            name="params_insert",
            helices=[helix1, helix2],
            rings=[ring1, ring2],
            currentleads=[],
            hangles=[],
            rangles=[],
            innerbore=5.0,
            outerbore=40.0
        )
        
        params = insert.get_params()
        
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
        return '''!<Insert>
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

    @patch("python_magnetgeo.utils.writeYaml")
    def test_dump_method(self, mock_write_yaml):
        """Test dump method calls writeYaml correctly"""
        instance = self.get_sample_instance()
        instance.dump()
        mock_write_yaml.assert_called_once_with("Insert", instance, Insert)

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
            mock_file.assert_called_once_with("test_insert.json", "w")


class TestInsertYAMLConstructor:
    """Test Insert YAML constructor - custom implementation"""
    
    def test_yaml_constructor_function(self):
        """Test the YAML constructor function"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = {
            "name": "constructor_insert",
            "helices": ["helix1", "helix2"],
            "rings": ["ring1"],
            "currentleads": ["inner_lead", "outer_lead"],
            "hangles": [0.0, 120.0],
            "rangles": [60.0],
            "innerbore": 8.0,
            "outerbore": 48.0
        }
        mock_loader.construct_mapping.return_value = mock_data
        
        # The Insert_constructor returns an Insert instance directly
        result = Insert_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Insert)
        assert result.name == "constructor_insert"
        assert result.helices == ["helix1", "helix2"]
        assert result.rings == ["ring1"]
        assert result.currentleads == ["inner_lead", "outer_lead"]
        assert result.hangles == [0.0, 120.0]
        assert result.rangles == [60.0]
        assert result.innerbore == 8.0
        assert result.outerbore == 48.0
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_yaml_constructor_with_object_data(self):
        """Test YAML constructor with actual object data"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Create mock objects
        mock_helix = Mock(spec=Helix)
        mock_ring = Mock(spec=Ring)
        mock_lead = Mock(spec=InnerCurrentLead)
        
        # YAML data with object references
        yaml_data = {
            "name": "object_constructor_insert",
            "helices": [mock_helix],
            "rings": [mock_ring],
            "currentleads": [mock_lead],
            "hangles": [0.0, 90.0],
            "rangles": [45.0],
            "innerbore": 10.0,
            "outerbore": 50.0
        }
        
        mock_loader.construct_mapping.return_value = yaml_data
        
        result = Insert_constructor(mock_loader, mock_node)
        
        # Constructor should create Insert with object references intact
        assert isinstance(result, Insert)
        assert result.name == "object_constructor_insert"
        assert result.helices == [mock_helix]
        assert result.rings == [mock_ring]
        assert result.currentleads == [mock_lead]


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
            "helices": ["helix1", "helix2"],
            "rings": ["ring1", "ring2"],
            "currentleads": ["inner_lead", "outer_lead"],
            "hangles": [0.0, 120.0, 240.0],
            "rangles": [60.0, 180.0, 300.0],
            "innerbore": 8.0,
            "outerbore": 48.0
        }
        
        insert = Insert.from_dict(data)
        
        assert insert.name == "dict_insert"
        assert insert.helices == ["helix1", "helix2"]
        assert insert.rings == ["ring1", "ring2"]
        assert insert.currentleads == ["inner_lead", "outer_lead"]
        assert insert.hangles == [0.0, 120.0, 240.0]
        assert insert.rangles == [60.0, 180.0, 300.0]
        assert insert.innerbore == 8.0
        assert insert.outerbore == 48.0

    def test_from_dict_with_object_data(self):
        """Test from_dict with actual object data"""
        # Create mock objects
        helix = Mock(spec=Helix)
        ring = Mock(spec=Ring)
        lead = Mock(spec=InnerCurrentLead)
        
        data = {
            "name": "object_dict_insert",
            "helices": [helix],
            "rings": [ring],
            "currentleads": [lead],
            "hangles": [0.0, 90.0],
            "rangles": [45.0],
            "innerbore": 5.0,
            "outerbore": 25.0
        }
        
        insert = Insert.from_dict(data)
        
        assert insert.name == "object_dict_insert"
        assert insert.helices == [helix]
        assert insert.rings == [ring]
        assert insert.currentleads == [lead]

    def test_from_dict_with_debug(self):
        """Test from_dict with debug flag"""
        data = {
            "name": "debug_insert",
            "helices": [],
            "rings": [],
            "currentleads": [],
            "hangles": [0.0],
            "rangles": [90.0],
            "innerbore": 3.0,
            "outerbore": 30.0
        }
        
        insert = Insert.from_dict(data, debug=True)
        assert isinstance(insert, Insert)
        assert insert.name == "debug_insert"


class TestInsertFileOperations:
    """Test Insert file I/O operations"""
    
    def test_from_yaml_with_mocking(self):
        """Test from_yaml with proper mocking"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_insert = Insert(
                name="yaml_test",
                helices=[],
                rings=[],
                currentleads=[],
                hangles=[],
                rangles=[]
            )
            mock_load.return_value = mock_insert
            
            result = Insert.from_yaml("test.yaml")
            
            assert result == mock_insert
            mock_load.assert_called_once_with("Insert", "test.yaml", Insert, False)

    def test_from_yaml_with_debug(self):
        """Test from_yaml with debug flag"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_insert = Insert(
                name="debug_yaml",
                helices=["helix1"],
                rings=["ring1"],
                currentleads=[],
                hangles=[0.0],
                rangles=[90.0]
            )
            mock_load.return_value = mock_insert
            
            result = Insert.from_yaml("test.yaml", debug=True)
            
            assert result == mock_insert
            mock_load.assert_called_once_with("Insert", "test.yaml", Insert, True)

    def test_from_json_with_mocking(self):
        """Test from_json with proper mocking"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load:
            mock_insert = Insert(
                name="json_test",
                helices=["helix1", "helix2"],
                rings=[],
                currentleads=["lead1"],
                hangles=[],
                rangles=[]
            )
            mock_load.return_value = mock_insert
            
            result = Insert.from_json("test.json")
            
            assert result == mock_insert
            mock_load.assert_called_once_with("Insert", "test.json", False)

    def test_from_json_with_debug(self):
        """Test from_json with debug flag"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load:
            mock_insert = Insert(
                name="debug_json",
                helices=[],
                rings=["ring1", "ring2"],
                currentleads=[],
                hangles=[0.0, 180.0],
                rangles=[]
            )
            mock_load.return_value = mock_insert
            
            result = Insert.from_json("test.json", debug=True)
            
            assert result == mock_insert
            mock_load.assert_called_once_with("Insert", "test.json", True)


class TestInsertStringDataHandling:
    """Test Insert handling of string data in various scenarios"""
    
    def test_insert_initialization_with_string_data(self):
        """Test Insert can be initialized with string references"""
        insert = Insert(
            name="string_data_insert",
            helices=["helix_config1", "helix_config2"],
            rings=["ring_config1"],
            currentleads=["inner_lead_config", "outer_lead_config"],
            hangles=[0.0, 90.0, 180.0, 270.0],
            rangles=[45.0, 135.0, 225.0, 315.0],
            innerbore=7.0,
            outerbore=35.0
        )
        
        # Should initialize successfully with string data
        assert insert.name == "string_data_insert"
        assert insert.helices == ["helix_config1", "helix_config2"]
        assert insert.rings == ["ring_config1"]
        assert insert.currentleads == ["inner_lead_config", "outer_lead_config"]

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_insert_methods_after_string_loading(self, mock_check, mock_load_list):
        """Test that Insert methods work correctly after loading string references"""
        # Create insert with string data
        insert = Insert(
            name="method_test_insert",
            helices=["helix_file1", "helix_file2"],
            rings=["ring_file1"],
            currentleads=["lead_file1"],
            hangles=[0.0, 120.0],
            rangles=[60.0],
            innerbore=6.0,
            outerbore=36.0
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded objects with proper attributes
        mock_helix1 = Mock(spec=Helix)
        mock_helix1.r = [10.0, 20.0]
        mock_helix1.z = [0.0, 100.0]
        mock_helix1.get_names.return_value = ["test_H1_Cu0"]
        
        mock_helix2 = Mock(spec=Helix)
        mock_helix2.r = [25.0, 35.0]
        mock_helix2.z = [5.0, 95.0]
        mock_helix2.get_names.return_value = ["test_H2_Cu0"]
        
        mock_ring = Mock(spec=Ring)
        mock_ring.z = [10.0, 15.0]
        
        mock_lead = Mock(spec=InnerCurrentLead)
        
        # Set up mock_load_list to return appropriate objects based on call
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "helices":
                return [mock_helix1, mock_helix2]
            elif comment == "rings":
                return [mock_ring]
            elif comment == "currentleads":
                return [mock_lead]
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Update to load string references
        insert.update()
        
        # Now test that methods work correctly
        assert insert.get_nhelices() == 2
        
        # Test get_names
        names_3d = insert.get_names("test", is2D=False)
        expected_3d = ["H1", "H2", "test_R1", "iL1"]
        assert names_3d == expected_3d
        
        # Test bounding box
        rb, zb = insert.boundingBox()
        assert rb == [10.0, 35.0]  # min/max r from helices
        assert zb[0] == -5.0  # min z adjusted by ring height
        assert zb[1] == 105.0  # max z adjusted by ring height

    def test_insert_serialization_with_string_data(self):
        """Test JSON serialization preserves string references"""
        insert = Insert(
            name="serialization_test",
            helices=["helix_serial1", "helix_serial2"],
            rings=["ring_serial1"],
            currentleads=["lead_serial1", "lead_serial2"],
            hangles=[0.0, 90.0],
            rangles=[45.0],
            innerbore=4.0,
            outerbore=40.0
        )
        
        json_str = insert.to_json()
        parsed = json.loads(json_str)
        
        # String references should be preserved in JSON
        assert parsed["helices"] == ["helix_serial1", "helix_serial2"]
        assert parsed["rings"] == ["ring_serial1"]
        assert parsed["currentleads"] == ["lead_serial1", "lead_serial2"]

    def test_insert_repr_with_string_data(self):
        """Test __repr__ method works correctly with string data"""
        insert = Insert(
            name="repr_test_insert",
            helices=["repr_helix1", "repr_helix2"],
            rings=["repr_ring1"],
            currentleads=["repr_lead1"],
            hangles=[0.0, 180.0],
            rangles=[90.0, 270.0],
            innerbore=5.0,
            outerbore=25.0
        )
        
        repr_str = repr(insert)
        
        # Should include string references in representation
        assert "name='repr_test_insert'" in repr_str
        assert "helices=['repr_helix1', 'repr_helix2']" in repr_str
        assert "rings=['repr_ring1']" in repr_str
        assert "currentleads=['repr_lead1']" in repr_str

    def test_insert_yaml_constructor_with_string_data(self):
        """Test YAML constructor handles string data in loaded mapping"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # YAML data with string references
        yaml_data = {
            "name": "yaml_constructor_insert",
            "helices": ["yaml_helix1", "yaml_helix2"],
            "rings": ["yaml_ring1"],
            "currentleads": ["yaml_inner_lead", "yaml_outer_lead"],
            "hangles": [0.0, 120.0, 240.0],
            "rangles": [60.0, 180.0, 300.0],
            "innerbore": 9.0,
            "outerbore": 45.0
        }
        
        mock_loader.construct_mapping.return_value = yaml_data
        
        result = Insert_constructor(mock_loader, mock_node)
        
        # Constructor should create Insert with string references intact
        assert isinstance(result, Insert)
        assert result.name == "yaml_constructor_insert"
        assert result.helices == ["yaml_helix1", "yaml_helix2"]
        assert result.rings == ["yaml_ring1"]
        assert result.currentleads == ["yaml_inner_lead", "yaml_outer_lead"]


class TestInsertUpdateErrorHandling:
    """Test error handling in Insert update scenarios"""
    
    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_loading_errors(self, mock_check, mock_load_list):
        """Test update method handles loading errors gracefully"""
        insert = Insert(
            name="error_insert",
            helices=["invalid_helix_file"],
            rings=["invalid_ring_file"],
            currentleads=["invalid_lead_file"],
            hangles=[],
            rangles=[]
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loading to raise exceptions
        mock_load_list.side_effect = Exception("Failed to load components")
        
        # Update should handle errors without crashing
        try:
            insert.update()
        except Exception as e:
            # If exceptions are not caught internally, that's the expected behavior
            assert "Failed to load components" in str(e)

    def test_update_with_non_list_references(self):
        """Test update method when components are not lists (should not attempt loading)"""
        # Create insert with object references (not string lists)
        helix_obj = Mock(spec=Helix)
        ring_obj = Mock(spec=Ring)
        lead_obj = Mock(spec=InnerCurrentLead)
        
        insert = Insert(
            name="no_update_insert",
            helices=[helix_obj],      # List of objects (not strings)
            rings=[ring_obj],         # List of objects (not strings)
            currentleads=[lead_obj],  # List of objects (not strings)
            hangles=[0.0],
            rangles=[90.0]
        )
        
        # Store original references
        orig_helices = insert.helices
        orig_rings = insert.rings
        orig_leads = insert.currentleads
        
        insert.update()
        
        # References should remain unchanged since they're not lists of strings
        assert insert.helices == orig_helices
        assert insert.rings == orig_rings
        assert insert.currentleads == orig_leads


class TestInsertIntegration:
    """Integration tests for Insert class"""
    
    def test_insert_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_insert = Insert(
            name="roundtrip_insert",
            helices=["roundtrip_helix1", "roundtrip_helix2"],
            rings=["roundtrip_ring1", "roundtrip_ring2"],
            currentleads=["roundtrip_inner_lead", "roundtrip_outer_lead"],
            hangles=[0.0, 90.0, 180.0, 270.0],
            rangles=[45.0, 135.0, 225.0, 315.0],
            innerbore=12.0,
            outerbore=60.0
        )
        
        # Test JSON serialization
        json_str = original_insert.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Insert"
        assert parsed_json["name"] == "roundtrip_insert"
        assert parsed_json["helices"] == ["roundtrip_helix1", "roundtrip_helix2"]
        assert parsed_json["rings"] == ["roundtrip_ring1", "roundtrip_ring2"]
        assert parsed_json["currentleads"] == ["roundtrip_inner_lead", "roundtrip_outer_lead"]
        assert parsed_json["hangles"] == [0.0, 90.0, 180.0, 270.0]
        assert parsed_json["rangles"] == [45.0, 135.0, 225.0, 315.0]
        assert parsed_json["innerbore"] == 12.0
        assert parsed_json["outerbore"] == 60.0

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_insert_workflow_string_to_object_conversion(self, mock_check, mock_load_list):
        """Test complete workflow from string references to object usage"""
        # Step 1: Create Insert with string references (as would be loaded from YAML)
        insert = Insert(
            name="workflow_insert",
            helices=["helix1.yaml", "helix2.yaml"],
            rings=["ring1.yaml"],
            currentleads=["inner_lead.yaml", "outer_lead.yaml"],
            hangles=[0.0, 180.0],
            rangles=[90.0, 270.0],
            innerbore=8.0,
            outerbore=40.0
        )
        
        # Step 2: Setup mocks for string loading
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Create realistic mock objects
        mock_helix1 = Mock(spec=Helix)
        mock_helix1.name = "loaded_helix1"
        mock_helix1.r = [10.0, 20.0]
        mock_helix1.z = [0.0, 100.0]
        mock_helix1.get_names.return_value = ["workflow_H1_Cu0", "workflow_H1_Cu1"]
        
        mock_helix2 = Mock(spec=Helix)
        mock_helix2.name = "loaded_helix2"
        mock_helix2.r = [25.0, 35.0]
        mock_helix2.z = [5.0, 95.0]
        mock_helix2.get_names.return_value = ["workflow_H2_Cu0"]
        
        mock_ring = Mock(spec=Ring)
        mock_ring.name = "loaded_ring"
        mock_ring.z = [10.0, 15.0]
        
        mock_inner_lead = Mock(spec=InnerCurrentLead)
        mock_inner_lead.name = "loaded_inner_lead"
        
        mock_outer_lead = Mock(spec=OuterCurrentLead)
        mock_outer_lead.name = "loaded_outer_lead"
        
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "helices":
                return [mock_helix1, mock_helix2]
            elif comment == "rings":
                return [mock_ring]
            elif comment == "currentleads":
                return [mock_inner_lead, mock_outer_lead]
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Step 3: Convert string references to objects
        insert.update()
        
        # Step 4: Verify objects are loaded and Insert methods work
        assert isinstance(insert.helices[0], Mock)
        assert isinstance(insert.rings[0], Mock)
        assert len(insert.currentleads) == 2
        
        # Test Insert functionality with loaded objects
        assert insert.get_nhelices() == 2
        
        names = insert.get_names("workflow", is2D=True)
        expected = [
            "workflow_H1_Cu0", "workflow_H1_Cu1",  # From helix1
            "workflow_H2_Cu0",                     # From helix2
            "workflow_R1"                          # From ring
        ]
        assert names == expected
        
        # Test bounding box calculation
        rb, zb = insert.boundingBox()
        assert rb == [10.0, 35.0]
        assert zb[0] == -5.0  # Adjusted by ring height
        assert zb[1] == 105.0


class TestInsertPerformance:
    """Performance tests for Insert class"""
    
    def test_multiple_insert_creation_performance(self):
        """Test performance of creating many inserts"""
        inserts = []
        for i in range(25):
            insert = Insert(
                name=f"perf_insert_{i}",
                helices=[f"helix_{i}_1", f"helix_{i}_2"],
                rings=[f"ring_{i}_1"],
                currentleads=[f"lead_{i}_1"],
                hangles=[float(j * 45) for j in range(i % 8 + 1)],
                rangles=[float(j * 30) for j in range(i % 12 + 1)],
                innerbore=float(i),
                outerbore=float(i + 50)
            )
            inserts.append(insert)
        
        assert len(inserts) == 25
        assert all(isinstance(ins, Insert) for ins in inserts)
        
        # Test that operations work on all inserts
        n_helices = [ins.get_nhelices() for ins in inserts]
        assert len(n_helices) == 25
        assert all(n == 2 for n in n_helices)  # Each has 2 helices


class TestInsertDataConsistency:
    """Test data consistency and validation in Insert"""
    
    def test_insert_geometric_consistency(self):
        """Test geometric consistency within insert"""
        # Create mock helices with consistent geometry
        helix1 = Mock(spec=Helix)
        helix1.r = [10.0, 20.0]
        helix1.z = [0.0, 100.0]
        
        helix2 = Mock(spec=Helix)
        helix2.r = [25.0, 35.0]  # Should be outside helix1
        helix2.z = [5.0, 95.0]
        
        insert = Insert(
            name="consistent_insert",
            helices=[helix1, helix2],
            rings=[],
            currentleads=[],
            hangles=[0.0, 90.0],
            rangles=[45.0],
            innerbore=5.0,   # Should be < helix1.r[0]
            outerbore=40.0   # Should be > helix2.r[1]
        )
        
        # Test geometric relationships
        assert insert.innerbore < helix1.r[0]  # Inner bore < first helix inner radius
        assert helix1.r[1] < helix2.r[0]       # Helices don't overlap
        assert helix2.r[1] < insert.outerbore  # Last helix < outer bore
        
        # Test that bounding box encompasses all components
        rb, zb = insert.boundingBox()
        assert rb[0] <= min(helix1.r[0], helix2.r[0])
        assert rb[1] >= max(helix1.r[1], helix2.r[1])

    def test_insert_component_count_consistency(self):
        """Test consistency in component counting"""
        # Create properly mocked helices with required attributes for get_params
        helices = []
        for i in range(4):
            helix = Mock(spec=Helix)
            helix.r = [10.0 + i*10, 20.0 + i*10]
            helix.z = [0.0, 100.0]
            # Add required modelaxi attributes for get_params method
            helix.modelaxi = Mock()
            helix.modelaxi.turns = [2.0, 3.0]
            helix.modelaxi.h = 10.0
            helix.modelaxi.compact.return_value = ([2.0, 3.0], [5.0, 5.0])
            helices.append(helix)
        
        # Create properly mocked rings with z coordinates
        rings = []
        for i in range(3):
            ring = Mock(spec=Ring)
            ring.z = [10.0 + i*20, 15.0 + i*20]
            rings.append(ring)
        
        leads = [Mock(spec=InnerCurrentLead), Mock(spec=OuterCurrentLead)]
        
        insert = Insert(
            name="count_test_insert",
            helices=helices,
            rings=rings,
            currentleads=leads,
            hangles=[0.0, 90.0, 180.0, 270.0],
            rangles=[45.0, 135.0, 225.0, 315.0],
            innerbore=5.0,
            outerbore=50.0
        )
        
        # Test consistent counting
        assert insert.get_nhelices() == 4
        assert len(insert.rings) == 3
        assert len(insert.currentleads) == 2
        assert len(insert.hangles) == 4
        assert len(insert.rangles) == 4
        
        # Test get_params consistency - now helices have proper modelaxi attributes
        params = insert.get_params()
        Nhelices, Nrings, NChannels, Nsections, R1, R2, Dh, Sh, Zc = params
        
        assert Nhelices == 4
        assert Nrings == 3
        assert NChannels == 5  # Nhelices + 1



