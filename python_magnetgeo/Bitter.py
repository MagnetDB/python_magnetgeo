#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Bitter:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""


from .ModelAxi import ModelAxi
from .tierod import Tierod
from .coolingslit import CoolingSlit

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Bitter(YAMLObjectBase):
    """
    name :
    r :
    z :

    axi :
    coolingslits: [(r, angle, n, dh, sh, contour2d)]
    tierods: [r, n, contour2d]
    """

    yaml_tag = "Bitter"

    def __init__(
        self,
        name,
        r: list[float],
        z: list[float],
        odd: bool,
        modelaxi: ModelAxi,
        coolingslits: List[CoolingSlit] = None,
        tierod: Tierod = None,
        innerbore: float = 0,
        outerbore: float = 0,
    ) -> None:
        """
        Initialize a Bitter disk magnet with cooling channels.
        
        A Bitter magnet is a stack of resistive disk-shaped plates with a helical cut
        pattern that represent the insulators distribution. Multiple cooling
        slits can be integrated at different radii for enhanced cooling performance.
        
        Args:
            name: Unique identifier for the Bitter
            r: [r_inner, r_outer] - radial extent in mm. Inner and outer radii
            of the conductor disk.
            z: [z_bottom, z_top] - axial extent in mm. Bottom and top positions
            of the disk along the z-axis.
            odd: Boolean indicating helix handedness. True for left-handed helix,
                False for right-handed helix. Determines the direction of the
                helical cut spiral.
            modelaxi: ModelAxi object or string reference to ModelAxi YAML file.
                    Defines the helical cut pattern (turns, pitch).
                    Can be None for simple disk without helical pattern.
            coolingslits: Optional list of CoolingSlit objects or string references.
                        Defines radial positions and properties of cooling channels
                        within the disk. Default: None (converted to empty list).
            tierod: Optional Tierod object or string reference. Defines tie rod
                holes for mechanical reinforcement. Default: None.
            innerbore: Inner bore radius in mm (experimental volume). Default: 0
            outerbore: Outer bore radius in mm (outer magnet boundary). Default: 0
        
        Raises:
            ValidationError: If name is invalid
            ValidationError: If r is not length 2 or not in ascending order
            ValidationError: If z is not length 2 or not in ascending order  
            ValidationError: If r[0] < 0 (negative inner radius)
        
        Notes:
            - Bitter magnets are typically stacked axially to create high fields
            - The helical cut is used to mimic insulators distribution in between Bitter disks
            - Multiple cooling slits improve heat removal at different radii
            - ModelAxi defines the geometry of the helical cut pattern
            - String references to nested objects are automatically loaded from YAML files
        
        Example:
            >>> # Simple Bitter disk without cooling slits
            >>> modelaxi = ModelAxi("helix", h=48, turns=[5, 7], pitch=[8, 8])
            >>> bitter = Bitter(
            ...     name="B1",
            ...     r=[100, 150],
            ...     z=[0, 50],
            ...     odd=True,
            ...     modelaxi=modelaxi,
            ...     coolingslits=[],
            ...     tierod=None,
            ...     innerbore=80,
            ...     outerbore=160
            ... )
            
            >>> # Bitter disk with cooling slits
            >>> slit1 = CoolingSlit(name="s1", r=120, angle=4.5, n=10, ...)
            >>> slit2 = CoolingSlit(name="s2", r=135, angle=4.5, n=12, ...)
            >>> bitter = Bitter(
            ...     name="B2",
            ...     r=[100, 150],
            ...     z=[60, 110],
            ...     odd=False,
            ...     modelaxi="helix",  # Load from file
            ...     coolingslits=[slit1, slit2],
            ...     tierod=None
            ... )
        """
        
        # Validate inputs
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        
        GeometryValidator.validate_numeric_list(z, 'z', expected_length=2)
        GeometryValidator.validate_ascending_order(z, "z")
        
        # Additional Ring-specific checks
        if r[0] < 0:
            raise ValidationError("Inner radius cannot be negative") 
        
        self.name = name
        self.r = r
        self.z = z
        self.odd = odd
        if modelaxi is not None and isinstance(modelaxi, str):
            self.modelaxi = ModelAxi.from_yaml(f"{modelaxi}.yaml")
        else:
            self.modelaxi = modelaxi
        
        self.innerbore = innerbore
        self.outerbore = outerbore

        self.coolingslits = []
        if coolingslits is not None:
            for coolingslit in coolingslits:
                if isinstance(coolingslit, str):
                    self.coolingslits.append(CoolingSlit.from_yaml(f"{coolingslit}.yaml"))
                else:
                    self.coolingslits.append(coolingslit)
                
        if tierod is not None and  isinstance(tierod, str):
            self.tireod = Tierod.from_yaml(f"{tierod}.yaml")
        else:
            self.tierod = tierod

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, r=%r, z=%r, odd=%r, axi=%r, coolingslits=%r, tierod=%r, innerbore=%r, outerbore=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.odd,
                self.modelaxi,
                self.coolingslits,
                self.tierod,
                self.innerbore,
                self.outerbore,
            )
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Bitter instance from dictionary representation.
        
        Supports flexible input formats for nested objects (modelaxi, cooling slits,
        tierod), allowing mixed specifications of inline definitions and file references.
        
        Args:
            values: Dictionary containing Bitter configuration with keys:
                - name (str): Bitter disk name
                - r (list[float]): Radial extent [inner, outer]
                - z (list[float]): Axial extent [bottom, top]
                - odd (bool): Helix handedness
                - modelaxi: ModelAxi specification (string/dict/object/None)
                - coolingslits (list, optional): List of CoolingSlit specs (default: [])
                - tierod (optional): Tierod specification (string/dict/object/None)
                - innerbore (float, optional): Inner bore radius (default: 0)
                - outerbore (float, optional): Outer bore radius (default: 0)
            debug: Enable debug output showing object loading process
        
        Returns:
            Bitter: New Bitter instance created from dictionary
        
        Raises:
            KeyError: If required keys are missing from dictionary
            ValidationError: If any nested object data is malformed
        
        Example:
            >>> data = {
            ...     "name": "B1",
            ...     "r": [100, 150],
            ...     "z": [0, 50],
            ...     "odd": True,
            ...     "modelaxi": "helix",  # Load from file
            ...     "coolingslits": [
            ...         {"name": "s1", "r": 120, "angle": 4.5, "n": 10, ...}  # Inline
            ...     ],
            ...     "tierod": None,
            ...     "innerbore": 80,
            ...     "outerbore": 160
            ... }
            >>> bitter = Bitter.from_dict(data)
        """
        modelaxi = cls._load_nested_modelaxi(values.get('modelaxi'), debug=debug)
        coolingslits = cls._load_nested_coolingslits(values.get('coolingslits'), debug=debug)
        tierod = cls._load_nested_tierod(values.get('tierod'), debug=debug)

        name = values["name"]
        r = values["r"]
        z = values["z"]
        odd = values["odd"]
        # modelaxi = values["modelaxi"]
        # coolingslits = values.get("coolingslits", [])
        # tierod = values.get("tierod", None)
        innerbore = values.get("innerbore", 0)
        outerbore = values.get("outerbore", 0)

        object = cls(name, r, z, odd, modelaxi, coolingslits, tierod, innerbore, outerbore)
        return object

    @classmethod  
    def _load_nested_modelaxi(cls, modelaxi_data, debug=False):
        """
        Load ModelAxi object from various input formats.
        
        Internal method handling flexible loading of the helical cut pattern definition.
        
        Args:
            modelaxi_data: ModelAxi specification in any format:
                - String: loads from "{string}.yaml" file
                - Dict: creates ModelAxi inline from dictionary
                - ModelAxi object: uses as-is
                - None: returns None (no helical pattern)
            debug: Enable debug output showing loading process
        
        Returns:
            ModelAxi or None: ModelAxi object defining helical pattern, or None
        
        Notes:
            - Uses utils.loadObject for file-based loading
            - Delegates to ModelAxi.from_dict for dictionary parsing
        
        Example:
            >>> # Load from file
            >>> modelaxi = Bitter._load_nested_modelaxi("helix")
            >>> 
            >>> # Create from dict
            >>> modelaxi = Bitter._load_nested_modelaxi({
            ...     "name": "helix", "h": 48, "turns": [5, 7], "pitch": [8, 8]
            ... })
        """
        if isinstance(modelaxi_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("modelaxi", modelaxi_data, ModelAxi, ModelAxi.from_yaml)
        elif isinstance(modelaxi_data, dict):
            # Inline object → create from dict
            return ModelAxi.from_dict(modelaxi_data)
        else:
            # None or already instantiated
            return modelaxi_data

    @classmethod  
    def _load_nested_coolingslits(cls, coolingslits_data, debug=False):
        """
        Load list of CoolingSlit objects from various input formats.
        
        Internal method handling flexible loading of cooling channel definitions.
        
        Args:
            coolingslits_data: List of CoolingSlit specifications:
                - String: loads from "{string}.yaml" file
                - Dict: creates CoolingSlit inline from dictionary
                - CoolingSlit object: uses as-is
                - None/empty list: returns empty list
            debug: Enable debug output showing loading process for each slit
        
        Returns:
            list[CoolingSlit]: List of CoolingSlit objects (empty if data is None/empty)
        
        Notes:
            - Each cooling slit defines a radial position with specific geometry
            - Slits are typically ordered from inner to outer radius
            - Uses utils.loadObject for file-based loading
            - Delegates to CoolingSlit.from_dict for dictionary parsing
        
        Example:
            >>> slits_data = [
            ...     "slit1",  # Load from file
            ...     {"name": "slit2", "r": 135, "angle": 4.5, ...}  # Inline
            ... ]
            >>> slits = Bitter._load_nested_coolingslits(slits_data)
        """
        if coolingslits_data is None:
            return []
        
        if not isinstance(coolingslits_data, list):
            raise TypeError(f"coolingslits must be a list, got {type(coolingslits_data)}")
        
        objects = []
        references = []
        for i, slit_data in enumerate(coolingslits_data):
            if isinstance(slit_data, str):
                # String reference → load from "slit_data.yaml" and track reference
                if debug:
                    print(f"Loading CoolingSlit[{i}] from file: {slit_data}")
                from .utils import loadObject
                obj = loadObject("coolingslit", slit_data, CoolingSlit, CoolingSlit.from_yaml)
                objects.append(obj)
            elif isinstance(slit_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating CoolingSlit[{i}] from inline dict: {slit_data.get('name', 'unnamed')}")
                obj = CoolingSlit.from_dict(slit_data)
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(slit_data)
                references.append(None)  # No string reference
        
        return objects

    @classmethod  
    def _load_nested_tierod(cls, tierod_data, debug=False):
        """
        Load Tierod object from various input formats.
        
        Internal method handling flexible loading of tie rod hole definition.
        
        Args:
            tierod_data: Tierod specification in any format:
                - String: loads from "{string}.yaml" file
                - Dict: creates Tierod inline from dictionary
                - Tierod object: uses as-is
                - None: returns None (no tie rods)
            debug: Enable debug output showing loading process
        
        Returns:
            Tierod or None: Tierod object defining mechanical reinforcement holes, or None
        
        Notes:
            - Tie rods provide mechanical support for the Bitter stack
            - Defined by radial position, number of holes, and geometry
            - Uses utils.loadObject for file-based loading
            - Delegates to Tierod.from_dict for dictionary parsing
        
        Example:
            >>> # Load from file
            >>> tierod = Bitter._load_nested_tierod("tierod1")
            >>> 
            >>> # Create from dict
            >>> tierod = Bitter._load_nested_tierod({
            ...     "name": "tierod", "r": 95, "n": 6, ...
            ... })
        """
        if isinstance(tierod_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("modelaxi", tierod_data, Tierod, Tierod.from_yaml)
        elif isinstance(tierod_data, dict):
            # Inline object → create from dict
            return Tierod.from_dict(tierod_data)
        else:
            # None or already instantiated
            return tierod_data


    def equivalent_eps(self, i: int):
        """
        Calculate equivalent annular ring thickness for a cooling slit.
        
        Computes the thickness (eps) of an equivalent solid annular ring that
        has the same cross-sectional area as n discrete cooling slit channels
        at the given radial position.
        
        Args:
            i: Index of cooling slit in self.coolingslits list (0-based)
        
        Returns:
            float: Equivalent thickness in mm
        
        Notes:
            - Formula: eps = n * sh / (2 * π * r)
            - Where: n = number of slits, sh = slit height, r = radial position
            - Used for hydraulic diameter and heat transfer calculations
            - Converts discrete slit geometry to continuous approximation
        
        Example:
            >>> bitter = Bitter(..., coolingslits=[slit1, slit2], ...)
            >>> eps0 = bitter.equivalent_eps(0)  # Equivalent thickness for first slit
            >>> eps1 = bitter.equivalent_eps(1)  # Equivalent thickness for second slit
        """
        from math import pi

        slit = self.coolingslits[i]
        x = slit.r
        eps = slit.n * slit.sh / (2 * pi * x)
        return eps

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list[str]:
        """
        Retrieve cooling channel identifiers for the Bitter disk.
        
        Generates list of channel markers based on the number of cooling slits.
        Channels are numbered sequentially from 0 to n_slits+1, where n_slits
        is the number of CoolingSlit objects in the disk.
        
        Args:
            mname: Magnet name prefix for channel identifiers
            hideIsolant: Ignored for Bitter (included for API consistency).
                        Bitter disks do not have isolant layers.
            debug: Enable debug output (currently unused)
        
        Returns:
            list[str]: List of channel identifier strings:
                - ["{prefix}Slit0", "{prefix}Slit1", ..., "{prefix}Slit{n+1}"]
                - Where n is the number of cooling slits
        
        Notes:
            - Channel numbering: Slit0 is innermost, Slit{n+1} is outermost
            - Number of channels = number of slits + 2 (inner and outer regions)
            - Debug output shows number of cooling slits and channel list
            - Channels used for flow analysis and thermal modeling
        
        Example:
            >>> bitter = Bitter("B1", ..., coolingslits=[slit1, slit2], ...)
            >>> channels = bitter.get_channels("M10_B1")
            >>> print(channels)
            >>> # ['M10_B1_Slit0', 'M10_B1_Slit1', 'M10_B1_Slit2', 'M10_B1_Slit3']
            >>> # 4 channels for 2 slits (inner, between slits, outer)
        """
        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Channels = [f"{prefix}Slit{0}"]
        n_slits = 0
        if self.coolingslits:
            n_slits = len(self.coolingslits)
            print(f"Bitter({self.name}): CoolingSlits={n_slits}")

            Channels += [f"{prefix}Slit{i+1}" for i in range(n_slits)]
        Channels += [f"{prefix}Slit{n_slits+1}"]
        print(f"Bitter({prefix}): {Channels}")
        return Channels

    def get_lc(self) -> float:
        """
        Calculate characteristic mesh length for the Bitter disk.
        
        Computes an appropriate mesh element size based on disk geometry and
        cooling slit spacing. Used for automatic mesh size determination.
        
        Returns:
            float: Characteristic length in mm
        
        Notes:
            - Without cooling slits: lc = (r_outer - r_inner) / 10
            - With cooling slits: lc = min(dr) / 5, where dr is the minimum
            radial spacing between consecutive features (inner radius, slits,
            outer radius)
            - Ensures adequate mesh resolution near cooling channels
            - Smaller lc produces finer mesh with better accuracy but more elements
        
        Example:
            >>> # Simple disk without slits
            >>> bitter1 = Bitter("B1", r=[100, 150], ..., coolingslits=[], ...)
            >>> lc1 = bitter1.get_lc()  # Returns (150-100)/10 = 5.0 mm
            >>> 
            >>> # Disk with cooling slits
            >>> bitter2 = Bitter("B2", r=[100, 150], ..., 
            ...                  coolingslits=[slit_at_120, slit_at_135], ...)
            >>> lc2 = bitter2.get_lc()  # Returns min spacing / 5
        """
        lc = (self.r[1] - self.r[0]) / 10.0
        if self.coolingslits:
            x: float = self.r[0]
            dr: list[float] = []
            for slit in self.coolingslits:
                _x = slit.r
                dr.append(_x - x)
                x = _x
            dr.append(self.r[1] - x)
            # print(f"Bitter: dr={dr}")
            lc = min(dr) / 5.0

        return lc

    def get_isolants(self, mname: str, debug: bool = False) -> list[str]:
        """
        Retrieve electrical isolant identifiers for the Bitter disk.
        
        Args:
            mname: Magnet name prefix for isolant identifiers
            debug: Enable debug output
        
        Returns:
            list[str]: Empty list (Bitter disks currently have no isolant tracking)
        
        Notes:
            This is a placeholder method for API consistency.
            Future implementation may track kapton or other insulation layers.
        
        Example:
            >>> bitter = Bitter("B1", ...)
            >>> isolants = bitter.get_isolants("M10")
            >>> print(isolants)  # []
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Generate marker names for geometric entities in the Bitter disk.
        
        Creates list of identifiers for solid components used in mesh generation,
        visualization, and post-processing. Naming convention differs significantly
        between 2D (sector-based) and 3D (whole disk) representations.
        
        Args:
            mname: Magnet name prefix (e.g., "M10_B1")
            is2D: If True, generate detailed 2D sector names for each helical section.
                Each section is subdivided by cooling slits.
                If False, use simplified 3D naming for whole disk components.
            verbose: Enable verbose output showing total marker count
        
        Returns:
            list[str]: List of marker names:
                - 2D mode: Detailed sector names like "{prefix}B{j}_Slit{i}" for
                each helical turn section and cooling slit combination
                - 3D mode: Simple names ["{prefix}B", "{prefix}Kapton"]
        
        Notes:
            - 2D naming accounts for helical turn sections from modelaxi
            - Tolerance tol = 1e-10 used for floating-point comparisons
            - 2D includes extra sections if disk extends beyond helical pattern
            - Kapton represents insulation/isolation layer between disks
            - Verbose mode prints: "Bitter/get_names: solid_names {count}"
        
        Example:
            >>> bitter = Bitter("B1", r=[100, 150], z=[-50, 50], 
            ...                 modelaxi=ModelAxi(..., turns=[5, 7]), 
            ...                 coolingslits=[slit1, slit2], ...)
            >>> 
            >>> # 3D naming (simple)
            >>> names_3d = bitter.get_names("M10_B1", is2D=False)
            >>> print(names_3d)
            >>> # ['M10_B1_B', 'M10_B1_Kapton']
            >>> 
            >>> # 2D naming (detailed sectors)
            >>> names_2d = bitter.get_names("M10_B1", is2D=True)
            >>> # Returns many sector names like:
            >>> # ['M10_B1_B0_Slit0', 'M10_B1_B0_Slit1', 'M10_B1_B0_Slit2',
            >>> #  'M10_B1_B1_Slit0', 'M10_B1_B1_Slit1', ...]
        """
        tol = 1.0e-10
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Nslits = 0
        if self.coolingslits:
            Nslits = len(self.coolingslits)

        if is2D:
            nsection = len(self.modelaxi.turns)
            if self.z[0] < -self.modelaxi.h and abs(self.z[0] + self.modelaxi.h) >= tol:
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B0_Slit{i}")

            for j in range(nsection):
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B{j+1}_Slit{i}")

            if self.z[1] > self.modelaxi.h and abs(self.z[1] - self.modelaxi.h) >= tol:
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B{nsection+1}_Slit{i}")
        else:
            solid_names.append(f"{prefix}B")
            solid_names.append(f"{prefix}Kapton")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def get_Nturns(self) -> float:
        """
        Get the total number of helical turns in the Bitter disk.
        
        Delegates to the modelaxi object to compute total turns from
        the helical cut pattern definition.
        
        Returns:
            float: Total number of turns (sum of all turn sections)
        
        Notes:
            - Returns 0 if modelaxi is None
            - Typically returns sum of modelaxi.turns list
            - Used for electrical resistance and inductance calculations
        
        Example:
            >>> modelaxi = ModelAxi("helix", h=48, turns=[5, 7, 3], ...)
            >>> bitter = Bitter("B1", ..., modelaxi=modelaxi, ...)
            >>> n_turns = bitter.get_Nturns()
            >>> print(n_turns)  # 15.0 (5 + 7 + 3)
        """
        return self.modelaxi.get_Nturns()

    def boundingBox(self) -> tuple:
        """
        Calculate the bounding box of the Bitter disk.
        
        Returns the radial and axial extents of the disk geometry.
        
        Returns:
            tuple: (rb, zb) where:
                - rb: [r_inner, r_outer] - radial bounds in mm
                - zb: [z_bottom, z_top] - axial bounds in mm
        
        Notes:
            - Simply returns the r and z attributes (disk extents)
            - Does not include tierods or other auxiliary features
            - Used for collision detection and assembly validation
        
        Example:
            >>> bitter = Bitter("B1", r=[100, 150], z=[0, 50], ...)
            >>> rb, zb = bitter.boundingBox()
            >>> print(f"Radial: {rb}, Axial: {zb}")
            >>> # Radial: [100, 150], Axial: [0, 50]
        """

        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if Bitter disk intersects with a rectangular region.
        
        Tests whether the disk's bounding box overlaps with a given
        rectangular region defined by radial and axial bounds.
        
        Args:
            r: [r_min, r_max] - radial bounds of test rectangle in mm
            z: [z_min, z_max] - axial bounds of test rectangle in mm
        
        Returns:
            bool: True if rectangles overlap (intersection non-empty),
                False if no intersection
        
        Notes:
            - Uses axis-aligned bounding box (AABB) intersection algorithm
            - Rectangles intersect if they overlap in BOTH r and z dimensions
            - Efficient for collision detection in magnet stack assembly
        
        Example:
            >>> bitter = Bitter("B1", r=[100, 150], z=[0, 50], ...)
            >>> 
            >>> # Check overlap with another component
            >>> if bitter.intersect([140, 160], [30, 70]):
            ...     print("Collision detected!")
            >>> 
            >>> # Check clearance
            >>> other_rb, other_zb = other_magnet.boundingBox()
            >>> if bitter.intersect(other_rb, other_zb):
            ...     print("Magnets intersect - invalid assembly")
        """

        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        
        return r_overlap and z_overlap


    def get_params(self, workingDir: str = ".") -> tuple:
        """
        Extract physical and geometric parameters for thermal/hydraulic analysis.
        
        Computes hydraulic diameters (Dh), cross-sectional areas (Sh), axial
        positions (Zh), and filling factors for all cooling channels, accounting
        for the helical turn pattern and cooling slit configuration.
        
        Args:
            workingDir: Working directory path for file operations (currently unused)
        
        Returns:
            tuple: (nslits, Dh, Sh, Zh, filling_factor) where:
                - nslits (int): Number of cooling slits
                - Dh (list[float]): Hydraulic diameters for each channel [mm]
                - Sh (list[float]): Cross-sectional areas for each channel [mm²]
                - Zh (list[float]): Axial positions defining channel boundaries [mm]
                - filling_factor (list[float]): Geometric filling factors for each channel
        
        Notes:
            - Channel 0: Inner bore to first conductor (r_inner to innerbore)
            - Channels 1 to n: Cooling slits (using CoolingSlit properties)
            - Channel n+1: Last conductor to outer bore (r_outer to outerbore)
            - Zh positions account for helical turn boundaries from modelaxi
            - filling_factor relates wetted perimeter to circumference
            - Tolerance tol = 1e-10 used for floating-point comparisons
            - Debug output shows Zh positions and filling factors
        
        Example:
            >>> bitter = Bitter("B1", r=[100, 150], z=[-50, 50],
            ...                 modelaxi=ModelAxi(...),
            ...                 coolingslits=[slit1, slit2],
            ...                 innerbore=80, outerbore=160)
            >>> 
            >>> nslits, Dh, Sh, Zh, ff = bitter.get_params()
            >>> print(f"Number of slits: {nslits}")
            >>> print(f"Hydraulic diameters: {Dh}")  # [inner, slit1, slit2, outer]
            >>> print(f"Cross sections: {Sh}")
            >>> print(f"Axial positions: {Zh}")
            >>> print(f"Filling factors: {ff}")
        """
        from math import pi

        tol = 1.0e-10

        Dh = [2 * (self.r[0] - self.innerbore)]
        Sh = [pi * (self.r[0] - self.innerbore) * (self.r[0] + self.innerbore)]
        filling_factor = [1]
        nslits = 0
        if self.coolingslits:
            nslits = len(self.coolingslits)
            Dh += [slit.dh for slit in self.coolingslits]
            # Dh += [2 * self.equivalent_eps(n) for n in range(len(self.coolingslits))]
            Sh += [slit.n * slit.sh for slit in self.coolingslits]

            # wetted perimeter per slit: (4*slit.sh)/slit.dh
            # wetted perimeter for annular ring: 2*pi*(slit.r-eps) + 2*pi*(slit.r+eps)
            # with eps = self.equivalent_eps(n)
            filling_factor += [
                slit.n * ((4 * slit.sh) / slit.dh) / (4 * pi * slit.r)
                for slit in self.coolingslits
            ]
        Dh += [2 * (self.outerbore - self.r[1])]
        Sh += [pi * (self.outerbore - self.r[1]) * (self.outerbore + self.r[1])]

        Zh = [self.z[0]]
        z = -self.modelaxi.h
        if abs(self.z[0] - z) >= tol:
            Zh.append(z)
        for n, p in zip(self.modelaxi.turns, self.modelaxi.pitch):
            z += n * p
            Zh.append(z)
        if abs(self.z[1] - z) >= tol:
            Zh.append(self.z[1])
        print(f"Zh={Zh}")

        filling_factor.append(1)
        print(f"filling_factor={filling_factor}")

        # return (nslits, Dh, Sh, Zh)
        return (nslits, Dh, Sh, Zh, filling_factor)

    def create_cut(self, format: str):
        """
        Generate helical cut definition file for manufacturing or CAD.
        
        Creates a file describing the helical cut pattern in the specified format,
        used for CAM (Computer-Aided Manufacturing) or CAD import.
        
        Args:
            format: Output format specification. Supported formats:
                - "lncmi": Format for LNCMI CAM machines
                - "salome": Format for Salome CAD software import
        
        Raises:
            RuntimeError: If format is not supported
        
        Notes:
            - Delegates to hcuts.create_cut function for actual file generation
            - Output filename: "{self.name}_lncmi.iso" or "{self.name}_cut_salome.dat"
            - File contains theta (angle) and z (axial) coordinates for cut path
            - Helical path computed from modelaxi turns and pitch
            - Handedness determined by self.odd attribute
        
        Example:
            >>> bitter = Bitter("B1", ..., modelaxi=ModelAxi(...), odd=True, ...)
            >>> 
            >>> # Create CAM file for manufacturing
            >>> bitter.create_cut("lncmi")  # Creates B1_lncmi.iso
            >>> 
            >>> # Create Salome import file
            >>> bitter.create_cut("salome")  # Creates B1_cut_salome.dat
        """
        from .hcuts import create_cut

        create_cut(self, format, self.name)

