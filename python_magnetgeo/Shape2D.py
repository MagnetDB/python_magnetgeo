#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for 2D Shape:

* Geom data: x, y
"""

import yaml
import json


class Shape2D(yaml.YAMLObject):
    """
    name :

    params :
      x, y: list of points
    """

    yaml_tag = "Shape2D"

    def __init__(self, name: str, pts: list[list[float]]):
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
            raise Exception(f"Failed to load Shape2D data {filename}")

        if basedir and basedir != ".":
            os.chdir(cwd)
        
        name = values["name"]
        pts = values["pts"]
        return cls(name, pts)

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'Shape2D.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)
    


def Shape_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    return values, "Shape2D"
    


yaml.add_constructor(Shape2D.yaml_tag, Shape_constructor)


def create_circle(r: float, n: int = 20) -> Shape2D:
    from math import pi, cos, sin

    if n < 0:
        raise RuntimeError(f"create_rectangle: n got {n}, expect a positive integer")

    name = f"circle-{2*r}-mm"
    pts = []
    theta = 2 * pi / float(n)
    for i in range(n):
        x = r * cos(i * theta)
        y = r * sin(i * theta)
        pts.append([x, y])

    return Shape2D(name, pts)


def create_rectangle(
    x: float, y: float, dx: float, dy: float, fillet: int = 0
) -> Shape2D:
    from math import pi, cos, sin

    if fillet < 0:
        raise RuntimeError(
            f"create_rectangle: fillet got {fillet}, expect a positive integer"
        )

    name = f"rectangle-{dx}-{dy}-mm"
    if fillet == 0:
        pts = [[x, y], [x + dx, y], [x + dx, y + dy], [x, y + dy]]
    else:

        pts = [[x, y]]
        theta = pi / float(fillet)
        xc = (x + dx) / 2.0
        yc = y
        r = dx / 2.0
        for i in range(fillet):
            _x = xc + r * cos(pi + i * theta)
            _y = yc + r * cos(pi + i * theta)
            pts.append([_x, _y])
        yc = y + dy
        for i in range(fillet):
            _x = xc + r * cos(i * theta)
            _y = yc + r * cos(i * theta)
            pts.append([_x, _y])

    return Shape2D(name, pts)


def create_angularslit(
    x: float, angle: float, dx: float, n: int = 10, fillet: int = 0
) -> Shape2D:
    from math import pi, cos, sin

    if fillet < 0:
        raise RuntimeError(
            f"create_angularslit: fillet got {fillet}, expect a positive integer"
        )
    if n < 0:
        raise RuntimeError(f"create_angularslit: n got {n}, expect a positive integer")

    name = f"angularslit-{dx}-{angle}-mm"

    pts = []
    theta = angle * pi / float(n)
    theta_ = None
    r = x
    r_ = dx / 2.0

    for i in range(n):
        x = r * cos(angle / 2.0 - i * theta)
        y = r * sin(angle / 2.0 - i * theta)
        pts.append([x, y])

    if fillet > 0:
        theta_ = pi / float(fillet)
        xc = (r + dx) * cos(-angle / 2.0) / 2
        yc = (r + dx) * sin(-angle / 2.0) / 2
        r_ = dx / 2.0
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            pts.append([_x, _y])

    r = x + dx
    for i in range(n):
        x = r * cos(-angle / 2.0 + i * theta)
        y = r * sin(-angle / 2.0 + i * theta)
        pts.append([x, y])

    if fillet > 0:
        xc = (r + dx) * cos(angle / 2.0) / 2
        yc = (r + dx) * sin(angle / 2.0) / 2
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            pts.append([_x, _y])

    return Shape2D(name, pts)
