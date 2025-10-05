#!/usr/bin/env python3
# encoding: UTF-8

"""defines Bitter Insert structure"""

# Add import at the top
from .Bitter import Bitter
from .Probe import Probe
from .utils import getObject


from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Bitters(YAMLObjectBase):
    """
    name :
    magnets :

    innerbore:
    outerbore:
    probes :       # NEW ATTRIBUTE
    """

    yaml_tag = "Bitters"

    def __init__(
            self, name: str, magnets: list, innerbore: float, outerbore: float, probes: list = None,  # NEW PARAMETER
    ) -> None:
        """
        Initialize a Bitters magnet assembly (collection of Bitter plates).
        
        A Bitters represents a complete assembly of multiple Bitter plate magnets,
        which are resistive disk-shaped magnets with helical cooling channels.
        The class validates that individual Bitter magnets do not intersect.
        
        Args:
            name: Unique identifier for the Bitters assembly
            magnets: List of Bitter objects or string references to Bitter YAML files.
                    Each Bitter represents a single disk/plate in the assembly.
            innerbore: Inner bore radius in mm (0 means unspecified)
            outerbore: Outer bore radius in mm (0 means unspecified)
            probes: Optional list of Probe objects or string references to probe YAML files
                for measurement instrumentation
        
        Raises:
            ValidationError: If name is invalid
            ValidationError: If innerbore >= outerbore (when both non-zero)
            ValidationError: If any two Bitter magnets intersect spatially
        
        Notes:
            - Magnets are loaded from YAML files if provided as strings
            - Intersection checking ensures physical validity of the stack
            - Bitter plates are typically stacked axially (along z-axis)
            - Inner/outer bore defines the usable experimental volume
        
        Example:
            >>> bitter1 = Bitter("B1", r=[100, 150], z=[0, 50], ...)
            >>> bitter2 = Bitter("B2", r=[100, 150], z=[60, 110], ...)
            >>> bitters = Bitters(
            ...     name="M10_Bitters",
            ...     magnets=[bitter1, bitter2],
            ...     innerbore=80,
            ...     outerbore=160,
            ...     probes=[]
            ... )
            
            >>> # Or load from files
            >>> bitters = Bitters(
            ...     name="M10_Bitters",
            ...     magnets=["B1", "B2"],  # Load from B1.yaml, B2.yaml
            ...     innerbore=80,
            ...     outerbore=160,
            ...     probes=None
            ... )
        """
        # General validation
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
        Return string representation of Bitters instance.
        
        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.
        
        Returns:
            str: String representation in constructor-like format showing:
                - name: Assembly identifier
                - magnets: List of Bitter objects
                - innerbore: Inner bore radius
                - outerbore: Outer bore radius
                - probes: List of probe objects
        
        Example:
            >>> bitters = Bitters("M10_Bitters", magnets=[b1, b2], 
            ...                   innerbore=80, outerbore=160, probes=[])
            >>> print(repr(bitters))
            Bitters(name='M10_Bitters', magnets=[Bitter(...), Bitter(...)], 
                    innerbore=80, outerbore=160, probes=[])
            >>>
            >>> # In Python REPL
            >>> bitters
            Bitters(name='M10_Bitters', magnets=[...], innerbore=80, ...)
        """
        return "%s(name=%r, magnets=%r, innerbore=%r, outerbore=%r, probes=%r)" % (
            self.__class__.__name__,
            self.name,
            self.magnets,
            self.innerbore,
            self.outerbore,
            self.probes,  # NEW
        )

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        """
        Retrieve cooling channel definitions for all Bitter magnets.
        
        Aggregates channel definitions from all constituent Bitter plates into a
        hierarchical dictionary structure. Each Bitter contributes its own
        channel definitions (including helical cooling slits).
        
        Args:
            mname: Magnet assembly name prefix for channel identifiers
            hideIsolant: If True, exclude isolant and kapton layer markers from
                        channel definitions. Passed to each Bitter's get_channels().
            debug: Enable debug output showing channel aggregation process.
                Also passed to each Bitter's get_channels() method.
        
        Returns:
            dict: Hierarchical dictionary of channels:
                {
                    "{mname}_{bitter1.name}": bitter1.get_channels(...),
                    "{mname}_{bitter2.name}": bitter2.get_channels(...),
                    ...
                }
                Each value is the channel structure from that Bitter's get_channels().
        
        Notes:
            - Channels are organized by Bitter plate name for clarity
            - Debug output prefixed with "Bitters/get_channels:"
            - Each Bitter may have multiple cooling slits with channels
            - Channel structure depends on Bitter geometry and cooling slit configuration
        
        Example:
            >>> bitters = Bitters("M10_Bitters", magnets=[b1, b2, b3], ...)
            >>> channels = bitters.get_channels("M10", hideIsolant=True)
            >>> print(channels.keys())
            >>> # dict_keys(['M10_B1', 'M10_B2', 'M10_B3'])
            >>> 
            >>> # Access specific Bitter's channels
            >>> b1_channels = channels['M10_B1']
        """
        print(f"Bitters/get_channels:")
        Channels = {}

        prefix = ""
        if mname:
            prefix = f'{mname}_'
        for magnet in self.magnets:
            oname = f"{prefix}{magnet.name}"
            Channels[oname] = magnet.get_channels(oname, hideIsolant, debug)

        if debug:
            print("Channels:")
            for key, value in Channels:
                print(f"\t{key}: {value}")
        return Channels  # flatten list?

    def get_isolants(self, mname: str, debug: bool = False) -> dict:
        """
        Retrieve electrical isolant definitions for the Bitters assembly.
        
        Returns dictionary of isolant regions that electrically insulate
        components within the assembly.
        
        Args:
            mname: Magnet assembly name prefix for isolant identifiers
            debug: Enable debug output
        
        Returns:
            dict: Dictionary of isolant regions (currently returns empty dict)
        
        Notes:
            This is a placeholder method for future isolant tracking functionality.
            Current implementation returns an empty dictionary.
            When implemented, will aggregate isolants from all Bitter plates.
        
        Example:
            >>> bitters = Bitters("M10_Bitters", ...)
            >>> isolants = bitters.get_isolants("M10")
            >>> # Currently returns {}
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Generate marker names for all geometric entities in the Bitters assembly.
        
        Aggregates marker names from all constituent Bitter plates, creating a
        complete list of identifiers for all solid components used in mesh
        generation, visualization, and post-processing.
        
        Args:
            mname: Magnet assembly name prefix (e.g., "M10")
            is2D: If True, generate detailed 2D marker names from each Bitter
                (includes individual sectors for helical cuts)
                If False, use simplified 3D naming convention
            verbose: Enable verbose output showing name generation process
        
        Returns:
            list[str]: Ordered list of marker names for all components:
                - Names from Bitter 1 (with prefix "{mname}_{bitter1.name}_")
                - Names from Bitter 2 (with prefix "{mname}_{bitter2.name}_")
                - ... (for all Bitter plates)
        
        Notes:
            - Each Bitter's names are prefixed with assembly and plate identifiers
            - Name format depends on is2D flag (passed to each Bitter)
            - 2D mode: Detailed sector names for each cooling slit section
            - 3D mode: Simplified names for whole plates
            - Order is deterministic: follows magnet order in self.magnets list
            - Verbose mode shows total count: "Bitters/get_names: solid_names {count}"
        
        Example:
            >>> bitters = Bitters("M10_Bitters", magnets=[b1, b2], ...)
            >>> 
            >>> # 3D naming (simplified)
            >>> names_3d = bitters.get_names("M10", is2D=False)
            >>> print(names_3d)
            >>> # ['M10_B1_B', 'M10_B1_Kapton', 'M10_B2_B', 'M10_B2_Kapton']
            >>> 
            >>> # 2D naming (detailed with sectors)
            >>> names_2d = bitters.get_names("M10", is2D=True)
            >>> # Returns detailed sector names for each cooling slit section
            >>> print(f"Total 2D markers: {len(names_2d)}")
        """
        prefix = ""
        if mname:
            prefix = f'{mname}_'
        
        solid_names = []
        for magnet in self.magnets:
            oname = f"{prefix}{magnet.name}"
            solid_names += magnet.get_names(oname, is2D, verbose)

        if verbose:
            print(f"Bitters/get_names: solid_names {len(solid_names)}")
        return solid_names

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Bitters instance from dictionary representation.
        
        Supports flexible input formats for nested Bitter magnet objects,
        allowing mixed specifications of inline definitions and external references.
        
        Args:
            values: Dictionary containing Bitters configuration with keys:
                - name (str): Bitters assembly name
                - magnets (list): List of Bitter magnets (strings/dicts/objects)
                - innerbore (float, optional): Inner bore radius (default: 0)
                - outerbore (float, optional): Outer bore radius (default: 0)
                - probes (list, optional): List of probes (default: empty list)
            debug: Enable debug output showing object loading process
        
        Returns:
            Bitters: New Bitters instance created from dictionary
        
        Raises:
            KeyError: If required 'name' or 'magnets' keys are missing
            ValidationError: If magnet data is malformed
            ValidationError: If magnets intersect
        
        Example:
            >>> data = {
            ...     "name": "M10_Bitters",
            ...     "magnets": [
            ...         "B1",  # Load from file
            ...         {"name": "B2", "r": [100, 150], "z": [60, 110], ...}  # Inline
            ...     ],
            ...     "innerbore": 80,
            ...     "outerbore": 160,
            ...     "probes": []
            ... }
            >>> bitters = Bitters.from_dict(data)
        """
        magnets = cls._load_nested_list(values.get('magnets'), Bitter, debug=debug)
        probes = cls._load_nested_list(values.get('probes'), Probe, debug=debug)  # NEW: Load probes

        name = values["name"]
        # magnets = values["magnets"]
        innerbore = values.get("innerbore", 0)
        outerbore = values.get("outerbore", 0)
        # probes = values.get("probes", [])  # NEW: Optional with default empty list

        object = cls(name, magnets, innerbore, outerbore, probes)
        return object
    
    
    ###################################################################
    #
    #
    ###################################################################

    def boundingBox(self) -> tuple:
        """
        Calculate the bounding box encompassing all Bitter magnets.
        
        Computes the minimum and maximum radial (r) and axial (z) extents
        that encompass all Bitter plates in the assembly.
        
        Returns:
            tuple: (rb, zb) where:
                - rb: [r_min, r_max] - radial bounds in mm
                - zb: [z_min, z_max] - axial bounds in mm
        
        Notes:
            - Takes union of all individual Bitter bounding boxes
            - Efficiently computed using list comprehensions with min/max
            - Probes are not included in bounding box calculation
            - Uses actual geometry from each Bitter plate
        
        Example:
            >>> bitter1 = Bitter("B1", r=[100, 150], z=[0, 50], ...)
            >>> bitter2 = Bitter("B2", r=[110, 160], z=[60, 110], ...)
            >>> bitters = Bitters("test", [bitter1, bitter2], ...)
            >>> 
            >>> rb, zb = bitters.boundingBox()
            >>> print(f"Radial: {rb[0]} to {rb[1]} mm")  # [100, 160]
            >>> print(f"Axial: {zb[0]} to {zb[1]} mm")   # [0, 110]
        """

        rb = [min([bitter.r[0] for bitter in self.magnets]), max([bitter.r[1] for bitter in self.magnets])]
        zb = [min([bitter.z[0] for bitter in self.magnets]), max([bitter.z[1] for bitter in self.magnets])]

        return (rb, zb)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if Bitters assembly intersects with a rectangular region.
        
        Tests whether the assembly's bounding box overlaps with a given
        rectangular region defined by radial and axial bounds.
        
        Args:
            r: [r_min, r_max] - radial bounds of test rectangle in mm
            z: [z_min, z_max] - axial bounds of test rectangle in mm
        
        Returns:
            bool: True if rectangles overlap (intersection non-empty),
                False if no intersection
        
        Notes:
            Uses the bounding box for intersection testing (not individual plates).
            Efficient for collision detection and spatial queries.
        
        Example:
            >>> bitters = Bitters("test", magnets=[b1, b2], ...)
            >>> 
            >>> # Check if assembly overlaps with region
            >>> if bitters.intersect([120, 140], [20, 80]):
            ...     print("Bitters overlaps with test region")
            >>> 
            >>> # Check clearance for another component
            >>> other_rb, other_zb = other_component.boundingBox()
            >>> if bitters.intersect(other_rb, other_zb):
            ...     print("WARNING: Components overlap!")
        """
        (r_i, z_i) = self.boundingBox()

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])
        
        return r_overlap and z_overlap
