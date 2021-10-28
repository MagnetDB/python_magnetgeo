#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Supra:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""

import json
import yaml
from . import deserialize

from . import ModelAxi

class Supra(yaml.YAMLObject):
    """
    name :
    r :
    z :

    TODO: to link with SuperEMFL geometry.py
    """

    yaml_tag = 'Supra'

    def __init__(self, name, r=[], z=[]):
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.r,
                self.z
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
            raise Exception("Failed to Supra dump")

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
            raise Exception("Failed to load Supra data %s.yaml"%self.name)

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.axi = data.axi

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(self, default=deserialize.serialize_instance, sort_keys=True, indent=4)


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

    def get_Nturns(self):
        """
        returns the number of turn
        """
        return self.axi.get_Nturns()

    def gmsh(self, Air=False, debug=False):
        """
        create gmsh geometry
        """
        import gmsh

        _id = gmsh.model.occ.addRectangle(self.r[0], self.z[0], 0, self.r[1]-self.r[0], self.z[1]-self.z[0])

        # Now create air
        if Air:
            r0_air = 0
            dr_air = self.r[1] * 2
            z0_air = self.z[0] * 1.2
            dz_air = (self.z[1]-self.z[0]) * 2
            A_id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
            ov, ovv = gmsh.model.occ.fragment([(2, A_id)], [(2, _id)] )
            return (_id, (A_id, dr_air, z0_air, dz_air))

        return (_id, None)

    def gmsh_bcs(self, ids: tuple, debug=False):
        """
        retreive ids for bcs in gmsh geometry
        """
        import gmsh
        
        (id, Air_data) = ids

        # set physical name
        ps = gmsh.model.addPhysicalGroup(2, [id])
        gmsh.model.setPhysicalName(2, ps, "%s_S" % self.name)
        
        # get BC ids
        gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

        eps = 1.e-3
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (self.z[0])* (1+eps), 0,
                                                 self.r[-1]* (1+eps), (self.z[0])* (1-eps), 0, 1)
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_HP" % self.name)
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (self.z[-1])* (1-eps), 0,
                                                 self.r[-1]* (1+eps), (self.z[-1])* (1+eps), 0, 1)
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_BP" % self.name)

        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), self.z[0]* (1+eps), 0,
                                                 self.r[0]* (1+eps), self.z[1]* (1+eps), 0, 1)
        r0_bc_ids = [tag for (dim,tag) in ov]
        if debug:
            print("r0_bc_ids:", len(r0_bc_ids), 
                     self.r[0]* (1-eps), self.z[0]* (1-eps),
                     self.r[0]* (1+eps), self.z[1]* (1+eps))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_Rint" % self.name)

        ov = gmsh.model.getEntitiesInBoundingBox(self.r[1]* (1-eps), self.z[0]* (1+eps), 0,
                                                 self.r[1]* (1+eps), self.z[1]* (1+eps), 0, 1)
        r1_bc_ids = [tag for (dim,tag) in ov]
        if debug:
            print("r1_bc_ids:", len(r1_bc_ids))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_Rext" % self.name)
        
        # TODO: Air
        if Air_data:
            (Air_id, dr_air, z0_air, dz_air) = Air_data

            ps = gmsh.model.addPhysicalGroup(2, [Air_id])
            gmsh.model.setPhysicalName(2, ps, "Air")

            # TODO: Axis, Inf
            gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)
            
            eps = 1.e-6
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, +eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Axis")
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, dr_air+eps, z0_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(dr_air-eps, z0_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(-eps, z0_air+dz_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Inf")            

        pass
    
def Supra_constructor(loader, node):
    """
    build an supra object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]

    return Supra(name, r, z)

yaml.add_constructor(u'!Supra', Supra_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the supra model to be stored", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    args = parser.parse_args()

    if not args.name:
        supra = Supra("ttt", [1, 2],[-1, 1], True)
        supra.dump()
    else:
        with open(args.name, 'r') as f:
            supra =  yaml.load(f, Loader = yaml.FullLoader)
            print (supra)

    if args.tojson:
        supra.write_to_json()
