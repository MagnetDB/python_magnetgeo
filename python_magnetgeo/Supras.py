#!/usr/bin/env python3
# encoding: UTF-8

"""defines Supra Insert structure"""

import json
import yaml

from .Supra import Supra

# Add import at the top
from .Probe import Probe

dict_probes = {
    "Probe": Probe.from_dict,
}

class Supras(yaml.YAMLObject):
    """
    name :
    magnets :

    innerbore:
    outerbore:
    """

    yaml_tag = "Supras"

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
        from .utils import check_objects, loadList
        if self.magnets:
            if check_objects(self.magnets, str):
                self.magnets = loadList("magnets", self.magnets, [None, Supra], {"Supra": Supra.from_dict})
                print("update magnets:", self.magnets)
        # NEW: Update probes
        if self.probes:
            if check_objects(self.probes, str):
                self.probes = loadList("probes", self.probes, [None, Probe], dict_probes)
                print("update probes:", self.probes)

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        return {}

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
            print(f"Supras_Gmsh: solid_names {len(solid_names)}")
        return solid_names

    def dump(self):
        """dump to a yaml file name.yaml"""
        from .utils import writeYaml
        writeYaml("Supras", self, Supras)

    def to_json(self):
        """convert from yaml to json"""
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self):
        """write to a json file"""
        with open(f"{self.name}.son", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        magnets = values["magnets"]        
        
        innerbore = values["innerbore"] if "innerbore" in values else 0
        outerbore = values["outerbore"] if "outerbore" in values else 0
        probes = values.get("probes", [])  # NEW: Optional with default empty list
        return cls(name, magnets, innerbore, outerbore, probes)        

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        object = loadYaml("Supras", filename, Supras, debug)
        object.update()
        return object

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("Supras", filename, debug)

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

        for i, Supra in enumerate(self.magnets):
            if i == 0:
                rb = Supra.r
                zb = Supra.z

            rb[0] = min(rb[0], Supra.r[0])
            zb[0] = min(zb[0], Supra.z[0])
            rb[1] = max(rb[1], Supra.r[1])
            zb[1] = max(zb[1], Supra.z[1])

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


def Supras_constructor(loader, node):
    values = loader.construct_mapping(node)
    return Supras.from_dict(values)


yaml.add_constructor(Supras.yaml_tag, Supras_constructor)
