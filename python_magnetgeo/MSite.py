#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Site:

"""
from typing import Union, Optional

import os

import json
import yaml

from .utils import load

from .Bitters import Bitters
from .Supras import Supras
from .Insert import Insert
from .Screen import Screen

dict_magnets = {
    "Bitters": Bitters.from_dict,
    "Supras": Supras.from_dict,
    "Insert": Insert.from_dict,
}

dict_screens = {
    "Screen": Screen.from_dict,
}

class MSite(yaml.YAMLObject):
    """
    name :
    magnets : dict holding magnet list ("insert", "Bitter", "Supra")
    screens :
    """

    yaml_tag = "MSite"

    def __init__(
        self,
        name: str,
        magnets: Union[str, list, dict],
        screens: Optional[Union[str, list, dict]],
        z_offset: Optional[list[float]],
        r_offset: Optional[list[float]],
        paralax: Optional[list[float]],
    ) -> None:
        """
        initialize onject
        """
        self.name = name

        self.magnets = []
        # str ou MSite
        # list: str ou Insert, Bitters, Supras
        # dict: str ou Insert, Bitters, Supras
        if magnets:
            self.magnets = load("magnets", magnets, [None, Insert, Bitters, Supras], dict_magnets)
        
        self.screens = []
        # str ou Screens
        # list: str ou Screen
        # dict: str ou Screen
        if screens:
            self.screens = load("sreens", screens, [None, Screen], dict_screens)

        self.z_offset = z_offset
        self.r_offset = r_offset
        self.paralax = paralax

    def __repr__(self):
        """
        representation of object
        """
        return f"name: {self.name}, magnets:{self.magnets}, screens: {self.screens}, z_offset={self.z_offset}, r_offset={self.r_offset}, paralax_offset={self.paralax}"

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        """
        get Channels def as dict
        """
        print(f"MSite/get_channels:")

        prefix = ""
        if mname:
            prefix = f"{mname}_"
        Channels = {}
        for magnet in self.magnets:
            oname = magnet.name
            Channels[f"{prefix}{oname}"] = magnet.get_channels(oname, hideIsolant, debug)

        return Channels

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
            prefix = f"{mname}_"
        
        solid_names = []
        for magnet in self.magnets:
            oname = f"{prefix}{magnet.name}"
            solid_names += magnet.get_names(oname, is2D, verbose)

        # TODO add Screens

        if verbose:
            print(f"MSite/get_names: solid_names {len(solid_names)}")
        return solid_names

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to dump MSite data")

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self):
        """
        write from json file
        """
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

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
                values = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load MSite data {filename}")

        print(f'data: type={type(values)}')

        name = values["name"]
        magnets = values["magnets"]
        screens = values["screens"]
        z_offset = values["z_offset"]
        r_offset = values["r_offset"]
        paralax = values["paralax"]
        object = cls(name, magnets, screens, z_offset, r_offset, paralax)
    
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
            print(f'MSite.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)

    def boundingBox(self) -> tuple:
        """"""
        zmin = None
        zmax = None
        rmin = None
        rmax = None

        def cboundingBox(rmin, rmax, zmin, zmax, r, z):
            if zmin == None:
                zmin = min(z)
                zmax = max(z)
                rmin = min(r)
                rmax = max(r)
            else:
                zmin = min(zmin, min(z))
                zmax = max(zmax, max(z))
                rmin = min(rmin, min(r))
                rmax = max(rmax, max(r))
            return (rmin, rmax, zmin, zmax)

        for magnet in self.magnets:
            (r, z) = magnet.boundingBox()
            (rmin, rmax, zmin, zmax) = cboundingBox(
                rmin, rmax, zmin, zmax, r, z
            )

        return ([rmin, rmax], [zmin, zmax])


def MSite_constructor(loader, node):
    """
    build an site object
    """
    print(f"MSite_constructor")
    values = loader.construct_mapping(node)
    return values




yaml.add_constructor(MSite.yaml_tag, MSite_constructor)
