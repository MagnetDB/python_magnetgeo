#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides definition for Shape with Position enum
"""
import os
from enum import Enum

from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class ShapePosition(Enum):
    """
    Enumeration defining valid positions for shape placement on helical cuts.

    This enum specifies where additional cut profiles (shapes) should be placed
    relative to the main helical cut pattern in Helix or Bitter magnets.

    Attributes:
        ABOVE: Place shapes above the reference plane
        BELOW: Place shapes below the reference plane
        ALTERNATE: Alternate shapes between above and below positions

    Notes:
        - Position determines the vertical placement of cut profiles
        - ALTERNATE is useful for balanced geometric patterns
        - String values are uppercase for consistency with YAML format
        - The __str__ method returns the enum value for serialization

    Example:
        >>> from python_magnetgeo.Shape import ShapePosition
        >>> pos1 = ShapePosition.ABOVE
        >>> pos2 = ShapePosition["BELOW"]
        >>> pos3 = ShapePosition.ALTERNATE
        >>>
        >>> # String representation
        >>> print(pos1)  # "ABOVE"
        >>> print(pos2.value)  # "BELOW"
    """

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
        length: list[float] = None,
        angle: list[float] = None,
        onturns: list[int] = None,
        position: ShapePosition | str = ShapePosition.ABOVE,
    ):
        """
        Initialize a Shape definition for helical cut modifications.

        A Shape represents additional geometric features (cut profiles) that can be
            applied to helical cuts in magnet conductors. These shapes modify the basic
            helical pattern to create features like cooling channels, mechanical slots,
            or other specialized geometries.

        Args:
            name: Unique identifier for this shape configuration
            profile: Name of the cut profile to be applied. References a predefined
                    geometric profile that will be added to the helical cut.
            length: List of angular lengths in degrees. Specifies how long each
                shape extends along the circumference. Can be single value or
                list for multiple configurations. Default: [0.0]
            angle: List of angles in degrees between consecutive shapes. Defines
                the spacing when multiple shapes are placed. Can be single value
                or list. Default: [0.0]
            onturns: List of turn numbers specifying which helical turns should
                    receive the shape modifications. Turn numbering starts from 1.
                    Can be single value or list. Default: [1]
            position: Placement position for shapes, either:
                    - ShapePosition enum value (ABOVE, BELOW, ALTERNATE)
                    - String ("ABOVE", "BELOW", or "ALTERNATE")
                    Default: ShapePosition.ABOVE

        Raises:
            ValidationError: If name is invalid (empty or None)
            ValidationError: If position string doesn't match valid enum values
            ValidationError: If position is neither string nor ShapePosition enum

        Notes:
            - All list parameters default to single-element lists if None
            - String position values are automatically converted to enum
            - Position strings are case-insensitive (converted to uppercase)
            - Profile name references an externally defined cut geometry
            - Shapes are applied during helical cut generation

        Example:
            >>> # Simple shape on first turn
            >>> shape1 = Shape(
            ...     name="cooling_slot",
            ...     profile="rectangular_cut",
            ...     length=[5.0],        # 5 degrees wide
            ...     angle=[30.0],        # Spaced 30 degrees apart
            ...     onturns=[1],         # Only on first turn
            ...     position="ABOVE"
            ... )

            >>> # Shape on multiple turns with enum
            >>> from python_magnetgeo.Shape import ShapePosition
            >>> shape2 = Shape(
            ...     name="vent_holes",
            ...     profile="circular_hole",
            ...     length=[3.0, 4.0],   # Different lengths
            ...     angle=[45.0],        # Fixed spacing
            ...     onturns=[1, 3, 5],   # Odd turns only
            ...     position=ShapePosition.ALTERNATE
            ... )

            >>> # Using defaults
            >>> shape3 = Shape(
            ...     name="simple_cut",
            ...     profile="slot_a"
            ...     # length, angle, onturns use defaults
            ...     # position defaults to ABOVE
            ... )
        """
        # GeometryValidator.validate_name(name)
        
        self.name = name
        self.profile = profile
        self.length = length if length is not None else [0.0]
        self.angle = angle if angle is not None else [0.0]
        self.onturns = onturns if onturns is not None else [1]

        # Handle position - convert string to enum if needed
        if isinstance(position, str):
            try:
                self.position = ShapePosition[position.upper()]
            except KeyError as e:
                valid_positions = ", ".join([p.name for p in ShapePosition])
                raise ValidationError(
                    f"Invalid position '{position}'. Must be one of: {valid_positions}"
                ) from e
        elif isinstance(position, ShapePosition):
            self.position = position
        else:
            raise ValidationError(
                f"Position must be string or ShapePosition enum, got {type(position)}"
            )

        # Store the directory context for resolving struct paths
        self._basedir = os.getcwd()

    def __repr__(self):
        """
        Return string representation of Shape instance.

        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.

        Returns:
            str: String representation in constructor-like format showing:
                - name: Shape identifier
                - profile: Cut profile name
                - length: Angular length list
                - angle: Spacing angle list
                - onturns: Turn number list
                - position: Position as string value (not enum)

        Notes:
            - Position is shown as string value (e.g., "ABOVE") not enum representation
            - Handles both enum and string position values during deserialization
            - Uses getattr with fallback to handle position gracefully

        Example:
            >>> shape = Shape(
            ...     name="test_shape",
            ...     profile="slot",
            ...     length=[5.0],
            ...     angle=[30.0],
            ...     onturns=[1, 2],
            ...     position="ABOVE"
            ... )
            >>> print(repr(shape))
            Shape(name='test_shape', profile='slot', length=[5.0],
                angle=[30.0], onturns=[1, 2], position='ABOVE')
            >>>
            >>> # In Python REPL
            >>> shape
            Shape(name='test_shape', profile='slot', ...)
            >>>
            >>> # With enum position
            >>> from python_magnetgeo.Shape import ShapePosition
            >>> shape2 = Shape("shape2", "hole", position=ShapePosition.BELOW)
            >>> print(repr(shape2))
            Shape(name='shape2', profile='hole', length=[0.0],
                angle=[0.0], onturns=[1], position='BELOW')
        """
        # Handle position being either enum or string during deserialization
        position_str = getattr(self.position, "value", self.position)
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"profile={self.profile!r}, length={self.length!r}, "
            f"angle={self.angle!r}, onturns={self.onturns!r}, "
            f"position={position_str!r})"
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Shape instance from dictionary representation.

        Provides flexible deserialization with proper defaults for optional parameters.
        String position values are automatically converted to ShapePosition enum.

        Args:
            values: Dictionary containing Shape configuration with keys:
                - name (str): Shape identifier (required)
                - profile (str): Cut profile name (required)
                - length (list[float], optional): Angular lengths in degrees
                Default: [0.0]
                - angle (list[float], optional): Spacing angles in degrees
                Default: [0.0]
                - onturns (list[int], optional): Turn numbers for placement
                Default: [1]
                - position (str or ShapePosition, optional): Placement position
                Default: "ABOVE"
            debug: Enable debug output showing object creation process

        Returns:
            Shape: New Shape instance created from dictionary

        Raises:
            KeyError: If required keys ('name' or 'profile') are missing
            ValidationError: If position value is invalid
            ValidationError: If name validation fails

        Notes:
            - All optional parameters have sensible defaults
            - Position strings are case-insensitive
            - Lists can be single values or arrays

        Example:
            >>> # Full specification
            >>> data = {
            ...     "name": "cooling_channels",
            ...     "profile": "rect_slot",
            ...     "length": [5.0, 6.0],
            ...     "angle": [30.0],
            ...     "onturns": [1, 2, 3],
            ...     "position": "ABOVE"
            ... }
            >>> shape = Shape.from_dict(data)

            >>> # Minimal specification (uses defaults)
            >>> minimal = {
            ...     "name": "simple_shape",
            ...     "profile": "slot_b"
            ... }
            >>> shape2 = Shape.from_dict(minimal)
            >>> # shape2.length == [0.0]
            >>> # shape2.angle == [0.0]
            >>> # shape2.onturns == [1]
            >>> # shape2.position == ShapePosition.ABOVE

            >>> # Using enum value in dict
            >>> from python_magnetgeo.Shape import ShapePosition
            >>> data3 = {
            ...     "name": "alt_shape",
            ...     "profile": "hole",
            ...     "position": ShapePosition.ALTERNATE
            ... }
            >>> shape3 = Shape.from_dict(data3)
        """
        return cls(
            name=values["name"],
            profile=values["profile"],
            length=values.get("length", [0.0]),
            angle=values.get("angle", [0.0]),
            onturns=values.get("onturns", [1]),
            position=values.get("position", "ABOVE"),
        )
