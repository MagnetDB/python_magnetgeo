#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
* Chamfers:
* Grooves:
"""

import math

from python_magnetgeo.hcuts import create_cut

from .Groove import Groove
from .Chamfer import Chamfer
from .Shape import Shape
from .ModelAxi import ModelAxi
from .Model3D import Model3D

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Helix(YAMLObjectBase):
    """
    name :
    r :
    z :
    cutwidth:
    dble :
    odd :

    modelaxi :
    model3d :
    shape :
    chamfer
    """

    yaml_tag = "Helix"
    
    def __init__(
        self,
        name: str,
        r: list[float],
        z: list[float],
        cutwidth: float,
        odd: bool,
        dble: bool,
        modelaxi: ModelAxi,
        model3d: Model3D,
        shape: Shape,
        chamfers: list = None,
        grooves: Groove = None,
    ) -> None:
        """
        initialize object
        """
        # General validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        
        GeometryValidator.validate_numeric_list(z, "z", expected_length=2) 
        GeometryValidator.validate_ascending_order(z, "z")
        

        self.name = name
        self.dble = dble
        self.odd = odd
        self.r = r
        self.z = z
        self.cutwidth = cutwidth
        
        if isinstance(modelaxi, str):
            self.modelaxi = ModelAxi.from_yaml(f"{modelaxi}.yaml")
        else:
            self.modelaxi = modelaxi

        if isinstance(model3d, str):
            self.model3d = Model3D.from_yaml(f"{model3d}.yaml")
        else:
            self.model3d = model3d

        if isinstance(shape, str):
            self.shape = Shape.from_yaml(f"{shape}.yaml")
        else:
            self.shape = shape
        
        self.chamfers = []
        for chamfer in chamfers:
            if isinstance(chamfer, str):
                self.chamfers.append(Chamfer.from_yaml(f"{chamfer}.yaml"))
            else:
                self.chamfers.append(chamfer)
                
        if grooves is not None:
            if isinstance(grooves, str):
                self.grooves = Groove.from_yaml(f"{grooves}.yam")
            else:
                self.grooves = grooves
        else:
            self.grooves = Groove()

    def get_type(self) -> str:
        if self.model3d.with_shapes and self.model3d.with_channels:
            return "HR"
        return "HL"

    def get_lc(self) -> float:
        return (self.r[1] - self.r[0]) / 10.0

    def get_names(self, mname: str, is2D: bool, verbose: bool = False) -> list[str]:
        """
        return names for Markers
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        sInsulator = "Glue"
        nInsulators = 0
        nturns = self.get_Nturns()
        htype = self.get_type()
        if self.model3d.with_shapes and self.model3d.with_channels:
            sInsulator = "Kapton"
            angle = self.shape.angle
            nshapes = nturns * (360 / float(angle[0]))  # only one angle to be checked
            if verbose:
                print("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

            nshapes = (
                lambda x: (
                    math.ceil(x)
                    if math.ceil(x) - x < x - math.floor(x)
                    else math.floor(x)
                )
            )(nshapes)
            nInsulators = int(nshapes)
            print("nKaptons=", nInsulators)
        else:
            nInsulators = 1
            if self.dble:
                nInsulators = 2
            if verbose:
                print("helix:", self.name, htype, nturns)

        if is2D:
            nsection = len(self.modelaxi.turns)
            solid_names.append(f"{prefix}Cu{0}")  # HP
            for j in range(nsection):
                solid_names.append(f"{prefix}Cu{j+1}")
            solid_names.append(f"{prefix}Cu{nsection+1}")  # BP
        else:
            solid_names.append("Cu")
            # TODO tell HR from HL
            for j in range(nInsulators):
                solid_names.append(f"{sInsulator}{j}")

        if verbose:
            print(f"Helix_Gmsh[{htype}]: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        msg = f"{self.__class__.__name__}(name={self.name},odd={self.odd},dble={self.dble},r={self.r},z={self.z},cutwidth={self.cutwidth},modelaxi={self.modelaxi},model3d={self.model3d},shape={self.shape}"
        if hasattr(self, 'chamfers'):
            msg += f",chamfers={self.chamfers}"
        else:
            msg += ",chamfers=None"
        if hasattr(self, 'grooves'):
            msg += f",grooves={self.grooves}"
        else:
            msg += ",grooves=None"
        msg += ")"
        return msg

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        modelaxi = cls._load_nested_modelaxi(values.get('modelaxi'), debug=debug)
        model3d = cls._load_nested_model3d(values.get('model3d'), debug=debug)
        shape = cls._load_nested_shape(values.get('shape'), debug=debug)
        chamfers = cls._load_nested_chamfers(values.get('chamfers'), debug=debug)
        grooves = cls._load_nested_groove(values.get('grooves'), debug=debug)
        
        name = values["name"]
        r = values["r"]
        z = values["z"]
        odd = values["odd"]
        dble = values["dble"]
        cutwidth = values["cutwidth"]
        # modelaxi = values["modelaxi"]
        # model3d = values["model3d"]
        # shape = values["shape"]

        # Make chamfers and grooves optional
        # chamfers = values.get("chamfers", [])
        # grooves = values.get("grooves", Groove())

        object = cls(
            name, r, z, cutwidth, odd, dble, modelaxi, model3d, shape, chamfers, grooves
        )
        # object.update()
        return object
    
    @classmethod  
    def _load_nested_modelaxi(cls, modelaxi_data, debug=False):
        if isinstance(modelaxi_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("modelaxi", modelaxi_data, ModelAxi, ModelAxi.from_yaml)
        elif isinstance(modelaxi_data, dict):
            # Inline object → create from dict
            return ModelAxi.from_dict(modelaxi_data)
        else:
            # None or already instantiated
            return modelaxi_data

    @classmethod  
    def _load_nested_model3d(cls, model3d_data, debug=False):
        if isinstance(model3d_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("model3d", model3d_data, Model3D, Model3D.from_yaml)
        elif isinstance(model3d_data, dict):
            # Inline object → create from dict
            return Model3D.from_dict(model3d_data)
        else:
            # None or already instantiated
            return model3d_data

    @classmethod  
    def _load_nested_shape(cls, shape_data, debug=False):
        if isinstance(shape_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("shape", shape_data, Shape, Shape.from_yaml)
        elif isinstance(shape_data, dict):
            # Inline object → create from dict
            return Shape.from_dict(shape_data)
        else:
            # None or already instantiated
            return shape_data

    @classmethod  
    def _load_nested_groove(cls, groove_data, debug=False):
        if groove_data is None:
            return Groove()
        
        if isinstance(groove_data, str):
            # String reference → load from "groove_data.yaml"
            from .utils import loadObject
            return loadObject("groove", groove_data, Groove, Groove.from_yaml)
        elif isinstance(groove_data, dict):
            # Inline object → create from dict
            return Groove.from_dict(groove_data)
        else:
            # None or already instantiated
            return groove_data

    @classmethod  
    def _load_nested_chamfers(cls, chamfers_data, debug=False):
        """Load list of Chamfer objects from various input formats and track references"""
        if chamfers_data is None:
            return []
        
        if not isinstance(chamfers_data, list):
            raise TypeError(f"chamfers must be a list, got {type(chamfers_data)}")
        
        objects = []
        references = []
        for i, chamfer_data in enumerate(chamfers_data):
            if isinstance(chamfer_data, str):
                # String reference → load from "chamfer_data.yaml" and track reference
                if debug:
                    print(f"Loading Chamfer[{i}] from file: {chamfer_data}")
                from .utils import loadObject
                obj = loadObject("chamfer", chamfer_data, Chamfer, Chamfer.from_yaml)
                objects.append(obj)
            elif isinstance(chamfer_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Chamfer[{i}] from inline dict: {chamfer_data.get('name', 'unnamed')}")
                obj = Chamfer.from_dict(chamfer_data)
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(chamfer_data)
                references.append(None)  # No string reference
        
        return objects

    def getModelAxi(self):
        return self.modelaxi

    def getModel3D(self):
        return self.model3d

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return self.modelaxi.get_Nturns()

    def generate_cut(self, format: str = "SALOME"):
        """
        create cut files
        """
        from .hcuts import create_cut

        create_cut(self, format, self.name)
        if self.model3d.with_shapes:
            angles = " ".join(f"{t:4.2f}" for t in self.shape.angle if t != 0)
            cmd = f'add_shape --angle="{angles}" --shape_angular_length={self.shape.length} --shape={self.shape.profile}.dat --format={format} --position="{self.shape.position} {self.name}"'
            print(f"create_cut: with_shapes not implemented - shall run {cmd}")

            import subprocess

            subprocess.run(cmd, shell=True, check=True)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """
        
        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        
        return r_overlap and z_overlap

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]

        so far exclude Leads
        """
        return (self.r, self.z)

    def insulators(self):
        """
        return name and number of insulators depending on htype
        """

        sInsulator = "Glue"
        nInsulators = 0
        htype = self.get_type()
        if htype == "HL":
            nInsulators = 2 if self.dble else 1
        else:
            sInsulator = "Kapton"
            angle = self.shape.angle
            nshapes = self.get_Nturns() * (360 / float(angle[0]))
            # print("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

            nshapes = (
                lambda x: (
                    math.ceil(x)
                    if math.ceil(x) - x < x - math.floor(x)
                    else math.floor(x)
                )
            )(nshapes)
            nInsulators = int(nshapes)
            # print("nKaptons=", nInsulators)

        return (sInsulator, nInsulators)

