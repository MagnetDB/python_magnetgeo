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
import json
import yaml

from .Groove import Groove
from .Chamfer import Chamfer
from .Shape import Shape
from .ModelAxi import ModelAxi
from .Model3D import Model3D

from .utils import loadObject, loadList

class Helix(yaml.YAMLObject):
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
    
    def __setstate__(self, state):
        """
        This method is called during deserialization (when loading from YAML or pickle)
        We use it to ensure the optional attributes always exist
        """
        self.__dict__.update(state)
        
        # Ensure these attributes always exist
        if not hasattr(self, 'chamfers'):
            self.chamfers = []
        if not hasattr(self, 'grooves'):
            self.grooves = Groove()

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
        
        self.name = name
        self.dble = dble
        self.odd = odd
        self.r = r
        self.z = z
        self.cutwidth = cutwidth
        self.modelaxi = modelaxi
        self.model3d = model3d

        self.shape = shape
        self.chamfers = chamfers if chamfers is not None else []
        self.grooves = grooves if grooves is not None else Groove()

    def update(self):
        """
        update magnets if there were loaded as str
        """
        from .utils import check_objects        
        if isinstance(self.modelaxi, str):
            self.modelaxi = loadObject("modelaxi", self.modelaxi, ModelAxi, ModelAxi.from_yaml)
        if isinstance(self.model3d, str):
            self.model3d = loadObject("model3d", self.model3d, Model3D, Model3D.from_yaml)
        if isinstance(self.shape, str):
            self.shape = loadObject("shape", self.shape, Shape, Shape.from_yaml)
        if check_objects(self.chamfers, str):
            self.chamfers = loadList("chamfers", self.chamfers, [None, Chamfer], {"Chamfer}": Chamfer.from_yaml})
        if isinstance(self.grooves, str):
            self.grooves = loadObject("groove", self.grooves, Groove, Groove.from_yaml)        


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
        if self.model3d.with_shapes and self.model3d.with_channels:
            sInsulator = "Kapton"
            htype = "HR"
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
            htype = "HL"
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

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception as e:
            raise Exception(f"Failed to Helix dump ({e})")

    @property
    def axi(self):
        return self.modelaxi

    @property
    def m3d(self):
        return self.model3d

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]
        odd = values["odd"]
        dble = values["dble"]
        cutwidth = values["cutwidth"]
        modelaxi = values["modelaxi"]
        model3d = values["model3d"]
        shape = values["shape"]

        # Make chamfers and grooves optional
        chamfers = values["chamfers"] if "chamfers" in values else []
        grooves = values["grooves"] if "grooves" in values else Groove()

        helix = cls(
            name, r, z, cutwidth, odd, dble, modelaxi, model3d, shape, chamfers, grooves
        )
        return helix

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("Helix", filename, Helix, debug)

        if basedir and basedir != ".":
            os.chdir(cwd)
        
        return helix

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("Helix", filename, debug)

    def write_to_json(self):
        """
        write from json file
        """
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

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

        if self.model3d.with_shapes:
            create_cut(self, "LNCMI", self.name)
            angles = " ".join(f"{t:4.2f}" for t in self.shape.angle if t != 0)
            cmd = f'add_shape --angle="{angles}" --shape_angular_length={self.shape.length} --shape={self.shape.name} --format={format} --position="{self.shape.position}"'
            print(f"create_cut: with_shapes not implemented - shall run {cmd}")

            import subprocess

            subprocess.run(cmd, shell=True, check=True)
        else:
            create_cut(self, format, self.name)

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]

        so far exclude Leads
        """
        return (self.r, self.z)

    def htype(self):
        """
        return the type of Helix (aka HR or HL)
        """
        htype = "HL"
        if self.model3d.with_shapes and self.model3d.with_channels:
            htype = "HR"
        return htype

    def insulators(self):
        """
        return name and number of insulators depending on htype
        """

        sInsulator = "Glue"
        nInsulators = 0
        if self.htype() == "HL":
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


def Helix_constructor(loader, node):
    """
    build an helix object
    """
    
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    dble = values["dble"]
    cutwidth = values["cutwidth"]
    modelaxi = values["modelaxi"]
    model3d = values["model3d"]
    shape = values["shape"]

    # Make chamfers and grooves optional
    chamfers = values.get("chamfers", [])
    grooves = values.get("grooves", Groove())

    return Helix(
        name, r, z, cutwidth, odd, dble, modelaxi, model3d, shape, chamfers, grooves
    )

    

yaml.add_constructor(Helix.yaml_tag, Helix_constructor)
