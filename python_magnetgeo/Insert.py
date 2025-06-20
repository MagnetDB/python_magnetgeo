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
from .utils import loadList

dict_leads = {
    "InnerCurrentLead": InnerCurrentLead.from_dict,
    "OuterCurrentLead": OuterCurrentLead.from_dict,
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


class Insert(yaml.YAMLObject):
    """
    name :
    helices :
    rings :
    currentleads :

    hangles :
    rangles :

    innerbore:
    outerbore:
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
    ):
        """
        constructor
        """
        self.name = name

        self.helices = helices

        self.rings = rings
            
        
        self.currentleads = []
        if currentleads:
            self.currentLeads = loadList("currentleads", currentleads, [None, InnerCurrentLead, OuterCurrentLead], dict_leads)

        self.hangles = hangles if hangles is not None else []
        print("hangles: ", self.hangles) if rangles is not None else []
            
        self.rangles = rangles if rangles is not None else []
        print("rangles: ", self.rangles) if rangles is not None else []

        self.innerbore = innerbore
        self.outerbore = outerbore

    def update(self):
        """
        update magnets if there were loaded as str
        """
        from .utils import check_objects        
        if check_objects(self.helices, str):
            self.helices = loadList("helices", self.helices, [None, Helix], {"Helix": Helix.from_dict})
            print("update helices:", self.helices)
        if check_objects(self.rings, str):
            self.rings = loadList("rings", self.rings, [None, Ring], {"Ring": Ring.from_dict})
            print("update rings:", self.rings)
        if check_objects(self.currentLeads, str):
            self.currentLeads = loadList("currentleads", self.currentleads, [None, InnerCurrentLead, OuterCurrentLead], dict_leads)
            print("update currentleads:", self.currentLeads)

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
            "%s(name=%r, helices=%r, rings=%r, currentleads=%r, hangles=%r, rangles=%r, innerbore=%r, outerbore=%r)"
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
            )
        )

    def dump(self):
        """dump to a yaml file name.yaml"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            print("Failed to Insert dump")

    def to_json(self):
        """convert from yaml to json"""
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self):
        """write to a json file"""
        ostream = open(self.name + ".json", "w")
        jsondata = self.to_json()
        ostream.write(str(jsondata))
        ostream.close()

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """
        create from dict
        """
        name = data["name"]

        helices = data["helices"]
        rings = data["rings"]
        currentleads = data["currentleads"]
        innerbore = data["innerbore"]
        outerbore = data["outerbore"]
        hangles = data["hangles"]
        rangles = data["rangles"]
    
        return cls(
            name, helices, rings, currentleads, hangles, rangles, innerbore, outerbore
        )

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("Insert", filename, Insert, debug)
    
    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("Insert", filename, debug)

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

        for i, helix in enumerate(self.helices):
            if i == 0:
                rb = helix.r
                zb = helix.z

            rb[0] = min(rb[0], helix.r[0])
            zb[0] = min(zb[0], helix.z[0])
            rb[1] = max(rb[1], helix.r[1])
            zb[1] = max(zb[1], helix.z[1])

        if self.rings:
            ring_dz_max = 0
            for i, ring in enumerate(self.rings):
                ring_dz_max = abs(ring.z[-1] - ring.z[0])

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

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(r_i[0] - r[0]) < abs(r_i[1] - r_i[0] + r[0] + r[1]) / 2.0
        isZ = abs(z_i[0] - z[0]) < abs(z_i[1] - z_i[0] + z[0] + z[1]) / 2.0
        if isR and isZ:
            collide = True
        return collide

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


def Insert_constructor(loader, node):
    print("Insert_constructor")
    data = loader.construct_mapping(node)

    name = data["name"]
    helices = data["helices"]
    rings = data["rings"]
    currentleads = data["currentleads"]
    innerbore = data["innerbore"]
    outerbore = data["outerbore"]
    hangles = data["hangles"]
    rangles = data["rangles"]

    return Insert(
        name, helices, rings, currentleads, hangles, rangles, innerbore, outerbore
    )


yaml.add_constructor(Insert.yaml_tag, Insert_constructor)
