#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the MSite class (Using factored approach)
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.MSite import MSite, MSite_constructor
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Screen import Screen
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_instance_attributes
)


class TestMSiteInitialization:
    """Test MSite object initialization"""
    
    def test_msite_basic_initialization(self):
        """Test MSite initialization with all parameters"""
        msite = MSite(
            name="test_site",
            magnets=["magnet1", "magnet2"],
            screens=["screen1"],
            z_offset=[0.0, 5.0],
            r_offset=[1.0, 2.0],
            paralax=[0.1, 0.2]
        )
        
        assert msite.name == "test_site"
        assert msite.magnets == ["magnet1", "magnet2"]
        assert msite.screens == ["screen1"]
        assert msite.z_offset == [0.0, 5.0]
        assert msite.r_offset == [1.0, 2.0]
        assert msite.paralax == [0.1, 0.2]

    def test_msite_with_none_optional_params(self):
        """Test MSite initialization with None optional parameters"""
        msite = MSite(
            name="minimal_site",
            magnets=["magnet1"],
            screens=None,
            z_offset=None,
            r_offset=None,
            paralax=None
        )
        
        assert msite.name == "minimal_site"
        assert msite.magnets == ["magnet1"]
        assert msite.screens is None
        assert msite.z_offset is None
        assert msite.r_offset is None
        assert msite.paralax is None

    def test_msite_with_dict_magnets(self):
        """Test MSite initialization with dict magnets"""
        magnets_dict = {"insert1": "insert_data", "bitter1": "bitter_data"}
        
        msite = MSite(
            name="dict_site",
            magnets=magnets_dict,
            screens=None,
            z_offset=[0.0],
            r_offset=[0.0],
            paralax=[0.0]
        )
        
        assert msite.magnets == magnets_dict

    def test_msite_with_string_magnets(self):
        """Test MSite initialization with string magnets"""
        msite = MSite(
            name="string_site",
            magnets="magnet_file",
            screens="screen_file",
            z_offset=[1.0, 2.0],
            r_offset=[0.5, 1.5],
            paralax=[0.05, 0.15]
        )
        
        assert msite.magnets == "magnet_file"
        assert msite.screens == "screen_file"


