#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for 2D Shape:

* Geom data: x, y
"""


from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Contour2D(YAMLObjectBase):
    """
    name :

    params :
      x, y: list of points
    """

    yaml_tag = "Contour2D"

    def __init__(self, name: str, points: list[list[float]]):
        """
        initialize object
        """
        # General validation
        GeometryValidator.validate_name(name)
        
        self.name = name
        self.points = points

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, points=%r)" % (self.__class__.__name__, self.name, self.points)

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        points = values["points"]

        object = cls(name, points)
        return object



def create_circle(r: float, n: int = 20) -> Contour2D:
    from math import pi, cos, sin

    if n < 0:
        raise RuntimeError(f"create_rectangle: n got {n}, expect a positive integer")

    name = f"circle-{2*r}-mm"
    points = []
    theta = 2 * pi / float(n)
    for i in range(n):
        x = r * cos(i * theta)
        y = r * sin(i * theta)
        points.append([x, y])

    return Contour2D(name, points)


def create_rectangle(
    x: float, y: float, dx: float, dy: float, fillet: int = 0
) -> Contour2D:
    from math import pi, cos, sin

    if fillet < 0:
        raise RuntimeError(
            f"create_rectangle: fillet got {fillet}, expect a positive integer"
        )

    name = f"rectangle-{dx}-{dy}-mm"
    if fillet == 0:
        points = [[x, y], [x + dx, y], [x + dx, y + dy], [x, y + dy]]
    else:

        points = [[x, y]]
        theta = pi / float(fillet)
        xc = (x + dx) / 2.0
        yc = y
        r = dx / 2.0
        for i in range(fillet):
            _x = xc + r * cos(pi + i * theta)
            _y = yc + r * cos(pi + i * theta)
            points.append([_x, _y])
        yc = y + dy
        for i in range(fillet):
            _x = xc + r * cos(i * theta)
            _y = yc + r * cos(i * theta)
            points.append([_x, _y])

    return Contour2D(name, points)


def create_angularslit(
    x: float, angle: float, dx: float, n: int = 10, fillet: int = 0
) -> Contour2D:
    from math import pi, cos, sin

    if fillet < 0:
        raise RuntimeError(
            f"create_angularslit: fillet got {fillet}, expect a positive integer"
        )
    if n < 0:
        raise RuntimeError(f"create_angularslit: n got {n}, expect a positive integer")

    name = f"angularslit-{dx}-{angle}-mm"

    points = []
    theta = angle * pi / float(n)
    theta_ = None
    r = x
    r_ = dx / 2.0

    for i in range(n):
        x = r * cos(angle / 2.0 - i * theta)
        y = r * sin(angle / 2.0 - i * theta)
        points.append([x, y])

    if fillet > 0:
        theta_ = pi / float(fillet)
        xc = (r + dx) * cos(-angle / 2.0) / 2
        yc = (r + dx) * sin(-angle / 2.0) / 2
        r_ = dx / 2.0
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            points.append([_x, _y])

    r = x + dx
    for i in range(n):
        x = r * cos(-angle / 2.0 + i * theta)
        y = r * sin(-angle / 2.0 + i * theta)
        points.append([x, y])

    if fillet > 0:
        xc = (r + dx) * cos(angle / 2.0) / 2
        yc = (r + dx) * sin(angle / 2.0) / 2
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            points.append([_x, _y])

    return Contour2D(name, points)
