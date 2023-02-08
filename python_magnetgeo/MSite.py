#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Site:

"""
from typing import Union, Optional

import os
import sys

import json
import yaml
from . import deserialize

class MSite(yaml.YAMLObject):
    """
    name :
    magnets : dict holding magnet list ("insert", "Bitter", "Supra")
    screens :
    """

    yaml_tag = 'MSite'

    def __init__(self, name: str, magnets: Union[str, list, dict], screens: Optional[Union[str, list, dict]]):
        """
        initialize onject
        """
        self.name = name
        self.magnets = magnets
        self.screens = screens

    def __repr__(self):
        """
        representation of object
        """
        return f"name: {self.name}, magnets:{self.magnets}, screens: {self.screens}"

    def get_channels(self, mname: str = None, hideIsolant: bool = True, debug: bool = False):
        """
        get Channels def as dict
        """
        print(f'MSite/get_channels:')

        Channels = {}
        if isinstance(self.magnets, str):
            YAMLFile = f'{self.magnets}.yaml' 
            with open(YAMLFile, "r") as f:
                Object = yaml.load(f, Loader=yaml.FullLoader)
                
            Channels[self.magnets] = Object.get_channels(self.name, hideIsolant, debug)
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                magnet = self.magnets[key]
                if isinstance(magnet, str):
                    YAMLFile = f'{magnet}.yaml' 
                    with open(YAMLFile, "r") as f:
                        Object = yaml.load(f, Loader=yaml.FullLoader)
                        print(f'{magnet}: {Object}')

                    Channels[key] = Object.get_channels(key, hideIsolant, debug)

                elif isinstance(magnet, list):
                    for part in magnet:
                        if isinstance(part, str):
                            YAMLFile = f'{part}.yaml' 
                            with open(YAMLFile, "r") as f:
                                Object = yaml.load(f, Loader=yaml.FullLoader)
                                print(f'{part}: {Object}')
                        else:
                            raise RuntimeError(f'MSite(magnets[{key}][{part}]): unsupported type of magnets ({type(part)})')
                        
                        _list = Object.get_channels(key, hideIsolant, debug)
                        print(f'MSite/get_channels: key={key} part={part} _list={_list}')
                        if key in Channels:
                            Channels[key].append(_list)
                        else:
                            Channels[key] = [_list]

                else:
                    raise RuntimeError(f'MSite(magnets[{key}]): unsupported type of magnets ({type(magnet)})')
        else:
            raise RuntimeError(f'MSite: unsupported type of magnets ({type(self.magnets)})')
        
        return Channels

    def get_isolants(self, mname: str = None, debug: bool = False):
        """
        return isolants
        """
        return {}

    def get_names(self, mname: str = None, is2D: bool = False, verbose: bool = False):
        """
        return names for Markers
        """
        solid_names = []

        if isinstance(self.magnets, str):
            YAMLFile = f'{self.magnets}.yaml' 
            with open(YAMLFile, "r") as f:
                Object = yaml.load(f, Loader=yaml.FullLoader)
                
            solid_names += Object.get_names(self.name, is2D, verbose)
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                magnet = self.magnets[key]
                if isinstance(magnet, str):
                    YAMLFile = f'{magnet}.yaml' 
                    with open(YAMLFile, "r") as f:
                        Object = yaml.load(f, Loader=yaml.FullLoader)
                        print(f'{magnet}: {Object}')

                    solid_names += Object.get_names(key, is2D, verbose)

                elif isinstance(magnet, list):
                    for part in magnet:
                        if isinstance(part, str):
                            YAMLFile = f'{part}.yaml' 
                            with open(YAMLFile, "r") as f:
                                Object = yaml.load(f, Loader=yaml.FullLoader)
                                print(f'{part}: {Object}')
                        else:
                            raise RuntimeError(f'MSite(magnets[{key}][{part}]): unsupported type of magnets ({type(part)})')
                        
                        solid_names += Object.get_names(key, is2D, verbose)

                else:
                    raise RuntimeError(f'MSite/get_names (magnets[{key}]): unsupported type of magnets ({type(magnet)})')
        else:
            raise RuntimeError(f'MSite/get_names: unsupported type of magnets ({type(self.magnets)})')

        if verbose:
            print(f"MSite/get_names: solid_names {len(solid_names)}")
        return solid_names

    def dump(self):
        """
        dump object to file
        """
        try:
            ostream = open(f'{self.name}.yaml', 'w')
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
        self.screens = data.screens

        # TODO: check that magnets are not interpenetring
        # define a boundingBox method for each type: Bitter, Supra, Insert


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
        istream.close()

    def boundingBox(self):
        """
        """
        zmin = None
        zmax = None
        rmin = None
        rmax = None

        def cboundingBox(rmin, rmax, zmin, zmax, r, z):
            if zmin == None:
                zmin = min(z)
                zmax = max(z)
                rmin = min(r)
                rmax = max(r)
            else:
                zmin = min(zmin, min(z))
                zmax = max(zmax, max(z))
                rmin = min(rmin, min(r))
                rmax = max(rmax, max(r))
            return (rmin, rmax, zmin, zmax)

        if isinstance(self.magnets, str):
            YAMLFile = os.path.join(f"{self.magnets}.yaml")
            with open(YAMLFile, 'r') as istream:
                Object = yaml.load(istream, Loader=yaml.FullLoader)
                (r, z) = Object.boundingBox()
                (rmin, rmax, zmin, zmax) = cboundingBox(rmin, rmax, zmin, zmax, r, z)

        elif isinstance(self.magnets, list):
            for mname in self.magnets:
                YAMLFile = os.path.join(f"{mname}.yaml")
                with open(YAMLFile, 'r') as istream:
                    Object = yaml.load(istream, Loader=yaml.FullLoader)
                    (r, z) = Object.boundingBox()
                    (rmin, rmax, zmin, zmax) = cboundingBox(rmin, rmax, zmin, zmax, r, z)
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                if isinstance(self.magnets[key], str):
                    YAMLFile = os.path.join(f"{self.magnets[key]}.yaml")
                    with open(YAMLFile, 'r') as istream:
                        Object = yaml.load(istream, Loader=yaml.FullLoader)
                        (r, z) = Object.boundingBox()
                        (rmin, rmax, zmin, zmax) = cboundingBox(rmin, rmax, zmin, zmax, r, z)
                elif isinstance(self.magnets[key], list):
                    for mname in self.magnets[key]:
                        YAMLFile = os.path.join(f"{mname}.yaml")
                        with open(YAMLFile, 'r') as istream:
                            Object = yaml.load(istream, Loader=yaml.FullLoader)
                            (r, z) = Object.boundingBox()
                            (rmin, rmax, zmin, zmax) = cboundingBox(rmin, rmax, zmin, zmax, r, z)
                else:
                    raise Exception(f"magnets: unsupported type {type(self.magnets[key])}")
        else:
            raise Exception(f"magnets: unsupported type {type(self.magnets)}")

        return (rmin, rmax, zmin, zmax)

    def gmsh(self, AirData=None, workingDir='.', debug: bool = False):
        """
        create gmsh geometry
        """
        import gmsh

        gmsh_ids = []

        if isinstance(self.magnets, str):
            print(f"msite/gmsh/{self.magnets} (str)")
            with open(self.magnets + '.yaml', 'r') as f:
                Magnet = yaml.load(f, Loader=yaml.FullLoader)
            gmsh_ids.append(Magnet.gmsh(None, debug))

        elif isinstance(self.magnets, list):
            for mname in self.magnets:
                print(f"msite/gmsh/{mname} (list)")
                with open(f'{mname}.yaml', 'r') as f:
                    Magnet = yaml.load(f, Loader=yaml.FullLoader)
                gmsh_ids.append(Magnet.gmsh(None, debug))

        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                print(f"msite/gmsh/{key} (dict)")
                if isinstance(self.magnets[key], str):
                    print(f"msite/gmsh/{self.magnets[key]} (dict/str)")
                    with open(f'{self.magnets[key]}.yaml', 'r') as f:
                        Magnet = yaml.load(f, Loader=yaml.FullLoader)
                    gmsh_ids.append(Magnet.gmsh(None, debug))

                if isinstance(self.magnets[key], list):
                    for mname in self.magnets[key]:
                        print(f"msite/gmsh/{mname} (dict/list)")
                        with open(f'{mname}.yaml', 'r') as f:
                            Magnet = yaml.load(f, Loader=yaml.FullLoader)
                        gmsh_ids.append(Magnet.gmsh(None, debug))

        else:
            raise Exception(f"magnets: unsupported type {type(self.magnets)}")

        # Now create air
        if AirData:
            (r_min, r_max, z_min, z_max) = self.boundingBox(workingDir)
            r0_air = 0
            dr_air = (r_min - r_max) * AirData[0]
            z0_air = z_min * AirData[1]
            dz_air = (z_max - z_min)  * AirData[1]
            A_id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)

            flat_list = []
            print("flat_list:", len(gmsh_ids))
            for sublist in gmsh_ids:
                if not isinstance(sublist, tuple):
                    raise Exception(f"python_magnetgeo/gmsh: flat_list: expect a tuple got a {type(sublist)}")
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
            ov, ovv = gmsh.model.occ.fragment([(2, A_id)], [(2, i) for i in flat_list])
            return (gmsh_ids, (A_id, dr_air, z0_air, dz_air))

        return (gmsh_ids, None)

    def gmsh_bcs(self, ids: tuple, debug: bool = False):
        """
        retreive ids for bcs in gmsh geometry
        """
        import gmsh
        print("MSite/gmsh_bcs:", type(ids))
        (gmsh_ids, Air_data) = ids

        defs = {}

        def load_defs(mdefs: dict):
            for key in mdefs:
                defs[key] = mdefs[key]

        for compound in [self.magnets, self.screens]:
            if isinstance(compound, str):
                with open(f'{compound}.yaml', 'r') as f:
                    Object = yaml.load(f, Loader=yaml.FullLoader)
                load_defs(Object.gmsh_bcs(gmsh_ids[0], debug))

            elif isinstance(compound, list):
                for i, mname in enumerate(compound):
                    with open(f'{mname}.yaml', 'r') as f:
                        Object = yaml.load(f, Loader=yaml.FullLoader)
                    load_defs(Object.gmsh_bcs(gmsh_ids[i], debug))

            elif isinstance(compound, dict):
                num = 0
                for i, key in enumerate(compound):
                    if isinstance(compound[key], str):
                        with open(f'{compound[key]}.yaml', 'r') as f:
                            Object = yaml.load(f, Loader=yaml.FullLoader)
                        print("ids:", type(gmsh_ids[num]), type(Object))
                        load_defs(Object.gmsh_bcs(gmsh_ids[num], debug))
                        num += 1

                    if isinstance(self.magnets[key], list):
                        for mname in self.magnets[key]:
                            with open(f'{mname}.yaml', 'r') as f:
                                Object = yaml.load(f, Loader=yaml.FullLoader)
                            print("ids:", type(gmsh_ids[num]), type(Object))
                            load_defs(Object.gmsh_bcs(gmsh_ids[num], True))
                            num += 1

            else:
                raise Exception(f"magnets: unsupported type {type(compound)}")

        # TODO: Air
        if Air_data:
            (Air_id, dr_air, z0_air, dz_air) = Air_data

            ps = gmsh.model.addPhysicalGroup(2, [Air_id])
            gmsh.model.setPhysicalName(2, ps, "Air")
            defs["Air" % self.name] = ps

            # TODO: Axis, Inf
            gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

            eps = 1.e-6

            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, +eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim, tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "ZAxis")
            defs["ZAxis" % self.name] = ps

            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, dr_air+eps, z0_air+eps, 0, 1)
            print("ov:", len(ov))

            ov += gmsh.model.getEntitiesInBoundingBox(dr_air-eps, z0_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))

            ov += gmsh.model.getEntitiesInBoundingBox(-eps, z0_air+dz_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))

            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim, tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Infty")
            defs["Infty" % self.name] = ps

        return defs

    def gmsh_msh(self, defs: dict, lc: list):
        import gmsh
        print("gmsh_msh: set characteristic lengths")

        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lc[0])
        if "Air" in defs:
            gmsh.model.mesh.setSize(gmsh.model.getEntitiesForPhysicalGroup(0, defs["ZAxis"]), lc[1])
            gmsh.model.mesh.setSize(gmsh.model.getEntitiesForPhysicalGroup(0, defs["Infty"]), lc[1])

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

def MSite_constructor(loader, node):
    """
    build an site object
    """
    print(f'MSite_constructor')
    values = loader.construct_mapping(node)
    name = values["name"]
    magnets = values["magnets"]
    screens = values["screens"]
    return MSite(name, magnets, screens)

yaml.add_constructor(u'!MSite', MSite_constructor)
