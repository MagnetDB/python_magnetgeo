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

from .ModelAxi import ModelAxi
from .coolingslit import CoolingSlit
from .tierod import Tierod


class Bitter(yaml.YAMLObject):
    """
    name :
    r :
    z :

    axi :
    coolingslits: [(r, angle, n, dh, sh, shape)]
    tierods: [r, n, shape]
    """

    yaml_tag = "Bitter"

    def __init__(
        self,
        name,
        r: List[float],
        z: List[float],
        odd: bool,
        axi: ModelAxi,
        coolingslits: List[CoolingSlit],
        tierod: Tierod,
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.odd = odd
        self.axi = axi
        self.coolingslits = coolingslits
        self.tierod = tierod

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> List[list]:
        """
        return channels
        """
        print(f"Bitter({self.name}): CoolingSlits={self.coolingslits}")
        n_slits = len(self.coolingslits)

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
            for slit in self.coolingslits:
                _x = slit.r
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
            if self.z[0] < - self.axi.h:
                solid_names.append(f"{prefix}{self.name}_B0")

            for j in range(nsection):
                solid_names.append(f"{prefix}{self.name}_B{j+1}")

            if self.z[1] > self.axi.h:
                solid_names.append(f"{prefix}{self.name}_B{nsection+1}")
        else:
            solid_names.append(f"{prefix}{self.name}_B")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, r=%r, z=%r, odd=%r, axi=%r, coolingslits=%r, tierod=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.odd,
                self.axi,
                self.coolingslits,
                self.tierod,
            )
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
        self.odd = data.odd
        self.axi = data.axi
        self.coolingslits = data.coolingslits
        self.tierod = data.tierod

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
            ostream.write(jsondata)

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

    def get_params(self, workingDir: str = ".") -> tuple:
        Dh = [slit.n * slit.dh for slit in self.coolingslits]
        Sh = [slit.n * slit.sh for slit in self.coolingslits]

        return (len(self.coolingslits), self.z[0], self.z[1], Dh, Sh)

    def create_cut(self, format: str):
        """
        create cut files
        """

        z0 = self.axi.h
        sign = 1
        if self.odd:
            sign = -1

        self.axi.create_cut(format, z0, sign, self.name)

def Bitter_constructor(loader, node):
    """
    build an bitter object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    axi = values["axi"]
    coolingslits = values["coolingslits"]
    tierod = values["tierod"]

    return Bitter(name, r, z, odd, axi, coolingslits, tierod)


yaml.add_constructor("!Bitter", Bitter_constructor)

if __name__ == "__main__":
    import os
    from .Shape2D import Shape2D

    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    tierod = Tierod(2, 20, Square)

    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    slit1 = CoolingSlit(2, 5, 20, 0.1, 0.2, Square)
    slit2 = CoolingSlit(10, 5, 20, 0.1, 0.2, Square)
    coolingSlits = [slit1, slit2]

    Axi = ModelAxi('test', 0.9, [2], [0.9])

    bitter = Bitter('B', [1,2], [-1, 1], True, Axi, coolingSlits, tierod)
    bitter.dump()

    with open("B.yaml", 'r') as f:
        bitter = yaml.load(f, Loader=yaml.FullLoader)

    print(bitter)
    for i,slit in enumerate(bitter.coolingslits):
        print(f'slit[{i}]: {slit}, shape={slit.shape}')

