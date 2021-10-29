#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

import json
import yaml
from . import deserialize

from . import Shape
from . import ModelAxi
from . import Model3D

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

    def gmsh(self, debug=False):
        """
        create gmsh geometry
        """
        import gmsh

       
        # TODO get axi model
        gmsh_ids = []
        x = self.r[0]
        dr = self.r[1] - self.r[0]
        y = -self.axi.h
        
        _id = gmsh.model.occ.addRectangle(self.r[0], self.z[0], 0, dr, y-self.z[0])
        gmsh_ids.append(_id)

        for i, (n, pitch) in enumerate(zip(self.axi.turns, self.axi.pitch)):
            dz = n * pitch
            _id = gmsh.model.occ.addRectangle(x, y, 0, dr, dz)
            gmsh_ids.append(_id)
                
            y += dz

        _id = gmsh.model.occ.addRectangle(self.r[0], y, 0, dr, self.z[1]-y)
        gmsh_ids.append(_id)

        if debug:
            print("gmsh_ids:", len(gmsh_ids))
            for i in gmsh_ids:
                print(i)

        return gmsh_ids

    def gmsh_bcs(self, name, ids, debug=False):
        """
        retreive ids for bcs in gmsh geometry
        """

        import gmsh
        
        # set physical name
        for i,id in enumerate(ids):
            ps = gmsh.model.addPhysicalGroup(2, [id])
            gmsh.model.setPhysicalName(2, ps, "%s_Cu%d" % (name, i))
        
        # get BC ids
        gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

        eps = 1.e-3
        # TODO: if z[xx] < 0 multiply by 1+eps to get a min by 1-eps to get a max
        zmin = self.z[0]* (1+eps)
        zmax = self.z[1]* (1+eps)
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), zmin, 0,
                                                 self.r[0]* (1+eps), zmax, 0, 1)
        r0_bc_ids = [tag for (dim,tag) in ov]

        ov = gmsh.model.getEntitiesInBoundingBox(self.r[1]* (1-eps), zmin, 0,
                                                 self.r[1]* (1+eps), zmax, 0, 1)
        r1_bc_ids = [tag for (dim,tag) in ov]

        return (r0_bc_ids, r1_bc_ids)

    
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

