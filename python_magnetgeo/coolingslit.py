#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for CoolingSlits:
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class CoolingSlit(YAMLObjectBase):
    """
    r: radius
    angle: anglar shift from tierod
    n:
    dh: 4*Sh/Ph with Ph wetted perimeter
    sh:
    shape:
    """

    yaml_tag = "CoolingSlit"

    def __init__(
        self, name: str, r: float, angle: float, n: int, dh: float, sh: float, shape
    ) -> None:
        self.name: str = name
        self.r: float = r
        self.angle: float = angle
        self.n: int = n
        self.dh: float = dh
        self.sh: float = sh
        self.shape = shape

    def __repr__(self):
        return "%s(name=%s, r=%r, angle=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.angle,
            self.n,
            self.dh,
            self.sh,
            self.shape,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        # Basic parameters
        _params = {
            "name": values.get("name", ""),
            "r": values["r"],
            "angle": values["angle"],
            "n": values["n"],
            "dh": values["dh"],
            "sh": values["sh"],
        }

        # Handle nested objects (they might be dicts or already instantiated)
        if 'shape' in values and values['shape']:
            shape_data = values['shape']
            if isinstance(shape_data, dict):
                from .Contour2D import Contour2D
                _params['shape'] = Contour2D.from_dict(shape_data)
            else:
                _params['shape'] = shape_data
        
        return cls(**_params)
    
