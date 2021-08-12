#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

import json
import yaml
import deserialize

import Shape
import ModelAxi
import Model3D

class Helix(yaml.YAMLObject):
    """
    name :
    r :
    z :
    cutwidth:
    dble :
    odd :

    axi :
    m3d :
    shape :
    """

    yaml_tag = 'Helix'

    def __init__(self, name, r=[], z=[], cutwidth=0.0, odd=False, dble=False, axi=ModelAxi.ModelAxi(), m3d=Model3D.Model3D(), shape=Shape.Shape()):
        """
        initialize object
        """
        self.name = name
        self.dble = dble
        self.odd = odd
        self.r = r
        self.z = z
        self.cutwidth = cutwidth
        self.axi = axi
        self.m3d = m3d
        self.shape = shape

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, odd=%r, dble=%r, r=%r, z=%r, cutwidth=%r, axi=%r, m3d=%r, shape=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.odd,
                self.dble,
                self.r,
                self.z,
                self.cutwidth,
                self.axi,
                self.m3d,
                self.shape
               )

    def dump(self):
        """
        dump object to file
        """
        try:
            ostream = open(self.name + '.yaml', 'w')
            yaml.dump(self, stream=ostream)
            ostream.close()
        except:
            raise Exception("Failed to Helix dump")

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
            raise Exception("Failed to load Helix data %s.yaml"%self.name)

        self.name = data.name
        self.dble = data.dble
        self.odd = data.odd
        self.r = data.r
        self.z = data.z
        self.cutwidth = data.cutwidth
        self.axi = data.axi
        self.m3d = data.m3d
        self.shape = data.shape

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(self, default=deserialize.serialize_instance, sort_keys=True, indent=4)


    def from_json(string):
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

    def get_Nturns(self):
        """
        returns the number of turn
        """
        return self.axi.get_Nturns()

def Helix_constructor(loader, node):
    """
    build an helix object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    dble = values["dble"]
    cutwidth = values["cutwidth"]
    axi = values["axi"]
    m3d = values["m3d"]
    shape = values["shape"]

    return Helix(name, r, z, cutwidth, odd, dble, axi, m3d, shape)

yaml.add_constructor(u'!Helix', Helix_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the helix model to be stored", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    args = parser.parse_args()

    if not args.name:
        helix = Helix("ttt", [1, 2],[-1, 1], True)
        helix.dump()
    else:
        try:
            helix =  yaml.load(open(args.name, 'r'))
            print (helix)
        except:
            print ("Failed to load Helix definition from %s" % args.name)
        
    if args.tojson:
        helix.write_to_json()
