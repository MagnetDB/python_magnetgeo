#!/usr/bin/env python3
# encoding: UTF-8

"""defines Insert structure"""

import math
import os

from .Helix import Helix
from .Ring import Ring
from .InnerCurrentLead import InnerCurrentLead
from .OuterCurrentLead import OuterCurrentLead
from .Probe import Probe
from .utils import getObject, flatten

from typing import List, Union
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


def filter(data: list[float], tol: float = 1.0e-6) -> list[float]:
    result = []
    ndata = len(data)
    for i in range(ndata):
        result += [
            j for j in range(i, ndata) if i != j and abs(data[i] - data[j]) <= tol
        ]
    # print(f"duplicate index: {result}")

    # remove result from data
    return [data[i] for i in range(ndata) if i not in result]


class Insert(YAMLObjectBase):
    """
    Complete magnet insert assembly.
    
    An Insert combines multiple helices (coils) with optional rings connecting them.
    
    Geometric Rules:
        - Rings connect adjacent helices: len(rings) = len(helices) - 1
        - Minimum 2 helices required when rings are present
        - Each helix can have one angle specification (hangles)
        - Each ring can have one angle specification (rangles)
        - innerbore < first helix inner radius
        - outerbore > last helix outer radius
    
    Args:
        name: Insert identifier
        helices: List of Helix objects or filenames (required)
        rings: List of Ring objects or filenames connecting helices (optional)
        currentleads: List of current lead objects or filenames (optional)
        hangles: Angular positions for each helix in degrees (optional)
        rangles: Angular positions for each ring in degrees (optional)
        innerbore: Inner bore diameter in mm (optional, default=0)
        outerbore: Outer bore diameter in mm (optional, default=0)
        probes: List of Probe objects for measurements (optional)
    
    Raises:
        ValidationError: If geometric constraints are violated
    
    Examples:
        >>> # Insert with 3 helices and 2 connecting rings
        >>> insert = Insert(
        ...     name="HL-31",
        ...     helices=["H1", "H2", "H3"],
        ...     rings=["R1", "R2"],  # R1 connects H1-H2, R2 connects H2-H3
        ...     innerbore=18.54,
        ...     outerbore=186.25
        ... )
    """

    yaml_tag = "Insert"

    def __init__(
        self,
        name: str,
        helices: List[Union[str, Helix]],
        rings: List[Union[str, Ring]],
        currentleads: List[Union[str, InnerCurrentLead, OuterCurrentLead]],
        hangles: list[float],
        rangles: list[float],
        innerbore: float = 0,
        outerbore: float = 0,
        probes: List[Union[str, Probe]] = None,  # NEW PARAMETER
    ):
        """
        Initialize an Insert magnet assembly.
        
        An Insert represents a complete resistive magnet insert assembly containing
        helical coils, reinforcement rings, current leads, and optional probes.
        
        Args:
            name: Unique identifier for the insert assembly
            helices: List of Helix objects or string references to helix YAML files
            rings: List of Ring objects or string references to ring YAML files
            currentleads: List of CurrentLead objects (InnerCurrentLead or OuterCurrentLead)
                        or string references to current lead YAML files
            hangles: List of angular positions (degrees) for helices placement
            rangles: List of angular positions (degrees) for rings placement
            innerbore: Inner bore radius in mm (0 means unspecified)
            outerbore: Outer bore radius in mm (0 means unspecified)
            probes: Optional list of Probe objects or string references to probe YAML files
        
        Raises:
            ValidationError: If name is invalid or if innerbore >= outerbore (when both non-zero)
            ValidationError: If helices list is empty
            ValidationError: If rings list length doesn't match helices (when rings present)
            ValidationError: If inner/outer current leads have inconsistent zinf values
        
        Example:
            >>> helix1 = Helix("H1", r=[10.0, 20.0], z=[0.0, 100.0], ...)
            >>> ring1 = Ring("R1", r=[8.0, 22.0], z=[40.0, 60.0])
            >>> insert = Insert(
            ...     name="HL-31",
            ...     helices=[helix1],
            ...     rings=[ring1],
            ...     currentleads=[],
            ...     hangles=[0.0],
            ...     rangles=[0.0],
            ...     innerbore=5.0,
            ...     outerbore=25.0
            ... )
        """
        # Validate inputs
        GeometryValidator.validate_name(name)
        
        # Validate bore dimensions if not zero (zero means not specified)
        if innerbore != 0 and outerbore != 0:
            if innerbore >= outerbore:
                raise ValidationError(
                    f"innerbore ({innerbore}) must be less than outerbore ({outerbore})"
                )
        
        if rings and len(rings) > 0:
            if len(rings) != len(helices) -1:
                raise ValidationError(
                    f"Number of rings ({len(rings)}) must be equal to number of helices ({len(helices)}) minus one"
                )
        
        if hangles and len(hangles) > 0:
            if len(hangles) > 0:
                if len(hangles) != len(helices):
                    raise ValidationError(
                        f"Number of hangles ({len(hangles)}) must match number of helices ({len(helices)})"
                    )
            
        if rangles and len(rangles) > 0:
            if len(rangles) > 0:
                if len(rangles) != len(rings):
                    raise ValidationError(
                        f"Number of rangles ({len(rangles)}) must match number of rings ({len(rings)})"
                    )
        
            
        self.name = name
        self.helices = []
        for helix in helices:
            if isinstance(helix, str):
                self.helices.append(Helix.from_yaml(f"{helix}.yaml"))
            else:
                self.helices.append(helix)

        self.rings = []
        for ring in rings:
            if isinstance(ring, str):
                self.rings.append(Ring.from_yaml(f"{ring}.yaml"))
            else:
                self.rings.append(ring)
                    
        self.currentleads = []
        for lead in currentleads:
            if isinstance(lead, str):
                self.currentleads.append(getObject(f"{lead}.yaml"))
            else:
                self.currentleads.append(lead)

        self.hangles = hangles
        self.rangles = rangles

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
        self.r, self.z = self.boundingBox()

        if self.helices and innerbore > self.helices[0].r[0]:
            raise ValidationError(
                f"innerbore ({innerbore}) must be less than first helix inner radius ({helices[0].r[0]})"
            )
        if self.helices and outerbore < self.helices[-1].r[1]:
            raise ValidationError(
                f"outerbore ({outerbore}) must be greater than last helix outer radius ({helices[-1].r[1]})"
            )

        # check that helices are stored in ascending order of radius
        for i in range(1, len(self.helices)):
            if self.helices[i].r[0] <= self.helices[i - 1].r[0]:
                raise ValidationError(
                    f"Helices must be ordered by ascending inner radius: helix {i} has inner radius {self.helices[i].r[0]} which is not greater than previous helix inner radius {self.helices[i - 1].r[0]}"
                )   
            
        # check that rings are stored in ascending order of radius
        for i in range(1, len(self.rings)):
            ring_side = "BP" if self.rings[i].bpside else "HP"
            if self.rings[i].r[0] <= self.rings[i - 1].r[0]:
                raise ValidationError(
                    f"Rings must be ordered by ascending inner radius: ring {i} has inner radius {self.rings[i].r[0]} which is not greater than previous ring inner radius {self.rings[i - 1].r[0]}"
                )
            
            # check that rings radius matches with helices[i] and helices[i+1] radius only valid when helix has not chamfer
            helix0 = self.helices[i]
            helix1 = self.helices[i+1] 
            helices_radius = [helix.r for helix in (helix0, helix1)]

            if helix0.chamfers:
                # select chamfer that are on same side as ring
                chamfers = [chamfer for chamfer in helix0.chamfers if chamfer.side == ring_side] # for chamfer in helix0.chamfers:
                for chamfer in chamfers:
                    if chamfer.rside == "rext":
                        helices_radius[1] -= chamfer.getDr() 
                    else:
                        helices_radius[0] -= chamfer.getDr()

            if helix1.chamfers:
                # select chamfer that are on same side as ring
                chamfers = [chamfer for chamfer in helix1.chamfers if chamfer.side == ring_side] # for chamfer in helix1.chamfers:
                for chamfer in chamfers:
                    if chamfer.rside == "rext":
                        helices_radius[3] -= chamfer.getDr() 
                    else:
                        helices_radius[2] -= chamfer.getDr()

            if self.rings[i].r != flatten(helices_radius):
                raise ValidationError(
                    f"Ring {i} radius {self.rings[i].r} does not match with adjacent helices radii {flatten(helices_radius)}"
                )

        for helix in self.helices:
            print(helix)

        # check leads radius
        if self.currentleads is not None:
            for lead in self.currentleads:
                print(lead, type(lead))
                zinf_inner = None
                if isinstance(lead, InnerCurrentLead):
                    rext = lead.r[1]
                    zinf_inner = self.helices[0].z[0] - lead.h
                    if lead.support is not None and lead.support:
                        if lead.support[1] != 0:
                            rext = lead.support[0]
                        zinf_inner -= lead.support[1]
                    if rext != self.helices[0].r[1]:
                        raise ValidationError(
                            f"InnerCurrentLead outer radius ({rext}) must be egal to first helix outer radius ({self.helices[0].r[1]})"
                        )
                else:
                    zinf_outer = self.helices[-1].z[0] - lead.h
                    if lead.bar is not None and lead.bar:
                        zinf_outer -= lead.bar[1]
                    if lead.support is not None and lead.support:
                        zinf_outer -= lead.support[1]
                    if zinf_inner is not None and zinf_inner != zinf_outer:
                        raise ValidationError(f"Insert: zinf_inner ({zinf_inner}) and zinf_outer ({zinf_outer}) must be egal")
                
        # Store the directory context for resolving struct paths
        self._basedir = os.getcwd()

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list[list]:
        """
        Retrieve cooling channel definitions for the insert.
        
        Generates lists of channel markers for each cooling channel between helices,
        including optional isolant and kapton layers. Channels are numbered based
        on the spaces between helices.
        
        Args:
            mname: Magnet name prefix for channel markers (e.g., "HL31")
            hideIsolant: If True, exclude isolant and kapton layer markers from output
            debug: Enable debug output showing channel generation process
        
        Returns:
            list[list[str]]: List of channels, where each channel is a list of
                            marker names. Number of channels = n_helices + 1
        
        Notes:
            - Channel numbering: Channel[i] is between Helix[i] and Helix[i+1]
            - Marker naming convention:
            * H{i}_rExt: Outer radius of helix i
            * H{i}_rInt: Inner radius of helix i
            * R{i}_rInt/rExt: Ring inner/outer radius
            * IrExt/IrInt: Isolant layers (if hideIsolant=False)
            * kaptonsIrExt/IrInt: Kapton layers for HR type (if hideIsolant=False)
        
        Example:
            >>> insert = Insert("HL31", helices=[h1, h2, h3], ...)
            >>> channels = insert.get_channels("HL31", hideIsolant=True)
            >>> # Returns 4 channels for 3 helices
            >>> for i, channel in enumerate(channels):
            ...     print(f"Channel {i}: {channel}")
        """

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Channels = []
        Nhelices = len(self.helices)
        NChannels = Nhelices + 1  # To be updated if there is any htype==HR in Insert

        for i in range(0, NChannels):
            names = []
            inames = []
            if i == 0:
                if self.rings:
                    names.append(f"{prefix}R{i+1}_rInt")  # check ring numerotation
            if i >= 1:
                names.append(f"{prefix}H{i}_rExt")
                if not hideIsolant:
                    isolant_names = [f"{prefix}H{i}_IrExt"]
                    kapton_names = [f"{prefix}H{i}_kaptonsIrExt"]  # Only for HR
                    names = names + isolant_names + kapton_names
            if i >= 2:
                if self.rings:
                    names.append(f"{prefix}R{i-1}_rExt")
            if i < NChannels:
                names.append(f"{prefix}H{i+1}_rInt")
                if not hideIsolant:
                    isolant_names = [f"{prefix}H{i+1}_IrInt"]
                    kapton_names = [f"{prefix}H{i+1}_kaptonsIrInt"]  # Only for HR
                    names = names + isolant_names + kapton_names

            # Better? if i+1 < nchannels:
            if i != 0 and i + 1 < NChannels:
                if self.rings:
                    names.append(f"{prefix}R{i}_CoolingSlits")
                    names.append(f"{prefix}R{i+1}_rInt")
            Channels.append(names)
            #
            # For the moment keep iChannel_Submeshes into
            # iChannel_Submeshes.append(inames)

        if debug:
            print("Channels:")
            for channel in Channels:
                print(f"\t{channel}")
        return Channels

    def get_isolants(self, mname: str, debug: bool = False):
        """
        Retrieve electrical isolant definitions for the insert.
        
        Returns list of isolant regions that electrically insulate components
        within the insert assembly.
        
        Args:
            mname: Magnet name prefix for isolant markers
            debug: Enable debug output
        
        Returns:
            list: List of isolant region identifiers (currently returns empty list)
        
        Notes:
            This is a placeholder method for future isolant tracking functionality.
            Current implementation returns an empty list.
        
        Example:
            >>> insert = Insert(...)
            >>> isolants = insert.get_isolants("HL31")
            >>> # Currently returns []
        """

        # if HL or HL
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        Generate marker names for all geometric entities in the insert.
        
        Creates a complete list of identifiers for all solid components,
        used for mesh generation, visualization, and post-processing.
        
        Args:
            mname: Magnet name prefix (e.g., "HL31")
            is2D: If True, generate detailed 2D marker names from helices
                If False, use simplified 3D naming convention
            verbose: Enable verbose output showing name generation process
        
        Returns:
            list[str]: Ordered list of marker names for all components:
                - Helix markers: "H{i+1}" (3D) or detailed names (2D)
                - Ring markers: "{prefix}R{i+1}"
                - Current lead markers: "iL{i+1}" (inner) or "oL{i+1}" (outer)
        
        Notes:
            - 2D mode: Generates detailed sector names from each helix
            - 3D mode: Uses simplified naming for whole components
            - Naming convention ensures unique identifiers for each component
            - Order is consistent: helices, then rings, then current leads
        
        Example:
            >>> insert = Insert("HL31", helices=[h1, h2], rings=[r1], ...)
            >>> names_3d = insert.get_names("HL31", is2D=False)
            >>> print(names_3d)  # ['H1', 'H2', 'HL31_R1', 'iL1']
            >>>
            >>> names_2d = insert.get_names("HL31", is2D=True)
            >>> # Returns detailed sector names from each helix
        """
        prefix = ""
        if mname:
            prefix = f"{mname}_"
        solid_names = []

        Nhelices = len(self.helices)
        NChannels = Nhelices + 1  # To be updated if there is any htype==HR in Insert
        NIsolants = []  # To be computed depend on htype and dble
        for i, helix in enumerate(self.helices):
            Ninsulators = 0
            if is2D:
                h_solid_names = helix.get_names(f"{prefix}H{i+1}", is2D, verbose)
                solid_names += h_solid_names
            else:
                solid_names.append(f"H{i+1}")

        if self.rings:
            for i, ring in enumerate(self.rings):
                if verbose:
                    print(f"ring: {ring}")
                solid_names.append(f"{prefix}R{i+1}")
            # print(f'Insert_Gmsh: ring_ids={ring_ids}')

        if not is2D:
            if self.currentleads is not None:
                for i, Lead in enumerate(self.currentleads):
                    prefix = "o"
                    if isinstance(Lead, InnerCurrentLead):
                        prefix = "i"
                    solid_names.append(f"{prefix}L{i+1}")

        if verbose:
            print(f"Insert_Gmsh: solid_names {len(solid_names)}")
        return solid_names

    def get_nhelices(self):
        """
        Get the number of helices in the insert.
        
        Returns:
            int: Total count of Helix objects in the insert assembly
        
        Example:
            >>> insert = Insert(..., helices=[h1, h2, h3], ...)
            >>> n = insert.get_nhelices()
            >>> print(f"Insert has {n} helices")  # Insert has 3 helices
        """

        return len(self.helices)

    def __repr__(self):
        """
        Return string representation of Insert instance.
        
        Provides a detailed string showing all attributes and their values,
        useful for debugging and logging.
        
        Returns:
            str: String representation in constructor-like format showing
                all instance attributes
        
        Example:
            >>> insert = Insert("HL-31", helices=[h1], rings=[], ...)
            >>> print(repr(insert))
            Insert(name='HL-31', helices=[...], rings=[], ...)
        """
        return (
            "%s(name=%r, helices=%r, rings=%r, currentleads=%r, hangles=%r, rangles=%r, innerbore=%r, outerbore=%r, probes=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.helices,
                self.rings,
                self.currentleads,
                self.hangles,
                self.rangles,
                self.innerbore,
                self.outerbore,
                self.probes,  # NEW
            )
        )

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """
        Create Insert instance from dictionary representation.
        
        Supports multiple input formats for nested objects:
        - String: loads object from "{string}.yaml" file
        - Dict: creates object inline from dictionary
        - Object: uses already instantiated object
        
        Args:
            data: Dictionary containing insert configuration with keys:
                - name (str): Insert name
                - helices (list): List of helices (strings/dicts/objects)
                - rings (list): List of rings (strings/dicts/objects)
                - currentleads (list, optional): List of current leads
                - hangles (list[float]): Helix angular positions
                - rangles (list[float]): Ring angular positions
                - innerbore (float): Inner bore radius
                - outerbore (float): Outer bore radius
                - probes (list, optional): List of probes
            debug: Enable debug output showing object loading process
        
        Returns:
            Insert: New Insert instance created from dictionary
        
        Raises:
            KeyError: If required keys are missing from dictionary
            TypeError: If nested object lists contain invalid types
            ValidationError: If any validation rules are violated
        
        Example:
            >>> data = {
            ...     "name": "HL-31",
            ...     "helices": ["H1", "H2"],  # Load from files
            ...     "rings": [{"name": "R1", "r": [8, 22], "z": [40, 60]}],  # Inline
            ...     "currentleads": [],
            ...     "hangles": [0.0, 180.0],
            ...     "rangles": [0.0],
            ...     "innerbore": 5.0,
            ...     "outerbore": 25.0
            ... }
            >>> insert = Insert.from_dict(data)
        """
        helices = cls._load_nested_list(
            data.get('helices'), 
            Helix, 
            debug=debug
        )
        
        rings = cls._load_nested_list(
            data.get('rings'), 
            Ring, 
            debug=debug
        )
    
        currentleads = cls._load_nested_list(data.get('currentleads'), (InnerCurrentLead, OuterCurrentLead), debug=debug)
        probes = cls._load_nested_list(
            data.get('probes'), 
            Probe, 
            debug=debug
        )

        name = data["name"]

        # helices = data["helices"]
        # rings = data["rings"]
        # currentleads = data.get("currentleads", [])
        innerbore = data["innerbore"]
        outerbore = data["outerbore"]
        hangles = data["hangles"]
        rangles = data["rangles"]
        # probes = data.get("probes", [])  # NEW: Optional with default empty list

        object = cls(
            name, helices, rings, currentleads, hangles, rangles, innerbore, outerbore, probes
        )
        return object

    ###################################################################
    #
    #
    ###################################################################

    def boundingBox(self) -> tuple:
        """
        Calculate the bounding box of the insert assembly.
        
        Computes the minimum and maximum radial (r) and axial (z) extents
        of the entire insert, including all helices and rings.
        Current leads are excluded from the bounding box calculation.
        
        Returns:
            tuple: (rb, zb) where:
                - rb: [r_min, r_max] - radial bounds in mm
                - zb: [z_min, z_max] - axial bounds in mm
                Returns ([0, 0], [0, 0]) if no helices present
        
        Notes:
            - Bounding box encompasses all helices
            - If rings are present, z-bounds are extended by maximum ring height
            - Current leads are intentionally excluded from bounds calculation
        
        Example:
            >>> insert = Insert(...)
            >>> rb, zb = insert.boundingBox()
            >>> print(f"Radial: {rb[0]:.1f} to {rb[1]:.1f} mm")
            >>> print(f"Axial: {zb[0]:.1f} to {zb[1]:.1f} mm")
        """

        if not self.helices:
            return ([0, 0], [0, 0])

        rb = [float('inf'), float('-inf')]
        zb = [float('inf'), float('-inf')]

        # Get bounds from all helices
        for helix in self.helices:
            rb[0] = min(rb[0], helix.r[0])
            rb[1] = max(rb[1], helix.r[1])
            zb[0] = min(zb[0], helix.z[0])
            zb[1] = max(zb[1], helix.z[1])

        # Adjust for rings if they exist
        if self.rings:
            ring_dz_max = 0
            for ring in self.rings:
                ring_height = abs(ring.z[1] - ring.z[0])
                ring_dz_max = max(ring_dz_max, ring_height)

            # Extend z bounds by maximum ring height
            zb[0] -= ring_dz_max
            zb[1] += ring_dz_max

        # TODO add Leads

        return (rb, zb)

    def intersect(self, r, z):
        """
        Check if insert intersects with a rectangular region.
        
        Tests whether the insert's bounding box overlaps with a given
        rectangular region defined by radial and axial bounds.
        
        Args:
            r: [r_min, r_max] - radial bounds of test rectangle in mm
            z: [z_min, z_max] - axial bounds of test rectangle in mm
        
        Returns:
            bool: True if rectangles overlap (intersection non-empty),
                False if no intersection
        
        Notes:
            Uses axis-aligned bounding box (AABB) intersection algorithm.
            Rectangles intersect if they overlap in both r and z dimensions.
        
        Example:
            >>> insert = Insert(...)
            >>> # Check if insert intersects region r=[15,25], z=[50,100]
            >>> if insert.intersect([15, 25], [50, 100]):
            ...     print("Insert overlaps with region")
            ... else:
            ...     print("No intersection")
        """
        (r_i, z_i) = self.boundingBox()

        # Check if rectangles overlap in r-dimension
        r_overlap = r_i[0] < r[1] and r[0] < r_i[1]

        # Check if rectangles overlap in z-dimension
        z_overlap = z_i[0] < z[1] and z[0] < z_i[1]

        # Rectangles intersect if they overlap in both dimensions
        return r_overlap and z_overlap

    def get_params(self, workingDir: str = ".") -> tuple:
        """
        Extract and return physical parameters of the insert assembly.
        
        Retrieves comprehensive geometric and physical properties including
        dimensions, materials, and configuration details for all components.
        
        Args:
            workingDir: Working directory path for file operations (default: ".")
        
        Returns:
            Detailed parameter dictionary containing insert properties
            (exact structure depends on implementation)
        
        Notes:
            This method aggregates parameters from all constituent objects:
            - Helix parameters (dimensions, turns, materials)
            - Ring parameters (dimensions, properties)
            - Current lead parameters
            - Overall assembly dimensions
        
        Example:
            >>> insert = Insert(...)
            >>> params = insert.get_params()
            >>> # Access specific parameters from returned dictionary
        """

        Nhelices = len(self.helices)
        Nrings = len(self.rings)
        NChannels = Nhelices + 1

        Nsections = []
        Nturns_h = []
        R1 = []
        R2 = []
        Nsections = []
        Nturns_h = []
        Dh = []
        Sh = []

        Zh = []
        for i, helix in enumerate(self.helices):
            n_sections = len(helix.modelaxi.turns)
            Nsections.append(n_sections)
            Nturns_h.append(helix.modelaxi.turns)

            R1.append(helix.r[0])
            R2.append(helix.r[1])

            z = -helix.modelaxi.h
            (turns, pitch) = helix.modelaxi.compact()

            tZh = []
            tZh.append(helix.z[0])
            tZh.append(z)
            for n, p in zip(turns, pitch):
                z += n * p
                tZh.append(z)
            tZh.append(helix.z[1])
            Zh.append(tZh)
            # print(f"Zh[{i}]: {Zh[-1]}")

        Rint = self.innerbore
        Rext = self.outerbore

        for i in range(Nhelices):
            Dh.append(2 * (R1[i] - Rint))
            Sh.append(math.pi * (R1[i] - Rint) * (R1[i] + Rint))

            Rint = R2[i]

        Zr = []
        for i, ring in enumerate(self.rings):
            dz = abs(ring.z[1] - ring.z[0])
            if i % 2 == 1:
                # print(f"ring[{i}]: minus dz_ring={dz} to Zh[i][0]")
                Zr.append(Zh[i][0] - dz)

            if i % 2 == 0:
                # print(f"ring[{i}]: add dz={dz} to Zh[i][-1]")
                Zr.append(Zh[i][-1] + dz)
        # print(f"Zr: {Zr}")

        # get Z per Channel for Tw(z) estimate
        Zc = []
        Zi = []
        for i in range(NChannels - 1):
            nZh = Zh[i] + Zi
            # print(f"C{i}:")
            if i >= 0 and i < NChannels - 2:
                # print(f"\tR{i}")
                nZh.append(Zr[i])
            if i >= 1 and i <= NChannels - 2:
                # print(f"\tR{i-1}")
                nZh.append(Zr[i - 1])
            if i >= 2 and i <= NChannels - 2:
                # print(f"\tR{i-2}")
                nZh.append(Zr[i - 2])

            nZh.sort()
            Zc.append(filter(nZh))
            # remove duplicates (requires to have a compare method with a tolerance: |z[i] - z[j]| <= tol means z[i] == z[j])
            Zi = Zh[i]

            # print(f"Zh[{i}]={Zh[i]}")
            # print(f"Zc[{i}]={Zc[-1]}")

        # Add latest Channel: Zh[-1] + R[-1]
        nZh = Zh[-1] + [Zr[-1]]
        nZh.sort()
        Zc.append(filter(nZh))
        nZh = []

        Zmin = 0
        Zmax = 0
        for i, _z in enumerate(Zc):
            Zmin = min(Zmin, min(_z))
            Zmax = max(Zmax, max(_z))
            # print(f"Zc[Channel{i}]={_z}")
        # print(f"Zmin={Zmin}")
        # print(f"Zmax={Zmax}")

        Dh.append(2 * (Rext - Rint))
        Sh.append(math.pi * (Rext - Rint) * (Rext + Rint))
        return (Nhelices, Nrings, NChannels, Nsections, R1, R2, Dh, Sh, Zc)

