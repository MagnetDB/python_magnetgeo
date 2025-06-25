#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test suite for Supra class using test_utils_common mixins
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type, Optional

# Import the class under test
from python_magnetgeo.Supra import Supra, Supra_constructor

# Import test utilities
from .test_utils_common import (
    BaseSerializationTestMixin,
    BaseYAMLConstructorTestMixin,
    BaseYAMLTagTestMixin,
    assert_json_structure,
    assert_instance_attributes,
    validate_geometric_data,
    parametrize_basic_values,
    temp_yaml_file,
    temp_json_file
)


class TestSupra(BaseSerializationTestMixin, BaseYAMLTagTestMixin):
    """
    Test class for Supra using common test mixins
    """
    
    # Implementation of BaseSerializationTestMixin abstract methods
    def get_sample_instance(self):
        """Return a sample Supra instance for testing"""
        return Supra(
            name="test_supra",
            r=[10.0, 50.0],
            z=[0.0, 100.0],
            n=25,
            struct="test_structure"
        )
    
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        return """
!<Supra>
name: test_supra
r: [10.0, 50.0]
z: [0.0, 100.0]
n: 25
struct: test_structure
"""
    
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        return {
            "name": "test_supra",
            "r": [10.0, 50.0],
            "z": [0.0, 100.0],
            "n": 25,
            "struct": "test_structure",
            "detail": "None"  # Default value
        }
    
    def get_class_under_test(self) -> Type:
        """Return the Supra class"""
        return Supra
    
    # Implementation of BaseYAMLTagTestMixin abstract methods
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        return Supra
    
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        return "Supra"


