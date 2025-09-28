#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides Inner and OuterCurrentLead class
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class OuterCurrentLead(YAMLObjectBase):
    """
    name :

    r : [R0, R1]
    h :
    bar : [R, DX, DY, L]
    support : [DX0, DZ, Angle, Angle_Zero]

    bar looks like that:
    A rectangle (dx,dy) cut by a disk of R radius centered on Origin X     

    -------------
    | (   x   ) |
    -------------

    create a prism along Oz with legnth L from the result
    bar translated to [r[1] - DX0 + DY/2, 0, 0]

    support:
    rectangle(DX, DX0)
    translated to [r[1] - DX0 + DY/2, 0, 0]
    rectangle cut by a disk of r[1] radius centered on Origin X
    """

    yaml_tag = "OuterCurrentLead"

    def __init__(
        self,
        name: str,
        r: list[float] = [],
        h: float = 0.0,
        bar: list = [],
        support: list = [],
    ) -> None:
        """
        create object
        """
        self.name = name
        self.r = r
        self.h = h
        self.bar = bar
        self.support = support

    def __repr__(self):
        """
        representation object
        """
        return "%s(name=%r, r=%r, h=%r, bar=%r, support=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.h,
            self.bar,
            self.support,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        h = values["h"]
        bar = values["bar"]
        support = values["support"]
        return cls(name, r, h, bar, support)


