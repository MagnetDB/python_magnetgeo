#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides definition for chamfer geometry features.

This module defines the Chamfer class for representing beveled edges on
helical conductor geometries. Chamfers can be defined either by angle and
height or by radial offset and height.

Classes:
    Chamfer: Represents a chamfer (beveled edge) on a helix geometry

The chamfer can be positioned on either the high-pressure (HP) or
low-pressure (BP) side, and on either the inner (rint) or outer (rext) radius.
"""

import math

from .base import YAMLObjectBase


class Chamfer(YAMLObjectBase):
    """
    Represents a chamfer (beveled edge) on helical conductor geometry.

    A chamfer is a beveled edge that transitions between two surfaces, typically
    used to avoid sharp edges on conductor geometries. The chamfer can be specified
    either by its angle and height, or by its radial offset and height.

    Attributes:
        name (str): Unique identifier for the chamfer
        side (str): Axial position - "BP" (low pressure side) or "HP" (high pressure side)
        rside (str): Radial position - "rint" (inner radius) or "rext" (outer radius)
        alpha (float, optional): Chamfer angle in degrees (0 < alpha < 90)
        dr (float, optional): Radial offset in millimeters (shift along r direction)
        l (float): Axial height of the chamfer in millimeters

    Notes:
        - Either alpha OR dr must be provided (not both)
        - If both are given, they should be geometrically consistent
        - The relationship is: dr = l * tan(alpha)

    Example:
        >>> # Create chamfer with angle specification
        >>> chamfer1 = Chamfer(
        ...     name="top_chamfer",
        ...     side="HP",
        ...     rside="rext",
        ...     alpha=45.0,
        ...     l=5.0
        ... )
        >>>
        >>> # Create chamfer with radial offset specification
        >>> chamfer2 = Chamfer(
        ...     name="bottom_chamfer",
        ...     side="BP",
        ...     rside="rint",
        ...     dr=3.0,
        ...     l=5.0
        ... )
        >>>
        >>> # Get computed values
        >>> dr_value = chamfer1.getDr()  # Computes from angle
        >>> angle_value = chamfer2.getAngle()  # Computes from dr
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
        Initialize a Chamfer object.

        The chamfer can be defined either by angle (alpha) or radial offset (dr),
        along with the height (l). At least one of alpha or dr must be provided.

        Args:
            name: Unique identifier for the chamfer. Must follow standard naming
                  conventions (alphanumeric, underscores, hyphens).
            side: Axial position of the chamfer:
                  - "BP": Bottom/low-pressure side
                  - "HP": Top/high-pressure side

            rside: Radial position of the chamfer:
                   - "rint": Inner radius
                   - "rext": Outer radius

            alpha: Chamfer angle in degrees (optional). Must be in range (0, 90).
                   This defines the slope of the beveled edge.

            dr: Radial offset in millimeters (optional). This is the horizontal
                extent of the chamfer. Must be positive if specified.

            l: Axial height of the chamfer in millimeters. Must be positive.

        Raises:
            ValidationError: If name is invalid

        Notes:
            - At least one of alpha or dr should be provided for the chamfer to be useful
            - If both alpha and dr are provided, they should satisfy: dr = l * tan(alpha)
            - The actual validation of this relationship is not enforced in __init__

        Example:
            >>> # Angle-based chamfer
            >>> c1 = Chamfer("chamfer1", "HP", "rext", alpha=30.0, l=10.0)
            >>>
            >>> # Offset-based chamfer
            >>> c2 = Chamfer("chamfer2", "BP", "rint", dr=5.0, l=10.0)
            >>>
            >>> # Both specified (should be consistent)
            >>> c3 = Chamfer("chamfer3", "HP", "rext", alpha=45.0, dr=10.0, l=10.0)
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
        # alpha must be in [0; pi/2[ - the actual upper limit depends on the helix thickness

    def __repr__(self):
        """
        Return string representation of the Chamfer object.

        Returns:
            str: String showing class name and all attribute values

        Example:
            >>> c = Chamfer("test", "HP", "rext", alpha=45.0, l=10.0)
            >>> repr(c)
            "Chamfer(name=test, (side=HP, rside=rext, alpha=45.0,l=10.0)"
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
        Create a Chamfer object from a dictionary.

        This method is used for deserialization from YAML/JSON formats.
        Alpha and dr are optional fields in the dictionary.

        Args:
            values: Dictionary containing chamfer specification with keys:
                    - 'name': str
                    - 'side': str ("BP" or "HP")
                    - 'rside': str ("rint" or "rext")
                    - 'alpha': float (optional)
                    - 'dr': float (optional)
                    - 'l': float (required)
            debug: Enable debug output (default: False)

        Returns:
            Chamfer: New instance created from the dictionary data

        Raises:
            KeyError: If required keys are missing ('name', 'side', 'rside', 'l')
            ValidationError: If name or other values are invalid

        Example:
            >>> data = {
            ...     "name": "top_chamfer",
            ...     "side": "HP",
            ...     "rside": "rext",
            ...     "alpha": 30.0,
            ...     "l": 5.0
            ... }
            >>> chamfer = Chamfer.from_dict(data)
            >>>
            >>> # With dr instead of alpha
            >>> data2 = {
            ...     "name": "bot_chamfer",
            ...     "side": "BP",
            ...     "rside": "rint",
            ...     "dr": 4.0,
            ...     "l": 8.0
            ... }
            >>> chamfer2 = Chamfer.from_dict(data2)
        """
        name = values["name"]
        side = values["side"]
        rside = values["rside"]

        # Make alpha and dr optional
        alpha = values.get("alpha", None)
        dr = values.get("dr", None)

        l = values["l"]

        return cls(name, side, rside, alpha, dr, l)

    def getDr(self):
        """
        Calculate and return the radial offset of the chamfer.

        If dr is directly specified, returns that value. Otherwise, computes
        dr from the angle and height using: dr = l * tan(alpha).

        Returns:
            float: Radial offset in millimeters

        Raises:
            ValueError: If neither dr nor alpha is defined

        Example:
            >>> # Chamfer defined with angle
            >>> c1 = Chamfer("c1", "HP", "rext", alpha=45.0, l=10.0)
            >>> dr = c1.getDr()  # Returns 10.0 (tan(45°) = 1)
            >>>
            >>> # Chamfer defined with dr
            >>> c2 = Chamfer("c2", "BP", "rint", dr=5.0, l=10.0)
            >>> dr = c2.getDr()  # Returns 5.0 directly

        Notes:
            The angle alpha must be in degrees and will be converted to radians
            for the calculation.
        """
        if self.dr is None:
            if self.alpha is None:
                raise ValueError("Chamfer must have alpha when dr is not defined")
        else:
            return self.dr

        dr = self.l * math.tan(math.pi / 180.0 * self.alpha)
        return dr

    def getAngle(self):
        """
        Calculate and return the chamfer angle in degrees.

        If alpha is directly specified, returns that value. Otherwise, computes
        alpha from the radial offset and height using: alpha = atan(dr/l).

        Returns:
            float: Chamfer angle in degrees

        Raises:
            ValueError: If neither alpha nor dr is defined

        Example:
            >>> # Chamfer defined with dr
            >>> c1 = Chamfer("c1", "HP", "rext", dr=10.0, l=10.0)
            >>> angle = c1.getAngle()  # Returns 45.0 degrees (atan(1) = 45°)
            >>>
            >>> # Chamfer defined with angle
            >>> c2 = Chamfer("c2", "BP", "rint", alpha=30.0, l=10.0)
            >>> angle = c2.getAngle()  # Returns 30.0 directly

        Notes:
            The returned angle is in degrees. The internal calculation uses
            radians but converts the result to degrees.
        """
        if self.alpha is None:
            if self.dr is None:
                raise ValueError("Chamfer must have dr when alpha is not defined")
        else:
            return self.alpha

        angle = math.atan2(self.dr, self.l)
        return angle * 180 / math.pi
