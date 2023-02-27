#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for 2D Shape:

* Geom data: x, y
"""
from typing import List

import yaml


class Shape2D(yaml.YAMLObject):
    """
    name :

    params :
      x, y: list of points
    """

    yaml_tag = "Shape2D"

    def __init__(self, name: str, pts: List[List[float]]):
        """
        initialize object
        """
        self.name = name
        self.pts = pts

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, pts=%r)" % (self.__class__.__name__, self.name, self.pts)

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Shape2D dump")

    def load(self, name: str):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Shape2D data {name}.yaml")

        self.name = name
        self.pts = data.pts



def Shape_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    pts = values["pts"]
    return Shape2D(name, pts)


yaml.add_constructor(u"!Shape2D", Shape_constructor)
