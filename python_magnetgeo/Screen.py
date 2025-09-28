#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Screen:

* Geom data: r, z
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError



class Screen(YAMLObjectBase):
    """
    name :
    r :
    z :
    """

    yaml_tag = "Screen"

    def __init__(self, name: str, r: list[float], z: list[float]):
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z

    def get_lc(self):
        return (self.r[1] - self.r[0]) / 10.0

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list:
        return []

    def get_isolants(self, mname: str, debug: bool = False):
        """
        return isolants
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        return names for Markers
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        solid_names.append(f"{prefix}{self.name}_Screen")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]
        return cls(name, r, z)        

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """
        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        return r_overlap and z_overlap

