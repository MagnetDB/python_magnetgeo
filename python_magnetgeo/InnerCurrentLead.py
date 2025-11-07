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
    Inner current lead geometry for magnet electrical connections.
    
    Represents the current lead structure on the inner bore of a magnet assembly,
    including mounting holes, support structure, and optional edge filleting.
    
    Attributes:
        name (str): Unique identifier for the current lead
        r (list[float]): Radial bounds [R0, R1] in mm, where R0 < R1
        h (float): Height/length of the current lead in mm (default: 0.0)
        holes (list): Hole pattern definition with 6 parameters (optional):
            [0] H_Holes: Hole height in mm (must be positive)
            [1] Shift_from_Top: Distance from top edge in mm (non-negative)
            [2] Angle_Zero: Starting angle in degrees [0, 360)
            [3] Angle: Angular span per hole in degrees (0, 360]
            [4] Angular_Position: Angular position offset in degrees [0, 360)
            [5] N_Holes: Number of holes (positive integer)

        support (list): Support structure with 2 parameters (optional):
            [0] R2: Support radius in mm (positive)
            [1] DZ: Vertical offset in mm (can be negative)

        fillet (bool): Apply edge filleting for smooth transitions (default: False)
    
    Validation Rules:
        - name must be non-empty string
        - r must have exactly 2 elements in ascending order
        - h must be non-negative
        - holes, if provided, must have exactly 6 elements with specific constraints
        - support, if provided, must have exactly 2 elements
    
    Example:
        >>> # Basic inner lead without holes
        >>> lead = InnerCurrentLead(
        ...     name="inner_lead_1",
        ...     r=[10.0, 20.0],
        ...     h=50.0
        ... )
        >>> 
        >>> # Complete inner lead with holes and support
        >>> lead_full = InnerCurrentLead(
        ...     name="inner_lead_complete",
        ...     r=[12.0, 24.0],
        ...     h=65.0,
        ...     holes=[6.5, 11.0, 0.0, 50.0, 0.0, 9],  # 9 holes pattern
        ...     support=[28.0, 6.5],                    # Support structure
        ...     fillet=True                              # With edge filleting
        ... )
    
    Notes:
        - Inner leads typically connect to helical coils on the inside bore
        - Hole patterns allow for cooling or mounting features
        - Support structure provides mechanical stability
        - Fillet option smooths edges for CAD model generation
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
        Initialize InnerCurrentLead with comprehensive validation.
        
        Args:
            name: Unique identifier for the current lead
            r: Radial bounds [R0, R1] in mm, must be ascending
            h: Height/length of current lead in mm (default: 0.0)
            holes: Optional hole pattern with 6 parameters:
                   [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]

            support: Optional support structure with 2 parameters: [R2, DZ]
            fillet: Apply edge filleting (default: False)
        
        Raises:
            ValidationError: If validation fails for:
                - Empty or invalid name
                - r not exactly 2 elements or not ascending
                - h negative
                - holes not exactly 6 elements or values out of range:
                  * H_Holes <= 0
                  * Shift_from_Top < 0
                  * Angle_Zero not in [0, 360)
                  * Angle not in (0, 360]
                  * Angular_Position not in [0, 360)
                  * N_Holes <= 0 or not an integer
                  
                - support not exactly 2 elements or R2 negative
        
        Example:
            >>> # Minimal configuration
            >>> lead = InnerCurrentLead("simple", [10.0, 20.0])
            >>> 
            >>> # Full configuration with validation
            >>> try:
            ...     lead = InnerCurrentLead(
            ...         name="test",
            ...         r=[15.0, 25.0],
            ...         h=60.0,
            ...         holes=[5.0, 10.0, 0.0, 45.0, 0.0, 8],
            ...         support=[30.0, 5.0],
            ...         fillet=True
            ...     )
            ... except ValidationError as e:
            ...     print(f"Configuration error: {e}")
        
        Notes:
            - All geometric parameters are in millimeters
            - Angles are in degrees
            - Empty lists for holes/support mean no feature
            - Validation is comprehensive and provides clear error messages
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
        Generate string representation of InnerCurrentLead.
        
        Returns:
            str: String showing all attributes with their values
        
        Example:
            >>> lead = InnerCurrentLead("test", [10.0, 20.0], h=50.0)
            >>> repr(lead)
            "InnerCurrentLead(name='test', r=[10.0, 20.0], h=50.0, holes=[], support=[], fillet=False)"
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
        Create InnerCurrentLead from dictionary representation.
        
        Args:
            values: Dictionary with keys matching constructor parameters:
                - name: Lead identifier (required)
                - r: Radial bounds (required)
                - h: Height (required)
                - holes: Hole pattern (required)
                - support: Support structure (required)
                - fillet: Edge filleting flag (required)
            debug: Enable debug output during construction
        
        Returns:
            InnerCurrentLead: New instance constructed from dictionary
        
        Example:
            >>> data = {
            ...     'name': 'lead_from_dict',
            ...     'r': [12.0, 22.0],
            ...     'h': 55.0,
            ...     'holes': [5.5, 10.0, 0.0, 60.0, 0.0, 6],
            ...     'support': [26.0, 5.0],
            ...     'fillet': True
            ... }
            >>> lead = InnerCurrentLead.from_dict(data)
        
        Notes:
            - All keys shown in example are expected in the dictionary
            - Uses standard constructor, so all validation applies
            - Part of the serialization/deserialization infrastructure
        """
        name = values["name"]
        r = values["r"]
        h = values["h"]
        holes = values["holes"]
        support = values["support"]
        fillet = values["fillet"]
        return cls(name, r, h, holes, support, fillet)        

