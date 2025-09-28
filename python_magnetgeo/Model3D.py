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
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Model3D(YAMLObjectBase):
    """
    name:
    cad :
    with_shapes :
    with_channels :
    """

    yaml_tag = "Model3D"

    def __init__(
            self, name: str, cad: str, with_shapes: bool = False, with_channels: bool = False
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.cad = cad
        self.with_shapes = with_shapes
        self.with_channels = with_channels

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, cad=%r, with_shapes=%r, with_channels=%r)" % (
            self.__class__.__name__,
            self.name,
            self.cad,
            self.with_shapes,
            self.with_channels,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values.get("name", "")
        cad = values["cad"]
        with_shapes = values.get("with_shapes", False)
        with_channels = values.get("with_channels", False)

        return cls(name, cad, with_shapes, with_channels)
    
