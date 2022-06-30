#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Screen:

* Geom data: r, z
"""

import os
import sys

import json
import yaml
from yaml.events import CollectionEndEvent
from yaml.nodes import CollectionNode
from . import deserialize


class Screen(yaml.YAMLObject):
    """
    name :
    r :
    z :
    """

    yaml_tag = 'Screen'

    def __init__(self, name: str, r: list =[], z: list =[]):
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
            raise Exception("Failed to Screen dump")

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
            raise Exception("Failed to load Screen data %s.yaml"%self.name)

        self.name = data.name
        self.r = data.r
        self.z = data.z

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

    def boundingBox(self):
        """
        return Bounding as r[], z[]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
        return (self.r, self.z)

    def intersect(self, r, z):
        """
        Check if intersection with rectangle defined by r,z is empty or not
        
        return False if empty, True otherwise
        """
        
        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(self.r[0] - r[0]) < abs(self.r[1]-self.r[0] + r[0] + r[1]) /2.
        isZ = abs(self.z[0] - z[0]) < abs(self.z[1]-self.z[0] + z[0] + z[1]) /2.
        if isR and isZ:
            collide = True
        return collide

    def gmsh(self, AirData=None, debug=False):
        """
        create gmsh geometry
        """

        # TODO: how to specify detail level to actually connect gmsh with struct data

        import gmsh

        _id = gmsh.model.occ.addRectangle(self.r[0], self.z[0], 0, self.r[1]-self.r[0], self.z[1]-self.z[0])

        # Now create air
        if AirData:
            r0_air = 0
            dr_air = self.r[1] * AirData[0]
            z0_air = self.z[0] * AirData[1]
            dz_air = (self.z[1]-self.z[0]) * AirData[1]
            A_id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
            ov, ovv = gmsh.model.occ.fragment([(2, A_id)], [(2, _id)] )
            return (_id, (A_id, dr_air, z0_air, dz_air))

        return (_id, None)

    def gmsh_bcs(self, ids: tuple, debug=False):
        """
        retreive ids for bcs in gmsh geometry
        """
        import gmsh

        defs = {}
        
        (id, Air_data) = ids

        # set physical name
        ps = gmsh.model.addPhysicalGroup(2, [id])
        gmsh.model.setPhysicalName(2, ps, "%s_S" % self.name)
        defs["%s_S" % self.name] = ps

        # get BC ids
        gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

        eps = 1.e-3

        # TODO: if z[xx] < 0 multiply by 1+eps to get a min by 1-eps to get a max
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (self.z[0])* (1+eps), 0,
                                                     self.r[-1]* (1+eps), (self.z[0])* (1-eps), 0, 1)
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_HP" % self.name)
        defs["%s_HP" % self.name] = ps
            
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (self.z[-1])* (1-eps), 0,
                                                     self.r[-1]* (1+eps), (self.z[-1])* (1+eps), 0, 1)
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_BP" % self.name)
        defs["%s_BP" % self.name] = ps

        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), self.z[0]* (1+eps), 0,
                                                     self.r[0]* (1+eps), self.z[1]* (1+eps), 0, 1)
        r0_bc_ids = [tag for (dim,tag) in ov]
        if debug:
            print("r0_bc_ids:", len(r0_bc_ids), 
                         self.r[0]* (1-eps), self.z[0]* (1-eps),
                         self.r[0]* (1+eps), self.z[1]* (1+eps))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_Rint" % self.name)
        defs["%s_Rint" % self.name] = ps

        ov = gmsh.model.getEntitiesInBoundingBox(self.r[1]* (1-eps), self.z[0]* (1+eps), 0,
                                                     self.r[1]* (1+eps), self.z[1]* (1+eps), 0, 1)
        r1_bc_ids = [tag for (dim,tag) in ov]
        if debug:
            print("r1_bc_ids:", len(r1_bc_ids))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "%s_Rext" % self.name)
        defs["%s_Rext" % self.name] = ps
            
        # TODO: Air
        if Air_data:
            (Air_id, dr_air, z0_air, dz_air) = Air_data

            ps = gmsh.model.addPhysicalGroup(2, [Air_id])
            gmsh.model.setPhysicalName(2, ps, "Air")
            defs["Air"] = ps

            # TODO: Axis, Inf
            gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)
            
            eps = 1.e-6
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, +eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "ZAxis")
            defs["ZAxis" % self.name] = ps
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, dr_air+eps, z0_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(dr_air-eps, z0_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(-eps, z0_air+dz_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Infty")            
            defs["Infty" % self.name] = ps

        return defs

    def gmsh_msh(self, defs: dict = {}, lc: list=[]):
        print("TODO: set characteristic lengths")
        """
        lcar = (nougat.getR1() - nougat.R(0) ) / 10.
        lcar_dp = nougat.dblpancakes[0].getW() / 10.
        lcar_p = nougat.dblpancakes[0].getPancake().getW() / 10.
        lcar_tape = nougat.dblpancakes[0].getPancake().getW()/3.

        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar)
        # Override this constraint on the points of the tapes:

        gmsh.model.mesh.setSize(gmsh.model.getBoundary(tapes, False, False, True), lcar_tape)
        """
        pass
    

def Screen_constructor(loader, node):
    """
    build an screen object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]

    return Screen(name, r, z)

yaml.add_constructor(u'!Screen', Screen_constructor)

