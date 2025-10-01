#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Supra:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""
from typing import Optional

import json
import yaml

from .SupraStructure import HTSinsert

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Supra(YAMLObjectBase):
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
        self, name: str, r: list[float], z: list[float], n: int = 0, struct: str = ""
    ) -> None:
        """
        initialize object
        """
        # General validation
        GeometryValidator.validate_name(name)
        
        GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        
        GeometryValidator.validate_numeric_list(z, "z", expected_length=2) 
        GeometryValidator.validate_ascending_order(z, "z")
       
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.struct = struct
        self.detail = "None"  # ['None', 'dblpancake', 'pancake', 'tape']

    def get_magnet_struct(self, directory: Optional[str] = None) -> HTSinsert:
        return HTSinsert.fromcfg(self.struct, directory)

    def check_dimensions(self, magnet: HTSinsert):
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

    def get_lc(self):
        if self.detail == "None":
            return (self.r[1] - self.r[0]) / 5.0
        else:
            hts = self.get_magnet_struct()
            return hts.get_lc()

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list:
        return []

    def get_isolants(self, mname: str, debug: bool = False):
        """
        return isolants
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        return names for Markers
        """

        if self.detail == "None":
            prefix = ""
            if mname:
                prefix = f"{mname}_"
            return [f"{prefix}{self.name}"]
        else:
            hts = self.get_magnet_struct()
            self.check_dimensions(hts)

            return hts.get_names(mname=mname, detail=self.detail, verbose=verbose)

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

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]
        n = values.get("n", 0)
        struct = values.get("struct", '')
        object = cls(name, r, z, n, struct)
        """
        # TODO: if struct load r,z and n from struct data
        # or at least check that values are valid
        if self.struct:
            magnet = self.get_magnet_struct()
            self.check_dimensions(magnet)
        """
        return object

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

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """

        (r_i, z_i) = self.boundingBox()

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])

        return r_overlap and z_overlap


    # def getFillingFactor(self) -> float:
    #     # self.detail = "None"  # ['None', 'dblpancake', 'pancake', 'tape']
    #     if self.detail == "None":
    #         return 1/self.get_Nturns()
    #     # else:
    #     #     # load HTSinsert
    #     #     # return fillingfactor according to self.detail:
    #     #     # aka tape.getFillingFactor() with tape = HTSinsert.tape when detail == "tape"

