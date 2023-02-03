#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

import math
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

    def compact(self):
        def indices(lst, item):
            return [i for i, x in enumerate(lst) if abs(1-item/x) <= 1.e-6]
            
        List = self.axi.pitch
        duplicates = dict((x, indices(List, x)) for x in set(List) if List.count(x) > 1)
        print(f'duplicates: {duplicates}')

        sum_index = {}
        for key in duplicates:
            index_fst = duplicates[key][0]
            sum_index[index_fst] = [index_fst]
            search_index = sum_index[index_fst]
            search_elem = search_index[-1]
            for index in duplicates[key]:
                print(f'index={index}, search_elem={search_elem}')
                if index-search_elem == 1:
                    search_index.append(index)
                    search_elem = index
                else:
                    sum_index[index] = [index]
                    search_index = sum_index[index]
                    search_elem = search_index[-1]
                            
        print(f'sum_index: {sum_index}')
        
        remove_ids = []
        for i in sum_index:
            for item in sum_index[i]:
                if item != i:
                    remove_ids.append(item)

        new_pitch = [p for i,p in enumerate(self.axi.pitch) if not i in remove_ids]
        print(f'new_pitch={new_pitch}')

        new_turns = self.axi.turns # use deepcopy: import copy and copy.deepcopy(self.axi.turns)
        for i in sum_index:
            for item in sum_index[i]:
                new_turns[i] += self.axi.turns[item]
        new_turns = [p for i,p in enumerate(self.axi.turns) if not i in remove_ids]
        print(f'new_turns={new_turns}')

        """
  int t = Magnet_Stack.back();

  MyDouble r1 = Tubes[t].get_R_int();
  MyDouble r2 = Tubes[t].get_R_ext();
  MyDouble h  = Tubes[t].get_Half_Electrical_Length();
  MyDouble z0 = Tubes[t].get_Z0();

  MyDouble z = (z0 + h);
  MyDouble theta = 0;

  MyDouble units = 1.e+3;
  MyDouble angle_units = M_PI/180.;

  MyDouble z_offset = 0;

  string ident = filename;
  string in_suffix;

  remove_file_extension(ident, in_suffix);

  cut_helix_file << "#theta[rad] \tShape_id[]\tZ[mm]\n";
  cut_helix_file << "#\n";
  cut_helix_file << setw(12) << setprecision(8) << theta * (-sign) << "\t";
  cut_helix_file << setw(12) << setprecision(8) << 0 << "\t";
  cut_helix_file << setw(12) << setprecision(8) << (z + z_offset) * units << "\n";

  vector<BitterMagnet>::const_iterator Magnet = Helix.begin();
  for (int s=Magnet_Stack.size()-1; s>=0; s--){
     int stack = Magnet_Stack[s];

     for (int n=Tubes[stack].get_n_elem()-1; n>=0; n--){
	 int num = n + Tubes[stack].get_index();
	 Magnet = Helix.begin();
	 Magnet += num;

	 MyDouble pitch = Tubes[stack].get_pitch(n);
	 MyDouble Nturns = Tubes[stack].get_nturn(n); // = fabs(Magnet->get_Z_sup() - Magnet->get_Z_inf()) / pitch;

	 z -= pitch * Nturns;
	 theta += Nturns * 2 * M_PI; // in radians

	 cut_helix_file << setw(12) << setprecision(8) << theta * (-sign) << "\t";
	 cut_helix_file << setw(12) << setprecision(8) << 0 << "\t";
	 cut_helix_file << setw(12) << setprecision(8) << (z + z_offset) * units << "\n";
     }
  }
        
        """



    
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

        defs = {}
        import gmsh
        
        # set physical name
        for i,id in enumerate(ids):
            ps = gmsh.model.addPhysicalGroup(2, [id])
            gmsh.model.setPhysicalName(2, ps, "%s_Cu%d" % (name, i))
            defs["%s_Cu%d" % (name, i)] = ps
        
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

        return (r0_bc_ids, r1_bc_ids, defs)

    def htype(self):
        """
        return the type of Helix (aka HR or HL)
        """
        if self.dble:
            return "HL"
        else:
            return "HR"

    def insulators(self):
        """
        return name and number of insulators depending on htype
        """
        
        sInsulator = "Glue"
        nInsulators = 1
        if self.htype() == "HL":
            nInsulators = 2
        else:
            sInsulator = "Kapton"
            angle = self.shape.angle
            nshapes = self.axi.nturns * (360 / float(angle))
            # print("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))
                    
            nshapes = (lambda x: math.ceil(x) if math.ceil(x) - x < x - math.floor(x) else math.floor(x))(nshapes)
            nInsulators = int(nshapes)
            # print("nKaptons=", nInsulators)
    
        return (sInsulator, nInsulators)

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

