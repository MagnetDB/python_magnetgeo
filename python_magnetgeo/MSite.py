#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Site:

"""

from .Insert import Insert
from .Bitter import Bitter
from .Supra import Supra
from .utils import getObject

from typing import Union, Optional, List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class MSite(YAMLObjectBase):
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
        # Validate inputs
        GeometryValidator.validate_name(name)
        
        self.name = name

        self.magnets = []
        for magnet in magnets:
            if isinstance(magnet, str):
                magnets.append(getObject(f"{magnet}.yaml"))
            else:
                self.magnets.append(magnet)

        # FIX: Keep None values as None instead of converting to empty lists
        self.screens = []
        if screens is not None:
            for screen in screens:
                if isinstance(screen, str):
                    self.screens.append(getObject(f"{screen}.yaml"))
                else:
                    self.screens.append(screen)

        self.z_offset = z_offset  
        self.r_offset = r_offset
        self.paralax = paralax

        # check that magnets are not intersecting
        for i in range(1, len(self.magnets)):
            rb, zb = self.magnets[i - 1].boundingBox()
            for j in range(i+1, len(self.magnets)):
                if self.magnets[i].intersect(rb, zb):
                    raise ValidationError(
                        f"magnets intersect: magnet[{i}] intersect magnet[{i-1}]: /n{self.magnets[i]} /n{self.magnets[i-1]}"
                    )   

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

    def get_magnet(self, name: str) -> Optional[Union[Insert, Bitter, Supra]]:
        """
        get magnet by name
        """
        for magnet in self.magnets:
            if magnet.name == name:
                return magnet
        return None

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        magnets = cls._load_nested_magnets(values.get('magnets'), debug=debug)
        screens = cls._load_nested_screens(values.get('screens'), debug=debug)  # NEW: Load screens

        name = values["name"]
        magnets = values["magnets"]
        # FIX: Use get() with None default instead of empty list default
        screens = values.get("screens", None)
        z_offset = values.get("z_offset", None)
        r_offset = values.get("r_offset", None)
        paralax = values.get("paralax", None)
        return cls(name, magnets, screens, z_offset, r_offset, paralax)

    @classmethod
    def _load_nested_magnets(cls, magnets_data, debug=False):   
        """
        Helper method to load nested magnets from dict or list
        """
        if magnets_data is None:
            return []
        elif isinstance(magnets_data, list):
            magnets = []
            for item in magnets_data:
                if isinstance(item, dict):
                    magnet = cls._load_single_magnet(item, debug)
                    magnets.append(magnet)
                elif isinstance(item, (Insert, Bitter, Supra)):
                    magnets.append(item)
                else:
                    raise ValidationError("Each magnet must be a dictionary")
            return magnets
        elif isinstance(magnets_data, dict):
            return [cls._load_single_magnet(magnets_data, debug)]
        else:
            raise ValidationError("Magnets must be a list or a dictionary")
        
    @classmethod
    def _load_nested_screens(cls, screens_data, debug=False):
        """
        Helper method to load nested screens from dict or list
        """
        if screens_data is None:
            return None
        elif isinstance(screens_data, list):
            screens = []
            for item in screens_data:
                if isinstance(item, dict):
                    screen = cls._load_single_screen(item, debug)
                    screens.append(screen)
                else:
                    raise ValidationError("Each screen must be a dictionary")
            return screens
        elif isinstance(screens_data, dict):
            return [cls._load_single_screen(screens_data, debug)]
        else:
            raise ValidationError("Screens must be a list or a dictionary") 
        
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

