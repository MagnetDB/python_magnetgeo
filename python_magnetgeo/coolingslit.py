#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for CoolingSlits:
"""

import yaml
import json
from .Shape2D import Shape2D


class CoolingSlit(yaml.YAMLObject):
    """
    r: radius
    angle: anglar shift from tierod
    n:
    dh: 4*Sh/Ph with Ph wetted perimeter
    sh:
    shape:
    """

    yaml_tag = "Slit"

    def __init__(
        self, r: float, angle: float, n: int, dh: float, sh: float, shape: Shape2D
    ) -> None:
        self.r: float = r
        self.angle: float = angle
        self.n: int = n
        self.dh: float = dh
        self.sh: float = sh
        self.shape: Shape2D = shape

    def __repr__(self):
        return "%s(r=%r, angle=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.__class__.__name__,
            self.r,
            self.angle,
            self.n,
            self.dh,
            self.sh,
            self.shape,
        )

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to CoolingSlit dump")

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        import os
        cwd = os.getcwd()

        (basedir, basename) = os.path.split(filename)
        print(f"basedir={basedir}, basename={basename}, cwd={cwd}")

        if basedir and basedir != ".":
            os.chdir(basedir)
            print(f"-> cwd={cwd}")

        try:
            with open(basename, "r") as istream:
                values, otype = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load CoolingSlit data {filename}")
        
        if basedir and basedir != ".":
            os.chdir(cwd)
            
        r = values["r"]
        angle = values["angle"]
        n = values["n"]
        dh = values["dh"]
        sh = values["sh"]
        print(f"constructor: {type(values['shape'])}")
        shape = values["shape"]

        return cls(r, angle, n, dh, sh, shape)
        
    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'Coolingslit.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)


def CoolingSlit_constructor(loader, node):
    """
    build an coolingslit object
    """
    print("CoolingSlit_constructor")
    values = loader.construct_mapping(node)
    return values, "CoolingSlit"

yaml.add_constructor(CoolingSlit.yaml_tag, CoolingSlit_constructor)
