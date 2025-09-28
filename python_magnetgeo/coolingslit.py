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
    contour2d:
    """

    yaml_tag = "CoolingSlit"

    def __init__(
        self, name: str, r: float, angle: float, n: int, dh: float, sh: float, contour2d
    ) -> None:
        self.name: str = name
        self.r: float = r
        self.angle: float = angle
        self.n: int = n
        self.dh: float = dh
        self.sh: float = sh
        self.contour2d = contour2d

    def __repr__(self):
        return "%s(name=%s, r=%r, angle=%r, n=%r, dh=%r, sh=%r, contour2d=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.angle,
            self.n,
            self.dh,
            self.sh,
            self.contour2d,
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
        if 'contour2d' in values and values['contour2d']:
            contour2d_data = values['contour2d']
            if isinstance(contour2d_data, dict):
                from .Contour2D import Contour2D
                _params['contour2d'] = Contour2D.from_dict(contour2d_data)
            else:
                _params['contour2d'] = contour2d_data
        
        return cls(**_params)
    
