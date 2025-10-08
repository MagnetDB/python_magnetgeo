#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Supra:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""
from typing import Optional, Union



from .SupraStructure import HTSInsert
from .enums import DetailLevel

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator

import os


class Supra(YAMLObjectBase):
    """
    Supra - Superconducting magnet component.
    
    Represents a single superconducting magnet element with geometric bounds
    and optional detailed structural definition. Can reference external HTS
    (High-Temperature Superconductor) structure definitions for detailed modeling.
    
    Attributes:
        name (str): Unique identifier for the Supra component
        r (list[float]): Radial bounds [r_inner, r_outer] in mm
        z (list[float]): Axial bounds [z_bottom, z_top] in mm
        n (int): Number of turns or sections (default 0 if using struct)
        struct (str): Path to external structure definition file (optional)
        detail (DetailLevel): Level of detail for modeling
    
    yaml_tag: "Supra"
    
    Notes:
        - If struct is provided, geometric dimensions can be overridden from structure file
        - detail level controls mesh refinement and physics modeling granularity
        - All serialization functionality inherited from YAMLObjectBase
    """

    yaml_tag = "Supra"

    def __init__(
        self, name: str, r: list[float], z: list[float], n: int = 0, struct:str = None, detail: DetailLevel = DetailLevel.NONE
    ) -> None:
        """
        Initialize Supra object with validation.
        
        Args:
            name: Unique identifier for the Supra component
            r: Radial bounds [r_inner, r_outer] in mm, must be ascending
            z: Axial bounds [z_bottom, z_top] in mm, must be ascending
            n: Number of turns or sections (default 0, can be set from struct)
            struct: Path to external HTS structure definition file (optional)
            detail: Level of detail for modeling (default DetailLevel.NONE)
        
        Raises:
            ValidationError: If validation fails for:
                - Empty or invalid name
                - r list not exactly 2 elements
                - z list not exactly 2 elements
                - r values not in ascending order
                - z values not in ascending order
        
        Notes:
            - detail attribute is initialized to "None" by default
            - If struct is provided, use check_dimensions() to sync geometry
        """
        # General validation
        GeometryValidator.validate_name(name)
        
        GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        
        GeometryValidator.validate_numeric_list(z, "z", expected_length=2) 
        GeometryValidator.validate_ascending_order(z, "z")
       
        self.name = name
        self.r = r
        self.z = z
        self.n = n

        self.struct = struct
        self.detail = detail
        
        # Store the directory context for resolving struct paths
        self._basedir = os.getcwd()


    def get_magnet_struct(self) -> HTSInsert:
        """
        Load HTS structure definition from configuration file.
       
        Args:
            directory: Optional directory path for structure files (default: None)
       
        Returns:
            HTSinsert: High-temperature superconductor insert structure object
       
        Notes:
            - Uses self.struct as the configuration file path
            - Returns HTSinsert object with detailed pancake/tape geometry
        """

        hts = HTSInsert.fromcfg(self.struct, directory=self._basedir)
        self.check_dimensions(hts)
        return hts

    def check_dimensions(self, magnet: HTSInsert):
        """
        Synchronize geometric dimensions with HTS structure definition.
        
        Updates r, z, and n attributes if they differ from the values defined
        in the provided HTSInsert structure. Prints notification if changes occur.
        
        Args:
            magnet: HTSInsert structure object to check against
        
        Notes:
            - Only updates if self.struct is non-empty
            - Compares and updates: r[0], r[1], z[0], z[1], and n
            - z bounds are computed from magnet center (Z0) ± height/2
            - n is computed from sum of tape counts across pancakes
        
        Example:
            >>> supra = Supra("test", [10, 20], [0, 50], struct="hts_config.json")
            >>> hts = supra.get_magnet_struct()
            >>> supra.check_dimensions(hts)
            Supra/check_dimensions: override dimensions for test from hts_config.json
        """
        # TODO: if struct load r,z and n from struct data
        if self.struct:
            changed = False
            if self.r[0] != magnet.getR0():
                changed = True
                self.r[0] = magnet.getR0()
            if self.r[1] != magnet.getR1():
                changed = True
                self.r[1] = magnet.getR1()
            if self.z[0] != magnet.getZ0() - magnet.getH() / 2.0:
                changed = True
                self.z[0] = magnet.getZ0() - magnet.getH() / 2.0
            if self.z[1] != magnet.getZ0() + magnet.getH() / 2.0:
                changed = True
                self.z[1] = magnet.getZ0() + magnet.getH() / 2.0
            if self.n != sum(magnet.getNtapes()):
                changed = True
                self.n = sum(magnet.getNtapes())

            if changed:
                print(
                    f"Supra/check_dimensions: override dimensions for {self.name} from {self.struct}"
                )
                print(self)

    def get_lc(self):
        """
        Calculate characteristic length for mesh generation.
        
        Returns:
            float: Characteristic length for mesh element sizing
        
        Algorithm:
            - If detail is "None": (r_outer - r_inner) / 5.0
            - Otherwise: delegates to HTSInsert.get_lc() for detailed mesh
        
        Notes:
            Used by mesh generators to determine appropriate element size.
            Finer detail levels produce smaller characteristic lengths.
        """
        if self.detail == DetailLevel.NONE:
            return (self.r[1] - self.r[0]) / 5.0
        else:
            hts = self.get_magnet_struct()
            return hts.get_lc()

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list:
        """
        Get cooling channel definitions.
        
        Args:
            mname: Magnet name prefix for channel identification
            hideIsolant: If True, exclude insulator channels from output
            debug: Enable debug output
        
        Returns:
            list: Empty list (placeholder - Supra doesn't define channels)
        
        Notes:
            Supra components typically don't have internal cooling channels.
            Override in subclasses if channel support is needed.
        """
        return []

    def get_isolants(self, mname: str, debug: bool = False):
        """
        Get electrical insulator/isolant definitions.
        
        Args:
            mname: Magnet name for isolant identification
            debug: Enable debug output
        
        Returns:
            list: Empty list (placeholder - isolants handled at detail level)
        
        Notes:
            Insulation is typically modeled in detailed structure (HTSInsert)
            rather than at the Supra component level.
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Generate marker names for mesh identification.
        
        Creates identifiers for different structural elements based on the
        level of detail requested.
        
        Args:
            mname: Name prefix to prepend (typically parent magnet name)
            is2D: True for 2D axisymmetric mesh, False for 3D mesh
            verbose: Enable verbose output showing name generation
        
        Returns:
            list[str]: List of marker names for mesh regions
        
        Algorithm:
            - detail="None": Returns single marker "{mname}_Supra"
            - detail="dblpancake": Generates markers for each double pancake
            - detail="pancake": Generates markers for individual pancakes  
            - detail="tape": Generates detailed tape-level markers
        
        Notes:
            - Marker names used by mesh generators for region identification
            - More detailed levels produce more marker names
            - Names include section indices when struct is loaded
        
        Example:
            >>> supra = Supra("M1", [10, 20], [0, 50], n=4)
            >>> supra.get_names("system", is2D=False)
            ['system_Supra']
            >>> supra.set_Detail("dblpancake")
            >>> supra.get_names("system", is2D=False)
            ['system_DblPancake0', 'system_DblPancake1', ...]
        """

        if self.detail == DetailLevel.NONE:
            prefix = ""
            if mname:
                prefix = f"{mname}_"
            return [f"{prefix}{self.name}"]
        else:
            hts = self.get_magnet_struct()
            self.check_dimensions(hts)
            return hts.get_names(mname=mname, detail=self.detail, verbose=verbose)

    def __repr__(self):
        """
        Generate string representation of Supra object.
        
        Returns:
            str: String showing class name and all key attributes
        
        Example:
            >>> supra = Supra("M1", [10.0, 20.0], [0.0, 50.0], n=5, struct="config")
            >>> repr(supra)
            "Supra(name='M1', r=[10.0, 20.0], z=[0.0, 50.0], n=5, struct='config')"
        """
        return "%s(name=%r, r=%r, z=%r, n=%d, struct=%r, detail=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
            self.n,
            self.struct,
            self.detail,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Supra instance from dictionary representation.
        
        Args:
            values: Dictionary containing Supra parameters with keys:
                - name: Component identifier (required)
                - r: Radial bounds [r_inner, r_outer] (required)
                - z: Axial bounds [z_bottom, z_top] (required)
                - n: Number of turns (optional, default 0)
                - struct: Structure file path (optional, default "")
            debug: Enable debug output during deserialization
        
        Returns:
            Supra: New Supra instance
        
        Example:
            >>> data = {
            ...     'name': 'M1',
            ...     'r': [10.0, 20.0],
            ...     'z': [0.0, 50.0],
            ...     'n': 5,
            ...     'struct': 'hts_config.yaml'
            ... }
            >>> supra = Supra.from_dict(data)
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]
        n = values.get("n", 0)

        struct = values.get("struct", None)
        
        # Handle detail field: convert string to enum
        detail_value = values.get("detail", "NONE")
        if isinstance(detail_value, str):
            detail = DetailLevel(detail_value.upper())
        else:
            detail = detail_valueobject = cls(name, r, z, n, struct)

        return cls(name, r, z, n, struct, detail)

    def get_Nturns(self) -> int:
        """
        Get the number of turns in the superconducting magnet.
        
        Returns:
            int: Number of turns (from n attribute or struct if loaded)
        
        Notes:
            - If struct is not set: returns self.n
            - If struct is set but not loaded: returns -1 (error indicator)
            - If struct is loaded: would return sum from HTSInsert (not implemented)
        
        Example:
            >>> supra = Supra("test", [10, 20], [0, 50], n=5)
            >>> supra.get_Nturns()
            5
        """
        if not self.struct:
            return self.n
        else:
            print("shall get nturns from %s" % self.struct)
            return -1

    def set_Detail(self, detail: Union[str, DetailLevel ]) -> None:
        """
        Set the level of detail for structural modeling.
        
        Args:
            detail: Detail level, can be either:
                - DetailLevel enum value (DetailLevel.PANCAKE, etc.)
                - String that will be converted to enum ("PANCAKE", "pancake", etc.)
        
        Raises:
            ValueError: If detail value cannot be converted to valid DetailLevel
        
        Notes:
            - Accepts both enum values and strings for flexibility
            - String values are case-insensitive and mapped to enum
            - Higher detail levels increase mesh complexity and solve time
            - Requires struct to be set for detail levels other than NONE
        
        Example:
            >>> supra = Supra("test", [10, 20], [0, 50], struct="config.yaml")
            >>> supra.set_Detail(DetailLevel.PANCAKE)
            >>> supra.set_Detail("PANCAKE")  # Also works
            >>> supra.set_Detail("pancake")  # Case-insensitive
        """
        if isinstance(detail, DetailLevel):
            self.detail = detail
        elif isinstance(detail, str):
            # Map old string values to new enum
            detail_map = {
                "NONE": DetailLevel.NONE,
                "DBLPANCAKE": DetailLevel.DBLPANCAKE,
                "PANCAKE": DetailLevel.PANCAKE,
                "TAPE": DetailLevel.TAPE
            }
            
            if detail.upper() in detail_map:
                self.detail = detail_map[detail.upper()]
            else:
                raise ValueError(
                    f"Supra/set_Detail: unexpected detail value (detail={detail}). "
                    f"Valid values are: {list(detail_map.keys())} or DetailLevel enum members"
                )
        else:
            raise TypeError(
                f"Supra/set_Detail: detail must be DetailLevel enum or string, got {type(detail)}"
            )

    def boundingBox(self) -> tuple:
        """
        Get the axis-aligned bounding box of the Supra geometry.
        
        Returns:
            tuple: (r_bounds, z_bounds) where:
                - r_bounds: [r_inner, r_outer] radial extent in mm
                - z_bounds: [z_bottom, z_top] axial extent in mm
        
        Notes:
            - Currently returns the basic r, z attributes
            - TODO: Account for mandrin (support structure) and insulation
                    even when detail="None"
        
        Example:
            >>> supra = Supra("test", [15.0, 25.0], [10.0, 80.0])
            >>> rb, zb = supra.boundingBox()
            >>> print(f"Radial: {rb}, Axial: {zb}")
            Radial: [15.0, 25.0], Axial: [10.0, 80.0]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if Supra intersects with a given rectangular region.
        
        Tests whether this Supra's bounding box overlaps with the specified
        axis-aligned rectangular region in cylindrical coordinates.
        
        Args:
            r: Radial bounds [r_min, r_max] of test region in mm
            z: Axial bounds [z_min, z_max] of test region in mm
        
        Returns:
            bool: True if bounding boxes overlap, False if separated
        
        Algorithm:
            Uses separating axis theorem for axis-aligned rectangles:
            - Check for overlap in radial direction
            - Check for overlap in axial direction
            - Both must overlap for intersection to occur
        
        Notes:
            - Conservative test using bounding box
            - Does not account for detailed internal structure
            - Suitable for collision detection and placement validation
        
        Example:
            >>> supra = Supra("test", [10.0, 20.0], [0.0, 50.0])
            >>> # Test overlapping region
            >>> supra.intersect([15.0, 25.0], [25.0, 75.0])
            True
            >>> # Test non-overlapping region
            >>> supra.intersect([30.0, 40.0], [0.0, 10.0])
            False
        """

        (r_i, z_i) = self.boundingBox()

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])

        return r_overlap and z_overlap


    # def getFillingFactor(self) -> float:
    #     # self.detail = "None"  # ['None', 'dblpancake', 'pancake', 'tape']
    #     if self.detail == "None":
    #         return 1/self.get_Nturns()
    #     # else:
    #     #     # load HTSInsert
    #     #     # return fillingfactor according to self.detail:
    #     #     # aka tape.getFillingFactor() with tape = HTSinsert.tape when detail == "tape"

