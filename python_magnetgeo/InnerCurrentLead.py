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
        # General validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        GeometryValidator.validate_positive(h, "h")
        
        if holes:
            GeometryValidator.validate_numeric_list(holes, "holes", expected_length=6)
            if holes[0] <= 0:
                raise ValidationError("H_Holes must be positive")
            if holes[1] < 0:
                raise ValidationError("Shift_from_Top must be non-negative")
            if not (0 <= holes[2] < 360):
                raise ValidationError("Angle_Zero must be in [0, 360)")
            if not (0 < holes[3] <= 360):
                raise ValidationError("Angle must be in (0, 360]")
            if not (0 <= holes[4] < 360):
                raise ValidationError("Angular_Position must be in [0, 360)")
            if holes[5] <= 0 or not isinstance(holes[5], int):
                raise ValidationError("N_Holes must be a positive integer")
        if support:
            GeometryValidator.validate_numeric_list(support, "support", expected_length=2)
            GeometryValidator.validate_positive(support[0], "R support")
            GeometryValidator.validate_numeric(support[1], "Dz support")

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

