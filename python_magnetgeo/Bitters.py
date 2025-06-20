#!/usr/bin/env python3
# encoding: UTF-8

"""defines Bitter Insert structure"""

import json
import yaml

from .Bitter import Bitter
from .utils import loadList


class Bitters(yaml.YAMLObject):
    """
    name :
    magnets :

    innerbore:
    outerbore:
    """

    yaml_tag = "Bitters"

    def __init__(
        self, name: str, magnets: list, innerbore: float, outerbore: float
    ) -> None:
        """constructor"""

        self.name = name
        self.magnets = magnets 
        self.innerbore = innerbore
        self.outerbore = outerbore

    def __repr__(self):
        """representation"""
        return "%s(name=%r, magnets=%r, innerbore=%r, outerbore=%r)" % (
            self.__class__.__name__,
            self.name,
            self.magnets,
            self.innerbore,
            self.outerbore,
        )

    def update(self):
        """
        update magnets if there were loaded as str
        """
        from .utils import check_objects        
        if check_objects(self.magnets, str):
            self.magnets = loadList("magnets", self.magnets, [None, Bitter], {"Bitter": Bitter.from_dict})
            print("update magnets:", self.magnets)

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
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Bitters dump")

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
    def from_dict(cls, values: str, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        magnets = values["magnets"]
        innerbore = values["innerbore"] if "innerbore" in values else 0
        outerbore = values["outerbore"] if "outerbore" in values else 0

        return cls(name, magnets, innerbore, outerbore)

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("Bitters", filename, Bitters, debug)

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

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(r_i[0] - r[0]) < abs(r_i[1] - r_i[0] + r[0] + r[1]) / 2.0
        isZ = abs(z_i[0] - z[0]) < abs(z_i[1] - z_i[0] + z[0] + z[1]) / 2.0
        if isR and isZ:
            collide = True
        return collide


def Bitters_constructor(loader, node):
    #print("Bitters_constructor: called")
    #print(node)
    values = loader.construct_mapping(node)
    #print(values)
    #for key, value in values.items():
    #    print(f"  {key}: {value} (type: {type(value)})")

    name = values["name"]
    magnets = values["magnets"]    
    #print("magnets:", values["magnets"], {len(values["magnets"])})

    innerbore = values["innerbore"]
    outerbore = values["outerbore"]

    return Bitters(name, magnets, innerbore, outerbore)   


yaml.add_constructor(Bitters.yaml_tag, Bitters_constructor)
