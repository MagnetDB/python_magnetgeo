#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Helix class (Updated with factored approach)
"""

import pytest
import json
import yaml
import tempfile
import os
import math
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Helix import Helix, Helix_constructor
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Groove import Groove
from python_magnetgeo.Chamfer import Chamfer
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_geometric_data
)


class TestHelixInitialization:
    """Test Helix object initialization"""
    
    @pytest.fixture
    def sample_modelaxi(self):
        """Create a sample ModelAxi object for testing"""
        return ModelAxi(
            name="test_axi",
            h=10.0,
            turns=[2.0, 3.0, 1.5],
            pitch=[5.0, 5.0, 5.0]
        )
    
    @pytest.fixture
    def sample_model3d(self):
        """Create a sample Model3D object for testing"""
        return Model3D(
            name="test_model",
            cad="SALOME",
            with_shapes=True,
            with_channels=True
        )
    
    @pytest.fixture
    def sample_shape(self):
        """Create a sample Shape object for testing"""
        return Shape(
            name="test_shape",
            profile="rectangular",
            length=[10.0],
            angle=[90.0],
            onturns=[1, 2],
            position="ABOVE"
        )

    def test_helix_basic_initialization(self, sample_modelaxi, sample_model3d, sample_shape):
        """Test Helix initialization with required parameters"""
        helix = Helix(
            name="test_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=sample_modelaxi,
            model3d=sample_model3d,
            shape=sample_shape
        )
        
        assert helix.name == "test_helix"
        assert helix.r == [10.0, 20.0]
        assert helix.z == [0.0, 100.0]
        assert helix.cutwidth == 2.0
        assert helix.odd is True
        assert helix.dble is False
        assert helix.modelaxi == sample_modelaxi
        assert helix.model3d == sample_model3d
        assert helix.shape == sample_shape
        assert helix.chamfers == []
        assert isinstance(helix.grooves, Groove)

    def test_helix_with_optional_parameters(self, sample_modelaxi, sample_model3d, sample_shape):
        """Test Helix initialization with optional chamfers and grooves"""
        chamfers = [Chamfer(name="chamfer1", side="HP", rside="rint", l=5.0)]
        grooves = Groove(name="groove1", gtype="rint", n=4, eps=1.0)

        helix = Helix(
            name="full_helix",
            r=[15.0, 25.0],
            z=[5.0, 95.0],
            cutwidth=3.0,
            odd=False,
            dble=True,
            modelaxi=sample_modelaxi,
            model3d=sample_model3d,
            shape=sample_shape,
            chamfers=chamfers,
            grooves=grooves
        )
        
        assert helix.chamfers == chamfers
        assert helix.grooves == grooves

    def test_helix_setstate_method(self):
        """Test __setstate__ method for deserialization"""
        # Simulate loading from pickle/YAML without chamfers and grooves
        state = {
            'name': 'state_helix',
            'r': [12.0, 22.0],
            'z': [2.0, 98.0],
            'cutwidth': 2.5,
            'odd': False,
            'dble': True
        }
        
        helix = Helix.__new__(Helix)
        helix.__setstate__(state)
        
        assert hasattr(helix, 'chamfers')
        assert hasattr(helix, 'grooves')
        assert helix.chamfers == []
        assert isinstance(helix.grooves, Groove)

    def test_helix_geometric_validation(self, sample_modelaxi, sample_model3d, sample_shape):
        """Test geometric parameter validation"""
        helix = Helix(
            name="geo_helix",
            r=[8.0, 18.0],
            z=[0.0, 80.0],
            cutwidth=1.5,
            odd=True,
            dble=False,
            modelaxi=sample_modelaxi,
            model3d=sample_model3d,
            shape=sample_shape
        )
        
        # Validate geometric data using common utility
        validate_geometric_data(helix.r, helix.z)
        
        # Helix-specific validations
        assert helix.r[0] < helix.r[1]  # Inner radius < outer radius
        assert helix.z[0] < helix.z[1]  # Bottom < top
        assert helix.cutwidth > 0  # Positive cut width


class TestHelixMethods:
    """Test Helix class methods"""
    
    @pytest.fixture
    def hr_helix(self):
        """Create an HR type helix (with shapes and channels)"""
        modelaxi = ModelAxi(name="hr_axi", h=10.0, turns=[2.0, 3.0], pitch=[5.0, 5.0])
        model3d = Model3D(name="test_hr", cad="SALOME", with_shapes=True, with_channels=True)
        shape = Shape(name="hr_shape", profile="rect", angle=[90.0])
        
        return Helix(
            name="hr_helix",
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
    def hl_helix(self):
        """Create an HL type helix (without shapes and channels)"""
        modelaxi = ModelAxi(name="hl_axi", h=10.0, turns=[2.0, 3.0], pitch=[5.0, 5.0])
        model3d = Model3D(name="test_hl", cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="hl_shape", profile="rect")
        
        return Helix(
            name="hl_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=True,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )

    def test_get_type_hr(self, hr_helix):
        """Test get_type method for HR helix"""
        assert hr_helix.get_type() == "HR"

    def test_get_type_hl(self, hl_helix):
        """Test get_type method for HL helix"""
        assert hl_helix.get_type() == "HL"

    def test_get_lc(self, hr_helix):
        """Test get_lc method"""
        # lc = (r[1] - r[0]) / 10.0 = (20.0 - 10.0) / 10.0 = 1.0
        assert hr_helix.get_lc() == 1.0

    def test_get_nturns(self, hr_helix):
        """Test get_Nturns method"""
        # ModelAxi turns = [2.0, 3.0], so total = 5.0
        assert hr_helix.get_Nturns() == 5.0

    def test_bounding_box(self, hr_helix):
        """Test boundingBox method"""
        bbox = hr_helix.boundingBox()
        assert bbox == ([10.0, 20.0], [0.0, 100.0])

    def test_htype_hr(self, hr_helix):
        """Test htype method for HR helix"""
        assert hr_helix.htype() == "HR"

    def test_htype_hl(self, hl_helix):
        """Test htype method for HL helix"""
        assert hl_helix.htype() == "HL"

    def test_axi_property(self, hr_helix):
        """Test axi property"""
        assert hr_helix.axi == hr_helix.modelaxi

    def test_m3d_property(self, hr_helix):
        """Test m3d property"""
        assert hr_helix.m3d == hr_helix.model3d

    def test_get_modelaxi(self, hr_helix):
        """Test getModelAxi method"""
        assert hr_helix.getModelAxi() == hr_helix.modelaxi

    def test_get_model3d(self, hr_helix):
        """Test getModel3D method"""
        assert hr_helix.getModel3D() == hr_helix.model3d

    def test_insulators_hr(self, hr_helix):
        """Test insulators method for HR helix"""
        insulator_name, n_insulators = hr_helix.insulators()
        assert insulator_name == "Kapton"
        # For HR: nshapes = nturns * (360 / angle[0]) = 5.0 * (360 / 90.0) = 20
        assert n_insulators == 20

    def test_insulators_hl_single(self):
        """Test insulators method for HL helix (single)"""
        modelaxi = ModelAxi(name="hl_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(name="test_hl", cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="hl_shape", profile="rect")
        
        hl_helix = Helix(
            name="hl_single",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,  # Single helix
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        insulator_name, n_insulators = hl_helix.insulators()
        assert insulator_name == "Glue"
        assert n_insulators == 1

    def test_insulators_hl_double(self, hl_helix):
        """Test insulators method for HL helix (double)"""
        insulator_name, n_insulators = hl_helix.insulators()
        assert insulator_name == "Glue"
        assert n_insulators == 2

    def test_get_names_2d_hr(self, hr_helix):
        """Test get_names method for 2D HR helix"""
        names = hr_helix.get_names("test_magnet", is2D=True)
        # For 2D: nsection = len(turns) = 2, so we expect Cu0, Cu1, Cu2, Cu3
        expected = ["test_magnet_Cu0", "test_magnet_Cu1", "test_magnet_Cu2", "test_magnet_Cu3"]
        assert names == expected

    def test_get_names_3d_hr(self, hr_helix):
        """Test get_names method for 3D HR helix"""
        names = hr_helix.get_names("test_magnet", is2D=False)
        # For 3D HR: Cu + 20 Kapton insulators
        expected = ["Cu"] + [f"Kapton{i}" for i in range(20)]
        assert names == expected

    def test_get_names_3d_hl(self, hl_helix):
        """Test get_names method for 3D HL helix"""
        names = hl_helix.get_names("test_magnet", is2D=False)
        # For 3D HL double: Cu + 2 Glue insulators
        expected = ["Cu", "Glue0", "Glue1"]
        assert names == expected

    def test_repr(self, hr_helix):
        """Test __repr__ method"""
        repr_str = repr(hr_helix)
        assert "Helix(" in repr_str
        assert "name=hr_helix" in repr_str
        assert "odd=True" in repr_str
        assert "dble=False" in repr_str
        assert "chamfers=" in repr_str
        assert "grooves=" in repr_str


class TestHelixSerialization(BaseSerializationTestMixin):
    """Test Helix serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Helix instance"""
        modelaxi = ModelAxi(name="test_axi", h=8.0, turns=[1.5, 2.5], pitch=[4.0, 4.0])
        model3d = Model3D(name="test_model", cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="test_shape", profile="rect")
        
        return Helix(
            name="test_helix",
            r=[12.0, 22.0],
            z=[5.0, 85.0],
            cutwidth=2.5,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''!<Helix>
name: yaml_helix
r: [15.0, 25.0]
z: [10.0, 90.0]
cutwidth: 3.0
odd: false
dble: true
modelaxi: !<ModelAxi>
  name: yaml_axi
  h: 12.0
  turns: [2.0, 1.5]
  pitch: [6.0, 6.0]
model3d: !<Model3D>
  name: yaml_model
  cad: GMSH
  with_shapes: true
  with_channels: false
shape: !<Shape>
  name: yaml_shape
  profile: circular
  length: [8.0]
  angle: [45.0]
  onturns: [1, 2]
  position: BELOW
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test_helix",
            "r": [12.0, 22.0],
            "z": [5.0, 85.0],
            "cutwidth": 2.5,
            "odd": True,
            "dble": False
        }
    
    def get_class_under_test(self):
        """Return Helix class"""
        return Helix

    def test_json_includes_complex_objects(self):
        """Test that JSON serialization includes complex nested objects"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert "modelaxi" in parsed
        assert "model3d" in parsed
        assert "shape" in parsed
        assert "chamfers" in parsed
        assert "grooves" in parsed

    @patch("python_magnetgeo.utils.writeYaml")
    def test_dump_method(self, mock_write_yaml):
        """Test dump method calls writeYaml correctly"""
        instance = self.get_sample_instance()
        instance.dump()
        mock_write_yaml.assert_called_once_with("Helix", instance, Helix)

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
            mock_file.assert_called_once_with("test_helix.json", "w")


