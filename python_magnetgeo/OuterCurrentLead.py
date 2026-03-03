#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides Inner and OuterCurrentLead class
"""

from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class OuterCurrentLead(YAMLObjectBase):
    """
    Outer current lead geometry for magnet electrical connections.

    Represents the current lead structure on the outer bore of a magnet assembly,
    including conductor bar geometry and support structure. The bar has a unique
    shape: a rectangular prism with a circular disk cut from it.

    Attributes:
        name (str): Unique identifier for the current lead
        r (list[float]): Radial bounds [R0, R1] in mm, where R0 < R1
        h (float): Height/length of the current lead in mm (default: 0.0)
        bar (list): Conductor bar geometry with 4 parameters (optional):
            [0] R: Radius of circular cut in mm (positive)
            [1] DX: Rectangle width in mm (positive)
            [2] DY: Rectangle height in mm (positive)
            [3] L: Extrusion length along Z axis in mm (positive)

        support (list): Support structure with 4 parameters (optional):
            [0] DX0: Support width in mm (positive)
            [1] DZ: Vertical offset in mm (positive)
            [2] Angle: Angular span in degrees (0, 360]
            [3] Angle_Zero: Starting angle in degrees [0, 360)

    Bar Geometry Description:
        The bar is created by:
        1. Start with a rectangle (DX × DY) in the XY plane
        2. Cut it with a circular disk of radius R centered at origin
        3. Extrude the result along Z axis for length L
        4. Translate to position [r[1] - DX0 + DY/2, 0, 0]

        ASCII representation:
            -------------
            | (   x   ) |  <- Rectangle with circular cut
            -------------

        Where the parentheses represent the circular disk cutting into the rectangle.

    Support Geometry Description:
        The support is:
        1. A rectangle (DX × DX0)
        2. Positioned at [r[1] - DX0 + DY/2, 0, 0]
        3. Cut by a disk of radius r[1] centered at origin
        4. Angular positioning controlled by Angle and Angle_Zero

    Validation Rules:
        - name must be non-empty string
        - r must have exactly 2 elements in ascending order
        - h must be non-negative
        - bar, if provided, must have exactly 4 positive elements
        - support, if provided, must have exactly 4 elements with:
          * First two positive
          * Angle in (0, 360]
          * Angle_Zero in [0, 360)

    Example:
        >>> # Basic outer lead without bar/support
        >>> lead = OuterCurrentLead(
        ...     name="outer_lead_1",
        ...     r=[50.0, 60.0],
        ...     h=100.0
        ... )
        >>>
        >>> # Complete outer lead with bar and support
        >>> lead_full = OuterCurrentLead(
        ...     name="outer_lead_complete",
        ...     r=[54.0, 64.0],
        ...     h=105.0,
        ...     bar=[59.0, 13.0, 19.0, 85.0],      # Conductor bar geometry
        ...     support=[6.5, 13.0, 38.0, 0.0]     # Support structure
        ... )

    Notes:
        - Outer leads typically connect to coils on the outside bore
        - Bar geometry is more complex than inner leads due to shape requirements
        - Support structure provides mechanical stability and alignment
        - Used in conjunction with InnerCurrentLead to complete electrical circuit
    """

    yaml_tag = "OuterCurrentLead"

    def __init__(
        self,
        name: str,
        r: list[float] = None,
        h: float = 0.0,
        bar: list = None,
        support: list = None,
    ) -> None:
        """
        Initialize OuterCurrentLead with comprehensive validation.

        Args:
            name: Unique identifier for the current lead
            r: Radial bounds [R0, R1] in mm, must be ascending
            h: Height/length of current lead in mm (default: 0.0)
            bar: Optional conductor bar with 4 parameters: [R, DX, DY, L]
                 All must be positive if provided
            support: Optional support structure with 4 parameters: [DX0, DZ, Angle, Angle_Zero]

        Raises:
            ValidationError: If validation fails for:
                - Empty or invalid name
                - r not exactly 2 elements or not ascending
                - h negative
                - bar not exactly 4 elements or any value non-positive
                - support not exactly 4 elements or values out of valid ranges:
                  * DX0 <= 0
                  * DZ <= 0
                  * Angle not in (0, 360]
                  * Angle_Zero not in [0, 360)

        Example:
            >>> # Minimal configuration
            >>> lead = OuterCurrentLead("simple", [50.0, 60.0], h=100.0)
            >>>
            >>> # Full configuration with validation
            >>> try:
            ...     lead = OuterCurrentLead(
            ...         name="test_outer",
            ...         r=[52.0, 62.0],
            ...         h=110.0,
            ...         bar=[57.0, 12.0, 18.0, 90.0],
            ...         support=[7.0, 12.0, 40.0, 0.0]
            ...     )
            ... except ValidationError as e:
            ...     print(f"Configuration error: {e}")

        Notes:
            - All geometric parameters are in millimeters
            - Angles are in degrees
            - Empty lists for bar/support mean no feature
            - Bar geometry creates unique conductor shape with circular cut
            - Support provides mechanical stability and alignment
        """
        # General validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        GeometryValidator.validate_positive(h, "h")

        if bar is not None and bar:
            GeometryValidator.validate_numeric_list(bar, "bar", expected_length=4)
            for i, item in enumerate(bar):
                GeometryValidator.validate_positive(item, f"bar[{i}]")
        if support is not None and support:
            GeometryValidator.validate_numeric_list(support, "support", expected_length=4)
            GeometryValidator.validate_positive(support[0], "support[0]")
            GeometryValidator.validate_positive(support[1], "support[1]")
            if not (0 < support[2] <= 360):
                raise ValidationError("Angle must be in (0, 360]")
            if not (0 <= support[3] < 360):
                raise ValidationError("Angle_Zero must be in [0, 360)")

        self.name = name
        self.r = r if r is not None else []
        self.h = h
        self.bar = bar if bar is not None else []
        self.support = support if support is not None else []

    def __repr__(self):
        """
        Generate string representation of OuterCurrentLead.

        Returns:
            str: String showing all attributes with their values

        Example:
            >>> lead = OuterCurrentLead("test", [50.0, 60.0], h=100.0)
            >>> repr(lead)
            "OuterCurrentLead(name='test', r=[50.0, 60.0], h=100.0, bar=[], support=[])"
        """
        return f"{self.__class__.__name__}(name={self.name!r}, r={self.r!r}, h={self.h!r}, bar={self.bar!r}, support={self.support!r})"

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create OuterCurrentLead from dictionary representation.

        Args:
            values: Dictionary with keys matching constructor parameters:
                - name: Lead identifier (required)
                - r: Radial bounds (required)
                - h: Height (required)
                - bar: Conductor bar geometry (required)
                - support: Support structure (required)
            debug: Enable debug output during construction

        Returns:
            OuterCurrentLead: New instance constructed from dictionary

        Example:
            >>> data = {
            ...     'name': 'lead_from_dict',
            ...     'r': [52.0, 62.0],
            ...     'h': 105.0,
            ...     'bar': [57.0, 12.0, 18.0, 88.0],
            ...     'support': [7.5, 12.5, 35.0, 0.0]
            ... }
            >>> lead = OuterCurrentLead.from_dict(data)

        Notes:
            - All keys shown in example are expected in the dictionary
            - Uses standard constructor, so all validation applies
            - Part of the serialization/deserialization infrastructure
        """
        name = values["name"]
        r = values["r"]
        h = values["h"]
        bar = values["bar"]
        support = values["support"]
        return cls(name, r, h, bar, support)
