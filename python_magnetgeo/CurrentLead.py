#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides Inner and OuterCurrentLead class
"""

import json
import yaml


class InnerCurrentLead(yaml.YAMLObject):
    """
    name :
    r : [R0, R1]
    h :
    holes: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
    support: [R2, DZ]
    fillet:
    """

    yaml_tag = "InnerCurrentLead"

    def __init__(self, name="None", r=[], h=0.0, holes=[], support=[], fillet=False):
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.h = h
        self.holes = holes
        self.support = support
        self.fillet = fillet

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, h=%r, holes=%r, support=%r, fillet=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.h,
            self.holes,
            self.support,
            self.fillet,
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            yaml.dump(self, open(self._name + ".yaml", "w"))
        except:
            raise Exception("Failed to dump InnerCurrentLead data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            istream = open(self._name + ".yaml", "r")
            data = yaml.load(istream, Loader=yaml.FullLoader)
            istream.close()
        except:
            raise Exception("Failed to load InnerCurrentLead data %s.yaml" % self._name)

        self._name = data.name
        self.r = data.r
        self.h = data.h
        self.holes = data.holes
        self.support = data.support
        self.fillet = data.fillet

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
            ofile = open(self.name + ".json", "w")
            ofile.write(str(jsondata))
            ofile.close()
        except:
            raise Exception(f"Failed to write to {self.name}.json")

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'InnerCurrentLead.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)
    


def InnerCurrentLead_constructor(loader, node):
    """
    build an inner object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    h = values["h"]
    holes = values["holes"]
    support = values["support"]
    fillet = values["fillet"]
    return InnerCurrentLead(name, r, h, holes, support, fillet)


class OuterCurrentLead(yaml.YAMLObject):
    """
    name :

    r : [R0, R1]
    h :
    bar : [R, DX, DY, L]
    support : [DX0, DZ, Angle, Angle_Zero]
    """

    yaml_tag = "OuterCurrentLead"

    def __init__(self, name="None", r=[], h=0.0, bar=[], support=[]):
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
            yaml.dump(self, open(self.name + ".yaml", "w"))
        except:
            raise Exception("Failed to dump OuterCurrentLead data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            istream = open(self.name + ".yaml", "r")
            data = yaml.load(stream=istream, Loader=yaml.FullLoader)
            istream.close()
        except:
            raise Exception("Failed to load OuterCurrentLead data %s.yaml" % self.name)

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
            ofile = open(self.name + ".json", "w")
            ofile.write(str(jsondata))
            ofile.close()
        except:
            raise Exception("Failed to write to %s.json" % self.name)

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


yaml.add_constructor("!InnerCurrentLead", InnerCurrentLead_constructor)
yaml.add_constructor("!OuterCurrentLead", OuterCurrentLead_constructor)
