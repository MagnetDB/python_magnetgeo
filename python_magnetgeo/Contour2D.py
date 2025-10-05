#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for 2D contours and shapes.

This module defines the Contour2D class for representing 2D geometric shapes
as a series of points, along with utility functions for creating common
geometric shapes (circles, rectangles, angular slits).

Classes:
    Contour2D: Represents a 2D contour defined by a list of points
    
Functions:
    create_circle: Generate a circular contour
    create_rectangle: Generate a rectangular contour with optional filleting
    create_angularslit: Generate an angular slit contour
"""


from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Contour2D(YAMLObjectBase):
    """
    Represents a 2D contour defined by a list of points.
    
    A Contour2D object defines a closed 2D shape as a sequence of (x, y) coordinate pairs.
    This is typically used for defining cross-sectional profiles or boundary shapes
    in magnet geometry definitions.
    
    Attributes:
        name (str): Unique identifier for the contour
        points (list[list[float]]): List of [x, y] coordinate pairs defining the contour
        
    Example:
        >>> # Create a simple square contour
        >>> square = Contour2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> 
        >>> # Load from YAML
        >>> contour = Contour2D.from_yaml("my_contour.yaml")
        >>> 
        >>> # Create from dictionary
        >>> data = {"name": "triangle", "points": [[0, 0], [1, 0], [0.5, 1]]}
        >>> triangle = Contour2D.from_dict(data)
    """

    yaml_tag = "Contour2D"

    def __init__(self, name: str, points: list[list[float]]):
        """
        Initialize a Contour2D object.
        
        Args:
            name: Unique identifier for the contour. Must be non-empty and follow
                  standard naming conventions (alphanumeric, underscores, hyphens).
            points: List of [x, y] coordinate pairs defining the contour vertices.
                   Each point must be a list or tuple of exactly 2 float values.
                   
        Raises:
            ValidationError: If name is invalid or empty
            
        Example:
            >>> contour = Contour2D("my_shape", [[0, 0], [10, 0], [10, 10], [0, 10]])
        """
        # General validation
        GeometryValidator.validate_name(name)
        
        self.name = name
        self.points = points

    def __repr__(self):
        """
        Return string representation of the Contour2D object.
        
        Returns:
            str: String showing class name, name, and points
            
        Example:
            >>> contour = Contour2D("test", [[0, 0], [1, 1]])
            >>> repr(contour)
            "Contour2D(name='test', points=[[0, 0], [1, 1]])"
        """
        return "%s(name=%r, points=%r)" % (self.__class__.__name__, self.name, self.points)

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create a Contour2D object from a dictionary.
        
        This method is used for deserialization from YAML/JSON formats.
        
        Args:
            values: Dictionary containing 'name' and 'points' keys
            debug: Enable debug output (default: False)
            
        Returns:
            Contour2D: New instance created from the dictionary data
            
        Raises:
            KeyError: If required keys ('name', 'points') are missing
            ValidationError: If name or points data is invalid
            
        Example:
            >>> data = {
            ...     "name": "profile",
            ...     "points": [[0, 0], [5, 0], [5, 5], [0, 5]]
            ... }
            >>> contour = Contour2D.from_dict(data)
        """
        name = values["name"]
        points = values["points"]

        object = cls(name, points)
        return object



