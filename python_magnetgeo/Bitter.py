#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Bitter:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""
from typing import List

import json
import yaml
from . import deserialize

from . import ModelAxi


class Bitter(yaml.YAMLObject):
    """
    name :
    r :
    z :

    axi :
    coolingslits: [(r, angle, n, dh, sh)]
    tierods: [r, n, shape]
    """

    yaml_tag = "Bitter"

    def __init__(
        self,
        name,
        r: List[float],
        z: List[float],
        axi: ModelAxi.ModelAxi,
        coolingslits: List = [],
        tierods: List = [],
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.axi = axi
        self.coolingslits = coolingslits
        self.tierods = tierods

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> List[list]:
        """
        return channels
        """
        print(f"Bitter({self.name}): CoolingSlits={self.coolingslits}")
        n_slits = 0
        for data in self.coolingslits:
            if "r" in data:
                n_slits = len(data["r"])
                break

        prefix = ""
        if mname:
            prefix = f"{mname}_"
        Channels = [[f"{prefix}slit{i}"] for i in range(n_slits)]
        print(f"Bitter({prefix}): {Channels}")
        return Channels

    def get_lc(self) -> float:
        lc = (self.r[1] - self.r[0]) / 10.0
        if self.coolingslits:
            x: float = self.r[0]
            dr: List[float] = []
            for data in self.coolingslits:
                if "r" in data:
                    for _x in data["r"]:
                        dr.append(_x - x)
                        x = _x
            dr.append(self.r[1] - x)
            # print(f"Bitter: dr={dr}")
            lc = min(dr) / 5.0

        return lc

    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """
        return isolants
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> List[str]:
        """
        return names for Markers
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        if is2D:
            nsection = len(self.axi.turns)
            if nsection == 1:
                solid_names.append(f"{prefix}{self.name}")
            else:
                for j in range(nsection):
                    solid_names.append(f"{prefix}{self.name}_B{j+1}")
        else:
            solid_names.append(f"{prefix}{self.name}_B")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r, axi=%r, coolingslits=%r, tierods=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
            self.axi,
            self.coolingslits,
            self.tierods,
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Bitter dump")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Bitter data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.axi = data.axi
        self.coolingslits = data.coolingslits
        self.tierods = data.tierods

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def from_json(self, string):
        """
        convert from json to yaml
        """
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """
        write from json file
        """
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    def read_from_json(self):
        """
        read from json file
        """
        with open(f"{self.name}.json", "r") as istream:
            jsondata = self.from_json(istream.read())

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return self.axi.get_Nturns()

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """

        return (self.r, self.z)

    def intersect(self, r: List[float], z: List[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not

        return False if empty, True otherwise
        """

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(self.r[0] - r[0]) < abs(self.r[1] - self.r[0] + r[0] + r[1]) / 2.0
        isZ = abs(self.z[0] - z[0]) < abs(self.z[1] - self.z[0] + z[0] + z[1]) / 2.0
        if isR and isZ:
            collide = True
        return collide


def Bitter_constructor(loader, node):
    """
    build an bitter object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    axi = values["axi"]
    coolingslits = values["coolingslits"]
    tierods = values["tierods"]

    return Bitter(name, r, z, axi, coolingslits, tierods)


yaml.add_constructor("!Bitter", Bitter_constructor)
