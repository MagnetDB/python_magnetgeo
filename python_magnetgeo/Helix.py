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
import os

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
    Helix geometry class representing a helical magnet coil.
    
    Attributes:
        name (str): Unique identifier for the helix
        r (list[float]): Radial bounds [r_inner, r_outer] in mm
        z (list[float]): Axial bounds [z_bottom, z_top] in mm
        cutwidth (float): Width of helical cut in mm
        odd (bool): Odd layer indicator
        dble (bool): Double layer indicator
        modelaxi (ModelAxi): Axisymmetric model definition
        model3d (Model3D): 3D CAD model configuration
        shape (Shape): Cross-sectional shape definition
        chamfers (list): List of Chamfer objects for edge modifications
        grooves (Groove): Groove configuration for cooling channels
    
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
        modelaxi: ModelAxi = None,
        model3d: Model3D = None,
        shape: Shape = None,
        chamfers: list = None,
        grooves: Groove = None,
    ) -> None:
        """
        Initialize a Helix object with validation.
        
        Args:
            name: Unique identifier for the helix
            r: Radial bounds [r_inner, r_outer] in mm, must be ascending
            z: Axial bounds [z_bottom, z_top] in mm, must be ascending
            cutwidth: Width of helical cut in mm
            odd: True if odd layer, False otherwise
            dble: True if double layer, False otherwise
            modelaxi: Axisymmetric model definition for helical cut
            model3d: 3D CAD model configuration
            shape: Cross-sectional shape definition
            chamfers: Optional list of Chamfer objects for edge modifications
            grooves: Optional Groove object for cooling channel definition
        
        Raises:
            ValidationError: If validation fails for name, r, z, or modelaxi.h constraint
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
        
        if modelaxi is not None and isinstance(modelaxi, str):
            self.modelaxi = ModelAxi.from_yaml(f"{modelaxi}.yaml")
        else:
            self.modelaxi = modelaxi

        if model3d is not None and isinstance(model3d, str):
            self.model3d = Model3D.from_yaml(f"{model3d}.yaml")
        else:
            self.model3d = model3d

        if shape is not None and isinstance(shape, str):
            self.shape = Shape.from_yaml(f"{shape}.yaml")
        else:
            self.shape = shape
        
        self.chamfers = []
        if chamfers is not None:
            for chamfer in chamfers:
                if isinstance(chamfer, str):
                    self.chamfers.append(Chamfer.from_yaml(f"{chamfer}.yaml"))
                else:
                    self.chamfers.append(chamfer)
                
        if grooves is not None and isinstance(grooves, str):
            if isinstance(grooves, str):
                self.grooves = Groove.from_yaml(f"{grooves}.yaml")
        else:
            self.grooves = grooves

        # validation for groove
        if self.grooves is not None:
            if self.grooves.gtype == "rint":
                if self.grooves.n * self.grooves.eps > 2*math.pi*self.r[0]:
                    raise ValidationError(f"Groove: {self.grooves.n} of eps={self.grooves.eps} exceed circumference on rint")
            if self.grooves.gtype == "rext":
                if self.grooves.n * self.grooves.eps > 2*math.pi*self.r[1]:
                    raise ValidationError(f"Groove: {self.grooves.n} of eps={self.grooves.eps} exceed circumference on rext")


        # add check for self.modelaxi.h must be less than (z[1]-z[0])/2.
        if self.modelaxi is not None and self.modelaxi.h > (z[1] - z[0]) / 2.0:
            raise ValidationError(
                f"modelaxi.h ({self.modelaxi.h}) must be less than half the helix height ({(z[1]-z[0])/2.0})"
            )
        
        # Store the directory context for resolving struct paths
        self._basedir = os.getcwd()

    def get_type(self) -> str:
        """
        Determine the helix type based on 3D model configuration.
        
        Returns:
            str: "HR" if model has both shapes and channels, "HL" otherwise
        
        Notes:
            - HR (Helix with Reinforcement): Includes shaped channels
            - HL (Helix Layer): Standard helical layer
        """
        if self.model3d.with_shapes and self.model3d.with_channels:
            return "HR"
        return "HL"

    def get_lc(self) -> float:
        """
        Calculate characteristic length for mesh generation.
        
        Returns:
            float: Characteristic length computed as radial thickness / 10
        
        Notes:
            Used by mesh generators to determine appropriate element size
        """
        return (self.r[1] - self.r[0]) / 10.0

    def get_names(self, mname: str, is2D: bool, verbose: bool = False) -> list[str]:
        """
        Generate marker names for mesh identification.
        
        Args:
            mname: Prefix for marker names (typically parent magnet name)
            is2D: True for 2D axisymmetric mesh, False for 3D mesh
            verbose: Enable verbose output for debugging
        
        Returns:
            list[str]: List of marker names for conductor and insulator regions
        
        Notes:
            - 2D mesh: Returns section-wise names (Cu0, Cu1, ..., CuN)
            - 3D mesh: Returns single Cu conductor and insulator names
            - Insulator type depends on helix type (Glue for HL, Kapton for HR)
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        sInsulator = "Glue"
        nInsulators = 0
        nturns = self.get_Nturns()
        htype = self.get_type()
        if htype == "HR":
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
        Generate string representation of Helix object.
        
        Returns:
            str: String representation including all parameters
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
        Create Helix instance from dictionary representation.
        
        Args:
            values: Dictionary containing helix parameters
            debug: Enable debug output during deserialization
        
        Returns:
            Helix: New Helix instance
        
        Notes:
            Handles nested objects (modelaxi, model3d, shape, chamfers, grooves)
            by loading from files or instantiating from dicts
        """
        modelaxi = cls._load_nested_single(values.get('modelaxi'), ModelAxi, debug=debug)
        model3d = cls._load_nested_single(values.get('model3d'), Model3D, debug=debug)
        shape = cls._load_nested_single(values.get('shape'), Shape, debug=debug)
        chamfers = cls._load_nested_list(values.get('chamfers'), Chamfer, debug=debug)
        grooves = cls._load_nested_single(values.get('grooves'), Groove, debug=debug)
        
        name = values["name"]
        r = values["r"]
        z = values["z"]
        odd = values["odd"]
        dble = values["dble"]
        cutwidth = values["cutwidth"]

        object = cls(
            name, r, z, cutwidth, odd, dble, modelaxi, model3d, shape, chamfers, grooves
        )
        # object.update()
        return object
    
    def getModelAxi(self):
        """
        Get the axisymmetric model definition.
        
        Returns:
            ModelAxi: Axisymmetric model object
        """
        return self.modelaxi

    def getModel3D(self):
        """
        Get the 3D CAD model configuration.
        
        Returns:
            Model3D: 3D model configuration object
        """
        return self.model3d

    def get_Nturns(self) -> float:
        """
        Get the number of turns in the helix.
        
        Returns:
            float: Number of turns from the axisymmetric model
        
        Notes:
            Delegates to modelaxi.get_Nturns() method
        """
        return self.modelaxi.get_Nturns()

    def generate_cut(self, format: str = "SALOME"):
        """
        Generate helical cut geometry file for CAD system.
        
        Args:
            format: Target CAD format (default: "SALOME")
        
        Notes:
            Creates helical cut definition file and optionally adds shapes
            if model3d.with_shapes is enabled. Uses external MagnetTools utilities.
        """
        

        create_cut(self, format, self.name)
        if self.model3d.with_shapes:

            # if Profile class is used: self.shape.profile.generate_dat_file()
            shape_profile = f"{self._basedir}/Shape_{self.shape.profile}.dat"
            if not os.path.exists(shape_profile):
                raise RuntimeError(f"Helix.generate_cut: {str(shape_profile)} no such file")
             
            if self.get_type() == "HL":
                angles = " ".join(f"{t:4.2f}" for t in self.shape.angle if t != 0)
                cmd = f'add_shape --angle="{angles}" --shape_angular_length={self.shape.length} --shape={shape_profile} --format={format} --position="{self.shape.position} {self.name}"'
                print(f"create_cut: with_shapes not implemented - shall run {cmd}")
            else:
                cmd = f'add_shape --angle="{angles[0]}" --shape_angular_length={self.shape.length[0]} --shape={shape_profile} --format={format} --position="{self.shape.position} {self.name}"'
                print(f"create_cut: with_shapes not implemented - shall run {cmd}")
            
            try:
                import subprocess

                subprocess.run(cmd, shell=True, check=True)
            except RuntimeError as e:
                raise Exception(f"cannot run add_shape properly: {e}")
            
    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if this helix intersects with a given rectangular region.
        
        Args:
            r: Radial bounds [r_min, r_max] of test region
            z: Axial bounds [z_min, z_max] of test region
        
        Returns:
            bool: True if regions overlap, False if no intersection
        
        Notes:
            Uses axis-aligned bounding box intersection test
        """
        
        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        
        return r_overlap and z_overlap

    def boundingBox(self) -> tuple:
        """
        Get the bounding box of the helix geometry.
        
        Returns:
            tuple: (r_bounds, z_bounds) where each is [min, max]
        
        Notes:
            Currently excludes current leads from bounding box calculation
        """
        return (self.r, self.z)

    def insulators(self):
        """
        Determine insulator material and count based on helix type.
        
        Returns:
            tuple: (insulator_name, count) where:
                - insulator_name: "Glue" for HL type, "Kapton" for HR type
                - count: Number of insulator regions
        
        Notes:
            - HL type: 1 or 2 insulators depending on dble flag
            - HR type: Calculated based on shape angular coverage and turns
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

