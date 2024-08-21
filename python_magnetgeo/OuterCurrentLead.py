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

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load OuterCurrentLead data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.h = data.h
        self.bar = data.bar
        self.support = data.support

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
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'OuterCurrentLead.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)
    

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


yaml.add_constructor("!OuterCurrentLead", OuterCurrentLead_constructor)


