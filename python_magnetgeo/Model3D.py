#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

import json
import yaml

# from Shape import *
# from ModelAxi import *
# from Model3D import *

from . import Shape
from . import ModelAxi


class Model3D(yaml.YAMLObject):
    """
    cad :
    with_shapes :
    with_channels :
    """

    yaml_tag = "Model3D"

    def __init__(
        self, cad: str, with_shapes: bool = False, with_channels: bool = False
    ) -> None:
        """
        initialize object
        """
        self.cad = cad
        self.with_shapes = with_shapes
        self.with_channels = with_channels

    def __repr__(self):
        """
        representation of object
        """
        return "%s(cad=%r, with_shapes=%r, with_channels=%r)" % (
            self.__class__.__name__,
            self.cad,
            self.with_shapes,
            self.with_channels,
        )

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self, name: str = ""):
        """
        write from json file
        """
        with open(f"{name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'Model3D.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)

def Model3D_constructor(loader, node):
    """
    build an Model3d object
    """
    values = loader.construct_mapping(node)
    cad = values["cad"]
    with_shapes = values["with_shapes"]
    with_channels = values["with_channels"]
    return Model3D(cad, with_shapes, with_channels)


yaml.add_constructor("!Model3D", Model3D_constructor)
