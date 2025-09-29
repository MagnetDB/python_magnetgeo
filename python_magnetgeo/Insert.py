#!/usr/bin/env python3
# encoding: UTF-8

"""defines Insert structure"""

import math
import datetime
import json
import yaml

from .Helix import Helix
from .Ring import Ring
from .InnerCurrentLead import InnerCurrentLead
from .OuterCurrentLead import OuterCurrentLead
from .Probe import Probe

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

dict_leads = {
    "InnerCurrentLead": InnerCurrentLead.from_dict,
    "OuterCurrentLead": OuterCurrentLead.from_dict,
}
dict_probes = {
    "Probe": Probe.from_dict,
}

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
    name :
    helices :
    rings :
    currentleads :

    hangles :
    rangles :

    innerbore:
    outerbore:
    probes :           # NEW ATTRIBUTE
    """

    yaml_tag = "Insert"

    def __init__(
        self,
        name: str,
        helices: list[Helix],
        rings: list[Ring],
        currentleads: list,
        hangles: list[float],
        rangles: list[float],
        innerbore: float = 0,
        outerbore: float = 0,
        probes: list = None,  # NEW PARAMETER
    ):
        """
        constructor
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

        self.helices = helices

        self.rings = rings
            
        
        self.currentleads = currentleads

        self.hangles = hangles
        self.rangles = rangles

        self.innerbore = innerbore
        self.outerbore = outerbore
        self.probes = probes if probes is not None else []  # NEW ATTRIBUTE

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list[list]:
        """
        return channels
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
        return isolants
        """

        # if HL or HL
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        return names for Markers
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
        return names for Markers
        """

        return len(self.helices)

    def __repr__(self):
        """representation"""
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
        create from dict
        """
        helices = cls._load_nested_helices(data.get('helices'), debug=debug)
        rings = cls._load_nested_rings(data.get('rings'), debug=debug)
        currentleads = cls._load_nested_currentleads(data.get('currentleads'), debug=debug)
        probes = cls._load_nested_probes(data.get('probes'), debug=debug)

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

    @classmethod  
    def _load_nested_helices(cls, data, debug=False):
        """Load list of Helices objects from various input formats and track references"""
        if data is None:
            return []
        
        if not isinstance(data, list):
            raise TypeError(f"helices must be a list, got {type(data)}")
        
        objects = []
        for i, _data in enumerate(data):
            if isinstance(_data, str):
                # String reference → load from "_data.yaml" and track reference
                if debug:
                    print(f"Loading Helix[{i}] from file: {_data}")
                from .utils import loadObject
                obj = loadObject("helix", _data, Helix, Helix.from_yaml)
                objects.append(obj)
            elif isinstance(_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Helix[{i}] from inline dict: {_data.get('name', 'unnamed')}")
                obj = Helix.from_dict(_data)
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(_data)
        
        return objects

    @classmethod  
    def _load_nested_rings(cls, data, debug=False):
        """Load list of Rings objects from various input formats and track references"""
        if data is None:
            return []
        
        if not isinstance(data, list):
            raise TypeError(f"rings must be a list, got {type(data)}")
        
        objects = []
        for i, _data in enumerate(data):
            if isinstance(_data, str):
                # String reference → load from "_data.yaml" and track reference
                if debug:
                    print(f"Loading Ring[{i}] from file: {_data}")
                from .utils import loadObject
                obj = loadObject("ring", _data, Ring, Ring.from_yaml)
                objects.append(obj)
            elif isinstance(_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Ring[{i}] from inline dict: {_data.get('name', 'unnamed')}")
                obj = Ring.from_dict(_data)
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(_data)
        
        return objects
    

    @classmethod  
    def _load_nested_currentleads(cls, data, debug=False):
        """Load list of CurrentLeads objects from various input formats and track references"""
        if data is None:
            return []
        
        if not isinstance(data, list):
            raise TypeError(f"currentleads must be a list, got {type(data)}")
        
        objects = []
        for i, _data in enumerate(data):
            if isinstance(_data, str):
                # String reference → load from "_data.yaml" and track reference
                if debug:
                    print(f"Loading Lead[{i}] from file: {_data}")
                from .utils import loadObject
                obj = loadObject("lead", _data, (InnerCurrentLead, OuterCurrentLead), None)
                objects.append(obj)
            elif isinstance(_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Lead[{i}] from inline dict: {_data.get('name', 'unnamed')}")
                try:
                    obj = InnerCurrentLead.from_dict(_data)
                except Exception:
                    try:
                        obj = OuterCurrentLead.from_dict(_data)
                    except Exception as e:
                        raise ValueError(f"Could not parse current lead (neither Inner or OuterLead) from dict: {_data}") from e    
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(_data)
        
        return objects

    @classmethod  
    def _load_nested_probes(cls, data, debug=False):
        """Load list of Probes objects from various input formats and track references"""
        if data is None:
            return []
        
        if not isinstance(data, list):
            raise TypeError(f"probes must be a list, got {type(data)}")
        
        objects = []
        for i, _data in enumerate(data):
            if isinstance(_data, str):
                # String reference → load from "_data.yaml" and track reference
                if debug:
                    print(f"Loading Probe[{i}] from file: {_data}")
                from .utils import loadObject
                obj = loadObject("probe", _data, Probe, Probe.from_yaml)
                objects.append(obj)
            elif isinstance(_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating Probe[{i}] from inline dict: {_data.get('name', 'unnamed')}")
                obj = Probe.from_dict(_data)
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(_data)
        
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
        Check if intersection with rectangle defined by r,z is empty or not

        return False if empty, True otherwise
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
        get params

        Nhelices,
        Nrings,
        NChannels,
        Nsections

        R1
        R2
        Z1
        Z2
        Dh,
        Sh,
        Zh
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

