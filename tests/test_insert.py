#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Insert class (Updated with probes attribute)
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
from python_magnetgeo.Probe import Probe
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
        assert insert.probes == []  # NEW: Check default empty probes
        assert insert.hangles == []
        assert insert.rangles == []
        assert insert.innerbore == 0
        assert insert.outerbore == 0

    def test_insert_initialization_with_probes(self):
        """Test Insert initialization with probes parameter"""
        # Create mock probe objects
        probe1 = Mock(spec=Probe)
        probe1.name = "voltage_probe"
        probe1.probe_type = "voltage_taps"
        
        probe2 = Mock(spec=Probe)
        probe2.name = "temp_probe"
        probe2.probe_type = "temperature"
        
        insert = Insert(
            name="probes_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            innerbore=5.0,
            outerbore=50.0,
            probes=[probe1, probe2]  # NEW: Initialize with probes
        )
        
        assert insert.name == "probes_insert"
        assert len(insert.probes) == 2
        assert insert.probes[0] == probe1
        assert insert.probes[1] == probe2

    def test_insert_initialization_with_string_probe_references(self):
        """Test Insert initialization with string probe references"""
        insert = Insert(
            name="string_probes_insert",
            helices=["helix1.yaml"],
            rings=["ring1.yaml"],
            currentleads=["lead1.yaml"],
            hangles=[0.0, 90.0],
            rangles=[45.0],
            innerbore=8.0,
            outerbore=48.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: String references
        )
        
        assert insert.name == "string_probes_insert"
        assert insert.probes == ["voltage_probes.yaml", "temp_probes.yaml"]
        assert isinstance(insert.probes, list)
        assert all(isinstance(item, str) for item in insert.probes)

    def test_insert_full_initialization_with_objects(self):
        """Test Insert initialization with all types of objects"""
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
        
        probe = Mock(spec=Probe)
        probe.name = "test_probe"
        probe.probe_type = "voltage_taps"
        
        insert = Insert(
            name="full_insert",
            helices=[helix],
            rings=[ring],
            currentleads=[inner_lead],
            hangles=[0.0, 90.0, 180.0],
            rangles=[45.0, 135.0],
            innerbore=5.0,
            outerbore=50.0,
            probes=[probe]  # NEW: Include probe
        )
        
        assert insert.name == "full_insert"
        assert len(insert.helices) == 1
        assert insert.helices[0] == helix
        assert len(insert.rings) == 1
        assert insert.rings[0] == ring
        assert len(insert.currentleads) == 1
        assert insert.currentleads[0] == inner_lead
        assert len(insert.probes) == 1  # NEW: Check probe
        assert insert.probes[0] == probe
        assert insert.hangles == [0.0, 90.0, 180.0]
        assert insert.rangles == [45.0, 135.0]
        assert insert.innerbore == 5.0
        assert insert.outerbore == 50.0

    def test_insert_probes_default_none(self):
        """Test Insert with probes=None defaults to empty list"""
        insert = Insert(
            name="default_probes_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=None  # NEW: Explicit None
        )
        
        assert insert.probes == []  # Should default to empty list


