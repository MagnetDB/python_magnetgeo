#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Chamfer:

* side: str for z position: HP or BP
* rside: str for r postion: rint or rext
* alpha: angle in degree
* L: height in mm
* radius: radius of chamfer (optional)

"""

import yaml
import json
import math


class Chamfer(yaml.YAMLObject):
    """
    name :

    params :
      x, y: list of points
    """

    yaml_tag = "Chamfer"

    def __init__(
        self,
        name: str,
        side: str,
        rside: str,
        alpha: float,
        L: float,
        radius: float | None = None,
    ):
        """
        initialize object
        """
        self.name = name
        self.side = side
        self.rside = rside
        self.alpha = alpha
        self.L = L
        if radius is not None:
            self.radius = radius
        else:
            self.radius = (
                L
                * math.sin(math.pi / 180.0 * alpha)
                / math.cos(math.pi / 180.0 * alpha)
            )

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, side=%r, rside=%r, alpha=%r, L=%r, radius=%r)" % (
            self.__class__.__name__,
            self.name,
            self.side,
            self.rside,
            self.alpha,
            self.L,
            self.radius,
        )

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

        self.name = name
        self.side = data.side
        self.rside = data.rside
        self.alpha = data.alpha
        self.L = data.L
        self.radius = (
            self.L
            * math.sin(self.alpha * math.pi / 180.0)
            / math.cos(self.alpha * math.pi / 180.0)
        )

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


def Shape_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    side = values["side"]
    rside = values["rside"]
    alpha = values["alpha"]
    L = values["L"]
    radius = None
    if "radius" in values:
        radius = values["radius"]
    return Chamfer(name, side, rside, alpha, L, radius)


yaml.add_constructor("!Chamfer", Shape_constructor)