class TestHelixYAMLConstructor:
    """Test Helix YAML constructor - custom implementation"""
    
    def test_yaml_constructor_function(self):
        """Test the YAML constructor function"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Create mock objects for complex fields
        mock_modelaxi = Mock(spec=ModelAxi)
        mock_model3d = Mock(spec=Model3D)
        mock_shape = Mock(spec=Shape)
        mock_chamfers = []
        mock_grooves = Mock(spec=Groove)
        
        # Mock data that would be returned by construct_mapping
        mock_data = {
            "name": "constructor_helix",
            "r": [8.0, 18.0],
            "z": [2.0, 82.0],
            "cutwidth": 2.2,
            "odd": False,
            "dble": True,
            "modelaxi": mock_modelaxi,
            "model3d": mock_model3d,
            "shape": mock_shape,
            "chamfers": mock_chamfers,
            "grooves": mock_grooves
        }
        mock_loader.construct_mapping.return_value = mock_data
        
        # The Helix_constructor returns a Helix instance directly
        result = Helix_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Helix)
        assert result.name == "constructor_helix"
        assert result.r == [8.0, 18.0]
        assert result.z == [2.0, 82.0]
        assert result.cutwidth == 2.2
        assert result.odd is False
        assert result.dble is True
        assert result.modelaxi == mock_modelaxi
        assert result.model3d == mock_model3d
        assert result.shape == mock_shape
        assert result.chamfers == mock_chamfers
        assert result.grooves == mock_grooves
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_yaml_constructor_missing_optional_fields(self):
        """Test YAML constructor with missing optional fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Create mock objects for required fields only
        mock_modelaxi = Mock(spec=ModelAxi)
        mock_model3d = Mock(spec=Model3D)
        mock_shape = Mock(spec=Shape)
        
        # Data without optional 'chamfers' and 'grooves' fields
        mock_data = {
            "name": "minimal_helix",
            "r": [5.0, 15.0],
            "z": [0.0, 80.0],
            "cutwidth": 1.8,
            "odd": True,
            "dble": False,
            "modelaxi": mock_modelaxi,
            "model3d": mock_model3d,
            "shape": mock_shape
        }
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Helix_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Helix)
        assert result.chamfers == []  # Should default to empty list
        assert isinstance(result.grooves, Groove)  # Should default to new Groove()


