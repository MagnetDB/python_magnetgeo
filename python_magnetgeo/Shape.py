#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Shape with Position enum
"""

from enum import Enum
from typing import List, Union
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class ShapePosition(Enum):
    """Valid positions for shape placement"""
    ABOVE = "ABOVE"
    BELOW = "BELOW"  # Note: fixed typo from BELLOW
    ALTERNATE = "ALTERNATE"
    
    def __str__(self):
        """String representation returns the value"""
        return self.value


class Shape(YAMLObjectBase):
    """
    Shape definition for helical cuts
    
    Attributes:
        name: Shape identifier
        profile: Name of the cut profile to be added
        length: Shape angular length in degrees - single value or list
        angle: Angle between 2 consecutive shapes (in deg) - single value or list
        onturns: Specify on which turns to add cuts - single value or list
        position: Shape position (ABOVE, BELOW, or ALTERNATE)
    """

    yaml_tag = "Shape"

    def __init__(
        self,
        name: str,
        profile: str,
        length: List[float] = None,
        angle: List[float] = None,
        onturns: List[int] = None,
        position: Union[ShapePosition, str] = ShapePosition.ABOVE,
    ):
        """
        Initialize Shape object
        
        Args:
            name: Shape identifier
            profile: Cut profile name
            length: Angular length(s) in degrees
            angle: Angle(s) between consecutive shapes
            onturns: Turn number(s) for cut placement
            position: Position (ABOVE, BELOW, or ALTERNATE)
        
        Raises:
            ValidationError: If name is invalid or position is not recognized
        """
        GeometryValidator.validate_name(name)
        
        self.name = name
        self.profile = profile
        self.length = length if length is not None else [0.0]
        self.angle = angle if angle is not None else [0.0]
        self.onturns = onturns if onturns is not None else [1]
        
        # Handle position - convert string to enum if needed
        if isinstance(position, str):
            try:
                self.position = ShapePosition[position.upper()]
            except KeyError:
                valid_positions = ', '.join([p.name for p in ShapePosition])
                raise ValidationError(
                    f"Invalid position '{position}'. Must be one of: {valid_positions}"
                )
        elif isinstance(position, ShapePosition):
            self.position = position
        else:
            raise ValidationError(
                f"Position must be string or ShapePosition enum, got {type(position)}"
            )

    def __repr__(self):
        """String representation of object"""
        # Handle position being either enum or string during deserialization
        position_str = getattr(self.position, 'value', self.position)
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"profile={self.profile!r}, length={self.length!r}, "
            f"angle={self.angle!r}, onturns={self.onturns!r}, "
            f"position={position_str!r})"
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Shape from dictionary with proper defaults
        
        Args:
            values: Dictionary containing shape data
            debug: Enable debug output
            
        Returns:
            New Shape instance
            
        Raises:
            ValidationError: If position value is invalid
        """
        return cls(
            name=values["name"],
            profile=values["profile"],
            length=values.get("length", [0.0]),
            angle=values.get("angle", [0.0]),
            onturns=values.get("onturns", [1]),
            position=values.get("position", "ABOVE")
        )