class TestMSiteMethods:
    """Test MSite class methods"""
    
    @pytest.fixture
    def sample_msite_with_magnets(self):
        """Create an MSite with mock magnet objects"""
        # Create mock magnets
        mock_insert = Mock(spec=Insert)
        mock_insert.name = "test_insert"
        mock_insert.get_channels.return_value = ["Channel1", "Channel2"]
        mock_insert.get_names.return_value = ["Insert_Cu", "Insert_Kapton"]
        mock_insert.boundingBox.return_value = ([10.0, 20.0], [0.0, 100.0])
        
        mock_bitter = Mock(spec=Bitters)
        mock_bitter.name = "test_bitter"
        mock_bitter.get_channels.return_value = ["Slit0", "Slit1", "Slit2"]
        mock_bitter.get_names.return_value = ["Bitter_B", "Bitter_Kapton"]
        mock_bitter.boundingBox.return_value = ([15.0, 25.0], [10.0, 90.0])
        
        msite = MSite(
            name="test_msite",
            magnets=[mock_insert, mock_bitter],
            screens=None,
            z_offset=[0.0, 5.0],
            r_offset=[1.0, 2.0],
            paralax=[0.1, 0.2]
        )
        
        return msite

    @pytest.fixture
    def sample_msite_with_strings(self):
        """Create an MSite with string-based magnets and screens"""
        return MSite(
            name="string_msite",
            magnets=["magnet1", "magnet2"],
            screens=["screen1"],
            z_offset=[2.0, 3.0],
            r_offset=[0.5, 1.0],
            paralax=[0.05, 0.1]
        )

    def test_repr(self, sample_msite_with_magnets):
        """Test __repr__ method"""
        repr_str = repr(sample_msite_with_magnets)
        
        assert "name: test_msite" in repr_str
        assert "magnets:" in repr_str
        assert "screens:" in repr_str
        assert "z_offset=[0.0, 5.0]" in repr_str
        assert "r_offset=[1.0, 2.0]" in repr_str
        assert "paralax_offset=[0.1, 0.2]" in repr_str

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_method_with_string_magnets(self, mock_check_objects, mock_load_list, sample_msite_with_strings):
        """Test update method when magnets are strings"""
        # Mock check_objects to return True for strings
        mock_check_objects.side_effect = lambda objects, obj_type: obj_type == str and isinstance(objects, list)
        
        # Mock loadList to return mock objects
        mock_insert = Mock(spec=Insert)
        mock_insert.name = "loaded_insert"
        mock_load_list.side_effect = [[mock_insert], None]  # magnets, then screens
        
        sample_msite_with_strings.update()
        
        # Verify loadList was called for magnets
        assert mock_load_list.call_count >= 1
        mock_check_objects.assert_called()

    def test_get_channels(self, sample_msite_with_magnets):
        """Test get_channels method"""
        channels = sample_msite_with_magnets.get_channels("site")
        
        # Should return dict with channels from each magnet
        expected_keys = ["site_test_insert", "site_test_bitter"]
        assert set(channels.keys()) == set(expected_keys)
        
        # Verify each magnet's get_channels was called
        for magnet in sample_msite_with_magnets.magnets:
            magnet.get_channels.assert_called_once()

    def test_get_channels_no_prefix(self, sample_msite_with_magnets):
        """Test get_channels with no prefix"""
        channels = sample_msite_with_magnets.get_channels("")
        
        expected_keys = ["test_insert", "test_bitter"]
        assert set(channels.keys()) == set(expected_keys)

    def test_get_isolants(self, sample_msite_with_magnets):
        """Test get_isolants method"""
        isolants = sample_msite_with_magnets.get_isolants("site")
        
        # Currently returns empty dict according to implementation
        assert isolants == {}

    def test_get_names(self, sample_msite_with_magnets):
        """Test get_names method"""
        names = sample_msite_with_magnets.get_names("site", is2D=False)
        
        # Should combine names from all magnets
        expected_names = ["Insert_Cu", "Insert_Kapton", "Bitter_B", "Bitter_Kapton"]
        assert names == expected_names
        
        # Verify each magnet's get_names was called with correct prefix
        sample_msite_with_magnets.magnets[0].get_names.assert_called_once_with("site_test_insert", False, False)
        sample_msite_with_magnets.magnets[1].get_names.assert_called_once_with("site_test_bitter", False, False)

    def test_get_names_2d(self, sample_msite_with_magnets):
        """Test get_names method for 2D case"""
        names = sample_msite_with_magnets.get_names("site", is2D=True, verbose=True)
        
        # Verify is2D parameter is passed correctly
        for magnet in sample_msite_with_magnets.magnets:
            magnet.get_names.assert_called_once()
            # Check that True was passed for is2D parameter
            call_args = magnet.get_names.call_args[0]
            assert call_args[1] is True  # is2D parameter
            assert call_args[2] is True  # verbose parameter

    def test_bounding_box(self, sample_msite_with_magnets):
        """Test boundingBox method"""
        rb, zb = sample_msite_with_magnets.boundingBox()
        
        # Should be union of all magnet bounding boxes
        # mock_insert: r=[10.0, 20.0], z=[0.0, 100.0]
        # mock_bitter: r=[15.0, 25.0], z=[10.0, 90.0]
        # Expected: r=[10.0, 25.0], z=[0.0, 100.0]
        assert rb == [10.0, 25.0]
        assert zb == [0.0, 100.0]
        
        # Verify each magnet's boundingBox was called
        for magnet in sample_msite_with_magnets.magnets:
            magnet.boundingBox.assert_called_once()

    def test_bounding_box_single_magnet(self):
        """Test boundingBox with single magnet"""
        mock_magnet = Mock()
        mock_magnet.boundingBox.return_value = ([5.0, 15.0], [20.0, 80.0])
        
        msite = MSite(
            name="single_magnet_site",
            magnets=[mock_magnet],
            screens=None,
            z_offset=None,
            r_offset=None,
            paralax=None
        )
        
        rb, zb = msite.boundingBox()
        assert rb == [5.0, 15.0]
        assert zb == [20.0, 80.0]