class TestSupraConstructor(BaseYAMLConstructorTestMixin):
    """
    Test class for Supra YAML constructor
    """
    
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        def wrapper(loader, node):
            result = Supra_constructor(loader, node)
            # Return the actual result and its type name, not the __dict__
            return result, type(result).__name__
        return wrapper
    
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        return {
            "name": "constructor_test",
            "r": [15.0, 45.0],
            "z": [5.0, 95.0],
            "n": 30,
            "struct": "constructor_structure"
        }
    
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        return "Supra"
    
    # Override the inherited test method that's causing issues
    def test_yaml_constructor_function(self):
        """Test the YAML constructor function"""
        constructor_func = self.get_constructor_function()
        
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = self.get_sample_constructor_data()
        mock_loader.construct_mapping.return_value = mock_data
        
        result, result_type = constructor_func(mock_loader, mock_node)
        
        # Check that we get a Supra instance with the expected attributes
        assert isinstance(result, Supra)
        assert result_type == self.get_expected_constructor_type()
        assert result.name == mock_data["name"]
        assert result.r == mock_data["r"]
        assert result.z == mock_data["z"]
        assert result.n == mock_data["n"]
        assert result.struct == mock_data["struct"]
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestSupraSpecific:
    """
    Specific tests for Supra functionality not covered by mixins
    """
    
    @pytest.fixture
    def sample_supra(self):
        """Fixture providing a sample Supra instance"""
        return Supra(
            name="sample_supra",
            r=[20.0, 80.0],
            z=[10.0, 110.0],
            n=50,
            struct="sample_structure"
        )
    
    @pytest.fixture
    def minimal_supra(self):
        """Fixture providing a minimal Supra instance"""
        return Supra(name="minimal", r=[0.0, 1.0], z=[0.0, 1.0], n=1, struct="")
    
    @pytest.fixture
    def mock_hts_insert(self):
        """Fixture providing a mock HTSinsert object"""
        mock_hts = Mock()
        mock_hts.getR0.return_value = 15.0
        mock_hts.getR1.return_value = 35.0
        mock_hts.getZ0.return_value = 25.0
        mock_hts.getH.return_value = 50.0
        mock_hts.getNtapes.return_value = [10, 15, 20]  # Total = 45
        mock_hts.get_lc.return_value = 2.5
        mock_hts.get_names.return_value = ["hts_name1", "hts_name2"]
        return mock_hts
    
    def test_init_with_parameters(self):
        """Test Supra initialization with all parameters"""
        supra = Supra(
            name="init_test",
            r=[5.0, 25.0],
            z=[0.0, 50.0],
            n=15,
            struct="init_structure"
        )
        assert supra.name == "init_test"
        assert supra.r == [5.0, 25.0]
        assert supra.z == [0.0, 50.0]
        assert supra.n == 15
        assert supra.struct == "init_structure"
        assert supra.detail == "None"  # Default value
    
    def test_init_default_n_and_struct(self):
        """Test Supra initialization with default n and struct"""
        supra = Supra(name="default_test", r=[1.0, 2.0], z=[0.0, 1.0])
        assert supra.name == "default_test"
        assert supra.r == [1.0, 2.0]
        assert supra.z == [0.0, 1.0]
        assert supra.n == 0  # Default value
        assert supra.struct == ""  # Default value
        assert supra.detail == "None"
    
    def test_repr(self, sample_supra):
        """Test string representation"""
        repr_str = repr(sample_supra)
        assert "Supra" in repr_str
        assert "name='sample_supra'" in repr_str
        assert "r=[20.0, 80.0]" in repr_str
        assert "z=[10.0, 110.0]" in repr_str
        assert "n=50" in repr_str
        assert "struct='sample_structure'" in repr_str
        assert "detail='None'" in repr_str
    
    def test_get_magnet_struct(self, sample_supra):
        """Test get_magnet_struct method"""
        with patch('python_magnetgeo.SupraStructure.HTSinsert.fromcfg') as mock_fromcfg:
            mock_hts = Mock()
            mock_fromcfg.return_value = mock_hts
            
            result = sample_supra.get_magnet_struct()
            
            mock_fromcfg.assert_called_once_with("sample_structure", None)
            assert result == mock_hts
    
    def test_get_magnet_struct_with_directory(self, sample_supra):
        """Test get_magnet_struct method with directory parameter"""
        with patch('python_magnetgeo.SupraStructure.HTSinsert.fromcfg') as mock_fromcfg:
            mock_hts = Mock()
            mock_fromcfg.return_value = mock_hts
            
            result = sample_supra.get_magnet_struct("/test/directory")
            
            mock_fromcfg.assert_called_once_with("sample_structure", "/test/directory")
            assert result == mock_hts
    
    def test_check_dimensions_no_struct(self, sample_supra):
        """Test check_dimensions with empty struct"""
        empty_struct_supra = Supra(name="no_struct", r=[1.0, 2.0], z=[0.0, 1.0], n=5, struct="")
        mock_magnet = Mock()
        
        # Should not modify anything when struct is empty
        original_r = empty_struct_supra.r.copy()
        original_z = empty_struct_supra.z.copy()
        original_n = empty_struct_supra.n
        
        empty_struct_supra.check_dimensions(mock_magnet)
        
        assert empty_struct_supra.r == original_r
        assert empty_struct_supra.z == original_z
        assert empty_struct_supra.n == original_n
    
    def test_check_dimensions_with_struct(self, mock_hts_insert):
        """Test check_dimensions with struct that updates dimensions"""
        supra = Supra(
            name="check_dims",
            r=[10.0, 30.0],  # Different from mock values
            z=[0.0, 40.0],   # Different from mock values
            n=20,            # Different from mock value (45)
            struct="test_struct"
        )
        
        with patch('builtins.print'):  # Suppress print output
            supra.check_dimensions(mock_hts_insert)
        
        # Should update to match mock values
        assert supra.r[0] == 15.0  # mock_hts.getR0()
        assert supra.r[1] == 35.0  # mock_hts.getR1()
        assert supra.z[0] == 0.0   # getZ0() - getH()/2 = 25 - 50/2 = 0
        assert supra.z[1] == 50.0  # getZ0() + getH()/2 = 25 + 50/2 = 50
        assert supra.n == 45       # sum(getNtapes()) = 10+15+20 = 45
    
    def test_check_dimensions_no_changes_needed(self, mock_hts_insert):
        """Test check_dimensions when no changes are needed"""
        supra = Supra(
            name="no_changes",
            r=[15.0, 35.0],  # Matches mock values
            z=[0.0, 50.0],   # Matches mock values
            n=45,            # Matches mock value
            struct="test_struct"
        )
        
        with patch('builtins.print') as mock_print:
            supra.check_dimensions(mock_hts_insert)
        
        # Should not print change message
        mock_print.assert_not_called()
    
    def test_get_lc_detail_none(self, sample_supra):
        """Test get_lc method with detail='None'"""
        sample_supra.detail = "None"
        lc = sample_supra.get_lc()
        expected_lc = (80.0 - 20.0) / 5.0  # (r[1] - r[0]) / 5.0
        assert lc == expected_lc
        assert lc == 12.0
    
    def test_get_lc_detail_not_none(self, sample_supra, mock_hts_insert):
        """Test get_lc method with detail != 'None'"""
        sample_supra.detail = "dblpancake"
        
        with patch.object(sample_supra, 'get_magnet_struct', return_value=mock_hts_insert):
            lc = sample_supra.get_lc()
            assert lc == 2.5  # From mock_hts.get_lc()
    
    def test_get_channels_returns_empty_list(self, sample_supra):
        """Test get_channels method returns empty list"""
        channels = sample_supra.get_channels("test_magnet")
        assert channels == []
        
        channels_with_params = sample_supra.get_channels("test", hideIsolant=False, debug=True)
        assert channels_with_params == []
    
    def test_get_isolants_returns_empty_list(self, sample_supra):
        """Test get_isolants method returns empty list"""
        isolants = sample_supra.get_isolants("test_magnet")
        assert isolants == []
        
        isolants_with_debug = sample_supra.get_isolants("test", debug=True)
        assert isolants_with_debug == []
    
    def test_get_names_detail_none(self, sample_supra):
        """Test get_names method with detail='None'"""
        sample_supra.detail = "None"
        
        names = sample_supra.get_names("prefix")
        expected_names = ["prefix_sample_supra"]
        assert names == expected_names
        
        names_no_prefix = sample_supra.get_names("")
        expected_names_no_prefix = ["sample_supra"]
        assert names_no_prefix == expected_names_no_prefix
    
    def test_get_names_detail_not_none(self, sample_supra, mock_hts_insert):
        """Test get_names method with detail != 'None'"""
        sample_supra.detail = "pancake"
        
        with patch.object(sample_supra, 'get_magnet_struct', return_value=mock_hts_insert):
            with patch.object(sample_supra, 'check_dimensions'):
                names = sample_supra.get_names("prefix", is2D=True, verbose=True)
                
                mock_hts_insert.get_names.assert_called_once_with(
                    mname="prefix", detail="pancake", verbose=True
                )
                assert names == ["hts_name1", "hts_name2"]
    
    @pytest.mark.parametrize("is2D,verbose", [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_names_parameters(self, sample_supra, is2D, verbose):
        """Test get_names method with different parameter combinations"""
        sample_supra.detail = "None"
        
        names = sample_supra.get_names("test", is2D=is2D, verbose=verbose)
        expected_names = ["test_sample_supra"]
        assert names == expected_names
    
    def test_write_to_json_creates_file(self, sample_supra):
        """Test write_to_json method creates file"""
        with patch("builtins.open", mock_open()) as mock_file:
            sample_supra.write_to_json()
            mock_file.assert_called_once_with("sample_supra.json", "w")
    
    def test_write_to_json_content(self, sample_supra):
        """Test write_to_json method writes correct content"""
        mock_file_handle = mock_open()
        with patch("builtins.open", mock_file_handle):
            sample_supra.write_to_json()
            
            # Get the written content
            written_content = mock_file_handle().write.call_args[0][0]
            
            # Should be valid JSON
            parsed = json.loads(written_content)
            assert parsed["__classname__"] == "Supra"
            assert parsed["name"] == "sample_supra"
    
    def test_get_Nturns_no_struct(self, sample_supra):
        """Test get_Nturns method without struct"""
        sample_supra.struct = ""
        nturns = sample_supra.get_Nturns()
        assert nturns == 50  # Should return self.n
    
    def test_get_Nturns_with_struct(self, sample_supra):
        """Test get_Nturns method with struct"""
        sample_supra.struct = "test_struct"
        
        with patch('builtins.print'):  # Suppress print output
            nturns = sample_supra.get_Nturns()
            assert nturns == -1  # Should return -1 when struct is present
    
    @pytest.mark.parametrize("detail,expected", [
        ("None", "None"),
        ("dblpancake", "dblpancake"),
        ("pancake", "pancake"),
        ("tape", "tape"),
    ])
    def test_set_Detail_valid_values(self, sample_supra, detail, expected):
        """Test set_Detail method with valid values"""
        sample_supra.set_Detail(detail)
        assert sample_supra.detail == expected
    
    @pytest.mark.parametrize("invalid_detail", [
        "invalid",
        "NONE",  # Case sensitive
        "double_pancake",
        "tapes",
        "",
        None
    ])
    def test_set_Detail_invalid_values(self, sample_supra, invalid_detail):
        """Test set_Detail method with invalid values"""
        with pytest.raises(Exception, match="unexpected detail value"):
            sample_supra.set_Detail(invalid_detail)
    
    def test_yaml_constructor_function_direct(self):
        """Test the Supra_constructor function directly"""
        mock_loader = Mock()
        mock_node = Mock()
        
        test_data = {
            "name": "direct_test",
            "r": [30.0, 70.0],
            "z": [20.0, 120.0],
            "n": 40,
            "struct": "direct_structure"
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Supra_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Supra)
        assert result.name == "direct_test"
        assert result.r == [30.0, 70.0]
        assert result.z == [20.0, 120.0]
        assert result.n == 40
        assert result.struct == "direct_structure"
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class TestSupraFromDict:
    """
    Test the from_dict class method
    """
    
    def test_from_dict_complete(self):
        """Test from_dict with complete data"""
        data = {
            "name": "dict_test",
            "r": [12.0, 48.0],
            "z": [5.0, 105.0],
            "n": 35,
            "struct": "dict_structure"
        }
        
        supra = Supra.from_dict(data)
        
        assert supra.name == "dict_test"
        assert supra.r == [12.0, 48.0]
        assert supra.z == [5.0, 105.0]
        assert supra.n == 35
        assert supra.struct == "dict_structure"
    
    def test_from_dict_with_debug(self):
        """Test from_dict with debug parameter"""
        data = {
            "name": "debug_test",
            "r": [1.0, 2.0],
            "z": [0.0, 1.0],
            "n": 5,
            "struct": "debug_struct"
        }
        
        supra = Supra.from_dict(data, debug=True)
        assert supra.name == "debug_test"
    
    def test_from_dict_missing_fields(self):
        """Test from_dict with missing required fields"""
        # Missing 'name'
        data1 = {
            "r": [1.0, 2.0],
            "z": [0.0, 1.0],
            "n": 5,
            "struct": "test"
        }
        
        with pytest.raises(KeyError):
            Supra.from_dict(data1)
        
        # Missing 'r'
        data2 = {
            "name": "no_r",
            "z": [0.0, 1.0],
            "n": 5,
            "struct": "test"
        }
        
        with pytest.raises(KeyError):
            Supra.from_dict(data2)


class TestSupraGeometry:
    """
    Test geometric operations for Supra
    """
    
    @pytest.fixture
    def geometric_supra(self):
        """Fixture with Supra having known geometric bounds"""
        return Supra(
            name="geometric_test",
            r=[10.0, 40.0],
            z=[5.0, 25.0],
            n=20,
            struct="geo_struct"
        )
    
    def test_boundingBox_returns_coordinates(self, geometric_supra):
        """Test boundingBox method returns r and z coordinates"""
        rb, zb = geometric_supra.boundingBox()
        
        assert rb == [10.0, 40.0]
        assert zb == [5.0, 25.0]
        assert rb == geometric_supra.r
        assert zb == geometric_supra.z
    
    def test_boundingBox_various_coordinates(self):
        """Test boundingBox with various coordinate combinations"""
        test_cases = [
            ([0.0, 1.0], [0.0, 1.0]),
            ([5.0, 15.0], [10.0, 20.0]),
            ([-5.0, 5.0], [-10.0, 10.0]),  # Negative coordinates
            ([100.0, 200.0], [500.0, 600.0]),  # Large coordinates
        ]
        
        for r_vals, z_vals in test_cases:
            supra = Supra(name="bbox_test", r=r_vals, z=z_vals, n=1, struct="")
            rb, zb = supra.boundingBox()
            assert rb == r_vals
            assert zb == z_vals
    
    @pytest.mark.parametrize("test_r,test_z,expected", [
        ([5.0, 45.0], [0.0, 30.0], True),    # Overlaps completely
        ([15.0, 35.0], [10.0, 20.0], True),  # Overlaps inside
        ([0.0, 50.0], [0.0, 30.0], True),    # Overlaps extending beyond
        ([50.0, 60.0], [5.0, 25.0], False),  # No overlap (too far in r)
        ([10.0, 40.0], [30.0, 40.0], False), # No overlap (too far in z)
        ([0.0, 5.0], [0.0, 2.0], False),     # No overlap (too small)
    ])
    def test_intersect(self, geometric_supra, test_r, test_z, expected):
        """Test intersect method with various test rectangles"""
        result = geometric_supra.intersect(test_r, test_z)
        assert result == expected
    
    def test_intersect_edge_cases(self, geometric_supra):
        """Test intersect method edge cases"""
        # Test with identical bounds
        rb, zb = geometric_supra.boundingBox()
        assert geometric_supra.intersect(rb, zb) is True
        
        # Test with very small overlap
        small_overlap_r = [39.9, 40.1]  # Tiny overlap with max r
        small_overlap_z = [24.9, 25.1]  # Tiny overlap with max z
        assert geometric_supra.intersect(small_overlap_r, small_overlap_z) is True
    
    def test_intersect_algorithm_details(self):
        """Test the specific intersection algorithm implementation"""
        supra = Supra(name="algo_test", r=[10.0, 20.0], z=[5.0, 15.0], n=1, struct="")
        
        # Test case that should definitely intersect
        test_r = [12.0, 18.0]  # Inside supra r range
        test_z = [7.0, 13.0]   # Inside supra z range
        
        # The algorithm should return True for overlapping rectangles
        assert supra.intersect(test_r, test_z) is True


class TestSupraDetailLevels:
    """
    Test different detail levels for Supra
    """
    
    @pytest.fixture
    def detail_supra(self):
        """Fixture for testing detail levels"""
        return Supra(
            name="detail_test",
            r=[10.0, 30.0],
            z=[0.0, 50.0],
            n=25,
            struct="detail_struct"
        )
    
    @pytest.fixture
    def mock_hts_insert(self):
        """Fixture providing a mock HTSinsert object for detail level tests"""
        mock_hts = Mock()
        mock_hts.getR0.return_value = 15.0
        mock_hts.getR1.return_value = 35.0
        mock_hts.getZ0.return_value = 25.0
        mock_hts.getH.return_value = 50.0
        mock_hts.getNtapes.return_value = [10, 15, 20]  # Total = 45
        mock_hts.get_lc.return_value = 2.5
        mock_hts.get_names.return_value = ["hts_name1", "hts_name2"]
        return mock_hts
    
    @pytest.mark.parametrize("detail_level", ["None", "dblpancake", "pancake", "tape"])
    def test_valid_detail_levels(self, detail_supra, detail_level):
        """Test all valid detail levels"""
        detail_supra.set_Detail(detail_level)
        assert detail_supra.detail == detail_level
    
    def test_detail_affects_get_lc(self, detail_supra, mock_hts_insert):
        """Test that detail level affects get_lc calculation"""
        # Test with detail="None"
        detail_supra.set_Detail("None")
        lc_none = detail_supra.get_lc()
        expected_lc_none = (30.0 - 10.0) / 5.0  # 4.0
        assert lc_none == expected_lc_none
        
        # Test with detail != "None"
        detail_supra.set_Detail("pancake")
        with patch.object(detail_supra, 'get_magnet_struct', return_value=mock_hts_insert):
            lc_pancake = detail_supra.get_lc()
            assert lc_pancake == 2.5  # From mock
    
    def test_detail_affects_get_names(self, detail_supra, mock_hts_insert):
        """Test that detail level affects get_names behavior"""
        # Test with detail="None"
        detail_supra.set_Detail("None")
        names_none = detail_supra.get_names("test")
        assert names_none == ["test_detail_test"]
        
        # Test with detail != "None"
        detail_supra.set_Detail("dblpancake")
        with patch.object(detail_supra, 'get_magnet_struct', return_value=mock_hts_insert):
            with patch.object(detail_supra, 'check_dimensions'):
                names_detail = detail_supra.get_names("test", verbose=True)
                mock_hts_insert.get_names.assert_called_once_with(
                    mname="test", detail="dblpancake", verbose=True
                )
                assert names_detail == ["hts_name1", "hts_name2"]


class TestSupraErrorHandling:
    """
    Test error handling and edge cases for Supra
    """
    
    @pytest.fixture
    def sample_supra(self):
        """Fixture providing a sample Supra instance for error handling tests"""
        return Supra(
            name="error_test_supra",
            r=[20.0, 80.0],
            z=[10.0, 110.0],
            n=50,
            struct="error_test_structure"
        )
    
    def test_init_with_invalid_detail(self):
        """Test initialization with invalid detail values"""
        supra = Supra(name="test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        # Should raise exception for invalid detail values
        with pytest.raises(Exception, match="unexpected detail value"):
            supra.set_Detail("invalid_detail")
    
    def test_get_magnet_struct_with_import_error(self, sample_supra):
        """Test get_magnet_struct when import fails"""
        with patch('python_magnetgeo.SupraStructure.HTSinsert.fromcfg', side_effect=ImportError("Module not found")):
            with pytest.raises(ImportError):
                sample_supra.get_magnet_struct()
    
    def test_check_dimensions_with_missing_methods(self):
        """Test check_dimensions with incomplete magnet object"""
        supra = Supra(name="test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="test_struct")
        
        # Mock magnet without required methods
        incomplete_magnet = Mock()
        del incomplete_magnet.getR0  # Remove required method
        
        with pytest.raises(AttributeError):
            supra.check_dimensions(incomplete_magnet)
    
    def test_to_json_with_serialization_error(self, sample_supra):
        """Test to_json when serialization fails"""
        with patch('python_magnetgeo.deserialize.serialize_instance', side_effect=TypeError("Cannot serialize")):
            with pytest.raises(TypeError):
                sample_supra.to_json()
    
    def test_dump_with_file_permission_error(self, sample_supra):
        """Test dump method with file permission error"""
        with patch('python_magnetgeo.utils.writeYaml', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception):
                sample_supra.dump()
    
    def test_write_to_json_with_io_error(self, sample_supra):
        """Test write_to_json with I/O error"""
        with patch("builtins.open", side_effect=IOError("Disk full")):
            with pytest.raises(IOError):
                sample_supra.write_to_json()


class TestSupraIntegration:
    """
    Integration tests for Supra with real-world scenarios
    """
    
    def test_complete_workflow(self):
        """Test complete workflow: create, serialize, deserialize"""
        # Create original instance
        original = Supra(
            name="integration_test",
            r=[25.0, 75.0],
            z=[10.0, 90.0],
            n=100,
            struct="integration_struct"
        )
        original.set_Detail("pancake")
        
        # Serialize to JSON
        json_str = original.to_json()
        
        # Verify JSON structure
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Supra"
        assert parsed["name"] == "integration_test"
        assert parsed["detail"] == "pancake"
    
    def test_yaml_integration(self):
        """Test YAML serialization integration"""
        supra = Supra(
            name="yaml_integration",
            r=[15.0, 45.0],
            z=[5.0, 55.0],
            n=75,
            struct="yaml_struct"
        )
        
        # Test YAML tag is properly set
        assert hasattr(Supra, 'yaml_tag')
        assert Supra.yaml_tag == "Supra"
        
        # Test constructor function exists and is callable
        assert callable(Supra_constructor)
        
        # Test that we can create a Supra using the constructor
        mock_loader = Mock()
        mock_node = Mock()
        test_data = {
            "name": "yaml_test",
            "r": [1.0, 2.0],
            "z": [0.0, 1.0],
            "n": 1,
            "struct": "test"
        }
        mock_loader.construct_mapping.return_value = test_data
        
        result = Supra_constructor(mock_loader, mock_node)
        assert isinstance(result, Supra)
        assert result.name == "yaml_test"
    
    def test_geometric_operations_integration(self):
        """Test integration of geometric operations"""
        supra = Supra(
            name="geo_integration",
            r=[20.0, 60.0],
            z=[15.0, 85.0],
            n=40,
            struct="geo_struct"
        )
        
        # Test bounding box
        rb, zb = supra.boundingBox()
        assert rb == [20.0, 60.0]
        assert zb == [15.0, 85.0]
        
        # Test intersection with various geometries
        test_cases = [
            # (test_r, test_z, expected_result)
            ([10.0, 30.0], [10.0, 20.0], True),   # Partial overlap
            ([50.0, 70.0], [80.0, 90.0], True),   # Partial overlap
            ([0.0, 10.0], [0.0, 10.0], False),    # No overlap
            ([70.0, 80.0], [90.0, 100.0], False), # No overlap
            ([25.0, 55.0], [20.0, 80.0], True),   # Contained within
        ]
        
        for test_r, test_z, expected in test_cases:
            result = supra.intersect(test_r, test_z)
            assert result == expected, f"Failed for r={test_r}, z={test_z}"


class TestSupraCompatibility:
    """
    Test Supra compatibility with different Python versions and edge cases
    """
    
    def test_floating_point_precision(self):
        """Test Supra with floating point precision edge cases"""
        precision_values = [
            1.0000000000001,
            1.9999999999999,
            0.1 + 0.2,  # Classic floating point precision issue
            1e-15,
            1e15
        ]
        
        for i, val in enumerate(precision_values[:-1]):
            supra = Supra(
                name=f"precision_test_{i}",
                r=[val, precision_values[i+1]],
                z=[0.0, 1.0],
                n=1,
                struct=""
            )
            
            # Values should be preserved as-is
            assert supra.r[0] == val
            assert supra.r[1] == precision_values[i+1]
            
            # JSON serialization should handle these values
            json_str = supra.to_json()
            parsed = json.loads(json_str)
            
            # Should be reasonably close (within floating point precision)
            assert abs(parsed["r"][0] - val) < 1e-10
            assert abs(parsed["r"][1] - precision_values[i+1]) < 1e-10
    
    def test_unicode_string_handling(self):
        """Test Supra with Unicode strings"""
        unicode_names = [
            "test_ñoño",
            "магнит",  # Russian
            "磁石",    # Japanese
            "🧲",      # Emoji
            "test with spaces",
            "test\nwith\nnewlines",
            "test\twith\ttabs"
        ]
        
        for name in unicode_names:
            supra = Supra(
                name=name,
                r=[1.0, 2.0],
                z=[0.0, 1.0],
                n=1,
                struct=""
            )
            
            assert supra.name == name
            
            # JSON serialization should handle Unicode
            json_str = supra.to_json()
            parsed = json.loads(json_str)
            assert parsed["name"] == name
    
    def test_extreme_numeric_values(self):
        """Test Supra with extreme numeric values"""
        extreme_cases = [
            # (r_values, z_values, n_value)
            ([0.0, 0.0], [0.0, 0.0], 0),           # Zero values
            ([1e-10, 2e-10], [1e-10, 2e-10], 1),   # Very small values
            ([1e10, 2e10], [1e10, 2e10], 1000000), # Very large values
            ([-1e5, 1e5], [-1e5, 1e5], 1),         # Negative values
        ]
        
        for i, (r_vals, z_vals, n_val) in enumerate(extreme_cases):
            supra = Supra(
                name=f"extreme_test_{i}",
                r=r_vals,
                z=z_vals,
                n=n_val,
                struct=""
            )
            
            assert supra.r == r_vals
            assert supra.z == z_vals
            assert supra.n == n_val
            
            # Should be able to serialize
            json_str = supra.to_json()
            parsed = json.loads(json_str)
            assert parsed["r"] == r_vals
            assert parsed["z"] == z_vals
            assert parsed["n"] == n_val
    
    def test_mixed_numeric_types(self):
        """Test Supra with mixed int/float types"""
        supra = Supra(
            name="mixed_types",
            r=[1, 2.5],      # int and float
            z=[0.0, 10],     # float and int
            n=42,            # int
            struct=""
        )
        
        assert supra.r == [1, 2.5]
        assert supra.z == [0.0, 10]
        assert supra.n == 42
        
        # Types should be preserved through JSON serialization
        json_str = supra.to_json()
        parsed = json.loads(json_str)
        assert parsed["r"] == [1, 2.5]
        assert parsed["z"] == [0.0, 10]
        assert parsed["n"] == 42


class TestSupraPerformance:
    """
    Performance tests for Supra operations
    """
    
    @pytest.mark.performance
    def test_repeated_operations(self):
        """Test performance of repeated operations"""
        supra = Supra(
            name="repeated_ops",
            r=[10.0, 50.0],
            z=[0.0, 100.0],
            n=25,
            struct=""
        )
        
        # Repeated bounding box calls should be fast
        for _ in range(1000):
            rb, zb = supra.boundingBox()
            assert rb == [10.0, 50.0]
            assert zb == [0.0, 100.0]
        
        # Repeated intersection calls should be fast
        for _ in range(1000):
            result = supra.intersect([20.0, 40.0], [25.0, 75.0])
            assert result is True
    


class TestSupraUseCases:
    """
    Test Supra with realistic use cases and scenarios
    """
    
    def test_solenoid_magnet_modeling(self):
        """Test Supra representing a solenoid magnet"""
        solenoid = Supra(
            name="main_solenoid",
            r=[50.0, 150.0],  # 50mm inner, 150mm outer radius
            z=[0.0, 300.0],   # 300mm height
            n=1000,           # 1000 turns
            struct="solenoid_nb3sn_tape"
        )
        
        # Set appropriate detail level
        solenoid.set_Detail("dblpancake")
        
        # Test properties
        assert solenoid.name == "main_solenoid"
        assert solenoid.r == [50.0, 150.0]
        assert solenoid.z == [0.0, 300.0]
        assert solenoid.n == 1000
        assert solenoid.detail == "dblpancake"
        
        # Test geometric operations
        rb, zb = solenoid.boundingBox()
        assert rb == [50.0, 150.0]
        assert zb == [0.0, 300.0]
        
        # Test intersection with bore
        bore_intersect = solenoid.intersect([0.0, 60.0], [50.0, 250.0])
        assert bore_intersect is True
        
        # Test no intersection outside magnet
        outside_intersect = solenoid.intersect([200.0, 250.0], [0.0, 300.0])
        assert outside_intersect is False
    
    def test_correction_coil_modeling(self):
        """Test Supra representing a correction coil"""
        correction_coil = Supra(
            name="z_correction_coil",
            r=[200.0, 220.0],  # Thin coil
            z=[100.0, 120.0],  # Short coil
            n=50,              # Few turns
            struct="correction_coil_structure"
        )
        
        # Correction coils typically have simple detail
        correction_coil.set_Detail("None")
        
        # Test properties
        assert correction_coil.name == "z_correction_coil"
        assert correction_coil.detail == "None"
        
        # Test characteristic length calculation
        lc = correction_coil.get_lc()
        expected_lc = (220.0 - 200.0) / 5.0  # 4.0
        assert lc == expected_lc
        
        # Test naming
        names = correction_coil.get_names("system")
        assert names == ["system_z_correction_coil"]
    
    def test_insert_magnet_modeling(self):
        """Test Supra representing an insert magnet with detailed structure"""
        insert = Supra(
            name="hts_insert",
            r=[30.0, 45.0],   # Small insert
            z=[50.0, 250.0],  # Tall insert
            n=200,            # Many turns
            struct="rebco_tape_insert"
        )
        
        # Insert magnets need detailed modeling
        insert.set_Detail("tape")
        
        # Mock the magnet structure for testing
        mock_hts = Mock()
        mock_hts.getR0.return_value = 30.0
        mock_hts.getR1.return_value = 45.0
        mock_hts.getZ0.return_value = 150.0
        mock_hts.getH.return_value = 200.0
        mock_hts.getNtapes.return_value = [50, 50, 50, 50]  # 4 pancakes, 200 total
        mock_hts.get_lc.return_value = 0.5
        mock_hts.get_names.return_value = ["tape_1", "tape_2", "mandrin", "isolation"]
        
        with patch.object(insert, 'get_magnet_struct', return_value=mock_hts):
            # Test dimension checking
            insert.check_dimensions(mock_hts)
            
            # Test detailed naming
            names = insert.get_names("system", verbose=False)
            assert names == ["tape_1", "tape_2", "mandrin", "isolation"]
            
            # Test characteristic length
            lc = insert.get_lc()
            assert lc == 0.5
    
    def test_magnet_system_integration(self):
        """Test multiple Supra objects in a system"""
        # Create background magnet
        background = Supra(
            name="background_magnet",
            r=[400.0, 600.0],
            z=[-500.0, 500.0],
            n=2000,
            struct="nb3sn_background"
        )
        
        # Create insert magnet
        insert = Supra(
            name="insert_magnet",
            r=[50.0, 80.0],
            z=[-100.0, 100.0],
            n=500,
            struct="rebco_insert"
        )
        
        # Create correction coils
        correction_coils = []
        for i in range(4):
            coil = Supra(
                name=f"correction_coil_{i+1}",
                r=[300.0 + i*10, 320.0 + i*10],
                z=[-50.0 + i*25, 50.0 + i*25],
                n=25,
                struct="correction_structure"
            )
            correction_coils.append(coil)
        
        # Test that all magnets have different geometries
        all_magnets = [background, insert] + correction_coils
        
        for i, magnet1 in enumerate(all_magnets):
            for j, magnet2 in enumerate(all_magnets):
                if i != j:
                    # Different magnets should have different names
                    assert magnet1.name != magnet2.name
                    
                    # Test intersection relationships
                    rb1, zb1 = magnet1.boundingBox()
                    rb2, zb2 = magnet2.boundingBox()
                    
                    # Some magnets should intersect, others should not
                    intersects = magnet1.intersect(rb2, zb2)
                    # This will depend on the specific geometry
                    assert isinstance(intersects, bool)
    
    def test_empty_bore_region(self):
        """Test Supra representing an empty bore region"""
        bore = Supra(
            name="experimental_bore",
            r=[0.0, 40.0],    # 40mm radius bore
            z=[0.0, 200.0],   # 200mm height
            n=0,              # No turns (empty space)
            struct=""         # No structure
        )
        
        # Bore regions don't have detail
        bore.set_Detail("None")
        
        # Test properties
        assert bore.name == "experimental_bore"
        assert bore.n == 0
        assert bore.struct == ""
        assert bore.detail == "None"
        
        # Test geometric operations
        rb, zb = bore.boundingBox()
        assert rb == [0.0, 40.0]
        assert zb == [0.0, 200.0]
        
        # Test intersection with sample space
        sample_intersect = bore.intersect([10.0, 30.0], [50.0, 150.0])
        assert sample_intersect is True
        
        # Test characteristic length
        lc = bore.get_lc()
        expected_lc = (40.0 - 0.0) / 5.0  # 8.0
        assert lc == expected_lc


class TestSupraDocumentation:
    """
    Test that Supra behavior matches its documentation and interface
    """
    
    def test_documented_methods_exist(self):
        """Test that all documented methods exist"""
        supra = Supra(name="doc_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        # Test all documented methods exist
        documented_methods = [
            'get_magnet_struct',
            'check_dimensions',
            'get_lc',
            'get_channels',
            'get_isolants',
            'get_names',
            'dump',
            'to_json',
            'from_dict',
            'from_yaml',
            'from_json',
            'write_to_json',
            'get_Nturns',
            'set_Detail',
            'boundingBox',
            'intersect'
        ]
        
        for method_name in documented_methods:
            assert hasattr(supra, method_name), f"Missing method: {method_name}"
            assert callable(getattr(supra, method_name)), f"Method {method_name} is not callable"
    
    def test_documented_attributes_exist(self):
        """Test that all documented attributes exist"""
        supra = Supra(name="attr_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        # Test all documented attributes exist
        documented_attributes = [
            'name',
            'r',
            'z', 
            'n',
            'struct',
            'detail'
        ]
        
        for attr_name in documented_attributes:
            assert hasattr(supra, attr_name), f"Missing attribute: {attr_name}"
    
    def test_yaml_interface_compliance(self):
        """Test that YAML interface is properly implemented"""
        # Test yaml_tag exists and is correct
        assert hasattr(Supra, 'yaml_tag')
        assert Supra.yaml_tag == "Supra"
        
        # Test YAML constructor is registered
        assert callable(Supra_constructor)
        
        # Test class methods exist
        assert hasattr(Supra, 'from_yaml')
        assert hasattr(Supra, 'from_dict')
        assert hasattr(Supra, 'from_json')
        
        # Test instance methods exist
        supra = Supra(name="yaml_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        assert hasattr(supra, 'dump')
        assert hasattr(supra, 'to_json')
        assert hasattr(supra, 'write_to_json')
    
    def test_geometric_interface_compliance(self):
        """Test that geometric interface is properly implemented"""
        supra = Supra(name="geo_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        # Test boundingBox returns tuple of two lists
        rb, zb = supra.boundingBox()
        assert isinstance(rb, list)
        assert isinstance(zb, list)
        assert len(rb) == 2
        assert len(zb) == 2
        
        # Test intersect returns boolean
        result = supra.intersect([0.5, 1.5], [-0.5, 0.5])
        assert isinstance(result, bool)
    
    def test_detail_level_interface(self):
        """Test that detail level interface works as documented"""
        supra = Supra(name="detail_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        # Test valid detail levels
        valid_details = ["None", "dblpancake", "pancake", "tape"]
        for detail in valid_details:
            supra.set_Detail(detail)
            assert supra.detail == detail
        
        # Test invalid detail level raises exception
        with pytest.raises(Exception):
            supra.set_Detail("invalid_detail")
    
    def test_serialization_interface_compliance(self):
        """Test that serialization interface works as documented"""
        supra = Supra(name="serial_test", r=[1.0, 2.0], z=[0.0, 1.0], n=1, struct="")
        
        # Test to_json returns valid JSON string
        json_str = supra.to_json()
        assert isinstance(json_str, str)
        
        # Should be parseable JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "__classname__" in parsed
        assert parsed["__classname__"] == "Supra"
        
        # Test from_dict works
        data = {
            "name": "from_dict_test",
            "r": [2.0, 3.0],
            "z": [1.0, 2.0],
            "n": 2,
            "struct": "test_struct"
        }
        
        new_supra = Supra.from_dict(data)
        assert isinstance(new_supra, Supra)
        assert new_supra.name == "from_dict_test"
            
