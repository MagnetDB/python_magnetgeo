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

from python_magnetgeo.Helix import Helix
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Groove import Groove
from python_magnetgeo.Chamfer import Chamfer
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLConstructorTestMixin,
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
        chamfers = [Chamfer(side="HP", rside="rint", l=5.0)]
        grooves = Groove(gtype="rint", n=4, eps=1.0)
        
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
        model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
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
        model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
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

    def test_insulators_hr(self, hr_helix):
        """Test insulators method for HR helix"""
        insulator_name, n_insulators = hr_helix.insulators()
        assert insulator_name == "Kapton"
        # For HR: nshapes = nturns * (360 / angle[0]) = 5.0 * (360 / 90.0) = 20
        assert n_insulators == 20

    def test_insulators_hl_single(self):
        """Test insulators method for HL helix (single)"""
        modelaxi = ModelAxi(name="hl_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
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
        model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
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
        return '''
<!Helix>
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

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to Helix dump"):
            instance.dump()

    def test_write_to_json_method(self):
        """Test write_to_json method"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.write_to_json()
            mock_file.assert_called_once_with("test_helix.json", "w")


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
        model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
        shape = Shape(name="dict_shape", profile="rectangular")
        chamfers = [Chamfer(side="HP", rside="rint", l=3.0)]
        grooves = Groove(gtype="rext", n=6, eps=1.5)
        
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
        model3d = Model3D(cad="SALOME")
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
        assert helix.grooves != Groove()


class TestHelixFileOperations:
    """Test Helix file operations and external dependencies"""
    
    @patch("subprocess.run")
    @patch("python_magnetgeo.hcuts.create_cut")
    def test_generate_cut_with_shapes(self, mock_create_cut, mock_subprocess):
        """Test generate_cut method with shapes"""
        modelaxi = ModelAxi(name="cut_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=False)
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
        
        mock_create_cut.assert_called_once()
        mock_subprocess.assert_called_once()

    @patch("python_magnetgeo.hcuts.create_cut")
    def test_generate_cut_without_shapes(self, mock_create_cut):
        """Test generate_cut method without shapes"""
        modelaxi = ModelAxi(name="no_shape_axi", h=10.0, turns=[2.0], pitch=[5.0])
        model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
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


class TestHelixComplexScenarios:
    """Test complex Helix scenarios and edge cases"""
    
    def test_helix_with_many_chamfers(self):
        """Test Helix with multiple chamfers"""
        modelaxi = ModelAxi(name="chamfer_axi", h=12.0, turns=[2.0, 3.0], pitch=[6.0, 6.0])
        model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
        shape = Shape(name="chamfer_shape", profile="rect")
        
        chamfers = [
            Chamfer(side="HP", rside="rint", alpha=45.0, l=2.0),
            Chamfer(side="HP", rside="rext", alpha=30.0, l=3.0),
            Chamfer(side="BP", rside="rint", dr=1.5, l=2.5),
            Chamfer(side="BP", rside="rext", dr=2.0, l=4.0)
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
        model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
        shape = Shape(name="groove_shape", profile="circular", angle=[60.0])
        
        grooves = Groove(gtype="rint", n=8, eps=2.5)
        
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
        model3d = Model3D(cad="SALOME")
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
        model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
        
        # Complex shape with many angles
        shape = Shape(
            name="complex_shape",
            profile="complex",
            angle=[i * 5.0+1 for i in range(72)],  # Every 5 degrees
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
        model3d = Model3D(cad="ROUNDTRIP", with_shapes=True, with_channels=False)
        shape = Shape(name="roundtrip_shape", profile="hexagonal", angle=[120.0])
        chamfers = [Chamfer(side="HP", rside="rint", alpha=60.0, l=4.0)]
        grooves = Groove(gtype="rext", n=12, eps=3.0)
        
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
        
        model3d = Model3D(cad="SALOME")
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


class TestHelixErrorHandling:
    """Test error handling in Helix class"""
    
    def test_helix_with_invalid_components(self):
        """Test Helix with potentially invalid component configurations"""
        # Test with None components (should raise errors or handle gracefully)
        try:
            helix = Helix(
                name="invalid_helix",
                r=[10.0, 20.0],
                z=[0.0, 100.0],
                cutwidth=2.0,
                odd=True,
                dble=False,
                modelaxi=None,
                model3d=None,
                shape=None
            )
            # If no error, implementation allows None values
        except (TypeError, AttributeError):
            # Expected if implementation validates components
            pass

    def test_helix_mathematical_edge_cases(self):
        """Test mathematical edge cases in Helix calculations"""
        # Test with zero turns
        zero_modelaxi = ModelAxi(name="zero_axi", h=10.0, turns=[0.0], pitch=[5.0])
        model3d = Model3D(cad="SALOME")
        shape = Shape(name="zero_shape", profile="rect")
        
        zero_helix = Helix(
            name="zero_helix",
            r=[10.0, 20.0],
            z=[0.0, 100.0],
            cutwidth=2.0,
            odd=True,
            dble=False,
            modelaxi=zero_modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        assert zero_helix.get_Nturns() == 0.0
        
        # Test insulators calculation with zero turns
        insulator_name, n_insulators = zero_helix.insulators()
        assert insulator_name == "Glue"
        assert n_insulators == 1

    def test_helix_extreme_geometry(self):
        """Test Helix with extreme geometric values"""
        modelaxi = ModelAxi(name="extreme_axi", h=1e6, turns=[1e3], pitch=[1e3])
        model3d = Model3D(cad="SALOME")
        shape = Shape(name="extreme_shape", profile="rect")
        
        # Very large helix
        large_helix = Helix(
            name="large_helix",
            r=[1e6, 1e7],
            z=[1e5, 1e6],
            cutwidth=1e4,
            odd=True,
            dble=False,
            modelaxi=modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        assert large_helix.get_lc() == 9e5  # (1e7 - 1e6) / 10.0
        assert large_helix.get_Nturns() == 1e3

    def test_helix_division_by_zero_scenarios(self):
        """Test scenarios that might cause division by zero"""
        # Test with shape angle of zero (might cause issues in insulators calculation)
        modelaxi = ModelAxi(name="zero_angle_axi", h=10.0, turns=[5.0], pitch=[5.0])
        model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
        
        try:
            zero_angle_shape = Shape(name="zero_angle", profile="rect", angle=[0.0])
            zero_angle_helix = Helix(
                name="zero_angle_helix",
                r=[10.0, 20.0],
                z=[0.0, 100.0],
                cutwidth=2.0,
                odd=True,
                dble=False,
                modelaxi=modelaxi,
                model3d=model3d,
                shape=zero_angle_shape
            )
            
            # This might cause division by zero in insulators calculation
            insulator_name, n_insulators = zero_angle_helix.insulators()
        except ZeroDivisionError:
            # Expected for zero angle
            pass


class TestHelixPerformance:
    """Performance tests for Helix class"""
    
    def test_large_turn_count_performance(self):
        """Test Helix performance with large number of turns"""
        # Create ModelAxi with many turns
        large_turns = [float(i) for i in range(100)]
        large_pitch = [5.0] * 100
        
        large_modelaxi = ModelAxi(
            name="large_axi",
            h=500.0,
            turns=large_turns,
            pitch=large_pitch
        )
        
        model3d = Model3D(cad="SALOME")
        shape = Shape(name="large_shape", profile="rect")
        
        large_helix = Helix(
            name="large_helix",
            r=[50.0, 150.0],
            z=[0.0, 2500.0],
            cutwidth=10.0,
            odd=True,
            dble=False,
            modelaxi=large_modelaxi,
            model3d=model3d,
            shape=shape
        )
        
        # Test that operations still work efficiently
        assert large_helix.get_Nturns() == sum(large_turns)
        
        # Test name generation (this might be slow but should work)
        names_2d = large_helix.get_names("test", is2D=True)
        assert len(names_2d) == 102  # 100 sections + HP + BP

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
            model3d = Model3D(cad="SALOME")
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
        model3d = Model3D(cad="SALOME")
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
        hr_model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
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
        hl_model3d = Model3D(cad="SALOME", with_shapes=False, with_channels=False)
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
        
        # For HL, get_type depends on model3d, htype depends on dble
        assert hl_helix.get_type() == "HL"
        assert hl_helix.htype() == "HL"

    def test_helix_insulator_calculation_consistency(self):
        """Test consistency in insulator calculations"""
        # Test HR helix with known parameters
        hr_modelaxi = ModelAxi(name="insulator_axi", h=10.0, turns=[4.0], pitch=[5.0])
        hr_model3d = Model3D(cad="SALOME", with_shapes=True, with_channels=True)
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])#!/usr/bin/env python3
# -*- coding:utf-8 -*-

