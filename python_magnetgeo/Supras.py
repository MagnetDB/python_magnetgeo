#!/usr/bin/env python3
# encoding: UTF-8

"""defines Supra Insert structure"""

import json
import yaml

from .Supra import Supra
from .utils import load

dict_supras = {
    "Supra": Supra.from_dict,
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
        self, name: str, magnets: list, innerbore: float, outerbore: float
    ) -> None:
        """constructor"""
        self.name = name
        self.magnets = magnets
        self.magnets = []
        # str ou Supras
        # list: str ou Supra
        # dict: str ou Supra
        if magnets:
            self.magnets = load("magnets", magnets, [None, Supra], dict_supras)

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
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Supras dump")

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
        return cls(name, magnets, innerbore, outerbore)        

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        import os
        cwd = os.getcwd()

        (basedir, basename) = os.path.split(filename)
        print(f"basedir={basedir}, basename={basename}, cwd={cwd}")

        if basedir and basedir != ".":
            os.chdir(basedir)
            print(f"-> cwd={cwd}")

        try:
            with open(basename, "r") as istream:
                values, otype = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Supras data {filename}")

        print(f'data: type={type(values)}')

        name = values["name"]
        magnets = values["magnets"]        
        
        innerbore = values["innerbore"] if "innerbore" in values else 0
        outerbore = values["outerbore"] if "outerbore" in values else 0
        object = cls(name, magnets, innerbore, outerbore)        
        
        if basedir and basedir != ".":
            os.chdir(cwd)

        return object

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'Supras.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)

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


def Supras_constructor(loader, node):
    values = loader.construct_mapping(node)
    return values, "Supras"


yaml.add_constructor(Supras.yaml_tag, Supras_constructor)
