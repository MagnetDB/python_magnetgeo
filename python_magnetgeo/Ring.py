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
    angle :
    BPside :
    fillets :
    """

    yaml_tag = 'Ring'

    def __init__(self, name='', r=[], z=[], n=0, angle=0, BPside=True, fillets=False):
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

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r, n=%r, angle=%r, BPside=%r, fillets=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.n,
                self.angle,
                self.BPside,
                self.fillets
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

    def gmsh(self, x, y, debug=False):
        """
        create gmsh geometry
        """
        import gmsh
        _id = gmsh.model.occ.addRectangle(self.r[0], y+self.z[0], 0, self.r[-1]-self.r[0], self.z[-1]-self.z[0])
        # print("gmsh/Ring:", _id, self.name, self.r, self.z)
        
        return _id

    def gmsh_bcs(self, name: str, hp: bool, y: float, id: int, debug: bool = False):
        """
        create gmsh geometry
        """
        import gmsh
        
        ps = gmsh.model.addPhysicalGroup(2, [id])
        gmsh.model.setPhysicalName(2, ps, name)
        
        # get BC (TODO review to keep on BP or HP)
        gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

        eps = 1.e-3
        if hp:
            ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (y+self.z[0])* (1-eps), 0,
                                                 self.r[-1]* (1+eps), (y+self.z[0])* (1+eps), 0, 1)
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "%s_HP" % name)
        else:
            ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (y+self.z[-1])* (1-eps), 0,
                                                 self.r[-1]* (1+eps), (y+self.z[-1])* (1+eps), 0, 1)
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "%s_BP" % name)
        
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[0]* (1-eps), (y+self.z[0])* (1-eps), 0,
                                                 self.r[0]* (1+eps), (y+self.z[-1])* (1+eps), 0, 1)
        r0_ids = [tag for (dim,tag) in ov]
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[-1]* (1-eps), (y+self.z[0])* (1-eps), 0,
                                                 self.r[-1]* (1+eps), (y+self.z[-1])* (1+eps), 0, 1)
        r1_ids = [tag for (dim,tag) in ov]
        
        # TODO cooling
        ov = gmsh.model.getEntitiesInBoundingBox(self.r[1]* (1-eps), (y+self.z[0])* (1-eps), 0,
                                                 self.r[2]* (1+eps), (y+self.z[-1])* (1+eps), 0, 1)
        slit_ids = [tag for (dim,tag) in ov]
        
        return (r0_ids, r1_ids, slit_ids)        

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
    return Ring(name, r, z, n, angle, BPside, fillets)

yaml.add_constructor(u'!Ring', Ring_constructor)