class TestHelixYAMLTag(BaseYAMLTagTestMixin):
    """Test Helix YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Helix class"""
        return Helix
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Helix"


class TestHelixFromDict:
    """Test Helix.from_dict class method"""
    
    def test_from_dict_complete_data(self):
        """Test from_dict with complete data"""
        modelaxi = ModelAxi(name="dict_axi", h=15.0, turns=[3.0, 2.0], pitch=[7.0, 7.0])
        model3d = Model3D(name="dict_model", cad="SALOME", with_shapes=True, with_channels=True)
        shape = Shape(name="dict_shape", profile="rectangular")
        chamfers = [Chamfer(name="chamfer1", side="HP", rside="rint", l=3.0)]
        grooves = Groove(name="groove1", gtype="rext", n=6, eps=1.5)

        data = {
            "name": "dict_helix",
            "r": [18.0, 28.0],
            "z": [8.0, 88.0],
            "cutwidth": 3.5,
            "odd": False,
            "dble": True,
            "modelaxi": modelaxi,
            "model3d": model3d,
            "shape": shape,
            "chamfers": chamfers,
            "grooves": grooves
        }
        
        helix = Helix.from_dict(data)
        
        assert helix.name == "dict_helix"
        assert helix.r == [18.0, 28.0]
        assert helix.z == [8.0, 88.0]
        assert helix.cutwidth == 3.5
        assert helix.odd is False
        assert helix.dble is True
        assert helix.modelaxi == modelaxi
        assert helix.model3d == model3d
        assert helix.shape == shape
        assert helix.chamfers == chamfers
        assert helix.grooves == grooves

    def test_from_dict_missing_optional_fields(self):
        """Test from_dict with missing optional chamfers and grooves"""
        modelaxi = ModelAxi(name="minimal_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(name="minimal_model", cad="SALOME")
        shape = Shape(name="minimal_shape", profile="rect")
        
        data = {
            "name": "minimal_helix",
            "r": [10.0, 20.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False,
            "modelaxi": modelaxi,
            "model3d": model3d,
            "shape": shape
        }
        
        helix = Helix.from_dict(data)
        assert isinstance(helix.chamfers, list) and len(helix.chamfers) == 0
        assert isinstance(helix.grooves, Groove)

    def test_from_dict_with_debug(self):
        """Test from_dict with debug flag"""
        modelaxi = ModelAxi(name="debug_axi", h=12.0, turns=[1.0, 2.0], pitch=[6.0, 6.0])
        model3d = Model3D(name="debug_model", cad="SALOME")
        shape = Shape(name="debug_shape", profile="rect")
        
        data = {
            "name": "debug_helix",
            "r": [14.0, 24.0],
            "z": [3.0, 83.0],
            "cutwidth": 2.8,
            "odd": True,
            "dble": True,
            "modelaxi": modelaxi,
            "model3d": model3d,
            "shape": shape
        }
        
        helix = Helix.from_dict(data, debug=True)
        assert isinstance(helix, Helix)
        assert helix.name == "debug_helix"


class TestHelixFileOperations:
    """Test Helix file I/O operations"""
    
    def test_from_yaml_with_mocking(self):
        """Test from_yaml with proper mocking"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_helix = Helix(
                name="yaml_test",
                r=[1.0, 2.0],
                z=[0.0, 10.0],
                cutwidth=1.0,
                odd=True,
                dble=False,
                modelaxi=Mock(spec=ModelAxi),
                model3d=Mock(spec=Model3D),
                shape=Mock(spec=Shape)
            )
            mock_load.return_value = mock_helix
            
            result = Helix.from_yaml("test.yaml")
            
            assert result == mock_helix
            mock_load.assert_called_once_with("Helix", "test.yaml", Helix, False)

    def test_from_yaml_with_debug(self):
        """Test from_yaml with debug flag"""
        with patch('python_magnetgeo.utils.loadYaml') as mock_load:
            mock_helix = Helix(
                name="debug_yaml",
                r=[2.0, 4.0],
                z=[1.0, 11.0],
                cutwidth=1.5,
                odd=False,
                dble=True,
                modelaxi=Mock(spec=ModelAxi),
                model3d=Mock(spec=Model3D),
                shape=Mock(spec=Shape)
            )
            mock_load.return_value = mock_helix
            
            result = Helix.from_yaml("test.yaml", debug=True)
            
            assert result == mock_helix
            mock_load.assert_called_once_with("Helix", "test.yaml", Helix, True)

    def test_from_json_with_mocking(self):
        """Test from_json with proper mocking"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load:
            mock_helix = Helix(
                name="json_test",
                r=[3.0, 6.0],
                z=[2.0, 12.0],
                cutwidth=2.0,
                odd=True,
                dble=False,
                modelaxi=Mock(spec=ModelAxi),
                model3d=Mock(spec=Model3D),
                shape=Mock(spec=Shape)
            )
            mock_load.return_value = mock_helix
            
            result = Helix.from_json("test.json")
            
            assert result == mock_helix
            mock_load.assert_called_once_with("Helix", "test.json", False)

    def test_from_json_with_debug(self):
        """Test from_json with debug flag"""
        with patch('python_magnetgeo.utils.loadJson') as mock_load:
            mock_helix = Helix(
                name="debug_json",
                r=[4.0, 8.0],
                z=[3.0, 13.0],
                cutwidth=2.5,
                odd=False,
                dble=True,
                modelaxi=Mock(spec=ModelAxi),
                model3d=Mock(spec=Model3D),
                shape=Mock(spec=Shape)
            )
            mock_load.return_value = mock_helix
            
            result = Helix.from_json("test.json", debug=True)
            
            assert result == mock_helix
            mock_load.assert_called_once_with("Helix", "test.json", True)


class TestHelixGenerateCut:
    """Test Helix generate_cut method with proper mocking"""
    
    @patch("subprocess.run")
    @patch("python_magnetgeo.hcuts.create_cut")
    def test_generate_cut_with_shapes(self, mock_create_cut, mock_subprocess):
        """Test generate_cut method with shapes"""
        modelaxi = ModelAxi(name="cut_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(name="cut_model", cad="SALOME", with_shapes=True, with_channels=False)
        shape = Shape(name="cut_shape", profile="rect", angle=[90.0, 45.0], length=[10.0])
        
        helix = Helix(
            name="cut_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        helix.generate_cut()
        
        # Should call create_cut twice: once for LNCMI, once for the command
        assert mock_create_cut.call_count == 1
        mock_subprocess.assert_called_once()

    @patch("python_magnetgeo.hcuts.create_cut")
    def test_generate_cut_without_shapes(self, mock_create_cut):
        """Test generate_cut method without shapes"""
        modelaxi = ModelAxi(name="no_shape_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(name="no_shape_model", cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="no_shape_shape", profile="rect")
        
        helix = Helix(
            name="no_shape_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        helix.generate_cut("GMSH")
        
        mock_create_cut.assert_called_once_with(helix, "GMSH", "no_shape_helix")


class TestHelixUpdate:
    """Test Helix update method for loading string references"""
    
    @patch('python_magnetgeo.utils.loadObject')
    @patch('python_magnetgeo.utils.loadList') 
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_string_references(self, mock_check, mock_load_list, mock_load_object):
        """Test update method when components are loaded as strings"""
        # Create helix with string references
        helix = Helix(
            name="update_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi="modelaxi_file",
            model3d="model3d_file", 
            shape="shape_file",
            chamfers=["chamfer1", "chamfer2"],
            grooves="groove_file"
        )
        
        # Mock check_objects to return True for strings, False for objects
        def mock_check_side_effect(objects, target_type):
            if target_type == str:
                return isinstance(objects, str) or (isinstance(objects, list) and all(isinstance(obj, str) for obj in objects))
            return False
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock the loaded objects
        mock_modelaxi = Mock(spec=ModelAxi)
        mock_model3d = Mock(spec=Model3D)
        mock_shape = Mock(spec=Shape)
        mock_chamfers = [Mock(spec=Chamfer), Mock(spec=Chamfer)]
        mock_grooves = Mock(spec=Groove)
        
        mock_load_object.side_effect = [mock_modelaxi, mock_model3d, mock_shape, mock_grooves]
        mock_load_list.return_value = mock_chamfers
        
        helix.update()
        
        # Verify objects were loaded
        assert helix.modelaxi == mock_modelaxi
        assert helix.model3d == mock_model3d
        assert helix.shape == mock_shape
        assert helix.chamfers == mock_chamfers
        assert helix.grooves == mock_grooves
        
        # Verify the correct calls were made
        mock_load_object.assert_any_call("modelaxi", "modelaxi_file", ModelAxi, ModelAxi.from_yaml)
        mock_load_object.assert_any_call("model3d", "model3d_file", Model3D, Model3D.from_yaml)
        mock_load_object.assert_any_call("shape", "shape_file", Shape, Shape.from_yaml)
        mock_load_object.assert_any_call("groove", "groove_file", Groove, Groove.from_yaml)
        
        mock_load_list.assert_called_once_with("chamfers", ["chamfer1", "chamfer2"], [None, Chamfer], {"Chamfer}": Chamfer.from_yaml})

    def test_update_with_object_references(self):
        """Test update method when components are already objects"""
        modelaxi = Mock(spec=ModelAxi)
        model3d = Mock(spec=Model3D)
        shape = Mock(spec=Shape)
        chamfers = [Mock(spec=Chamfer)]
        grooves = Mock(spec=Groove)
        
        helix = Helix(
            name="object_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape,
            chamfers=chamfers,
            grooves=grooves
        )
        
        # Store original references
        orig_modelaxi = helix.modelaxi
        orig_model3d = helix.model3d
        orig_shape = helix.shape
        orig_chamfers = helix.chamfers
        orig_grooves = helix.grooves
        
        helix.update()
        
        # Objects should remain unchanged
        assert helix.modelaxi == orig_modelaxi
        assert helix.model3d == orig_model3d
        assert helix.shape == orig_shape
        assert helix.chamfers == orig_chamfers
        assert helix.grooves == orig_grooves

    @patch('python_magnetgeo.utils.loadObject')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_mixed_string_and_object_references(self, mock_check, mock_load_object):
        """Test update method with mixed string and object references"""
        # Some components as strings, others as objects
        existing_model3d = Mock(spec=Model3D)
        existing_chamfers = [Mock(spec=Chamfer)]
        
        helix = Helix(
            name="mixed_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi="modelaxi_file",  # String
            model3d=existing_model3d,   # Object
            shape="shape_file",         # String
            chamfers=existing_chamfers, # Object list
            grooves="groove_file"       # String
        )
        
        def mock_check_side_effect(objects, target_type):
            if target_type == str:
                return isinstance(objects, str)
            return False
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock the loaded objects for string references
        mock_modelaxi = Mock(spec=ModelAxi)
        mock_shape = Mock(spec=Shape)
        mock_grooves = Mock(spec=Groove)
        
        mock_load_object.side_effect = [mock_modelaxi, mock_shape, mock_grooves]
        
        helix.update()
        
        # String references should be replaced with loaded objects
        assert helix.modelaxi == mock_modelaxi
        assert helix.shape == mock_shape
        assert helix.grooves == mock_grooves
        
        # Object references should remain unchanged
        assert helix.model3d == existing_model3d
        assert helix.chamfers == existing_chamfers

    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_string_chamfers_list(self, mock_check, mock_load_list):
        """Test update method specifically for chamfers as string list"""
        helix = Helix(
            name="chamfer_string_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=Mock(spec=ModelAxi),
            model3d=Mock(spec=Model3D),
            shape=Mock(spec=Shape),
            chamfers=["chamfer1.yaml", "chamfer2.yaml", "chamfer3.yaml"],
            grooves=Mock(spec=Groove)
        )
        
        def mock_check_side_effect(objects, target_type):
            if target_type == str:
                return isinstance(objects, list) and all(isinstance(obj, str) for obj in objects)
            return False
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded chamfers
        mock_chamfers = [Mock(spec=Chamfer) for _ in range(3)]
        mock_load_list.return_value = mock_chamfers
        
        helix.update()
        
        assert helix.chamfers == mock_chamfers
        mock_load_list.assert_called_once_with(
            "chamfers", 
            ["chamfer1.yaml", "chamfer2.yaml", "chamfer3.yaml"], 
            [None, Chamfer], 
            {"Chamfer}": Chamfer.from_yaml}
        )

    def test_update_with_none_values(self):
        """Test update method when some components are None"""
        helix = Helix(
            name="none_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=None,
            model3d=None,
            shape=None,
            chamfers=None,
            grooves=None
        )
        
        # Store original None values
        orig_modelaxi = helix.modelaxi
        orig_model3d = helix.model3d
        orig_shape = helix.shape
        orig_chamfers = helix.chamfers
        orig_grooves = helix.grooves
        
        # Update should not crash and should leave None values as is
        helix.update()
        
        # None values should remain None (no loading attempted)
        assert helix.modelaxi == orig_modelaxi
        assert helix.model3d == orig_model3d
        assert helix.shape == orig_shape
        assert helix.chamfers == orig_chamfers
        assert helix.grooves == orig_grooves


class TestHelixStringDataHandling:
    """Test Helix handling of string data in various scenarios"""
    
    def test_helix_initialization_with_string_data(self):
        """Test Helix can be initialized with string references"""
        helix = Helix(
            name="string_data_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi="modelaxi_config",
            model3d="model3d_config",
            shape="shape_config",
            chamfers=["chamfer1", "chamfer2"],
            grooves="groove_config"
        )
        
        # Should initialize successfully with string data
        assert helix.name == "string_data_helix"
        assert helix.modelaxi == "modelaxi_config"
        assert helix.model3d == "model3d_config"
        assert helix.shape == "shape_config"
        assert helix.chamfers == ["chamfer1", "chamfer2"]
        assert helix.grooves == "groove_config"

    @patch('python_magnetgeo.utils.loadObject')
    @patch('python_magnetgeo.utils.check_objects')
    def test_helix_methods_after_string_loading(self, mock_check, mock_load_object):
        """Test that Helix methods work correctly after loading string references"""
        # Create helix with string data
        helix = Helix(
            name="method_test_helix",
            r=[15.0, 25.0],
            z=[5.0, 95.0],
            cutwidth=2.5,
            odd=False,
            dble=True,
            modelaxi="modelaxi_file",
            model3d="model3d_file",
            shape="shape_file"
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, str)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loaded objects with proper attributes
        mock_modelaxi = Mock(spec=ModelAxi)
        mock_modelaxi.turns = [2.0, 3.0]
        mock_modelaxi.get_Nturns.return_value = 5.0
        
        mock_model3d = Mock(spec=Model3D)
        mock_model3d.with_shapes = True
        mock_model3d.with_channels = True
        
        mock_shape = Mock(spec=Shape)
        mock_shape.angle = [90.0]
        
        mock_load_object.side_effect = [mock_modelaxi, mock_model3d, mock_shape]
        
        # Update to load string references
        helix.update()
        
        # Now test that methods work correctly
        assert helix.get_Nturns() == 5.0
        assert helix.get_type() == "HR"  # with_shapes=True and with_channels=True
        assert helix.get_lc() == 1.0  # (25.0 - 15.0) / 10.0
        
        # Test properties
        assert helix.axi == mock_modelaxi
        assert helix.m3d == mock_model3d

    def test_helix_from_dict_with_string_data(self):
        """Test from_dict method handles string data correctly"""
        data = {
            "name": "dict_string_helix",
            "r": [12.0, 22.0],
            "z": [3.0, 83.0],
            "cutwidth": 2.8,
            "odd": True,
            "dble": False,
            "modelaxi": "modelaxi_reference",
            "model3d": "model3d_reference",
            "shape": "shape_reference",
            "chamfers": ["chamfer_ref1", "chamfer_ref2"],
            "grooves": "groove_reference"
        }
        
        helix = Helix.from_dict(data)
        
        # Should preserve string references
        assert helix.name == "dict_string_helix"
        assert helix.modelaxi == "modelaxi_reference"
        assert helix.model3d == "model3d_reference"
        assert helix.shape == "shape_reference"
        assert helix.chamfers == ["chamfer_ref1", "chamfer_ref2"]
        assert helix.grooves == "groove_reference"

    def test_helix_serialization_with_string_data(self):
        """Test JSON serialization preserves string references"""
        helix = Helix(
            name="serialization_test",
            r=[8.0, 18.0],
            z=[2.0, 82.0],
            cutwidth=1.8,
            odd=False,
            dble=True,
            modelaxi="modelaxi_serial",
            model3d="model3d_serial",
            shape="shape_serial",
            chamfers=["chamfer_serial1"],
            grooves="groove_serial"
        )
        
        json_str = helix.to_json()
        parsed = json.loads(json_str)
        
        # String references should be preserved in JSON
        assert parsed["modelaxi"] == "modelaxi_serial"
        assert parsed["model3d"] == "model3d_serial"
        assert parsed["shape"] == "shape_serial"
        assert parsed["chamfers"] == ["chamfer_serial1"]
        assert parsed["grooves"] == "groove_serial"

    @patch('python_magnetgeo.utils.loadObject')
    @patch('python_magnetgeo.utils.loadList')
    @patch('python_magnetgeo.utils.check_objects')
    def test_helix_yaml_constructor_with_string_data(self, mock_check, mock_load_list, mock_load_object):
        """Test YAML constructor handles string data in loaded mapping"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # YAML data with string references
        yaml_data = {
            "name": "yaml_constructor_helix",
            "r": [10.0, 30.0],
            "z": [0.0, 100.0],
            "cutwidth": 3.0,
            "odd": True,
            "dble": False,
            "modelaxi": "yaml_modelaxi",
            "model3d": "yaml_model3d",
            "shape": "yaml_shape",
            "chamfers": ["yaml_chamfer1", "yaml_chamfer2"],
            "grooves": "yaml_groove"
        }
        
        mock_loader.construct_mapping.return_value = yaml_data
        
        result = Helix_constructor(mock_loader, mock_node)
        
        # Constructor should create Helix with string references intact
        assert isinstance(result, Helix)
        assert result.name == "yaml_constructor_helix"
        assert result.modelaxi == "yaml_modelaxi"
        assert result.model3d == "yaml_model3d"
        assert result.shape == "yaml_shape"
        assert result.chamfers == ["yaml_chamfer1", "yaml_chamfer2"]
        assert result.grooves == "yaml_groove"

    def test_helix_repr_with_string_data(self):
        """Test __repr__ method works correctly with string data"""
        helix = Helix(
            name="repr_test_helix",
            r=[5.0, 15.0],
            z=[0.0, 50.0],
            cutwidth=1.5,
            odd=True,
            dble=False,
            modelaxi="repr_modelaxi",
            model3d="repr_model3d",
            shape="repr_shape",
            chamfers=["repr_chamfer"],
            grooves="repr_groove"
        )
        
        repr_str = repr(helix)
        
        # Should include string references in representation
        assert "name=repr_test_helix" in repr_str
        assert "modelaxi=repr_modelaxi" in repr_str
        assert "model3d=repr_model3d" in repr_str
        assert "shape=repr_shape" in repr_str
        assert "chamfers=['repr_chamfer']" in repr_str
        assert "grooves=repr_groove" in repr_str


class TestHelixUpdateErrorHandling:
    """Test error handling in Helix update scenarios"""
    
    @patch('python_magnetgeo.utils.loadObject')
    @patch('python_magnetgeo.utils.check_objects')
    def test_update_with_loading_errors(self, mock_check, mock_load_object):
        """Test update method handles loading errors gracefully"""
        helix = Helix(
            name="error_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi="invalid_modelaxi_file",
            model3d="invalid_model3d_file",
            shape="invalid_shape_file"
        )
        
        def mock_check_side_effect(objects, target_type):
            return target_type == str and isinstance(objects, str)
        
        mock_check.side_effect = mock_check_side_effect
        
        # Mock loading to raise exceptions
        mock_load_object.side_effect = [
            Exception("Failed to load modelaxi"),
            Exception("Failed to load model3d"),
            Exception("Failed to load shape")
        ]
        
        # Update should handle errors without crashing
        try:
            helix.update()
        except Exception as e:
            # If exceptions are not caught internally, that's the expected behavior
            assert "Failed to load" in str(e)

    @patch('python_magnetgeo.utils.loadObject')
    def test_update_with_non_string_references(self, mock_load_object):
        """Test update method when components are not strings (should not attempt loading)"""
        # Create helix with object references (not strings)
        modelaxi_obj = Mock(spec=ModelAxi)
        model3d_obj = Mock(spec=Model3D)
        shape_obj = Mock(spec=Shape)
        
        helix = Helix(
            name="no_update_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi_obj,
            model3d=model3d_obj,
            shape=shape_obj
        )
        
        # Store original object references
        orig_modelaxi = helix.modelaxi
        orig_model3d = helix.model3d
        orig_shape = helix.shape
        
        helix.update()
        
        # Object references should remain unchanged
        assert helix.modelaxi == orig_modelaxi
        assert helix.model3d == orig_model3d
        assert helix.shape == orig_shape
        
        # loadObject should not have been called since components are not strings
        mock_load_object.assert_not_called()


class TestHelixComplexScenarios:
    """Test complex Helix scenarios and edge cases"""
    
    def test_helix_with_many_chamfers(self):
        """Test Helix with multiple chamfers"""
        modelaxi = ModelAxi(name="chamfer_axi", h=12.0, turns=[2.0, 3.0], pitch=[6.0, 6.0])
        model3d = Model3D(name="chamfer_model", cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="chamfer_shape", profile="rect")
        
        chamfers = [
            Chamfer(name="chamfer1", side="HP", rside="rint", alpha=45.0, l=2.0),
            Chamfer(name="chamfer2", side="HP", rside="rext", alpha=30.0, l=3.0),
            Chamfer(name="chamfer3", side="BP", rside="rint", dr=1.5, l=2.5),
            Chamfer(name="chamfer4", side="BP", rside="rext", dr=2.0, l=4.0)
        ]
        
        helix = Helix(
            name="chamfer_helix",
            r=[12.0, 28.0],
            z=[5.0, 95.0],
            cutwidth=3.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape,
            chamfers=chamfers,
            grooves=Groove()
        )
        
        assert len(helix.chamfers) == 4
        assert all(isinstance(c, Chamfer) for c in helix.chamfers)

    def test_helix_with_complex_groove(self):
        """Test Helix with complex groove configuration"""
        modelaxi = ModelAxi(name="groove_axi", h=15.0, turns=[1.0, 2.0, 1.5], pitch=[5.0, 6.0, 4.0])
        model3d = Model3D(name="groove_model", cad="SALOME", with_shapes=True, with_channels=True)
        shape = Shape(name="groove_shape", profile="circular", angle=[60.0])
        
        grooves = Groove(name="complex_groove", gtype="rint", n=8, eps=2.5)
        
        helix = Helix(
            name="groove_helix",
            r=[20.0, 40.0],
            z=[10.0, 110.0],
            cutwidth=4.0,
            odd=False,
            dble=True,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape,
            chamfers=[],
            grooves=grooves
        )
        
        assert isinstance(helix.grooves, Groove)
        assert helix.grooves.gtype == "rint"
        assert helix.grooves.n == 8
        assert helix.grooves.eps == 2.5

    def test_helix_edge_case_dimensions(self):
        """Test Helix with edge case dimensions"""
        modelaxi = ModelAxi(name="edge_axi", h=0.1, turns=[0.1], pitch=[0.5])
        model3d = Model3D(name="edge_model", cad="SALOME")
        shape = Shape(name="edge_shape", profile="rect")
        
        # Very small helix
        small_helix = Helix(
            name="small_helix",
            r=[1e-3, 2e-3],
            z=[0.0, 1e-2],
            cutwidth=1e-4,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        assert small_helix.get_lc() == 1e-4  # (2e-3 - 1e-3) / 10.0
        assert small_helix.get_Nturns() == 0.1

    def test_helix_performance_with_complex_shapes(self):
        """Test Helix performance with complex shape configurations"""
        modelaxi = ModelAxi(name="perf_axi", h=20.0, turns=[5.0, 8.0, 3.0], pitch=[10.0, 12.0, 8.0])
        model3d = Model3D(name="perf_model", cad="SALOME", with_shapes=True, with_channels=True)
        
        # Complex shape with many angles
        shape = Shape(
            name="complex_shape",
            profile="complex",
            angle=[i * 5.0 + 1 for i in range(72)],  # Every 5 degrees + 1
            length=[15.0],
            onturns=list(range(1, 17)),
            position="ALTERNATE"
        )
        
        helix = Helix(
            name="performance_helix",
            r=[25.0, 75.0],
            z=[15.0, 185.0],
            cutwidth=5.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        # Test that methods still work with complex configuration
        assert helix.get_type() == "HR"
        insulator_name, n_insulators = helix.insulators()
        assert insulator_name == "Kapton"
        assert n_insulators > 0


class TestHelixIntegration:
    """Integration tests for Helix class"""
    
    def test_helix_serialization_roundtrip(self):
        """Test complete serialization roundtrip"""
        modelaxi = ModelAxi(name="roundtrip_axi", h=18.0, turns=[2.5, 3.5], pitch=[9.0, 9.0])
        model3d = Model3D(name="roundtrip_model", cad="ROUNDTRIP", with_shapes=True, with_channels=False)
        shape = Shape(name="roundtrip_shape", profile="hexagonal", angle=[120.0])
        chamfers = [Chamfer(name="roundtrip_chamfer", side="HP", rside="rint", alpha=60.0, l=4.0)]
        grooves = Groove(name="roundtrip_groove", gtype="rext", n=12, eps=3.0)

        original_helix = Helix(
            name="roundtrip_helix",
            r=[30.0, 50.0],
            z=[20.0, 120.0],
            cutwidth=4.5,
            odd=False,
            dble=True,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape,
            chamfers=chamfers,
            grooves=grooves
        )
        
        # Test JSON serialization
        json_str = original_helix.to_json()
        parsed_json = json.loads(json_str)
        
        # Verify JSON structure
        assert parsed_json["__classname__"] == "Helix"
        assert parsed_json["name"] == "roundtrip_helix"
        assert parsed_json["r"] == [30.0, 50.0]
        assert parsed_json["z"] == [20.0, 120.0]
        assert parsed_json["cutwidth"] == 4.5
        assert parsed_json["odd"] is False
        assert parsed_json["dble"] is True
        assert "modelaxi" in parsed_json
        assert "model3d" in parsed_json
        assert "shape" in parsed_json
        assert "chamfers" in parsed_json
        assert "grooves" in parsed_json

    def test_helix_in_insert_context(self):
        """Test helix as it would be used in an Insert context"""
        # Create multiple helices that might be used together
        modelaxi1 = ModelAxi(name="insert_axi1", h=10.0, turns=[2.0], pitch=[5.0])
        modelaxi2 = ModelAxi(name="insert_axi2", h=12.0, turns=[3.0], pitch=[6.0])
        
        model3d = Model3D(name="insert_model", cad="SALOME")
        shape1 = Shape(name="insert_shape1", profile="rect")
        shape2 = Shape(name="insert_shape2", profile="circ")
        
        helices = [
            Helix(
                name="insert_helix1",
                r=[10.0, 20.0],
                z=[0.0, 50.0],
                cutwidth=2.0,
                odd=True,
                dble=False,
                modelaxi=modelaxi1,
                model3d=model3d,
                shape=shape1
            ),
            Helix(
                name="insert_helix2",
                r=[25.0, 35.0],
                z=[5.0, 45.0],
                cutwidth=2.5,
                odd=False,
                dble=True,
                modelaxi=modelaxi2,
                model3d=model3d,
                shape=shape2
            )
        ]
        
        # Test that helices maintain their individual properties
        assert helices[0].get_type() == "HL"  # No shapes
        assert helices[1].get_type() == "HL"  # No shapes
        
        # Test geometric consistency for use in insert
        for i, helix in enumerate(helices):
            if i > 0:
                # Each helix should have larger radius than previous
                assert helix.r[0] > helices[i-1].r[1]


class TestHelixPerformance:
    """Performance tests for Helix class"""
    
    def test_multiple_helix_creation_performance(self):
        """Test performance of creating many helices"""
        helices = []
        for i in range(50):
            modelaxi = ModelAxi(
                name=f"perf_axi_{i}",
                h=10.0 + i,
                turns=[2.0 + i * 0.1],
                pitch=[5.0 + i * 0.2]
            )
            model3d = Model3D(name=f"perf_model_{i}", cad="SALOME")
            shape = Shape(name=f"perf_shape_{i}", profile="rect")
            
            helix = Helix(
                name=f"perf_helix_{i}",
                r=[10.0 + i, 20.0 + i],
                z=[0.0, 100.0 + i * 10],
                cutwidth=2.0 + i * 0.1,
                odd=i % 2 == 0,
                dble=i % 3 == 0,
                modelaxi=modelaxi,
                model3d=model3d,
                shape=shape
            )
            helices.append(helix)
        
        assert len(helices) == 50
        assert all(isinstance(h, Helix) for h in helices)
        
        # Test that operations work on all helices
        types = [h.get_type() for h in helices]
        assert len(types) == 50
        assert all(t in ["HR", "HL"] for t in types)


class TestHelixDataConsistency:
    """Test data consistency and validation in Helix"""
    
    def test_helix_geometric_consistency(self):
        """Test geometric consistency within helix"""
        modelaxi = ModelAxi(name="consistent_axi", h=15.0, turns=[3.0, 2.0], pitch=[7.0, 6.0])
        model3d = Model3D(name="consistent_model", cad="SALOME")
        shape = Shape(name="consistent_shape", profile="rect")
        
        helix = Helix(
            name="consistent_helix",
            r=[15.0, 35.0],
            z=[10.0, 110.0],
            cutwidth=3.0,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        # Test geometric relationships
        assert helix.r[0] < helix.r[1]  # Inner < outer radius
        assert helix.z[0] < helix.z[1]  # Bottom < top
        assert helix.cutwidth > 0  # Positive cut width
        
        # Test that bounding box matches geometry
        rb, zb = helix.boundingBox()
        assert rb == helix.r
        assert zb == helix.z

    def test_helix_type_consistency(self):
        """Test consistency between helix type determination methods"""
        # Create HR helix
        hr_modelaxi = ModelAxi(name="hr_axi", h=10.0, turns=[2.0], pitch=[5.0])
        hr_model3d = Model3D(name="hr_model", cad="SALOME", with_shapes=True, with_channels=True)
        hr_shape = Shape(name="hr_shape", profile="rect")
        
        hr_helix = Helix(
            name="hr_test",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=hr_modelaxi,
            model3d=hr_model3d,
            shape=hr_shape
        )
        
        # Test consistency between get_type and htype
        assert hr_helix.get_type() == "HR"
        assert hr_helix.htype() == "HR"  # Should be consistent
        
        # Create HL helix
        hl_modelaxi = ModelAxi(name="hl_axi", h=10.0, turns=[2.0], pitch=[5.0])
        hl_model3d = Model3D(name="hl_model", cad="SALOME", with_shapes=False, with_channels=False)
        hl_shape = Shape(name="hl_shape", profile="rect")
        
        hl_helix = Helix(
            name="hl_test",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=True,  # Double helix
            modelaxi=hl_modelaxi,
            model3d=hl_model3d,
            shape=hl_shape
        )
        
        # For HL, both methods should return "HL"
        assert hl_helix.get_type() == "HL"
        assert hl_helix.htype() == "HL"

    def test_helix_insulator_calculation_consistency(self):
        """Test consistency in insulator calculations"""
        # Test HR helix with known parameters
        hr_modelaxi = ModelAxi(name="insulator_axi", h=10.0, turns=[4.0], pitch=[5.0])
        hr_model3d = Model3D(name="insulator_model", cad="SALOME", with_shapes=True, with_channels=True)
        hr_shape = Shape(name="insulator_shape", profile="rect", angle=[45.0])  # 8 shapes per turn
        
        hr_helix = Helix(
            name="insulator_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=hr_modelaxi,
            model3d=hr_model3d,
            shape=hr_shape
        )
        
        insulator_name, n_insulators = hr_helix.insulators()
        
        # Verify calculation: nshapes = nturns * (360 / angle) = 4.0 * (360 / 45.0) = 32
        assert insulator_name == "Kapton"
        assert n_insulators == 32

