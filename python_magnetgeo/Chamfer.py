#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Chamfer:

* side: str for z position: HP or BP
* rside: str for r postion: rint or rext
* alpha: angle in degree
* L: height in mm

"""

import yaml
import json
import math


class Chamfer(yaml.YAMLObject):
    """
    name :

    params :
      side: BP or HP
      rside: rint or rext in mm
      alpha: angle in degree
      dr: shift along r in mm
      l: height in mm
    """

    yaml_tag = "Chamfer"

    def __setstate__(self, state):
        """
        This method is called during deserialization (when loading from YAML or pickle)
        We use it to ensure the optional attributes always exist
        """
        self.__dict__.update(state)
        
        # Ensure these attributes always exist
        if not hasattr(self, 'dr'):
            self.dr = None
        if not hasattr(self, 'alpha'):
            self.alpha = None

    def __init__(
        self,
        side: str,
        rside: str,
        alpha: float = None,
        dr: float = None,
        l: float = None,
    ):
        """
        initialize object
        """
        self.side = side
        self.rside = rside
        self.alpha = alpha
        self.dr = dr
        self.l = l

        # TODO: data validation 
        # at least alpha or dr must be given
        # if alpha et dr are given, check if they are consistant
        # alpha must be in [0; pi/2[ - the actual upper limit depends on the helix thcikness 

    def __repr__(self):
        """
        representation of object
        """
        msg = self.__class__.__name__
        msg += f"(side={self.side}, "
        msg += f", rside={self.rside}"
        if hasattr(self, "alpha"):
            msg += f", alpha={self.alpha}"
        if hasattr(self, "dr"):
            msg += f", dr={self.dr}"
        msg += f",l={self.l})"
        return msg

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception("Failed to Chamfer dump")

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        import os
        cwd = os.getcwd()

        (basedir, basename) = os.path.split(filename)
        print(f"basedir={basedir}, basename={basename}, cwd={cwd}")

        if basedir and basedir != ".":
            os.chdir(basedir)
            print(f"-> cwd={cwd}")

        try:
            with open(basename, "r") as istream:
                values, otype = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Chamfer data {filename}")
        
        if basedir and basedir != ".":
            os.chdir(cwd)

        side = values["side"]
        rside = values["rside"]

        # Make chamfers and grooves optional
        alpha = values.get("alpha", None)
        dr = values.get("dr", None)

        l = values["l"]
        return cls(side, rside, alpha, l)

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f"Chamfer.from_json: filename={filename}")
        with open(filename, "r") as istream:
            return json.loads(
                istream.read(), object_hook=deserialize.unserialize_object
            )

    def getRadius(self):
        """
        returns chamfer radius reduction 
        """
        if self.dr:
            return self.dr

        radius = (
                self.l
                * math.tan(math.pi / 180.0 * self.alpha)
            )
        return radius

    def getAngle(self):
        """
        returns chamfer angle 
        """
        if self.alpha:
            return self.alpha

        angle = math.atan2(self.dr, self.l)
        return angle * 180 / math.pi
    

def Chamfer_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    return values, "Chamfer"


yaml.add_constructor(Chamfer.yaml_tag, Chamfer_constructor)
