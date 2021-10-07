#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Site:

"""

import json
import yaml
from . import deserialize

class Site(yaml.YAMLObject):
    """
    name :
    magnets : dict holding magnet list ("insert", "Bitter", "Supra")
    """

    yaml_tag = 'Site'

    def __init__(self, name='', magnets={}):
        """
        initialize onject
        """
        self.name = name
        self.magnets = magnets
        
    def __repr__(self):
        """
        representation of object
        """
        return "%(name=%r, magnets=%r)" % \
            (self.name,
             self.magnets)

    
    def dump(self):
        """
        dump object to file
        """
        try:
            ostream = open(self.name + '.yaml', 'w')
            yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to dump Site data")

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
            raise Exception("Failed to load Site data %s.yaml"%self.name)

        self.name = data.name
        self.magnets = data.magnets

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


def Site_constructor(loader, node):
    """
    build an site object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    magnets = values["magnets"]
    return Site(name, magnets)

yaml.add_constructor(u'!Site', Site_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the site model to be stored", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    args = parser.parse_args()

    if not args.name:
        magnets = {}
        magnets["insert"] = "HL-31"
        magnets["bitter"] = ["Bint", "Bext"]
        magnets["insert"] = "Hybride"
        site = Site("Test_Site", magnets)
        site.dump()
    else:
        with  open(args.name, 'r') as f:
            site = yaml.load(f)
            print (site)

    if args.tojson:
        rsite.write_to_json()
