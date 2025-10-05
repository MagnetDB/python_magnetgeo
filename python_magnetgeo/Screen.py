#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for magnetic screening geometry.

This module defines the Screen class for representing magnetic shielding
or screening elements in magnet assemblies. Screens are typically cylindrical
shells used to shape or redirect magnetic fields.

Classes:
    Screen: Represents a magnetic screening element with cylindrical geometry
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError



class Screen(YAMLObjectBase):
    """
    Represents a magnetic screening element in axisymmetric geometry.
    
    A Screen is a cylindrical shell structure used for magnetic field shaping,
    shielding, or redirection. It is defined by its radial extent (inner and
    outer radius) and axial extent (bottom and top z-coordinates).
    
    Common uses:
    - Magnetic field shaping
    - Flux return paths
    - Magnetic shielding
    - Structural support with magnetic properties
    
    Attributes:
        name (str): Unique identifier for the screen
        r (list[float]): Radial bounds [r_inner, r_outer] in millimeters
        z (list[float]): Axial bounds [z_bottom, z_top] in millimeters
        
    Example:
        >>> # Create a simple screen
        >>> screen = Screen(
        ...     name="outer_screen",
        ...     r=[100.0, 120.0],
        ...     z=[0.0, 500.0]
        ... )
        >>> 
        >>> # Load from YAML
        >>> screen = Screen.from_yaml("screen.yaml")
        >>> 
        >>> # Check characteristic length scale
        >>> lc = screen.get_lc()
        >>> 
        >>> # Get bounding box
        >>> r_bounds, z_bounds = screen.boundingBox()
    """

    yaml_tag = "Screen"

    def __init__(self, name: str, r: list[float], z: list[float]):
        """
        Initialize a Screen object.
        
        Creates a cylindrical screening element with the specified geometry.
        
        Args:
            name: Unique identifier for the screen. Must follow standard naming
                  conventions (alphanumeric, underscores, hyphens).
            r: Radial bounds as [r_inner, r_outer] in millimeters.
               Must be a list of exactly 2 positive values with r_inner < r_outer.
            z: Axial bounds as [z_bottom, z_top] in millimeters.
               Must be a list of exactly 2 values with z_bottom < z_top.
               
        Example:
            >>> # Screen from r=50mm to r=60mm, z=0 to z=200mm
            >>> screen = Screen("shield_1", [50.0, 60.0], [0.0, 200.0])
            >>> 
            >>> # Screen with negative z-coordinates (symmetric about z=0)
            >>> screen2 = Screen("shield_2", [40.0, 45.0], [-100.0, 100.0])
        """
        self.name = name
        self.r = r
        self.z = z

    def get_lc(self):
        """
        Calculate characteristic length scale for mesh generation.
        
        Returns a length scale suitable for finite element mesh sizing,
        based on the radial thickness of the screen.
        
        Returns:
            float: Characteristic length in millimeters (radial thickness / 10)
            
        Example:
            >>> screen = Screen("test", [100.0, 120.0], [0.0, 500.0])
            >>> lc = screen.get_lc()  # Returns 2.0 mm
            
        Notes:
            This is used as a hint for automatic mesh generation algorithms
            to create appropriately sized elements for this geometry.
        """
        return (self.r[1] - self.r[0]) / 10.0

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list:
        """
        Get cooling channels for the screen.
        
        Currently returns an empty list as screens typically do not have
        internal cooling channels in the standard implementation.
        
        Args:
            mname: Parent magnet name for hierarchical naming
            hideIsolant: If True, hide insulation in the output (default: True)
            debug: Enable debug output (default: False)
            
        Returns:
            list: Empty list (screens have no cooling channels in current implementation)
            
        Example:
            >>> screen = Screen("shield", [100.0, 110.0], [0.0, 500.0])
            >>> channels = screen.get_channels("Insert1")
            >>> print(len(channels))  # 0
            
        Notes:
            This method exists for interface compatibility with other conductor
            classes (Helix, Bitter) that do have cooling channels. It may be
            extended in future versions if screen cooling becomes necessary.
        """
        return []

    def get_isolants(self, mname: str, debug: bool = False):
        """
        Get electrical isolation elements for the screen.
        
        Currently returns an empty list as screens are typically single
        conducting elements without internal insulation layers.
        
        Args:
            mname: Parent magnet name for hierarchical naming
            debug: Enable debug output (default: False)
            
        Returns:
            list: Empty list (screens have no isolants in current implementation)
            
        Example:
            >>> screen = Screen("shield", [100.0, 110.0], [0.0, 500.0])
            >>> isolants = screen.get_isolants("Insert1")
            >>> print(len(isolants))  # 0
            
        Notes:
            This method exists for interface compatibility with other conductor
            classes that may have insulation. Screens are typically modeled as
            single homogeneous conducting shells.
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Get list of geometry part names for CAD/mesh markers.
        
        Returns a list of names used to identify this screen's geometry
        in CAD models, meshes, or visualization. Typically used for
        setting material properties or boundary conditions.
        
        Args:
            mname: Parent magnet name to prepend to part names.
                   If empty, no prefix is added.
            is2D: If True, generate names for 2D (axisymmetric) geometry.
                  If False, generate names for 3D geometry (default: False).
                  Currently this parameter is not used.
            verbose: If True, print debug information about generated names
                    (default: False)
                    
        Returns:
            list[str]: List containing the single screen part name
            
        Example:
            >>> screen = Screen("outer_shield", [100.0, 110.0], [0.0, 500.0])
            >>> 
            >>> # With parent magnet name
            >>> names = screen.get_names("M1")
            >>> print(names)  # ['M1_outer_shield_Screen']
            >>> 
            >>> # Without parent magnet name
            >>> names = screen.get_names("")
            >>> print(names)  # ['outer_shield_Screen']
            >>> 
            >>> # With verbose output
            >>> names = screen.get_names("M1", verbose=True)
            # Prints: Bitter/get_names: solid_names 1
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        solid_names.append(f"{prefix}{self.name}_Screen")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]
        return cls(name, r, z)        

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """
        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        return r_overlap and z_overlap

