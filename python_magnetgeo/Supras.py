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
    Supras - Collection of Supra magnets with probes.
    
    Represents a superconducting magnet insert containing multiple Supra objects.
    All serialization functionality inherited from YAMLObjectBase.
    
    Attributes:
        name: Identifier for the Supras collection
        magnets: List of Supra objects or string references
        innerbore: Inner bore radius [m]
        outerbore: Outer bore radius [m]
        probes: List of Probe objects (optional)
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
        Initialize Supras collection.
        
        Args:
            name: Collection identifier
            magnets: List of Supra objects or string references
            innerbore: Inner bore radius
            outerbore: Outer bore radius
            probes: Optional list of Probe objects
            
        Raises:
            ValidationError: If validation fails
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
                    self.probes.append(Probe.from_yam(f"{probe}.yaml"))
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
            if self.magnets[i].intersect(rb, zb):
                raise ValidationError(
                    f"magnets intersect: magnet[{i}] intersect magnet[{i-1}]: /n{self.magnets[i]} /n{self.magnets[i-1]}"
                )   
        
        
                

    def __repr__(self):
        """String representation"""
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"magnets={self.magnets!r}, innerbore={self.innerbore!r}, "
            f"outerbore={self.outerbore!r}, probes={self.probes!r})"
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Supras from dictionary.
        
        Handles nested Supra and Probe objects properly.
        
        Args:
            values: Dictionary containing Supras data
            debug: Enable debug output
            
        Returns:
            Supras instance
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
        Load nested Supra objects from data.
        
        Handles both Supra instances and dictionaries.
        
        Args:
            magnets_data: List of Supra objects, dicts, or string references
            debug: Enable debug output
            
        Returns:
            List of Supra objects (or string references)
            
        Raises:
            ValidationError: If magnet data is invalid
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
        Load nested Probe objects from data.
        
        Args:
            probes_data: List of Probe objects, dicts, or string references
            debug: Enable debug output
            
        Returns:
            List of Probe objects (or string references)
            
        Raises:
            ValidationError: If probe data is invalid
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
        Get channel definitions (placeholder - returns empty dict).
        
        Args:
            mname: Magnet name prefix
            hideIsolant: Hide isolant channels
            debug: Enable debug output
            
        Returns:
            Empty dictionary
        """
        return {}

    def get_isolants(self, mname: str, debug: bool = False) -> dict:
        """
        Get isolant definitions (placeholder - returns empty dict).
        
        Args:
            mname: Magnet name
            debug: Enable debug output
            
        Returns:
            Empty dictionary
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Get names for markers/identifiers.
        
        Args:
            mname: Name prefix
            is2D: 2D mode flag
            verbose: Enable verbose output
            
        Returns:
            List of solid names
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
        Calculate bounding box encompassing all magnets.
        
        Returns:
            Tuple of (rb, zb) where:
                rb: [r_min, r_max] radial bounds
                zb: [z_min, z_max] axial bounds
        """
        rb = [0, 0]
        zb = [0, 0]

        for i, supra in enumerate(self.magnets):
            if i == 0:
                rb = supra.r.copy()
                zb = supra.z.copy()
            else:
                rb[0] = min(rb[0], supra.r[0])
                zb[0] = min(zb[0], supra.z[0])
                rb[1] = max(rb[1], supra.r[1])
                zb[1] = max(zb[1], supra.z[1])

        return (rb, zb)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if rectangle defined by r,z intersects with bounding box.
        
        Args:
            r: [r_min, r_max] radial bounds to check
            z: [z_min, z_max] axial bounds to check
            
        Returns:
            True if intersection is non-empty, False otherwise
        """
        (r_i, z_i) = self.boundingBox()

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])
        
        return r_overlap and z_overlap


# Automatic YAML constructor registration via YAMLObjectBase!
