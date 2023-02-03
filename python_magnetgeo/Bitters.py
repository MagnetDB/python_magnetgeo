#!/usr/bin/env python3
# encoding: UTF-8

"""defines Bitter Insert structure"""

import datetime
import json
import yaml
from . import deserialize

class Bitters(yaml.YAMLObject):
    """
    name :
    magnets :

    innerbore:
    outerbore:
    """

    yaml_tag = 'Bitters'

    def __init__(self, name: str, magnets: list, innerbore=None, outerbore=None):
        """constructor"""
        self.name = name
        self.amgnets = magnets
        self.innerbore = innerbore
        self.outerbore = outerbore

    def __repr__(self):
        """representation"""
        return "%s(name=%r, magnets=%r, innerbore=%r, outerbore=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.magnets,
                self.innerbore,
                self.outerbore)

    def dump(self):
        """dump to a yaml file name.yaml"""
        try:
            ostream = open(f'{self.name}.yaml', 'w')
            yaml.dump(self, stream=ostream)
            ostream.close()
        except:
            raise Exception("Failed to Bitters dump")

    def load(self):
        """load from a yaml file"""
        data = None
        try:
            istream = open(f'{self.name}.yaml', 'r')
            data = yaml.load(stream=istream)
        except:
            raise Exception(f"Failed to load Insert data {self.name}.yaml")

        self.name = data.name
        self.magnets = data.magnets

        self.innerbore = data.innerbore
        self.outerbore = data.outerbore

    def to_json(self):
        """convert from yaml to json"""
        return json.dumps(self, default=deserialize.serialize_instance, \
            sort_keys=True, indent=4)

    def from_json(self, string):
        """get from json"""
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """write to a json file"""
        ostream = open(f'{self.name}.json', 'w')
        jsondata = self.to_json()
        ostream.write(str(jsondata))
        ostream.close()

    def read_from_json(self):
        """read from a json file"""
        istream = open(f'{self.name}.json', 'r')
        jsondata = self.from_json(istream.read())
        istream.close()

    ###################################################################
    #
    #
    ###################################################################

    def boundingBox(self):
        """
        return Bounding as r[], z[]

        so far exclude Leads
        """

        rb = [0, 0]
        zb = [0, 0]

        for i, mname in enumerate(self.magnets):
            bitter = None
            with open(f'{mname}.yaml', 'r') as f:
                bitter = yaml.load(f, Loader=yaml.FullLoader)

            if i == 0:
                rb = bitter.r
                zb = bitter.z

            rb[0] = min(rb[0], bitter.r[0])
            zb[0] = min(zb[0], bitter.z[0])
            rb[1] = max(rb[1], bitter.r[1])
            zb[1] = max(zb[1], bitter.z[1])

        return (rb, zb)

    def intersect(self, r, z):
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """

        (r_i, z_i) = self.boundingBox()

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(r_i[0] - r[0]) < abs(r_i[1]-r_i[0] + r[0] + r[1]) /2.
        isZ = abs(z_i[0] - z[0]) < abs(z_i[1]-z_i[0] + z[0] + z[1]) /2.
        if isR and isZ:
            collide = True
        return collide

    def gmsh(self, AirData=None, debug: bool = False):
        """
        create gmsh geometry
        """
        pass

    def gmsh_bcs(self, ids: tuple, debug: bool = False):
        """
        retreive ids for bcs in gmsh geometry
        """
        pass

    def gmsh_msh(self, defs: dict, lc: list):
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

    def Create_AxiGeo(self, AirData):
        """
        create Axisymetrical Geo Model for gmsh

        return
        H_ids, BC_ids, Air_ids, BC_Air_ids
        """
        pass

def Bitters_constructor(loader, node):
    values = loader.construct_mapping(node)
    name = values["name"]
    magnets = values["magnets"]
    innerbore = 0
    if "innerbore":
        innerbore = values["innerbore"]
    innerbore = 0
    if "outerbore":
        outerbore = values["outerbore"]
    return Bitters(name, magnets, innerbore, outerbore)

yaml.add_constructor(u'!Bitters', Bitters_constructor)
