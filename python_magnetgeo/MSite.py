#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Site:

"""

from .Insert import Insert
from .Bitter import Bitter
from .Supra import Supra
from .Bitters import Bitters
from .Supras import Supras
from .Screen import Screen
from .utils import getObject

from typing import Union, Optional, List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class MSite(YAMLObjectBase):
    """
    name :
    magnets : dict holding magnet list ("insert", "Bitter", "Supra")
    screens :
    """

    yaml_tag = "MSite"

    def __init__(
        self,
        name: str,
        magnets: Union[str, list, dict],
        screens: Optional[Union[str, list, dict]],
        z_offset: Optional[list[float]],
        r_offset: Optional[list[float]],
        paralax: Optional[list[float]],
    ) -> None:
        """
        Initialize a measurement site (MSite) assembly.
        
        An MSite represents a complete measurement site containing multiple magnet
        assemblies (Insert, Bitter, Supra), optional screening elements, and spatial
        offsets for positioning. The class validates that magnets do not intersect.
        
        Args:
            name: Unique identifier for the measurement site
            magnets: Magnet assemblies in any of these formats:
                - List of magnet objects (Insert, Bitter, Supra)
                - List of string references to magnet YAML files
                - Single string reference to load one magnet
                - Dictionary representation of magnet(s)
            screens: Optional screening elements in any of these formats:
                - None (no screens)
                - List of Screen objects
                - List of string references to screen YAML files
                - Single string reference
                - Dictionary representation
            z_offset: Optional list of axial position offsets (mm) for each magnet.
                    Length should match number of magnets. None means no offsets.
            r_offset: Optional list of radial position offsets (mm) for each magnet.
                    Length should match number of magnets. None means no offsets.
            paralax: Optional list of parallax corrections for each magnet.
                    Length should match number of magnets. None means no corrections.
        
        Raises:
            ValidationError: If name is invalid
            ValidationError: If any two magnets intersect (overlap in space)
        
        Notes:
            - Magnets are loaded from YAML files if provided as strings
            - Intersection checking ensures physical validity of the assembly
            - Screens are optional and can be None or empty list
            - Offsets allow precise spatial positioning of individual magnets
        
        Example:
            >>> insert = Insert("HL-31", ...)
            >>> bitter = Bitter("B1", ...)
            >>> msite = MSite(
            ...     name="M9",
            ...     magnets=[insert, bitter],
            ...     screens=None,
            ...     z_offset=[0.0, 150.0],  # Bitter 150mm above insert
            ...     r_offset=[0.0, 0.0],
            ...     paralax=[0.0, 0.0]
            ... )
            
            >>> # Or load from files
            >>> msite = MSite(
            ...     name="M9",
            ...     magnets=["HL-31", "B1"],  # Load from YAML files
            ...     screens=["screen1"],
            ...     z_offset=[0.0, 150.0],
            ...     r_offset=None,
            ...     paralax=None
            ... )
        """
        # Validate inputs
        GeometryValidator.validate_name(name)
        
        self.name = name

        self.magnets = []
        for magnet in magnets:
            if isinstance(magnet, str):
                magnets.append(getObject(f"{magnet}.yaml"))
            else:
                self.magnets.append(magnet)

        # FIX: Keep None values as None instead of converting to empty lists
        self.screens = []
        if screens is not None:
            for screen in screens:
                if isinstance(screen, str):
                    self.screens.append(getObject(f"{screen}.yaml"))
                else:
                    self.screens.append(screen)

        self.z_offset = z_offset  
        self.r_offset = r_offset
        self.paralax = paralax

        # check that magnets are not intersecting
        for i in range(1, len(self.magnets)):
            rb, zb = self.magnets[i - 1].boundingBox()
            for j in range(i+1, len(self.magnets)):
                if self.magnets[i].intersect(rb, zb):
                    raise ValidationError(
                        f"magnets intersect: magnet[{i}] intersect magnet[{i-1}]: /n{self.magnets[i]} /n{self.magnets[i-1]}"
                    )   

    def __repr__(self):
        """
        representation of object
        """
        return f"name: {self.name}, magnets:{self.magnets}, screens: {self.screens}, z_offset={self.z_offset}, r_offset={self.r_offset}, paralax_offset={self.paralax}"

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        """
        Retrieve cooling channel definitions for all magnets in the site.
        
        Aggregates channel definitions from all constituent magnets into a
        hierarchical dictionary structure. Each magnet contributes its own
        channel definitions under its name as a key.
        
        Args:
            mname: Measurement site name prefix for channel identifiers
            hideIsolant: If True, exclude isolant and kapton layer markers from
                        channel definitions. Passed to each magnet's get_channels().
            debug: Enable debug output showing channel aggregation process.
                Also passed to each magnet's get_channels() method.
        
        Returns:
            dict: Hierarchical dictionary of channels:
                {
                    "{mname}_{magnet1.name}": magnet1.get_channels(...),
                    "{mname}_{magnet2.name}": magnet2.get_channels(...),
                    ...
                }
                Each value is the channel list returned by that magnet's get_channels().
        
        Notes:
            - Channels are organized by magnet name for clarity
            - Each magnet type (Insert, Bitter, Supra) has its own channel structure
            - Debug output prefixed with "MSite/get_channels:"
            - Screens do not contribute channels
        
        Example:
            >>> msite = MSite("M9", magnets=[insert, bitter], ...)
            >>> channels = msite.get_channels("M9", hideIsolant=True)
            >>> print(channels.keys())
            >>> # dict_keys(['M9_HL-31', 'M9_B1'])
            >>> 
            >>> # Access specific magnet's channels
            >>> insert_channels = channels['M9_HL-31']
            >>> for i, channel in enumerate(insert_channels):
            ...     print(f"Channel {i}: {channel}")
        """
        print(f"MSite/get_channels:")

        prefix = ""
        if mname:
            prefix = f"{mname}_"
        Channels = {}
        for magnet in self.magnets:
            oname = magnet.name
            Channels[f"{prefix}{oname}"] = magnet.get_channels(oname, hideIsolant, debug)

        return Channels

    def get_isolants(self, mname: str, debug: bool = False) -> dict:
        """
        Retrieve electrical isolant definitions for the measurement site.
        
        Returns dictionary of isolant regions that electrically insulate
        components within the site assembly.
        
        Args:
            mname: Measurement site name prefix for isolant identifiers
            debug: Enable debug output
        
        Returns:
            dict: Dictionary of isolant regions (currently returns empty dict)
        
        Notes:
            This is a placeholder method for future isolant tracking functionality.
            Current implementation returns an empty dictionary.
            When implemented, will aggregate isolants from all magnets.
        
        Example:
            >>> msite = MSite("M9", ...)
            >>> isolants = msite.get_isolants("M9")
            >>> # Currently returns {}
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Generate marker names for all geometric entities in the measurement site.
        
        Aggregates marker names from all constituent magnets (and screens when
        implemented), creating a complete list of identifiers for all solid
        components used in mesh generation, visualization, and post-processing.
        
        Args:
            mname: Measurement site name prefix (e.g., "M9")
            is2D: If True, generate detailed 2D marker names from each magnet
                If False, use simplified 3D naming convention
            verbose: Enable verbose output showing name generation process
        
        Returns:
            list[str]: Ordered list of marker names for all components:
                - Names from magnet 1 (with prefix "{mname}_{magnet1.name}_")
                - Names from magnet 2 (with prefix "{mname}_{magnet2.name}_")
                - ... (for all magnets)
                - Screen names (when implemented)
        
        Notes:
            - Each magnet's names are prefixed with site and magnet identifiers
            - Name format depends on is2D flag (passed to each magnet)
            - Order is deterministic: follows magnet order in self.magnets list
            - Verbose mode shows total count: "MSite/get_names: solid_names {count}"
            - TODO: Add screen names to output
        
        Example:
            >>> msite = MSite("M9", magnets=[insert, bitter], ...)
            >>> names = msite.get_names("M9", is2D=False)
            >>> print(names[:5])  # First 5 names
            >>> # ['M9_HL-31_H1', 'M9_HL-31_H2', 'M9_HL-31_R1', 'M9_B1_B1', ...]
            >>>
            >>> # Get count
            >>> print(f"Total markers: {len(names)}")
        """
        prefix = ""
        if mname:
            prefix = f"{mname}_"
        
        solid_names = []
        for magnet in self.magnets:
            oname = f"{prefix}{magnet.name}"
            solid_names += magnet.get_names(oname, is2D, verbose)

        # TODO add Screens

        if verbose:
            print(f"MSite/get_names: solid_names {len(solid_names)}")
        return solid_names

    def get_magnet(self, name: str) -> Optional[Union[Insert, Bitter, Supra]]:
        """
        Retrieve a specific magnet by name from the site assembly.
        
        Searches through all magnets in the site and returns the first magnet
        whose name matches the given name parameter.
        
        Args:
            name: Name of the magnet to retrieve (case-sensitive exact match)
        
        Returns:
            Union[Insert, Bitter, Supra] or None: The magnet object if found,
                                                None if no magnet with that name exists
        
        Notes:
            - Performs linear search through self.magnets list
            - Returns first match (assumes unique names)
            - Case-sensitive name comparison
            - Returns None rather than raising exception if not found
        
        Example:
            >>> msite = MSite("M9", magnets=[insert, bitter, supra], ...)
            >>> 
            >>> # Retrieve specific magnet
            >>> insert = msite.get_magnet("HL-31")
            >>> if insert:
            ...     print(f"Found insert with {insert.get_nhelices()} helices")
            ... else:
            ...     print("Insert not found")
            >>>
            >>> # Check if magnet exists
            >>> if msite.get_magnet("Unknown"):
            ...     print("Magnet exists")
            ... else:
            ...     print("Magnet not found")
        """
        for magnet in self.magnets:
            if magnet.name == name:
                return magnet
        return None

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create MSite instance from dictionary representation.
        
        Supports flexible input formats for nested magnet and screen objects,
        allowing mixed specifications of inline definitions and external references.
        
        Args:
            values: Dictionary containing MSite configuration with keys:
                - name (str): Site name
                - magnets (list/dict): List of magnets (strings/dicts/objects)
                - screens (list/dict/None, optional): List of screens
                - z_offset (list[float]/None, optional): Axial offsets
                - r_offset (list[float]/None, optional): Radial offsets
                - paralax (list[float]/None, optional): Parallax corrections
            debug: Enable debug output showing object loading process
        
        Returns:
            MSite: New MSite instance created from dictionary
        
        Raises:
            KeyError: If required 'name' or 'magnets' keys are missing
            ValidationError: If magnet or screen data is malformed
            ValidationError: If magnets intersect
        
        Example:
            >>> data = {
            ...     "name": "M9",
            ...     "magnets": [
            ...         "HL-31",  # Load from file
            ...         {"name": "B1", "r": [...], ...}  # Inline definition
            ...     ],
            ...     "screens": None,
            ...     "z_offset": [0.0, 150.0],
            ...     "r_offset": [0.0, 0.0],
            ...     "paralax": None
            ... }
            >>> msite = MSite.from_dict(data)
        """
        magnets = cls._load_nested_list(values.get('magnets'), (Insert, Bitters, Supras), debug=debug)
        screens = cls._load_nested_list(values.get('screens'), Screen, debug=debug)  # NEW: Load screens

        name = values["name"]
        magnets = values["magnets"]
        # FIX: Use get() with None default instead of empty list default
        screens = values.get("screens", None)
        z_offset = values.get("z_offset", None)
        r_offset = values.get("r_offset", None)
        paralax = values.get("paralax", None)
        return cls(name, magnets, screens, z_offset, r_offset, paralax)

    @classmethod
    def _load_nested_magnets(cls, magnets_data, debug=False):   
        """
        Load list of magnet objects from various input formats.
        
        This internal method handles flexible loading of magnets (Insert, Bitter, Supra),
        supporting multiple input formats for maximum flexibility.
        
        Args:
            magnets_data: Magnet specifications in any of these formats:
                - None: returns empty list
                - List: each item can be dict (inline) or magnet object
                - Dict: single magnet definition, returns list with one magnet
            debug: Enable debug output showing loading process for each magnet
        
        Returns:
            list: List of magnet objects (Insert, Bitter, or Supra instances)
                Empty list if magnets_data is None
        
        Raises:
            ValidationError: If magnets_data is not None/list/dict
            ValidationError: If list items are not dictionaries or magnet objects
        
        Notes:
            - Delegates to _load_single_magnet for individual magnet loading
            - Accepts pre-instantiated magnet objects directly
            - Converts single dict input to single-item list
        
        Example:
            >>> magnets_data = [
            ...     {"name": "insert1", "helices": [...], ...},  # Inline Insert
            ...     existing_bitter_object,  # Pre-created object
            ...     {"name": "supra1", ...}  # Inline Supra
            ... ]
            >>> magnets = MSite._load_nested_magnets(magnets_data)
        """
        if magnets_data is None:
            return []
        elif isinstance(magnets_data, list):
            magnets = []
            for item in magnets_data:
                if isinstance(item, dict):
                    magnet = cls._load_single_magnet(item, debug)
                    magnets.append(magnet)
                elif isinstance(item, (Insert, Bitter, Supra)):
                    magnets.append(item)
                else:
                    raise ValidationError("Each magnet must be a dictionary")
            return magnets
        elif isinstance(magnets_data, dict):
            return [cls._load_single_magnet(magnets_data, debug)]
        else:
            raise ValidationError("Magnets must be a list or a dictionary")
        
        
    def boundingBox(self) -> tuple:
        """
        Calculate the bounding box encompassing all magnets in the site.
        
        Computes the minimum and maximum radial (r) and axial (z) extents
        that encompass all magnet assemblies in the measurement site.
        Screens are not included in the bounding box calculation.
        
        Returns:
            tuple: (rb, zb) where:
                - rb: [r_min, r_max] - radial bounds in mm
                - zb: [z_min, z_max] - axial bounds in mm
        
        Notes:
            - Iterates through all magnets calling their boundingBox() methods
            - Takes the union of all individual bounding boxes
            - Does NOT include screens in calculation
            - Does NOT currently account for z_offset or r_offset
            (magnets are assumed at their nominal positions)
        
        Example:
            >>> msite = MSite("M9", magnets=[insert, bitter], ...)
            >>> rb, zb = msite.boundingBox()
            >>> print(f"Site radial extent: {rb[0]:.1f} to {rb[1]:.1f} mm")
            >>> print(f"Site axial extent: {zb[0]:.1f} to {zb[1]:.1f} mm")
            >>> 
            >>> # Calculate total dimensions
            >>> radial_span = rb[1] - rb[0]
            >>> axial_span = zb[1] - zb[0]
        """
        zmin = None
        zmax = None
        rmin = None
        rmax = None

        def cboundingBox(rmin, rmax, zmin, zmax, r, z):
            if zmin == None:
                zmin = min(z)
                zmax = max(z)
                rmin = min(r)
                rmax = max(r)
            else:
                zmin = min(zmin, min(z))
                zmax = max(zmax, max(z))
                rmin = min(rmin, min(r))
                rmax = max(rmax, max(r))
            return (rmin, rmax, zmin, zmax)

        for magnet in self.magnets:
            (r, z) = magnet.boundingBox()
            (rmin, rmax, zmin, zmax) = cboundingBox(
                rmin, rmax, zmin, zmax, r, z
            )

        return ([rmin, rmax], [zmin, zmax])

