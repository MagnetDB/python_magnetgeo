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
      L: height in mm
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
        L: float = None,
    ):
        """
        initialize object
        """
        self.side = side
        self.rside = rside
        self.alpha = alpha
        self.dr = dr
        self.L = L

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
        msg += f", L=self.{L})"
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

    def load(self, name: str):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Chamfer data {name}.yaml")

        self.side = data.side
        self.rside = data.rside

        # Always ensure these attributes exist for backward compatibility
        # Even if they don't exist in the loaded data
        self.alpha = getattr(data, 'alpha', None)
        self.dr = getattr(data, 'dr', None)

        self.L = data.L

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

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
                self.L
                * math.tan(math.pi / 180.0 * self.alpha)
            )
        return radius

    def getAngle(self):
        """
        returns chamfer angle 
        """
        if self.alpha:
            return self.alpha

        angle = math.atan2(dr, L)
        return angle * 180 / math.pi
    

def Chamfer_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    side = values["side"]
    rside = values["rside"]

    # Make chamfers and grooves optional
    alpha = values.get("alpha", None)
    dr = values.get("dr", None)

    L = values["L"]
    return Chamfer(side, rside, alpha, L)


yaml.add_constructor("!Chamfer", Chamfer_constructor)
