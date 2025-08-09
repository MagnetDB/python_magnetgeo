#!/usr/bin/env python3
# encoding: UTF-8

"""defines Bitter Insert structure"""

import json
import yaml

# Add import at the top
from .Probe import Probe

dict_probes = {
    "Probe": Probe.from_dict,
}

class Bitters(yaml.YAMLObject):
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

        self.name = name
        self.magnets = magnets 
        self.innerbore = innerbore
        self.outerbore = outerbore
        self.probes = probes if probes is not None else []  # NEW ATTRIBUTE

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

    def update(self):
        """
        update magnets if there were loaded as str
        """
        from .Bitter import Bitter
        from .utils import check_objects, loadList
        if self.magnets:
            if check_objects(self.magnets, str):
                self.magnets = loadList("magnets", self.magnets, [None, Bitter], {"Bitter": Bitter.from_dict})
                print("update magnets:", self.magnets)
        # NEW: Update probes
        if self.probes:
            if check_objects(self.probes, str):
                self.probes = loadList("probes", self.probes, [None, Probe], dict_probes)
                print("update probes:", self.probes)

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

    def dump(self):
        """dump to a yaml file name.yaml"""
        from .utils import writeYaml
        writeYaml("Bitters", self, Bitters)

    def to_json(self):
        """convert from yaml to json"""
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self):
        """write to a json file"""
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        magnets = values["magnets"]
        innerbore = values.get("innerbore", 0)
        outerbore = values.get("outerbore", 0)
        probes = values.get("probes", [])  # NEW: Optional with default empty list

        object = cls(name, magnets, innerbore, outerbore, probes)
        object.update()
        return object
    
    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        object = loadYaml("Bitters", filename, Bitters, debug)
        object.update()
        return object

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("Bitters", filename, debug)

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

        # Check if rectangles overlap in r-dimension
        r_overlap = r_i[0] < r[1] and r[0] < r_i[1]

        # Check if rectangles overlap in z-dimension
        z_overlap = z_i[0] < z[1] and z[0] < z_i[1]

        # Rectangles intersect if they overlap in both dimensions
        return r_overlap and z_overlap


def Bitters_constructor(loader, node):
    #print("Bitters_constructor: called")
    #print(node)
    values = loader.construct_mapping(node)
    return Bitters.from_dict(values)


yaml.add_constructor(Bitters.yaml_tag, Bitters_constructor)
