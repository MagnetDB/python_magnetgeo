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

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

    
class Chamfer(YAMLObjectBase):
    """
    name :

    params :
      name:
      side: BP or HP
      rside: rint or rext in mm
      alpha: angle in degree
      dr: shift along r in mm
      l: height in mm
    """

    yaml_tag = "Chamfer"

    def __init__(
        self,
        name: str,
        side: str,
        rside: str,
        alpha: float = None,
        dr: float = None,
        l: float = None,
    ):
        """
        initialize object
        """
        self.name = name
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
        msg += f"(name={self.name}, "
        msg += f"(side={self.side}, "
        msg += f", rside={self.rside}"
        if hasattr(self, "alpha"):
            msg += f", alpha={self.alpha}"
        if hasattr(self, "dr"):
            msg += f", dr={self.dr}"
        msg += f",l={self.l})"
        return msg

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        side = values["side"]
        rside = values["rside"]

        # Make chamfers and grooves optional
        alpha = values.get("alpha", None)
        dr = values.get("dr", None)

        l = values["l"]

        return cls(name, side, rside, alpha, dr, l)
    
    def getDr(self):
        """
        returns chamfer radius reduction 
        """
        if self.dr is None:
            if self.alpha is None:
                raise ValueError("Chamfer must have alpha when dr is not defined")
        else:
            return self.dr
        
        dr = (
                self.l
                * math.tan(math.pi / 180.0 * self.alpha)
            )
        return dr

    def getAngle(self):
        """
        returns chamfer angle 
        """
        if self.alpha is None:
            if self.dr is None:
                raise ValueError("Chamfer must have dr when alpha is not defined")
        else:
            return self.alpha

        angle = math.atan2(self.dr, self.l)
        return angle * 180 / math.pi
    