class TestMSiteSerialization(BaseSerializationTestMixin):
    """Test MSite serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample MSite instance"""
        return MSite(
            name="test_msite",
            magnets=["magnet1", "magnet2"],
            screens=["screen1"],
            z_offset=[1.0, 2.0],
            r_offset=[0.5, 1.5],
            paralax=[0.1, 0.15]
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
!<Msite
name: yaml_msite
magnets: ["yaml_magnet1", "yaml_magnet2"]
screens: ["yaml_screen1"]
z_offset: [2.0, 3.0]
r_offset: [1.0, 2.0]
paralax: [0.05, 0.1]
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_msite",
            "magnets": ["magnet1", "magnet2"],
            "screens": ["screen1"],
            "z_offset": [1.0, 2.0],
            "r_offset": [0.5, 1.5],
            "paralax": [0.1, 0.15]
        }
    
    def get_class_under_test(self):
        """Return MSite class"""
        return MSite

    def test_json_includes_all_fields(self):
        """Test that JSON serialization includes all MSite fields"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "MSite"
        assert "magnets" in parsed
        assert "screens" in parsed
        assert "z_offset" in parsed
        assert "r_offset" in parsed
        assert "paralax" in parsed

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to dump MSite data"):
            instance.dump()

    def test_write_to_json_method(self):
        """Test write_to_json method"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.write_to_json()
            mock_file.assert_called_once_with("test_msite.json", "w")


