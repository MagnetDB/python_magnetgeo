#!/usr/bin/env python3
# encoding: UTF-8

"""defines Supra Insert structure"""


from .Supra import Supra

# Add import at the top
from .Probe import Probe

dict_probes = {
    "Probe": Probe.from_dict,
}

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Supras(YAMLObjectBase):
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

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        magnets = cls._load_nested_magnets(values.get('magnets'), debug=debug)
        probes = cls._load_nested_probes(values.get('probes'), debug=debug)  # NEW: Load probes 

        name = values["name"]
        # magnets = values["magnets"]        
        
        innerbore = values["innerbore"] if "innerbore" in values else 0
        outerbore = values["outerbore"] if "outerbore" in values else 0
        # probes = values.get("probes", [])  # NEW: Optional with default empty list
        object = cls(name, magnets, innerbore, outerbore, probes)        
        return object
    
    @classmethod
    def _load_nested_magnets(cls, magnets_data, debug=False) -> List[Supra]:
        """Load nested Supra objects from data"""
        magnets = []
        if magnets_data:
            for item in magnets_data:
                if isinstance(item, Supra):
                    magnets.append(item)
                elif isinstance(item, dict):
                    magnets.append(Supra.from_dict(item, debug=debug))
                elif isinstance(item, Supra):
                    magnets.append(item)
                else:
                    raise ValidationError(f"Invalid magnet entry: {item}")
        return magnets
    
    @classmethod
    def _load_nested_probes(cls, probes_data, debug=False) -> List[Probe]:
        """Load nested Probe objects from data"""
        probes = []
        if probes_data:
            for item in probes_data:
                if isinstance(item, Probe):
                    probes.append(item)
                elif isinstance(item, dict):
                    probes.append(Probe.from_dict(item, debug=debug))
                else:
                    raise ValidationError(f"Invalid probe entry: {item}")
        return probes
    
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

        r_overlap = max(r_i[0], r[0]) < min(r_i[1], r[1])
        z_overlap = max(z_i[0], z[0]) < min(z_i[1], z[1])
        
        return r_overlap and z_overlap

