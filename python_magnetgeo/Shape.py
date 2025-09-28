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

class Shape(YAMLObjectBase):
    """
    name :
    profile : name of the cut profile to be added
      if some ids are non-nul it means that micro-channels are to be added

    params :
      length : specify shape angular length in degree - single value or list
      angle : angle between 2 consecutive shape (in deg) - single value or list
      onturns : specify on which turns to add cuts - single value or list
      position : ABOVE|BELLOW|ALTERNATE
    """

    yaml_tag = "Shape"

    def __init__(
        self,
        name: str,
        profile: str,
        length: list[float] = [0.0],
        angle: list[float] = [0.0],
        onturns: list[int] = [1],
        position: str = "ABOVE",
    ):
        """
        initialize object
        """
        self.name = name
        self.profile = profile
        self.length = length
        self.angle = angle
        self.onturns = onturns
        self.position = position

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, profile=%r, length=%r, angle=%r, onturns=%r, position=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.profile,
                self.length,
                self.angle,
                self.onturns,
                self.position,
            )
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        profile = values["profile"]
        length = values["length"]
        angle = values["angle"]
        onturns = values["onturns"]
        position = values["position"]
        return cls(name, profile, length, angle, onturns, position)

