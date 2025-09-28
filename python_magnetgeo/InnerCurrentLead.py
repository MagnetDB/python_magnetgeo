#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides Inner and OuterCurrentLead class
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class InnerCurrentLead(YAMLObjectBase):
    """
    name :
    r : [R0, R1]
    h :
    holes: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
    support: [R2, DZ]
    fillet:
    """

    yaml_tag = "InnerCurrentLead"

    def __init__(
        self,
        name: str,
        r: list[float],
        h: float = 0.0,
        holes: list = [],
        support: list = [],
        fillet: bool = False,
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.h = h
        self.holes = holes
        self.support = support
        self.fillet = fillet

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, h=%r, holes=%r, support=%r, fillet=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.h,
            self.holes,
            self.support,
            self.fillet,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        h = values["h"]
        holes = values["holes"]
        support = values["support"]
        fillet = values["fillet"]
        return cls(name, r, h, holes, support, fillet)        

