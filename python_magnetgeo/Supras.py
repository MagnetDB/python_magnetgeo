#!/usr/bin/env python3
# encoding: UTF-8

"""defines Supra Insert structure"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

from .Supra import Supra
from .Probe import Probe
from .utils import getObject

class Supras(YAMLObjectBase):
    """
    Supras - Collection of superconducting Supra magnets with measurement probes.
    
    Represents a superconducting magnet insert containing multiple Supra objects
    arranged with defined bore dimensions. All serialization functionality is
    inherited from YAMLObjectBase.
    
    Attributes:
        name (str): Unique identifier for the Supras collection
        magnets (list): List of Supra objects or string references to Supra definitions
        innerbore (float): Inner bore radius in meters
        outerbore (float): Outer bore radius in meters  
        probes (list): Optional list of Probe objects for measurements
    
    Notes:
        - Validates that magnets do not intersect each other
        - Ensures bore dimensions are consistent with magnet geometry
        - Automatically computes overall bounding box from constituent magnets
    """

    yaml_tag = "Supras"

    def __init__(
        self, 
        name: str, 
        magnets: list, 
        innerbore: float, 
        outerbore: float, 
        probes: list = None
    ) -> None:
        """
        Initialize Supras collection with validation.
        
        Args:
            name: Unique identifier for the Supras collection
            magnets: List of Supra objects or string references to YAML files
            innerbore: Inner bore radius in meters
            outerbore: Outer bore radius in meters
            probes: Optional list of Probe objects or string references
            
        Raises:
            ValidationError: If any validation fails:
                - Empty or invalid name
                - innerbore >= outerbore (when both non-zero)
                - innerbore larger than minimum magnet inner radius
                - outerbore smaller than maximum magnet outer radius
                - Magnets intersect each other
        
        Notes:
            String references in magnets or probes are automatically loaded
            from corresponding YAML files (e.g., "magnet_name" → "magnet_name.yaml")
        """
        # Validate inputs
        GeometryValidator.validate_name(name)
        
        # Validate bore dimensions if not zero (zero means not specified)
        if innerbore != 0 and outerbore != 0:
            if innerbore >= outerbore:
                raise ValidationError(
                    f"innerbore ({innerbore}) must be less than outerbore ({outerbore})"
                )
        self.name = name

        self.magnets = []
        for magnet in magnets:
            if isinstance(magnet, str):
                self.magnets.append(getObject(f"{magnet}.yaml"))
            else:
                self.magnets.append(magnet)
        self.innerbore = innerbore
        self.outerbore = outerbore

        self.probes = []
        if probes is not None:
            for probe in probes:
                if isinstance(probe, str):
                    self.probes.append(Probe.from_yaml(f"{probe}.yaml"))
                else:
                    self.probes.append(probe)
        
        # Compute overall bounding box
        if self.magnets and innerbore > min([magnet.r[0] for magnet in self.magnets]):
            raise ValidationError(
                f"innerbore ({innerbore}) must be less than ({min([magnet.r[0] for magnet in self.magnets])})"
            )
        if self.magnets and outerbore < max([magnet.r[1] for magnet in self.magnets]):
            raise ValidationError(
                f"outerbore ({outerbore}) must be greater than last bitter outer radius ({max([magnet.r[1] for magnet in self.magnets])})"
            )
        
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
        Generate string representation of Supras object.
        
        Returns:
            str: String representation including name, magnets, bore dimensions, and probes
        """
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"magnets={self.magnets!r}, innerbore={self.innerbore!r}, "
            f"outerbore={self.outerbore!r}, probes={self.probes!r})"
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Supras instance from dictionary representation.
        
        Handles nested Supra and Probe objects properly, supporting both
        inline objects (dicts) and string references to external files.
        
        Args:
            values: Dictionary containing Supras data with keys:
                - name: Collection identifier (required)
                - magnets: List of Supra objects/dicts/strings (required)
                - innerbore: Inner bore radius (optional, default 0)
                - outerbore: Outer bore radius (optional, default 0)
                - probes: List of Probe objects/dicts/strings (optional)
            debug: Enable debug output for nested object loading
            
        Returns:
            Supras: New Supras instance
        
        Notes:
            Uses helper methods to handle complex nested object loading
        """
        magnets = cls._load_nested_magnets(values.get('magnets'), debug=debug)
        probes = cls._load_nested_probes(values.get('probes'), debug=debug)

        name = values["name"]
        innerbore = values.get("innerbore", 0)
        outerbore = values.get("outerbore", 0)
        
        return cls(name, magnets, innerbore, outerbore, probes)
    
    @classmethod
    def _load_nested_magnets(cls, magnets_data, debug: bool = False) -> List[Supra]:
        """
        Load nested Supra objects from various input formats.
        
        Handles three input formats for each magnet:
        1. Supra instance - used directly
        2. Dictionary - converted to Supra via from_dict()
        3. String reference - kept as-is for lazy loading
        
        Args:
            magnets_data: List of Supra objects, dicts, or string references
            debug: Enable debug output showing loading details
            
        Returns:
            list: List of Supra objects (or string references for lazy loading)
            
        Raises:
            ValidationError: If any magnet entry has invalid type
        
        Notes:
            String references allow lazy loading where magnets are loaded
            from YAML files only when needed
        """
        magnets = []
        if magnets_data:
            for item in magnets_data:
                if isinstance(item, Supra):
                    # Already a Supra object
                    magnets.append(item)
                elif isinstance(item, dict):
                    # Dictionary - convert to Supra
                    magnets.append(Supra.from_dict(item, debug=debug))
                elif isinstance(item, str):
                    # String reference - keep as-is for lazy loading
                    magnets.append(item)
                else:
                    raise ValidationError(
                        f"Invalid magnet entry: {item} (type: {type(item)})"
                    )
        return magnets
    
    @classmethod
    def _load_nested_probes(cls, probes_data, debug: bool = False) -> List[Probe]:
        """
        Load nested Probe objects from various input formats.
        
        Handles three input formats for each probe:
        1. Probe instance - used directly
        2. Dictionary - converted to Probe via from_dict()
        3. String reference - kept as-is for lazy loading
        
        Args:
            probes_data: List of Probe objects, dicts, or string references
            debug: Enable debug output showing loading details
            
        Returns:
            list: List of Probe objects (or string references for lazy loading)
            
        Raises:
            ValidationError: If any probe entry has invalid type
        
        Notes:
            Returns empty list if probes_data is None
        """
        probes = []
        if probes_data:
            for item in probes_data:
                if isinstance(item, Probe):
                    # Already a Probe object
                    probes.append(item)
                elif isinstance(item, dict):
                    # Dictionary - convert to Probe
                    probes.append(Probe.from_dict(item, debug=debug))
                elif isinstance(item, str):
                    # String reference - keep as-is for lazy loading
                    probes.append(item)
                else:
                    raise ValidationError(
                        f"Invalid probe entry: {item} (type: {type(item)})"
                    )
        return probes

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        """
        Get channel definitions for cooling or instrumentation.
        
        Args:
            mname: Magnet name prefix for channel identification
            hideIsolant: If True, hide insulator channels in output
            debug: Enable debug output
            
        Returns:
            dict: Empty dictionary (placeholder for future implementation)
        
        Notes:
            Currently returns empty dict as Supras don't define internal channels.
            Override in subclasses if channel definitions are needed.
        """
        return {}

    def get_isolants(self, mname: str, debug: bool = False) -> dict:
        """
        Get isolant/insulator definitions.
        
        Args:
            mname: Magnet name for isolant identification
            debug: Enable debug output
            
        Returns:
            dict: Empty dictionary (placeholder for future implementation)
        
        Notes:
            Currently returns empty dict as Supras don't define isolants at this level.
            Individual Supra objects may have their own isolant definitions.
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Generate marker names for mesh identification and physics assignments.
        
        Aggregates names from all constituent Supra magnets, adding an
        optional prefix for hierarchical identification.
        
        Args:
            mname: Name prefix to prepend to all magnet names (e.g., "system_")
            is2D: True for 2D axisymmetric mesh, False for 3D mesh
            verbose: Enable verbose output showing name generation details
            
        Returns:
            list[str]: List of marker names from all magnets with prefix applied
        
        Notes:
            - Each magnet's names are prefixed with "{mname}_{magnet.name}_"
            - Delegates to each Supra's get_names() method
            - Used by mesh generators and physics solvers for region identification
        
        Example:
            If mname="M20" and magnets are ["supra1", "supra2"], names might be:
            ["M20_supra1_DblPancake1", "M20_supra1_DblPancake2", "M20_supra2_DblPancake1", ...]
        """
        prefix = ""
        if mname:
            prefix = f'{mname}_'
        
        solid_names = []
        for magnet in self.magnets:
            oname = f"{prefix}{magnet.name}"
            solid_names += magnet.get_names(oname, is2D, verbose)

        if verbose:
            print(f"Supras.get_names: solid_names {len(solid_names)}")
        
        return solid_names

    def boundingBox(self) -> tuple:
        """
        Calculate bounding box encompassing all constituent magnets.
        
        Computes the minimal axis-aligned bounding box that contains all
        Supra magnets in the collection.
        
        Returns:
            tuple: (r_bounds, z_bounds) where:
                - r_bounds: [r_min, r_max] radial extent in meters
                - z_bounds: [z_min, z_max] axial extent in meters
        
        Notes:
            - r_min: minimum inner radius across all magnets
            - r_max: maximum outer radius across all magnets
            - z_min: minimum bottom z-coordinate across all magnets
            - z_max: maximum top z-coordinate across all magnets
        
        Example:
            >>> supras = Supras("test", [supra1, supra2], 10, 50)
            >>> rb, zb = supras.boundingBox()
            >>> print(f"Radial: {rb}, Axial: {zb}")
            Radial: [15.0, 45.0], Axial: [0.0, 100.0]
        """
        rb = [min([bitter.r[0] for bitter in self.magnets]), max([bitter.r[1] for bitter in self.magnets])]
        zb = [min([bitter.z[0] for bitter in self.magnets]), max([bitter.z[1] for bitter in self.magnets])]
        return (rb, zb)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if Supras collection intersects with a given rectangular region.
        
        Uses the overall bounding box to test for intersection with the
        specified region. This is a conservative test - returns True if
        the bounding box overlaps, even if individual magnets don't.
        
        Args:
            r: Radial bounds [r_min, r_max] of test region in meters
            z: Axial bounds [z_min, z_max] of test region in meters
        
        Returns:
            bool: True if bounding boxes overlap, False otherwise
        
        Algorithm:
            Uses separating axis theorem for axis-aligned rectangles:
            - Computes overlap in r direction
            - Computes overlap in z direction  
            - Returns True only if both directions overlap
        
        Example:
            >>> supras = Supras("test", [supra], 10, 50)
            >>> # Test region [20, 30] × [40, 60]
            >>> supras.intersect([20.0, 30.0], [40.0, 60.0])
            True  # Overlaps
            >>> supras.intersect([100.0, 110.0], [0.0, 10.0])
            False  # No overlap
        """
        (r_i, z_i) = self.boundingBox()

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])
        
        return r_overlap and z_overlap


# Automatic YAML constructor registration via YAMLObjectBase!