class TestMSiteYAMLConstructor(BaseYAMLConstructorTestMixin):
    """Test MSite YAML constructor using common test mixin"""
    
    def get_constructor_function(self):
        """Return the MSite constructor function"""
        return MSite_constructor
    
    def get_sample_constructor_data(self):
        """Return sample constructor data"""
        return {
            "name": "constructor_msite",
            "magnets": ["constructor_magnet"],
            "screens": ["constructor_screen"],
            "z_offset": [3.0, 4.0],
            "r_offset": [1.5, 2.5],
            "paralax": [0.2, 0.25]
        }
    
    def get_expected_constructor_type(self):
        """Return expected constructor type"""
        return "MSite"

    def test_constructor_function_direct(self):
        """Test MSite_constructor function directly"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        mock_data = self.get_sample_constructor_data()
        mock_loader.construct_mapping.return_value = mock_data
        
        result = MSite_constructor(mock_loader, mock_node)
        
        # Constructor returns MSite object directly, not tuple
        assert isinstance(result, MSite)
        assert result.name == "constructor_msite"
        assert result.magnets == ["constructor_magnet"]
        assert result.screens == ["constructor_screen"]


class TestMSiteYAMLTag(BaseYAMLTagTestMixin):
    """Test MSite YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return MSite class"""
        return MSite
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "MSite"


class TestMSiteFromDict:
    """Test MSite.from_dict class method"""
    
    def test_from_dict_complete_data(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_msite",
            "magnets": ["dict_magnet1", "dict_magnet2"],
            "screens": ["dict_screen1", "dict_screen2"],
            "z_offset": [5.0, 6.0, 7.0],
            "r_offset": [2.0, 3.0, 4.0],
            "paralax": [0.3, 0.35, 0.4]
        }
        
        msite = MSite.from_dict(data)
        
        assert msite.name == "dict_msite"
        assert msite.magnets == ["dict_magnet1", "dict_magnet2"]
        assert msite.screens == ["dict_screen1", "dict_screen2"]
        assert msite.z_offset == [5.0, 6.0, 7.0]
        assert msite.r_offset == [2.0, 3.0, 4.0]
        assert msite.paralax == [0.3, 0.35, 0.4]

    def test_from_dict_minimal_data(self):
        """Test from_dict with minimal data"""
        data = {
            "name": "minimal_dict_msite",
            "magnets": ["minimal_magnet"],
            "screens": None,
            "z_offset": None,
            "r_offset": None,
            "paralax": None
        }
        
        msite = MSite.from_dict(data)
        assert msite.name == "minimal_dict_msite"
        assert msite.magnets == ["minimal_magnet"]
        assert msite.screens is None
        assert msite.z_offset is None
        assert msite.r_offset is None
        assert msite.paralax is None


class TestMSiteFileOperations:
    """Test MSite file operations"""
    
    @patch('python_magnetgeo.utils.loadYaml')
    def test_from_yaml_method(self, mock_load_yaml):
        """Test from_yaml class method"""
        mock_msite = MSite(
            name="yaml_loaded_msite",
            magnets=["yaml_magnet"],
            screens=None,
            z_offset=[0.0],
            r_offset=[0.0],
            paralax=[0.0]
        )
        mock_load_yaml.return_value = mock_msite
        
        result = MSite.from_yaml("test_msite.yaml")
        
        mock_load_yaml.assert_called_once_with("MSite", "test_msite.yaml", MSite, False)
        assert result == mock_msite

    @patch('python_magnetgeo.utils.loadJson')
    def test_from_json_method(self, mock_load_json):
        """Test from_json class method"""
        mock_msite = MSite(
            name="json_loaded_msite",
            magnets=["json_magnet"],
            screens=None,
            z_offset=[1.0],
            r_offset=[1.0],
            paralax=[0.1]
        )
        mock_load_json.return_value = mock_msite
        
        result = MSite.from_json("test_msite.json")
        
        mock_load_json.assert_called_once_with("MSite", "test_msite.json", False)
        assert result == mock_msite


class TestMSiteIntegration:
    """Integration tests for MSite class"""
    
    def test_msite_with_mixed_magnet_types(self):
        """Test MSite with different types of magnets"""
        # Create different types of mock magnets
        mock_insert = Mock(spec=Insert)
        mock_insert.name = "test_insert"
        mock_insert.get_channels.return_value = ["InsertChannel1", "InsertChannel2"]
        mock_insert.get_names.return_value = ["Insert_H1", "Insert_H2"]
        mock_insert.boundingBox.return_value = ([10.0, 30.0], [0.0, 100.0])
        
        mock_bitters = Mock(spec=Bitters)
        mock_bitters.name = "test_bitters"
        mock_bitters.get_channels.return_value = ["BittersChannel1"]
        mock_bitters.get_names.return_value = ["Bitters_B1", "Bitters_B2"]
        mock_bitters.boundingBox.return_value = ([20.0, 40.0], [10.0, 90.0])
        
        mock_supras = Mock(spec=Supras)
        mock_supras.name = "test_supras"
        mock_supras.get_channels.return_value = ["SuprasChannel1"]
        mock_supras.get_names.return_value = ["Supras_S1"]
        mock_supras.boundingBox.return_value = ([15.0, 35.0], [5.0, 95.0])
        
        msite = MSite(
            name="mixed_msite",
            magnets=[mock_insert, mock_bitters, mock_supras],
            screens=None,
            z_offset=[0.0, 5.0, 10.0],
            r_offset=[1.0, 2.0, 3.0],
            paralax=[0.1, 0.2, 0.3]
        )
        
        # Test that all magnets are handled correctly
        channels = msite.get_channels("mixed")
        assert len(channels) == 3
        
        names = msite.get_names("mixed", is2D=False)
        expected_names = ["Insert_H1", "Insert_H2", "Bitters_B1", "Bitters_B2", "Supras_S1"]
        assert names == expected_names
        
        # Test bounding box includes all magnets
        rb, zb = msite.boundingBox()
        assert rb == [10.0, 40.0]  # Union of all r bounds
        assert zb == [0.0, 100.0]  # Union of all z bounds

    def test_msite_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        original_msite = MSite(
            name="roundtrip_msite",
            magnets=["roundtrip_magnet1", "roundtrip_magnet2"],
            screens=["roundtrip_screen"],
            z_offset=[10.0, 15.0],
            r_offset=[2.0, 4.0],
            paralax=[0.5, 0.75]
        )
        
        # Test JSON serialization
        json_str = original_msite.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "MSite"
        assert parsed_json["name"] == "roundtrip_msite"
        assert parsed_json["magnets"] == ["roundtrip_magnet1", "roundtrip_magnet2"]
        assert parsed_json["screens"] == ["roundtrip_screen"]
        assert parsed_json["z_offset"] == [10.0, 15.0]
        assert parsed_json["r_offset"] == [2.0, 4.0]
        assert parsed_json["paralax"] == [0.5, 0.75]

    def test_msite_workflow_simulation(self):
        """Test MSite in a typical workflow"""
        # 1. Create MSite with string-based magnet references
        msite = MSite(
            name="workflow_msite",
            magnets=["workflow_insert", "workflow_bitter"],
            screens=["workflow_screen"],
            z_offset=[0.0, 5.0],
            r_offset=[0.0, 2.0],
            paralax=[0.0, 0.1]
        )
        
        # 2. Simulate update process (loading actual objects)
        mock_insert = Mock(spec=Insert)
        mock_insert.name = "workflow_insert"
        mock_insert.get_channels.return_value = ["Chan1", "Chan2"]
        mock_insert.get_names.return_value = ["Insert_Part1", "Insert_Part2"]
        mock_insert.boundingBox.return_value = ([8.0, 18.0], [0.0, 80.0])
        
        mock_bitter = Mock(spec=Bitters)
        mock_bitter.name = "workflow_bitter"
        mock_bitter.get_channels.return_value = ["Slit1", "Slit2"]
        mock_bitter.get_names.return_value = ["Bitter_Part1"]
        mock_bitter.boundingBox.return_value = ([12.0, 22.0], [10.0, 70.0])
        
        # Manually update for testing (simulating successful load)
        msite.magnets = [mock_insert, mock_bitter]
        
        # 3. Test operations work correctly
        channels = msite.get_channels("workflow")
        assert len(channels) == 2
        
        names = msite.get_names("workflow")
        assert len(names) == 3
        
        rb, zb = msite.boundingBox()
        assert rb == [8.0, 22.0]
        assert zb == [0.0, 80.0]
        
        # 4. Test serialization of loaded site
        json_str = msite.to_json()
        assert "workflow_msite" in json_str




class TestMSitePerformance:
    """Performance tests for MSite class"""
    
    def test_msite_with_many_magnets(self):
        """Test MSite performance with many magnets"""
        # Create many mock magnets
        mock_magnets = []
        for i in range(50):
            mock_magnet = Mock()
            mock_magnet.name = f"magnet_{i}"
            mock_magnet.get_channels.return_value = [f"Channel_{i}_1", f"Channel_{i}_2"]
            mock_magnet.get_names.return_value = [f"Magnet_{i}_Part1", f"Magnet_{i}_Part2"]
            mock_magnet.boundingBox.return_value = ([i * 2.0, (i + 1) * 2.0], [0.0, 100.0])
            mock_magnets.append(mock_magnet)
        
        msite = MSite(
            name="many_magnets_site",
            magnets=mock_magnets,
            screens=None,
            z_offset=None,
            r_offset=None,
            paralax=None
        )
        
        # Test that operations still work efficiently
        channels = msite.get_channels("many")
        assert len(channels) == 50
        
        names = msite.get_names("many")
        assert len(names) == 100  # 2 names per magnet * 50 magnets
        
        # Test bounding box calculation
        rb, zb = msite.boundingBox()
        assert rb == [0.0, 100.0]  # Should span all magnet bounds
        assert zb == [0.0, 100.0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
