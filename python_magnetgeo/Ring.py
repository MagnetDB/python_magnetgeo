#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Ring:

"""

import json
import yaml
from . import deserialize

class Ring(yaml.YAMLObject):
    """
    name :
    r :
    z :
    orientation:
    angle :
    BPside :
    fillets :
    """

    yaml_tag = 'Ring'

    def __init__(self, name='', r=[], z=[], n=0, angle=0, BPside=True, fillets=False, orientation=0):
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.BPside = BPside
        self.fillets = fillets
        self.orientation = 0

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r, n=%r, angle=%r, BPside=%r, fillets=%r, orientation=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.n,
                self.angle,
                self.BPside,
                self.fillets,
                self.orientation
               )

    def dump(self):
        """
        dump object to file
        """
        try:
            ostream = open(self.name + '.yaml', 'w')
            yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to dump Ring data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            istream = open(self.name + '.yaml', 'r')
            data = yaml.load(stream=istream)
            istream.close()
        except:
            raise Exception("Failed to load Ring data %s.yaml"%self.name)

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.n = data.n
        self.angle = data.angle
        self.BPside = data.BPside
        self.fillets = data.fillets
        self.orientation = data.orientation

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(self, default=deserialize.serialize_instance, \
            sort_keys=True, indent=4)

    def from_json(self, string):
        """
        convert from json to yaml
        """
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """
        write from json file
        """
        ostream = open(self.name + '.json', 'w')
        jsondata = self.to_json()
        ostream.write(str(jsondata))
        ostream.close()

    def read_from_json(self):
        """
        read from json file
        """
        istream = open(self.name + '.json', 'r')
        jsondata = self.from_json(istream.read())
        print (type(jsondata))
        istream.close()


def Ring_constructor(loader, node):
    """
    build an ring object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    n = values["n"]
    angle = values["angle"]
    BPside = values["BPside"]
    fillets = values["fillets"]
    orientation = values["orientation"]
    return Ring(name, r, z, n, angle, BPside, fillets, orientation)

yaml.add_constructor(u'!Ring', Ring_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the ring model to be stored", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    args = parser.parse_args()

    if not args.name:
        ring = Ring("Test_Ring", [19.3, 24.2, 25.1, 30.7], [0, 20], 6, 30, True, False)
        ring.dump()
    else:
        try:
            ring = yaml.load(open(args.name, 'r'))
            print (ring)
        except:
            print ("Failed to load Ring definition from %s" % args.name)

    if args.tojson:
        ring.write_to_json()
