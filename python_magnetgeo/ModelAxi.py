#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""
from typing import List

import json
import yaml
from . import deserialize


class ModelAxi(yaml.YAMLObject):
    """
    name :
    h :
    turns :
    pitch :
    """

    yaml_tag = "ModelAxi"

    def __init__(
        self,
        name: str = "",
        h: float = 0.0,
        turns: List[float] = [],
        pitch: List[float] = [],
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.h = h
        self.turns = turns
        self.pitch = pitch

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, h=%r, turns=%r, pitch=%r)" % (
            self.__class__.__name__,
            self.name,
            self.h,
            self.turns,
            self.pitch,
        )

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def from_json(self, string: str):
        """
        convert from json to yaml
        """
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return sum(self.turns)


def ModelAxi_constructor(loader, node):
    """
    build an ModelAxi object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    h = values["h"]
    turns = values["turns"]
    pitch = values["pitch"]
    return ModelAxi(name, h, turns, pitch)


yaml.add_constructor(u"!ModelAxi", ModelAxi_constructor)