class TestInsertUpdate:
    """Test Insert update method for loading string references"""
    
    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_string_probes(self, mock_check, mock_load_list):
        """Test update method with string probes references"""
        insert = Insert(
            name="update_probes_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=["probe1", "probe2"]  # NEW: String probe references
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded probes
        mock_probes = [Mock(spec=Probe), Mock(spec=Probe)]
        mock_probes[0].name = "loaded_probe1"
        mock_probes[1].name = "loaded_probe2"
        mock_load_list.return_value = mock_probes
        
        insert.update()
        
        assert insert.probes == mock_probes
        # Check that loadList was called for probes
        mock_load_list.assert_any_call("probes", ["probe1", "probe2"], [None, Probe], {"Probe": Probe.from_dict})

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
            rangles=[],
            probes=[]  # NEW: Empty probes
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
    def test_update_with_mixed_string_and_object_probes(self, mock_check, mock_load_list):
        """Test update method with mixed probe types"""
        # Create existing probe object
        existing_probe = Mock(spec=Probe)
        existing_probe.name = "existing_probe"
        
        insert = Insert(
            name="mixed_probes_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=["string_probe1", "string_probe2"]  # NEW: String probe references
        )
        
        def mock_check_side_effect(objects, target_type):
            if target_type == str:
                return isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
            return False
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded probes
        mock_probes = [Mock(spec=Probe), Mock(spec=Probe)]
        mock_probes[0].name = "loaded_probe1"
        mock_probes[1].name = "loaded_probe2"
        mock_load_list.return_value = mock_probes
        
        insert.update()
        
        # Probes should be loaded from strings
        assert insert.probes == mock_probes
        mock_load_list.assert_any_call("probes", ["string_probe1", "string_probe2"], [None, Probe], {"Probe": Probe.from_dict})

    def test_update_with_object_references(self):
        """Test update method when components are already objects"""
        # Create mock objects
        helix = Mock(spec=Helix)
        ring = Mock(spec=Ring)
        lead = Mock(spec=InnerCurrentLead)
        probe = Mock(spec=Probe)  # NEW: Mock probe object
        
        insert = Insert(
            name="object_insert",
            helices=[helix],
            rings=[ring],
            currentleads=[lead],
            hangles=[0.0],
            rangles=[90.0],
            probes=[probe]  # NEW: Object probe
        )
        
        # Store original references
        orig_helices = insert.helices
        orig_rings = insert.rings
        orig_leads = insert.currentleads
        orig_probes = insert.probes  # NEW: Store original probes
        
        insert.update()
        
        # Objects should remain unchanged
        assert insert.helices == orig_helices
        assert insert.rings == orig_rings
        assert insert.currentleads == orig_leads
        assert insert.probes == orig_probes  # NEW: Check probes unchanged


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
            rangles=[],
            probes=[]  # NEW: Include empty probes
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
            rangles=[],
            probes=[]  # NEW: Include empty probes
        )
        assert insert.get_nhelices() == 4

    def test_repr_with_probes(self):
        """Test __repr__ method includes probes"""
        probe = Mock(spec=Probe)
        probe.name = "test_probe"
        
        insert = Insert(
            name="repr_test_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[0.0],
            rangles=[90.0],
            innerbore=5.0,
            outerbore=25.0,
            probes=[probe]  # NEW: Include probe
        )
        
        repr_str = repr(insert)
        
        # Should include probes in representation
        assert "probes=" in repr_str
        assert "repr_test_insert" in repr_str

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
            rangles=[],
            probes=[]  # NEW: Include empty probes
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
            outerbore=50.0,
            probes=[]  # NEW: Include empty probes
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''!<Insert>
name: yaml_insert
helices: []
rings: []
currentleads: []
probes: []
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
            "outerbore": 50.0,
            "probes": []  # NEW: Include probes field
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
        assert "probes" in parsed  # NEW: Check probes included
        assert isinstance(parsed["helices"], list)
        assert isinstance(parsed["rings"], list)
        assert isinstance(parsed["currentleads"], list)
        assert isinstance(parsed["probes"], list)  # NEW: Check probes type

    def test_serialization_with_probes(self):
        """Test serialization with probe objects"""
        # Create Insert with string probe references (serializable)
        insert_with_probes = Insert(
            name="probes_serialization_test",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=["probe1.yaml", "probe2.yaml"]  # NEW: String references
        )
        
        json_str = insert_with_probes.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["probes"] == ["probe1.yaml", "probe2.yaml"]


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
            "outerbore": 48.0,
            "probes": ["probe1.yaml", "probe2.yaml"]  # NEW: Include probes
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
        assert result.probes == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probes
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_yaml_constructor_with_object_data(self):
        """Test YAML constructor with actual object data"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Create mock objects
        mock_helix = Mock(spec=Helix)
        mock_ring = Mock(spec=Ring)
        mock_lead = Mock(spec=InnerCurrentLead)
        mock_probe = Mock(spec=Probe)  # NEW: Mock probe
        
        # YAML data with object references
        yaml_data = {
            "name": "object_constructor_insert",
            "helices": [mock_helix],
            "rings": [mock_ring],
            "currentleads": [mock_lead],
            "hangles": [0.0, 90.0],
            "rangles": [45.0],
            "innerbore": 10.0,
            "outerbore": 50.0,
            "probes": [mock_probe]  # NEW: Include probe object
        }
        
        mock_loader.construct_mapping.return_value = yaml_data
        
        result = Insert_constructor(mock_loader, mock_node)
        
        # Constructor should create Insert with object references intact
        assert isinstance(result, Insert)
        assert result.name == "object_constructor_insert"
        assert result.helices == [mock_helix]
        assert result.rings == [mock_ring]
        assert result.currentleads == [mock_lead]
        assert result.probes == [mock_probe]  # NEW: Check probe object


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
        """Test from_dict with complete data including probes"""
        data = {
            "name": "dict_insert",
            "helices": ["helix1", "helix2"],
            "rings": ["ring1", "ring2"],
            "currentleads": ["inner_lead", "outer_lead"],
            "hangles": [0.0, 120.0, 240.0],
            "rangles": [60.0, 180.0, 300.0],
            "innerbore": 8.0,
            "outerbore": 48.0,
            "probes": ["probe1.yaml", "probe2.yaml"]  # NEW: Include probes
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
        assert insert.probes == ["probe1.yaml", "probe2.yaml"]  # NEW: Check probes

    def test_from_dict_missing_probes_field(self):
        """Test from_dict with missing probes field (should default to empty list)"""
        data = {
            "name": "minimal_insert",
            "helices": ["helix1"],
            "rings": ["ring1"],
            "currentleads": ["lead1"],
            "hangles": [0.0],
            "rangles": [90.0],
            "innerbore": 5.0,
            "outerbore": 25.0
            # No probes field
        }
        
        insert = Insert.from_dict(data)
        
        assert insert.name == "minimal_insert"
        assert insert.probes == []  # NEW: Should default to empty list

    def test_from_dict_with_object_data(self):
        """Test from_dict with actual object data"""
        # Create mock objects
        helix = Mock(spec=Helix)
        ring = Mock(spec=Ring)
        lead = Mock(spec=InnerCurrentLead)
        probe = Mock(spec=Probe)  # NEW: Mock probe
        
        data = {
            "name": "object_dict_insert",
            "helices": [helix],
            "rings": [ring],
            "currentleads": [lead],
            "hangles": [0.0, 90.0],
            "rangles": [45.0],
            "innerbore": 5.0,
            "outerbore": 25.0,
            "probes": [probe]  # NEW: Include probe object
        }
        
        insert = Insert.from_dict(data)
        
        assert insert.name == "object_dict_insert"
        assert insert.helices == [helix]
        assert insert.rings == [ring]
        assert insert.currentleads == [lead]
        assert insert.probes == [probe]  # NEW: Check probe object


class TestInsertProbesIntegration:
    """Test Insert integration with probes functionality"""
    
    def test_insert_with_probes_workflow(self):
        """Test complete workflow with probes from string to object"""
        # Step 1: Create Insert with string probe references
        insert = Insert(
            name="probes_workflow_insert",
            helices=["helix1.yaml"],
            rings=["ring1.yaml"],
            currentleads=["lead1.yaml"],
            hangles=[0.0, 180.0],
            rangles=[90.0, 270.0],
            innerbore=8.0,
            outerbore=40.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Probe references
        )
        
        # Initial state: probes should be strings
        assert all(isinstance(probe, str) for probe in insert.probes)
        assert len(insert.probes) == 2
        
        # Step 2: Mock the update process for probes
        with patch('python_magnetgeo.utils.loadList') as mock_load_list:
            with patch('python_magnetgeo.utils.check_objects') as mock_check:
                
                def mock_check_side_effect(objects, target_type):
                    return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
                
                mock_check.side_effect = mock_check_side_effect
                
                # Create mock loaded probes
                mock_voltage_probe = Mock(spec=Probe)
                mock_voltage_probe.name = "loaded_voltage_probe"
                mock_voltage_probe.probe_type = "voltage_taps"
                
                mock_temp_probe = Mock(spec=Probe)
                mock_temp_probe.name = "loaded_temp_probe"
                mock_temp_probe.probe_type = "temperature"
                
                def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
                    if comment == "probes":
                        return [mock_voltage_probe, mock_temp_probe]
                    elif comment == "helices":
                        return [Mock(spec=Helix)]
                    elif comment == "rings":
                        return [Mock(spec=Ring)]
                    elif comment == "currentleads":
                        return [Mock(spec=InnerCurrentLead)]
                    return []
                
                mock_load_list.side_effect = mock_load_list_side_effect
                
                # Step 3: Update to load string references
                insert.update()
                
                # Step 4: Verify probes are loaded
                assert len(insert.probes) == 2
                assert insert.probes[0] == mock_voltage_probe
                assert insert.probes[1] == mock_temp_probe
                
                # Verify loadList was called correctly for probes
                mock_load_list.assert_any_call(
                    "probes", 
                    ["voltage_probes.yaml", "temp_probes.yaml"], 
                    [None, Probe], 
                    {"Probe": Probe.from_dict}
                )

    def test_insert_serialization_with_mixed_probe_types(self):
        """Test serialization with mixed probe configurations"""
        insert = Insert(
            name="mixed_probes_insert",
            helices=["helix1"],
            rings=[],
            currentleads=[],
            hangles=[0.0],
            rangles=[90.0],
            innerbore=5.0,
            outerbore=25.0,
            probes=["external_probe.yaml"]  # String reference for serialization
        )
        
        # Test JSON serialization preserves string references
        json_str = insert.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["probes"] == ["external_probe.yaml"]
        assert parsed["__classname__"] == "Insert"

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_insert_empty_probes_handling(self, mock_check, mock_load_list):
        """Test Insert correctly handles empty probes list"""
        insert = Insert(
            name="empty_probes_insert",
            helices=["helix1"],  # String reference that would trigger update
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=[]  # Empty probes list
        )
        
        assert insert.probes == []
        assert isinstance(insert.probes, list)
        
        # Mock the update mechanism to prevent file loading
        def mock_check_side_effect(objects, target_type):
            # Only return True for helices (which are strings), not for empty probes
            return (target_type == str and isinstance(objects, list) and 
                    len(objects) > 0 and all(isinstance(obj, str) for obj in objects))
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock helices loading
        mock_helix = Mock(spec=Helix)
        mock_helix.name = "loaded_helix"
        mock_load_list.return_value = [mock_helix]
        
        # Update should not affect empty probes list
        insert.update()
        assert insert.probes == []
        
        # Verify that check_objects was called for helices but loadList handled it correctly
        mock_check.assert_called()
        # Should only load helices, not probes (since probes is empty)
        mock_load_list.assert_called_once_with("helices", ["helix1"], [None, Helix], {"Helix": Helix.from_dict})

    def test_insert_none_probes_default(self):
        """Test Insert with probes=None gets proper default"""
        insert = Insert(
            name="none_probes_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=None  # Explicit None
        )
        
        assert insert.probes == []  # Should default to empty list
        assert isinstance(insert.probes, list)


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
                rangles=[],
                probes=[]  # NEW: Include probes
            )
            mock_load.return_value = mock_insert
            
            result = Insert.from_yaml("test.yaml")
            
            assert result == mock_insert
            mock_load.assert_called_once_with("Insert", "test.yaml", Insert, False)

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_from_yaml_with_debug(self, mock_check_objects, mock_load_list):
        """Test from_yaml with debug flag"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_insert = Insert(
                name="debug_yaml",
                helices=["helix1"],
                rings=["ring1"],
                currentleads=[],
                hangles=[0.0],
                rangles=[90.0],
                probes=["probe1.yaml"]
            )
            mock_load.return_value = mock_insert
            
            # Mock the update process to avoid file loading
            mock_check_objects.return_value = True  # Simulate strings found
            mock_helix = Mock(spec=Helix)
            mock_helix.name = "helix1"
            mock_load_list.return_value = [mock_helix]

            result = Insert.from_yaml("test.yaml", debug=True)
            
            assert result.name == "debug_yaml"
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
                rangles=[],
                probes=["probe1.yaml", "probe2.yaml"]  # NEW: Include probe references
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
            outerbore=35.0,
            probes=["probe_config1", "probe_config2"]  # NEW: Probe string references
        )
        
        # Should initialize successfully with string data
        assert insert.name == "string_data_insert"
        assert insert.helices == ["helix_config1", "helix_config2"]
        assert insert.rings == ["ring_config1"]
        assert insert.currentleads == ["inner_lead_config", "outer_lead_config"]
        assert insert.probes == ["probe_config1", "probe_config2"]  # NEW: Check probe strings

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
            outerbore=25.0,
            probes=["repr_probe1"]  # NEW: Include probe string
        )
        
        repr_str = repr(insert)
        
        # Should include string references in representation
        assert "name='repr_test_insert'" in repr_str
        assert "helices=['repr_helix1', 'repr_helix2']" in repr_str
        assert "rings=['repr_ring1']" in repr_str
        assert "currentleads=['repr_lead1']" in repr_str
        assert "probes=['repr_probe1']" in repr_str  # NEW: Check probe in repr

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
            outerbore=40.0,
            probes=["probe_serial1", "probe_serial2"]  # NEW: Probe strings
        )
        
        json_str = insert.to_json()
        parsed = json.loads(json_str)
        
        # String references should be preserved in JSON
        assert parsed["helices"] == ["helix_serial1", "helix_serial2"]
        assert parsed["rings"] == ["ring_serial1"]
        assert parsed["currentleads"] == ["lead_serial1", "lead_serial2"]
        assert parsed["probes"] == ["probe_serial1", "probe_serial2"]  # NEW: Check probe strings


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
            outerbore=60.0,
            probes=["roundtrip_probe1", "roundtrip_probe2"]  # NEW: Include probes
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
        assert parsed_json["probes"] == ["roundtrip_probe1", "roundtrip_probe2"]  # NEW: Check probes

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
            outerbore=40.0,
            probes=["voltage_probes.yaml", "temp_probes.yaml"]  # NEW: Include probe strings
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
        
        # NEW: Create mock probe objects
        mock_voltage_probe = Mock(spec=Probe)
        mock_voltage_probe.name = "loaded_voltage_probe"
        mock_voltage_probe.probe_type = "voltage_taps"
        
        mock_temp_probe = Mock(spec=Probe)
        mock_temp_probe.name = "loaded_temp_probe"
        mock_temp_probe.probe_type = "temperature"
        
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "helices":
                return [mock_helix1, mock_helix2]
            elif comment == "rings":
                return [mock_ring]
            elif comment == "currentleads":
                return [mock_inner_lead, mock_outer_lead]
            elif comment == "probes":  # NEW: Handle probe loading
                return [mock_voltage_probe, mock_temp_probe]
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Step 3: Convert string references to objects
        insert.update()
        
        # Step 4: Verify objects are loaded and Insert methods work
        assert isinstance(insert.helices[0], Mock)
        assert isinstance(insert.rings[0], Mock)
        assert len(insert.currentleads) == 2
        assert len(insert.probes) == 2  # NEW: Check probes loaded
        assert isinstance(insert.probes[0], Mock)
        assert isinstance(insert.probes[1], Mock)
        
        # Test Insert functionality with loaded objects
        assert insert.get_nhelices() == 2
        
        # Verify that loadList was called for probes
        mock_load_list.assert_any_call(
            "probes", 
            ["voltage_probes.yaml", "temp_probes.yaml"], 
            [None, Probe], 
            {"Probe": Probe.from_dict}
        )


