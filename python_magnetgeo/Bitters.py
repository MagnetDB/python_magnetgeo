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
        """constructor"""
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
                magnets.append(getObject(f"{magnet}.yaml"))
            else:
                self.magnets.append(magnet)
        self.innerbore = innerbore
        self.outerbore = outerbore
        
        self.probes = []
        for probe in probes:
            if isinstance(probe, str):
                self.probes.append(Probe.from_yam(f"{probe}.yaml"))
            else:
                self.probes.append(probe)
        
        # Compute overall bounding box
        self.r, self.z = self.boundingBox()

        if self.magnets and innerbore > self.magnets[0].r[0]:
            raise ValidationError(
                f"innerbore ({innerbore}) must be less than first bitter inner radius ({self.magnets[0].r[0]})"
            )
        if self.magnets and outerbore < self.magnets[-1].r[1]:
            raise ValidationError(
                f"outerbore ({outerbore}) must be greater than last bitter outer radius ({self.magnets[-1].r[1]})"
            )
        
        # check that magnets are stored in ascending order of radius
        for i in range(1, len(self.magnets)):
            if self.magnets[i].r[0] <= self.magnets[i - 1].r[0]:
                raise ValidationError(
                    f"magnets must be ordered by ascending inner radius: magnet {i} has inner radius {self.magnets[i].r[0]} which is not greater than previous helix inner radius {self.magnets[i - 1].r[0]}"
                )   
        

    def __repr__(self):
        """representation"""
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
        get Channels def as dict
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
        return isolants
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        return names for Markers
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
        create from dict
        """
        magnets = cls._load_nested_magnets(values.get('magnets'), debug=debug)
        probes = cls._load_nested_probes(values.get('probes'), debug=debug)  # NEW: Load probes

        name = values["name"]
        # magnets = values["magnets"]
        innerbore = values.get("innerbore", 0)
        outerbore = values.get("outerbore", 0)
        # probes = values.get("probes", [])  # NEW: Optional with default empty list

        object = cls(name, magnets, innerbore, outerbore, probes)
        return object
    
    @classmethod
    def _load_nested_magnets(cls, magnets_data: List, debug: bool = False) -> List:
        """
        Helper method to load nested magnets from a list of data.
        """ 
        objects = []
        if not magnets_data:
            return objects

        for i, magnet_data in enumerate(magnets_data):
            if isinstance(magnet_data, str):
                # Reference to external file → load from file
                if debug:
                    print(f"Loading Magnet[{i}] from file: {magnet_data}", flush=True)
                from .utils import loadObject
                obj = loadObject("ring", magnet_data, Bitter, Bitter.from_yaml)
                objects.append(obj)
            elif isinstance(magnet_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Magnet[{i}] from inline dict: {magnet_data.get('name', 'unnamed')}", flush=True)
                obj = Bitter.from_dict(magnet_data)
                objects.append(obj)
            elif isinstance(magnet_data, Bitter):
                # None or already instantiated
                objects.append(magnet_data)
            else:
                raise ValidationError(f"Invalid magnet data at index {i}: {magnet_data}")            
        return objects
    
    @classmethod
    def _load_nested_probes(cls, probes_data: List, debug: bool = False) -> List:
        """
        Helper method to load nested probes from a list of data.
        """             
        objects = []
        if not probes_data:
            return objects

        for i, probe_data in enumerate(probes_data):
            if isinstance(probe_data, str):
                # Reference to external file → load from file
                if debug:
                    print(f"Loading Probe[{i}] from file: {probe_data}")
                from .utils import loadObject
                obj = loadObject("probe", probe_data, Probe, Probe.from_yaml)
                objects.append(obj)
            elif isinstance(probe_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Probe[{i}] from inline dict: {probe_data.get('name', 'unnamed')}")
                obj = Probe.from_dict(probe_data)
                objects.append(obj)
            else:
                raise ValidationError(f"Invalid probe data at index {i}: {probe_data}")
        return objects
    
    ###################################################################
    #
    #
    ###################################################################

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]

        so far exclude Leads
        """

        rb = [0, 0]
        zb = [0, 0]

        for i, bitter in enumerate(self.magnets):

            if i == 0:
                rb = bitter.r
                zb = bitter.z

            rb[0] = min(rb[0], bitter.r[0])
            zb[0] = min(zb[0], bitter.z[0])
            rb[1] = max(rb[1], bitter.r[1])
            zb[1] = max(zb[1], bitter.z[1])

        return (rb, zb)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """

        (r_i, z_i) = self.boundingBox()

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])#
        
        return r_overlap and z_overlap

