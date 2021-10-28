#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Bitter:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""

import json
import yaml
from . import deserialize

from . import ModelAxi

class Bitter(yaml.YAMLObject):
    """
    name :
    r :
    z :

    axi :
    """

    yaml_tag = 'Bitter'

    def __init__(self, name, r=[], z=[], axi=ModelAxi.ModelAxi()):
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.axi = axi

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r, axi=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.axi
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
            raise Exception("Failed to Bitter dump")

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
            raise Exception("Failed to load Bitter data %s.yaml"%self.name)

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

        gmsh_ids = []
        x = self.r[0]
        dr = self.r[1] - self.r[0]
        y = -self.axi.h
        for i, (n, pitch) in enumerate(zip(self.axi.turns, self.axi.pitch)):
            dz = n * pitch
            _id = gmsh.model.occ.addRectangle(x, y, 0, dr, dz)
            gmsh_ids.append(_id)
                
            y += dz
        # Now create air
        if Air:
            r0_air = 0
            dr_air = dr * 2
            z0_air = y * 1.2
            dz_air = (2 * abs(y) ) * 1.2 
            _id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
            ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, i) for i in gmsh_ids] )
            return (gmsh_ids, (_id, dr_air, z0_air, dz_air))

        return (gmsh_ids, None)

def gmsh_bcs(self, ids: tuple, debug=False):
        """
        retreive ids for bcs in gmsh geometry
        """
        import gmsh

        (B_ids, Air_data) = ids

        # set physical name
        for i,id in enumerate(B_ids):
            ps = gmsh.model.addPhysicalGroup(2, [id])
            gmsh.model.setPhysicalName(2, ps, "%s_Cu%d" % (self.name, i))
        
        # get BC ids
        gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

        eps = 1.e-3
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (self.z[0])* (1-eps), 0,
                                                 self.r[-1]* (1+eps), (self.z[0])* (1+eps), 0, 1)
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_HP" % self.name)
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (self.z[-1])* (1-eps), 0,
                                                 self.r[-1]* (1+eps), (self.z[-1])* (1+eps), 0, 1)
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_BP" % self.name)
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), self.z[0]* (1-eps), 0,
                                                 self.r[0]* (1+eps), self.z[1]* (1+eps), 0, 1)
        r0_bc_ids = [tag for (dim,tag) in ov]
        if debug:
            print("r0_bc_ids:", len(r0_bc_ids))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_Rint" % self.name)

        ov = gmsh.model.getEntitiesInBoundingBox(self.r[1]* (1-eps), self.z[0]* (1-eps), 0,
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
    
def Bitter_constructor(loader, node):
    """
    build an bitter object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    axi = values["axi"]

    return Bitter(name, r, z, axi)

yaml.add_constructor(u'!Bitter', Bitter_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the bitter model to be stored", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    args = parser.parse_args()

    if not args.name:
        bitter = Bitter("ttt", [1, 2],[-1, 1], True)
        bitter.dump()
    else:
        with open(args.name, 'r') as f:
            bitter =  yaml.load(f, Loader = yaml.FullLoader)
            print (bitter)

    if args.tojson:
        bitter.write_to_json()
