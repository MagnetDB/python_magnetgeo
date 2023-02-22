#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Supra:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""
from typing import List, Type

import json
import yaml
from . import deserialize

from . import SupraStructure


class Supra(yaml.YAMLObject):
    """
    name :
    r :
    z :
    n :
    struct:

    TODO: to link with SuperEMFL geometry.py
    """

    yaml_tag = "Supra"

    def __init__(
        self, name: str, r: List[float], z: List[float], n: int = 0, struct: str = ""
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.struct = struct
        self.detail = "None"  # ['None', 'dblpancake', 'pancake', 'tape']

    def get_magnet_struct(self) -> SupraStructure.HTSinsert:
        return SupraStructure.HTSinsert.fromcfg(self.struct)

    def check_dimensions(self, magnet: SupraStructure.HTSinsert):
        # TODO: if struct load r,z and n from struct data
        if self.struct:
            changed = False
            if self.r[0] != magnet.getR0():
                changed = True
                self.r[0] = magnet.getR0()
            if self.r[1] != magnet.getR1():
                changed = True
                self.r[1] = magnet.getR1()
            if self.z[0] != magnet.getZ0() - magnet.getH() / 2.0:
                changed = True
                self.z[0] = magnet.getZ0() - magnet.getH() / 2.0
            if self.z[1] != magnet.getZ0() + magnet.getH() / 2.0:
                changed = True
                self.z[1] = magnet.getZ0() + magnet.getH() / 2.0
            if self.n != sum(magnet.getNtapes()):
                changed = True
                self.n = sum(magnet.getNtapes())

            if changed:
                print(
                    f"Supra/check_dimensions: override dimensions for {self.name} from {self.struct}"
                )
                print(self)

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list:
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

        if self.detail == "None":
            solid_names.append(f"{prefix}{self.name}")
        else:
            hts = self.get_magnet_struct()
            self.check_dimensions(hts)

            n_dp = len(hts.dblpancakes)
            cadname = f"{prefix}{self.name}"
            for i, dp in enumerate(hts.dblpancakes):
                dp_name = f"{cadname}_dp{i}"
                if self.detail == "dblpancake":
                    solid_names.append(f"{dp_name}")

                if self.detail == "pancake":
                    solid_names.append(f"{dp_name}_p0")
                    solid_names.append(f"{dp_name}_i")
                    solid_names.append(f"{dp_name}_p1")
                if self.detail == "tape":
                    solid_names.append(f"{dp_name}_p0_Mandrin")
                    for j in range(dp.pancake.n):
                        solid_names.append(f"{dp_name}_p0_t{j}_SC")
                        solid_names.append(f"{dp_name}_p0_t{j}_Duromag")
                    solid_names.append(f"{dp_name}_i")
                    solid_names.append(f"{dp_name}_p1_Mandrin")
                    for j in range(dp.pancake.n):
                        solid_names.append(f"{dp_name}_p1_t{j}_SC")
                        solid_names.append(f"{dp_name}_p1_t{j}_Duromag")
                if i != n_dp - 1:
                    solid_names.append(f"{cadname}_i{i}")

        if verbose:
            print(f"Supra_Gmsh: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r, n=%d, struct=%r, detail=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
            self.n,
            self.struct,
            self.detail,
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Supra dump")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Supra data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.n = data.n
        self.struct = data.struct
        self.detail = data.detail

        # TODO: if struct load r,z and n from struct data
        # or at least check that values are valid
        if self.struct:
            magnet = self.get_magnet_struct()
            self.check_dimensions(magnet)

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

    def get_Nturns(self) -> int:
        """
        returns the number of turn
        """
        if not self.struct:
            return self.n
        else:
            print("shall get nturns from %s" % self.struct)
            return -1

    def set_Detail(self, detail: str) -> None:
        """
        returns detail level
        """
        if detail in ["None", "dblpancake", "pancake", "tape"]:
            self.detail = detail
        else:
            raise Exception(
                f"Supra/set_Detail: unexpected detail value (detail={detail}) : valid values are: {['None', 'dblpancake', 'pancake', 'tape']}"
            )

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
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


def Supra_constructor(loader, node):
    """
    build an supra object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    n = values["n"]
    struct = values["struct"]

    return Supra(name, r, z, n, struct)


yaml.add_constructor("!Supra", Supra_constructor)