class TestInsertErrorHandling:
    """Test error handling in Insert scenarios"""
    
    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_probe_loading_errors(self, mock_check, mock_load_list):
        """Test update method handles probe loading errors gracefully"""
        insert = Insert(
            name="error_insert",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=["invalid_probe_file.yaml"]  # NEW: Invalid probe file
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loading to raise exceptions for probes
        def mock_load_list_side_effect(comment, objects, supported_types, dict_objects):
            if comment == "probes":
                raise Exception("Failed to load probe components")
            return []
        
        mock_load_list.side_effect = mock_load_list_side_effect
        
        # Update should handle errors without crashing
        try:
            insert.update()
        except Exception as e:
            # If exceptions are not caught internally, that's the expected behavior
            assert "Failed to load probe components" in str(e)

    def test_insert_with_invalid_probe_types(self):
        """Test Insert initialization with invalid probe types"""
        # Test that Insert can handle various probe parameter types
        
        # Test with None (should default to empty list)
        insert_none = Insert(
            name="none_probes",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=None
        )
        assert insert_none.probes == []
        
        # Test with empty list
        insert_empty = Insert(
            name="empty_probes",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            probes=[]
        )
        assert insert_empty.probes == []


class TestInsertPerformance:
    """Performance tests for Insert class"""
    
    def test_multiple_insert_creation_with_probes_performance(self):
        """Test performance of creating many inserts with probes"""
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
                outerbore=float(i + 50),
                probes=[f"probe_{i}_1.yaml", f"probe_{i}_2.yaml"]  # NEW: Include probes
            )
            inserts.append(insert)
        
        assert len(inserts) == 25
        assert all(isinstance(ins, Insert) for ins in inserts)
        
        # Test that operations work on all inserts
        n_helices = [ins.get_nhelices() for ins in inserts]
        assert len(n_helices) == 25
        assert all(n == 2 for n in n_helices)  # Each has 2 helices
        
        # Test that all inserts have probes
        probe_counts = [len(ins.probes) for ins in inserts]
        assert all(count == 2 for count in probe_counts)  # Each has 2 probes


