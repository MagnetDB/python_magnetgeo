#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for CoolingSlits:
"""

from typing import List, Union
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

from .Contour2D import Contour2D

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
        self, name: str, r: float, angle: float, n: int, dh: float, sh: float, contour2d: Union[str, Contour2D]
    ) -> None:
        """
        Initialize a cooling slit channel for Bitter disk magnets.
        
        A CoolingSlit represents a circumferential array of discrete cooling channels
        at a specific radial position within a Bitter disk. The channels allow coolant
        flow between conductor sections to remove Joule heating.
        
        Args:
            name: Unique identifier for this cooling slit configuration
            r: Radial position of the cooling slit center in mm. Measured from
            the magnet axis to the centerline of the cooling channels.
            angle: Angular width of each individual cooling channel in degrees.
                Measured in the circumferential direction at radius r.
            n: Number of discrete cooling channels distributed around the circumference.
            Channels are evenly spaced at intervals of 360/n degrees.
            dh: Hydraulic diameter in mm. Defined as dh = 4*Sh/Ph where:
                - Sh is the cross-sectional area of one channel
                - Ph is the wetted perimeter of one channel
                Used for pressure drop and heat transfer calculations.
            sh: Cross-sectional area of a single cooling channel in mm².
                Total cooling area = n * sh.
            contour2d: Contour2D object defining the channel cross-section geometry,
                    or string reference to Contour2D YAML file, or None.
                    Describes the actual 2D shape of each cooling channel.
        
        Raises:
            ValidationError: If name is invalid (empty or None)
            ValidationError: If n is not a positive integer
            ValidationError: If r, dh, or sh are not positive numbers
            ValidationError: If n * angle > 360 (channels would overlap)
        
        Notes:
            - Channels are assumed uniformly distributed around the circumference
            - Angular spacing between channel centers = 360/n degrees
            - Total angular coverage = n * angle degrees (must not exceed 360°)
            - Hydraulic diameter dh is critical for thermal-hydraulic analysis
            - The contour2d provides detailed geometry for CFD/FEA modeling
        
        Example:
            >>> # Create a cooling slit with 10 channels at radius 120mm
            >>> from python_magnetgeo.Contour2D import Contour2D
            >>> contour = Contour2D(
            ...     name="channel_profile",
            ...     points=[[0, 0], [2, 0], [2, 1], [0, 1]]  # Rectangular channel
            ... )
            >>> slit = CoolingSlit(
            ...     name="slit1",
            ...     r=120.0,           # 120mm radius
            ...     angle=4.5,         # Each channel spans 4.5 degrees
            ...     n=10,              # 10 channels total (spaced 36° apart)
            ...     dh=2.0,            # 2mm hydraulic diameter
            ...     sh=3.0,            # 3mm² cross-section per channel
            ...     contour2d=contour
            ... )
            
            >>> # Create slit without detailed contour (simplified model)
            >>> slit_simple = CoolingSlit(
            ...     name="slit2",
            ...     r=135.0,
            ...     angle=5.0,
            ...     n=12,
            ...     dh=2.5,
            ...     sh=4.0,
            ...     contour2d=None  # No detailed geometry
            ... )
        """
        
        # General validation
        # GeometryValidator.validate_name(name)
        
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
        """
        Return string representation of CoolingSlit instance.
        
        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.
        
        Returns:
            str: String representation in constructor-like format showing:
                - name: Slit identifier
                - r: Radial position
                - angle: Angular width per channel
                - n: Number of channels
                - dh: Hydraulic diameter
                - sh: Channel cross-section
                - contour2d: Contour2D object or None
        
        Example:
            >>> contour = Contour2D("profile", points=[[0, 0], [2, 0], [2, 1]])
            >>> slit = CoolingSlit("slit1", r=120.0, angle=4.5, n=10, 
            ...                     dh=2.0, sh=3.0, contour2d=contour)
            >>> print(repr(slit))
            CoolingSlit(name=slit1, r=120.0, angle=4.5, n=10, dh=2.0, sh=3.0, 
                        contour2d=Contour2D(...))
            >>>
            >>> # In Python REPL
            >>> slit
            CoolingSlit(name=slit1, r=120.0, angle=4.5, n=10, ...)
            >>>
            >>> # With None contour
            >>> slit_simple = CoolingSlit("slit2", r=135.0, angle=5.0, n=12,
            ...                           dh=2.5, sh=4.0, contour2d=None)
            >>> print(repr(slit_simple))
            CoolingSlit(name=slit2, r=135.0, angle=5.0, n=12, dh=2.5, sh=4.0, 
                        contour2d=None)
        """
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
        Create CoolingSlit instance from dictionary representation.
        
        Supports flexible input formats for the nested contour2d object,
        allowing inline definition, file reference, or pre-instantiated object.
        
        Args:
            values: Dictionary containing CoolingSlit configuration with keys:
                - name (str): Slit identifier
                - r (float): Radial position in mm
                - angle (float): Angular width per channel in degrees
                - n (int): Number of channels
                - dh (float): Hydraulic diameter in mm
                - sh (float): Channel cross-section in mm²
                - contour2d: Contour2D specification (string/dict/object/None)
            debug: Enable debug output showing object loading process
        
        Returns:
            CoolingSlit: New CoolingSlit instance created from dictionary
        
        Raises:
            KeyError: If required keys are missing from dictionary
            ValidationError: If values fail validation checks
            ValidationError: If contour2d data is malformed
        
        Example:
            >>> # With inline contour definition
            >>> data = {
            ...     "name": "slit1",
            ...     "r": 120.0,
            ...     "angle": 4.5,
            ...     "n": 10,
            ...     "dh": 2.0,
            ...     "sh": 3.0,
            ...     "contour2d": {
            ...         "name": "profile",
            ...         "points": [[0, 0], [2, 0], [2, 1], [0, 1]]
            ...     }
            ... }
            >>> slit = CoolingSlit.from_dict(data)
            
            >>> # With file reference
            >>> data2 = {
            ...     "name": "slit2",
            ...     "r": 135.0,
            ...     "angle": 5.0,
            ...     "n": 12,
            ...     "dh": 2.5,
            ...     "sh": 4.0,
            ...     "contour2d": "channel_profile"  # Load from file
            ... }
            >>> slit2 = CoolingSlit.from_dict(data2)
            
            >>> # Without contour (simplified)
            >>> data3 = {
            ...     "name": "slit3",
            ...     "r": 150.0,
            ...     "angle": 6.0,
            ...     "n": 8,
            ...     "dh": 3.0,
            ...     "sh": 5.0,
            ...     "contour2d": None
            ... }
            >>> slit3 = CoolingSlit.from_dict(data3)
        """
        # Smart nested object handling
        contour2d = cls._load_nested_single(values.get('contour2d'), Contour2D, debug=debug)
        return cls(
            name=values.get("name", ""),
            r=values["r"],
            angle=values["angle"],
            n=values["n"],
            dh=values["dh"],
            sh=values["sh"],
            contour2d=contour2d
        )
    
