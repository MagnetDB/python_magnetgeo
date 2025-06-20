#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides Inner and OuterCurrentLead class
"""

import os
import json
import yaml


class OuterCurrentLead(yaml.YAMLObject):
    """
    name :

    r : [R0, R1]
    h :
    bar : [R, DX, DY, L]
    support : [DX0, DZ, Angle, Angle_Zero]

    bar looks like that:
    A rectangle (dx,dy) cut by a disk of R radius centered on Origin X     

    -------------
    | (   x   ) |
    -------------

    create a prism along Oz with legnth L from the result
    bar translated to [r[1] - dx0 + dy/2, 0, 0]

    support:
    rectangle(dx, dx0)
    translated to [r[1] - dx0 + dy/2, 0, 0]
    rectangle cut by a disk of r[1] radius centered on Origin X
    """

    yaml_tag = "OuterCurrentLead"

    def __init__(
        self,
        name: str,
        r: list[float] = [],
        h: float = 0.0,
        bar: list = [],
        support: list = [],
    ) -> None:
        """
        create object
        """
        self.name = name
        self.r = r
        self.h = h
        self.bar = bar
        self.support = support

    def __repr__(self):
        """
        representation object
        """
        return "%s(name=%r, r=%r, h=%r, bar=%r, support=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.h,
            self.bar,
            self.support,
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            yaml.dump(self, open(f"{self.name}.yaml", "w"))
        except:
            raise Exception("Failed to dump OuterCurrentLead data")

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
        jsondata = self.to_json()
        try:
            with open(f"{self.name}.json", "w") as ofile:
                ofile.write(str(jsondata))
        except:
            raise Exception(f"Failed to write to {self.name}.json")

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        h = values["h"]
        bar = values["bar"]
        support = values["support"]
        return cls(name, r, h, bar, support)

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("OuterCurrentLead", filename, OuterCurrentLead, debug)

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("OuterCurrentLead", filename, debug)


def OuterCurrentLead_constructor(loader, node):
    """
    build an outer object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    h = values["h"]
    bar = values["bar"]
    support = values["support"]
    return OuterCurrentLead(name, r, h, bar, support)


yaml.add_constructor(OuterCurrentLead.yaml_tag, OuterCurrentLead_constructor)


