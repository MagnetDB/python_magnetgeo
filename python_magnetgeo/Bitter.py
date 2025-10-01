#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Bitter:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""


from .ModelAxi import ModelAxi
from .tierod import Tierod
from .coolingslit import CoolingSlit

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Bitter(YAMLObjectBase):
    """
    name :
    r :
    z :

    axi :
    coolingslits: [(r, angle, n, dh, sh, contour2d)]
    tierods: [r, n, contour2d]
    """

    yaml_tag = "Bitter"

    def __init__(
        self,
        name,
        r: list[float],
        z: list[float],
        odd: bool,
        modelaxi,
        coolingslits: list = None,
        tierod: Tierod = None,
        innerbore: float = 0,
        outerbore: float = 0,
    ) -> None:
        """
        initialize object
        """
        
        # Validate inputs
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")
        
        GeometryValidator.validate_numeric_list(z, 'z', expected_length=2)
        GeometryValidator.validate_ascending_order(z, "z")
        
        # Additional Ring-specific checks
        if r[0] < 0:
            raise ValidationError("Inner radius cannot be negative") 
        
        self.name = name
        self.r = r
        self.z = z
        self.odd = odd
        if isinstance(modelaxi, str):
            self.modelaxi = ModelAxi.from_yaml(f"{modelaxi}.yaml")
        else:
            self.modelaxi = modelaxi
        
        self.innerbore = innerbore
        self.outerbore = outerbore

        self.coolingslits = []
        for coolingslit in coolingslits:
            if isinstance(coolingslit, str):
                self.coolingslits.append(CoolingSlit.from_yaml(f"{coolingslit}.yaml"))
            else:
                self.coolingslits.append(coolingslit)
                
        if isinstance(tierod, str):
            self.tireod = Tierod.from_yaml(f"{tierod}.yaml")
        else:
            self.tierod = tierod

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, r=%r, z=%r, odd=%r, axi=%r, coolingslits=%r, tierod=%r, innerbore=%r, outerbore=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.odd,
                self.modelaxi,
                self.coolingslits,
                self.tierod,
                self.innerbore,
                self.outerbore,
            )
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from yaml
        """
        modelaxi = cls._load_nested_modelaxi(values.get('modelaxi'), debug=debug)
        coolingslits = cls._load_nested_coolingslits(values.get('coolingslits'), debug=debug)
        tierod = cls._load_nested_tierod(values.get('tierod'), debug=debug)

        name = values["name"]
        r = values["r"]
        z = values["z"]
        odd = values["odd"]
        # modelaxi = values["modelaxi"]
        # coolingslits = values.get("coolingslits", [])
        # tierod = values.get("tierod", None)
        innerbore = values.get("innerbore", 0)
        outerbore = values.get("outerbore", 0)

        object = cls(name, r, z, odd, modelaxi, coolingslits, tierod, innerbore, outerbore)
        return object

    @classmethod  
    def _load_nested_modelaxi(cls, modelaxi_data, debug=False):
        if isinstance(modelaxi_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("modelaxi", modelaxi_data, ModelAxi, ModelAxi.from_yaml)
        elif isinstance(modelaxi_data, dict):
            # Inline object → create from dict
            return ModelAxi.from_dict(modelaxi_data)
        else:
            # None or already instantiated
            return modelaxi_data

    @classmethod  
    def _load_nested_coolingslits(cls, coolingslits_data, debug=False):
        """Load list of CoolingSlit objects from various input formats and track references"""
        if coolingslits_data is None:
            return []
        
        if not isinstance(coolingslits_data, list):
            raise TypeError(f"coolingslits must be a list, got {type(coolingslits_data)}")
        
        objects = []
        references = []
        for i, slit_data in enumerate(coolingslits_data):
            if isinstance(slit_data, str):
                # String reference → load from "slit_data.yaml" and track reference
                if debug:
                    print(f"Loading CoolingSlit[{i}] from file: {slit_data}")
                from .utils import loadObject
                obj = loadObject("coolingslit", slit_data, CoolingSlit, CoolingSlit.from_yaml)
                objects.append(obj)
            elif isinstance(slit_data, dict):
                # Inline object → create from dict, no reference to track
                if debug:
                    print(f"Creating CoolingSlit[{i}] from inline dict: {slit_data.get('name', 'unnamed')}")
                obj = CoolingSlit.from_dict(slit_data)
                objects.append(obj)
            else:
                # Already instantiated or None
                objects.append(slit_data)
                references.append(None)  # No string reference
        
        return objects

    @classmethod  
    def _load_nested_tierod(cls, tierod_data, debug=False):
        if isinstance(tierod_data, str):
            # String reference → load from "modelaxi_data.yaml"
            from .utils import loadObject
            return loadObject("modelaxi", tierod_data, Tierod, Tierod.from_yaml)
        elif isinstance(tierod_data, dict):
            # Inline object → create from dict
            return Tierod.from_dict(tierod_data)
        else:
            # None or already instantiated
            return tierod_data


    def equivalent_eps(self, i: int):
        """
        eps: thickness of annular ring equivalent to n * coolingslit surface
        """
        from math import pi

        slit = self.coolingslits[i]
        x = slit.r
        eps = slit.n * slit.sh / (2 * pi * x)
        return eps

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list[str]:
        """
        return channels
        """
        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Channels = [f"{prefix}Slit{0}"]
        n_slits = 0
        if self.coolingslits:
            n_slits = len(self.coolingslits)
            print(f"Bitter({self.name}): CoolingSlits={n_slits}")

            Channels += [f"{prefix}Slit{i+1}" for i in range(n_slits)]
        Channels += [f"{prefix}Slit{n_slits+1}"]
        print(f"Bitter({prefix}): {Channels}")
        return Channels

    def get_lc(self) -> float:
        lc = (self.r[1] - self.r[0]) / 10.0
        if self.coolingslits:
            x: float = self.r[0]
            dr: list[float] = []
            for slit in self.coolingslits:
                _x = slit.r
                dr.append(_x - x)
                x = _x
            dr.append(self.r[1] - x)
            # print(f"Bitter: dr={dr}")
            lc = min(dr) / 5.0

        return lc

    def get_isolants(self, mname: str, debug: bool = False) -> list[str]:
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
        tol = 1.0e-10
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Nslits = 0
        if self.coolingslits:
            Nslits = len(self.coolingslits)

        if is2D:
            nsection = len(self.modelaxi.turns)
            if self.z[0] < -self.modelaxi.h and abs(self.z[0] + self.modelaxi.h) >= tol:
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B0_Slit{i}")

            for j in range(nsection):
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B{j+1}_Slit{i}")

            if self.z[1] > self.modelaxi.h and abs(self.z[1] - self.modelaxi.h) >= tol:
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B{nsection+1}_Slit{i}")
        else:
            solid_names.append(f"{prefix}B")
            solid_names.append(f"{prefix}Kapton")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return self.modelaxi.get_Nturns()

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """

        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """

        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        
        return r_overlap and z_overlap


    def get_params(self, workingDir: str = ".") -> tuple:
        from math import pi

        tol = 1.0e-10

        Dh = [2 * (self.r[0] - self.innerbore)]
        Sh = [pi * (self.r[0] - self.innerbore) * (self.r[0] + self.innerbore)]
        filling_factor = [1]
        nslits = 0
        if self.coolingslits:
            nslits = len(self.coolingslits)
            Dh += [slit.dh for slit in self.coolingslits]
            # Dh += [2 * self.equivalent_eps(n) for n in range(len(self.coolingslits))]
            Sh += [slit.n * slit.sh for slit in self.coolingslits]

            # wetted perimeter per slit: (4*slit.sh)/slit.dh
            # wetted perimeter for annular ring: 2*pi*(slit.r-eps) + 2*pi*(slit.r+eps)
            # with eps = self.equivalent_eps(n)
            filling_factor += [
                slit.n * ((4 * slit.sh) / slit.dh) / (4 * pi * slit.r)
                for slit in self.coolingslits
            ]
        Dh += [2 * (self.outerbore - self.r[1])]
        Sh += [pi * (self.outerbore - self.r[1]) * (self.outerbore + self.r[1])]

        Zh = [self.z[0]]
        z = -self.modelaxi.h
        if abs(self.z[0] - z) >= tol:
            Zh.append(z)
        for n, p in zip(self.modelaxi.turns, self.modelaxi.pitch):
            z += n * p
            Zh.append(z)
        if abs(self.z[1] - z) >= tol:
            Zh.append(self.z[1])
        print(f"Zh={Zh}")

        filling_factor.append(1)
        print(f"filling_factor={filling_factor}")

        # return (nslits, Dh, Sh, Zh)
        return (nslits, Dh, Sh, Zh, filling_factor)

    def create_cut(self, format: str):
        """
        create cut files
        """
        from .hcuts import create_cut

        create_cut(self, format, self.name)