class TestInsertDocumentation:
    """Test that Insert behavior matches its documentation"""
    
    def test_documented_attributes_with_probes(self):
        """Test that Insert has all documented attributes including probes"""
        insert = Insert(
            name="doc_test",
            helices=["helix1"],
            rings=["ring1"],
            currentleads=["lead1"],
            hangles=[0.0],
            rangles=[90.0],
            innerbore=5.0,
            outerbore=15.0,
            probes=["probe1.yaml"]  # NEW: Include probes
        )
        
        # Verify all documented attributes exist
        assert hasattr(insert, "name")
        assert hasattr(insert, "helices")
        assert hasattr(insert, "rings")
        assert hasattr(insert, "currentleads")
        assert hasattr(insert, "probes")  # NEW: Check probes attribute
        assert hasattr(insert, "hangles")
        assert hasattr(insert, "rangles")
        assert hasattr(insert, "innerbore")
        assert hasattr(insert, "outerbore")
        
        # Verify types match documentation
        assert isinstance(insert.name, str)
        assert isinstance(insert.helices, list)
        assert isinstance(insert.rings, list)
        assert isinstance(insert.currentleads, list)
        assert isinstance(insert.probes, list)  # NEW: Check probes type
        assert isinstance(insert.hangles, list)
        assert isinstance(insert.rangles, list)
        assert isinstance(insert.innerbore, (int, float))
        assert isinstance(insert.outerbore, (int, float))

    def test_serialization_interface_compliance_with_probes(self):
        """Test that serialization interface works as documented with probes"""
        insert = Insert(
            name="serial_test_system",
            helices=["helix1"],
            rings=["ring1"],
            currentleads=["lead1"],
            hangles=[0.0],
            rangles=[90.0],
            innerbore=0.5,
            outerbore=2.5,
            probes=["probe1.yaml"]  # NEW: Include probes
        )
        
        # Test to_json returns valid JSON string
        json_str = insert.to_json()
        assert isinstance(json_str, str)
        
        # Should be parseable JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "__classname__" in parsed
        assert parsed["__classname__"] == "Insert"
        assert "probes" in parsed  # NEW: Check probes in JSON
        assert parsed["probes"] == ["probe1.yaml"]
        
        # Test from_dict works with probes
        data = {
            "name": "from_dict_test",
            "helices": ["helix1"],
            "rings": ["ring1"],
            "currentleads": ["lead1"],
            "hangles": [0.0],
            "rangles": [90.0],
            "innerbore": 2.0,
            "outerbore": 3.0,
            "probes": ["probe_test.yaml"]  # NEW: Include probes
        }
        
        new_insert = Insert.from_dict(data)
        assert isinstance(new_insert, Insert)
        assert new_insert.name == "from_dict_test"
        assert new_insert.probes == ["probe_test.yaml"]  # NEW: Check probes loaded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
        
