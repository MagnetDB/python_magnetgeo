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
        
        # General validation
        GeometryValidator.validate_name(name)
        
        # Ring-specific validation
        GeometryValidator.validate_integer(n, "n")
        GeometryValidator.validate_positive(n, "n")
        GeometryValidator.validate_positive(r, "r")
        GeometryValidator.validate_positive(dh, "dh")
        GeometryValidator.validate_positive(sh, "sh") 

        # Check ring cooling slits
        if n * angle > 360:
            raise ValidationError(f"CoolingSlit: {n} slits total angular length ({n * angle} cannot exceed 360 degrees")

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
        # Smart nested object handling
        contour2d = cls._load_nested_contour2d(values.get('contour2d'), debug=debug)
        return cls(
            name=values.get("name", ""),
            r=values["r"],
            angle=values["angle"],
            n=values["n"],
            dh=values["dh"],
            sh=values["sh"],
            contour2d=contour2d
        )
    
    @classmethod  
    def _load_nested_contour2d(cls, contour2d_data, debug=False):
        if isinstance(contour2d_data, str):
            # String reference → load from "contour2d_data.yaml"
            from .utils import loadObject
            from .Contour2D import Contour2D
            return loadObject("contour2d", contour2d_data, Contour2D, Contour2D.from_yaml)
        elif isinstance(contour2d_data, dict):
            # Inline object → create from dict
            from .Contour2D import Contour2D
            return Contour2D.from_dict(contour2d_data)
        else:
            # None or already instantiated
            return contour2d_data
