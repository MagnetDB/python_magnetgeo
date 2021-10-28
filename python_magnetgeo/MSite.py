#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Site:

"""

import os
import sys

import json
import yaml
from . import deserialize

class MSite(yaml.YAMLObject):
    """
    name :
    magnets : dict holding magnet list ("insert", "Bitter", "Supra")
    """

    yaml_tag = 'MSite'

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
        return "%(name)s, %(magnets)s" % \
            {'name': self.name, 'magnets':self.magnets}

    
    def dump(self):
        """
        dump object to file
        """
        try:
            ostream = open(self.name + '.yaml', 'w')
            yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to dump MSite data")

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
            raise Exception("Failed to load MSite data %s.yaml"%self.name)

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

    def gmsh(self, Air: bool =False, debug: bool =False):
        """
        create gmsh geometry
        """
        import gmsh

        isAir = False
        gmsh_ids = []

        if isinstance(self.magnets, str):
            print("msite/gmsh/%s (str)" % self.magnets)
            with open(self.magnets + '.yaml', 'r') as f:
                Magnet = yaml.load(f, Loader = yaml.FullLoader)
            gmsh_ids.append( Magnet.gmsh(isAir, debug) )

        elif isinstance(self.magnets, list):
            for mname in self.magnets:
                print("msite/gmsh/%s (list)" % mname)
                with open(mname + '.yaml', 'r') as f:
                    Magnet = yaml.load(f, Loader = yaml.FullLoader)
                gmsh_ids.append( Magnet.gmsh(isAir, debug) )

        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                print("msite/gmsh/%s (dict)" % key)
                if isinstance(self.magnets[key], str):
                    print("msite/gmsh/%s (dict/str)" % self.magnets[key])
                    with open(self.magnets[key] + '.yaml', 'r') as f:
                        Magnet = yaml.load(f, Loader = yaml.FullLoader)
                    gmsh_ids.append( Magnet.gmsh(isAir, debug) )

                if isinstance(self.magnets[key], list):
                    for mname in self.magnets[key]:
                        print("msite/gmsh/%s (dict/list)" % mname)
                        with open(mname + '.yaml', 'r') as f:
                            Magnet = yaml.load(f, Loader = yaml.FullLoader)
                        gmsh_ids.append( Magnet.gmsh(isAir, debug) )

        else:
            print("magnets: unsupported type (%s" % type(self.magnets) )
            sys.exit(1)
        
        # Now create air
        if Air:
            r0_air = 0
            dr_air = 2000
            z0_air = -1000
            dz_air = 2000
            A_id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
            flat_list = []
            print("flat_list:", len(gmsh_ids))
            for sublist in gmsh_ids:
                if not isinstance(sublist, tuple):
                    print("flat_list: expect a tuple got a %s" % type(sublist))
                    sys.exit(1)
                for elem in sublist:
                    print("elem:", elem, type(elem))
                    if isinstance(elem, list):
                        for item in elem:
                            print("item:", elem, type(item))
                            if isinstance(item, list):
                                flat_list += item
                            elif isinstance(item, int):
                                flat_list.append(item)

            print("flat_list:", flat_list)
            ov, ovv = gmsh.model.occ.fragment([(2, A_id)], [(2, i) for i in flat_list] )
            return (gmsh_ids, (A_id, dr_air, z0_air, dz_air))

        return (gmsh_ids, None)

    def gmsh_bcs(self, ids: list, debug: bool =False):
        """
        retreive ids for bcs in gmsh geometry
        """
        import gmsh
        """
        if isinstance(self.magnets, str):
            with open(self.magnets + '.yaml', 'r') as f:
                Magnet = yaml.load(f, Loader = yaml.FullLoader)
            Magnet.gmsh_bcs(ids[0], debug)

        elif isinstance(self.magnets, list):
            for i,mname in enumerate(self.magnets):
                with open(mname + '.yaml', 'r') as f:
                    Magnet = yaml.load(f, Loader = yaml.FullLoader)
                Magnet.gmsh_bcs(ids[i], debug)

        elif isinstance(self.magnets, dict):
            num = 0
            for i,key in enumerate(self.magnets):
                if isinstance(self.magnets[key], str):
                    with open(self.magnets[key] + '.yaml', 'r') as f:
                        Magnet = yaml.load(f, Loader = yaml.FullLoader)
                    Magnet.gmsh_bcs(ids[num], debug)
                    num += 1

                if isinstance(self.magnets[key], list):
                    for mname in self.magnets[key]:
                        with open(mname + '.yaml', 'r') as f:
                            Magnet = yaml.load(f, Loader = yaml.FullLoader)
                        Magnet.gmsh_bcs(ids[num], debug)
                        num += 1

        else:
            print("magnets: unsupported type (%s" % type(self.magnets) )
            sys.exit(1)
        """

        # TODO get BCs
        pass


def MSite_constructor(loader, node):
    """
    build an site object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    magnets = values["magnets"]
    return MSite(name, magnets)

yaml.add_constructor(u'!MSite', MSite_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the site model to be stored", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    
    parser.add_argument("--wd", help="set a working directory", type=str, default="data")
    parser.add_argument("--air", help="activate air generation", action="store_true")
    parser.add_argument("--gmsh_api", help="use gmsh api to create geofile", action="store_true")
    parser.add_argument("--mesh", help="create gmsh mesh ", action="store_true")
    parser.add_argument("--show", help="display gmsh geofile when api is on", action="store_true")
    
    args = parser.parse_args()

    cwd = os.getcwd()
    if args.wd:
        os.chdir(args.wd)

    site = None
    if not args.name:
        magnets = {}
        magnets["insert"] = "HL-31"
        magnets["bitter"] = ["Bint", "Bext"]
        magnets["insert"] = "Hybride"
        site = MSite("Test_Site", magnets)
        site.dump()
    else:
        with  open(args.name+".yaml", 'r') as f:
            site = yaml.load(f, Loader=yaml.FullLoader)
            print("site=",site)

    if args.tojson:
        site.write_to_json()

    if args.gmsh_api:
        import gmsh
        gmsh.initialize()
        gmsh.model.add(args.name)
        gmsh.logger.start()

        ids = site.gmsh(args.air)
        gmsh.model.occ.synchronize()

        # TODO create Physical here
        site.gmsh_bcs(ids)
        # TODO set mesh characteristics here
        if args.mesh:
            gmsh.model.mesh.generate(2)
            gmsh.write(args.name + ".msh")        

        log = gmsh.logger.get()
        print("Logger has recorded " + str(len(log)) + " lines")
        gmsh.logger.stop()
        # Launch the GUI to see the results:
        if args.show:
            gmsh.fltk.run()
        gmsh.finalize()

    if args.wd:
        os.chdir(cwd)