def create_circle(r: float, n: int = 20) -> Contour2D:
    """
    Create a circular contour centered at the origin.
    
    Generates a circle as a polygon with n vertices, distributed evenly
    around the circumference. The circle is centered at (0, 0).
    
    Args:
        r: Radius of the circle in millimeters. Must be positive.
        n: Number of vertices to approximate the circle (default: 20).
           Higher values give smoother circles. Must be positive.
           
    Returns:
        Contour2D: A contour representing the circle, with name "circle-{diameter}-mm"
        
    Raises:
        RuntimeError: If n is not a positive integer
        
    Example:
        >>> # Create a circle with 10mm radius using 20 points
        >>> circle = create_circle(10.0)
        >>> 
        >>> # Create a smoother circle with 40 points
        >>> smooth_circle = create_circle(10.0, n=40)
        >>> 
        >>> # Circle name includes diameter
        >>> print(circle.name)
        'circle-20.0-mm'
    """
    from math import pi, cos, sin

    if n < 0:
        raise RuntimeError(f"create_circle: n got {n}, expect a positive integer")

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
    """
    Create a rectangular contour with optional rounded corners.
    
    Generates a rectangle with lower-left corner at (x, y) and dimensions
    (dx, dy). Optionally adds rounded corners using circular fillets.
    
    Args:
        x: X-coordinate of the lower-left corner in millimeters
        y: Y-coordinate of the lower-left corner in millimeters
        dx: Width of the rectangle in millimeters. Must be positive.
        dy: Height of the rectangle in millimeters. Must be positive.
        fillet: Number of points per rounded corner (default: 0 for sharp corners).
               If > 0, corners are rounded with semicircular arcs. Must be non-negative.
               
    Returns:
        Contour2D: A contour representing the rectangle, with name "rectangle-{dx}-{dy}-mm"
        
    Raises:
        RuntimeError: If fillet is negative
        
    Example:
        >>> # Create sharp-cornered rectangle
        >>> rect = create_rectangle(0, 0, 20, 10)
        >>> 
        >>> # Create rectangle with rounded corners (5 points per corner)
        >>> rounded = create_rectangle(0, 0, 20, 10, fillet=5)
        >>> 
        >>> # Rectangle positioned at specific location
        >>> offset_rect = create_rectangle(5, 5, 15, 8)
    
    Note:
        When fillet > 0, the function creates semicircular rounded corners
        at the top of the rectangle. The rounding uses dx/2 as the radius.
    """
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
    """
    Create an angular slit (sector) contour with optional rounded ends.
    
    Generates a radial sector shape (like a slice of pie) from radius x to x+dx,
    spanning the specified angle. The sector is centered at the origin and
    symmetric about the x-axis. Optional filleting rounds the outer corners.
    
    Args:
        x: Inner radius of the slit in millimeters. Must be positive.
        angle: Angular extent of the slit in radians. The slit extends from
               -angle/2 to +angle/2 from the positive x-axis.
        dx: Radial thickness of the slit in millimeters. Must be positive.
        n: Number of points along each radial arc (default: 10). Higher values
           give smoother curves. Must be positive.
        fillet: Number of points for rounded corners at the outer edges (default: 0).
               If > 0, adds semicircular fillets at the outer corners. Must be non-negative.
               
    Returns:
        Contour2D: A contour representing the angular slit, 
                  with name "angularslit-{dx}-{angle}-mm"
        
    Raises:
        RuntimeError: If fillet is negative or n is not positive
        
    Example:
        >>> # Create 45-degree slit from r=10 to r=12
        >>> slit = create_angularslit(10.0, 0.785, 2.0)  # 0.785 rad ≈ 45°
        >>> 
        >>> # Create wider slit with smooth arcs
        >>> smooth_slit = create_angularslit(10.0, 1.57, 2.0, n=20)  # 1.57 rad ≈ 90°
        >>> 
        >>> # Create slit with rounded outer corners
        >>> rounded_slit = create_angularslit(10.0, 0.785, 2.0, n=10, fillet=5)
    
    Note:
        The slit is symmetric about the x-axis and extends from -angle/2 to +angle/2.
        When fillet > 0, semicircular rounds are added at the outer corners with
        radius dx/2.
        
    Coordinate system:
        - Origin at (0, 0)
        - Inner arc at radius x
        - Outer arc at radius x + dx
        - Angular range: [-angle/2, +angle/2]
    """
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

    # Generate inner arc from +angle/2 to -angle/2
    for i in range(n):
        x = r * cos(angle / 2.0 - i * theta)
        y = r * sin(angle / 2.0 - i * theta)
        points.append([x, y])

    # Add rounded corner at -angle/2 if fillet requested
    if fillet > 0:
        theta_ = pi / float(fillet)
        xc = (r + dx) * cos(-angle / 2.0) / 2
        yc = (r + dx) * sin(-angle / 2.0) / 2
        r_ = dx / 2.0
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            points.append([_x, _y])

    # Generate outer arc from -angle/2 to +angle/2
    r = x + dx
    for i in range(n):
        x = r * cos(-angle / 2.0 + i * theta)
        y = r * sin(-angle / 2.0 + i * theta)
        points.append([x, y])

    # Add rounded corner at +angle/2 if fillet requested
    if fillet > 0:
        xc = (r + dx) * cos(angle / 2.0) / 2
        yc = (r + dx) * sin(angle / 2.0) / 2
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            points.append([_x, _y])

    return Contour2D(name, points)
