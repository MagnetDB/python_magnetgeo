#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides definition for groove geometry features.

This module defines the Groove class for representing square-profile grooves
on helical conductor geometries. Grooves are radial indentations used for
various purposes such as cooling channels or structural features.

Classes:
    Groove: Represents square-profile grooves on a helix geometry

Notes:
    Grooves are assumed to have a square cross-section profile. They can be
    positioned on either the inner or outer radius of the conductor.
"""

from .base import YAMLObjectBase


class Groove(YAMLObjectBase):
    """
    Represents square-profile grooves on helical conductor geometry.

    Grooves are radial indentations or channels machined into the conductor
    surface. They typically have a square cross-section and are distributed
    circumferentially around the conductor. Common uses include:
    - Cooling channels
    - Stress relief features
    - Mounting features
    - Electrical isolation

    Attributes:
        name (str): Unique identifier for the groove set (default: '')
        gtype (str): Groove location - "rint" (inner radius) or "rext" (outer radius)
        n (int): Number of grooves distributed around the circumference (default: 0)
        eps (float): Depth of each groove in millimeters (default: 0)

    Example:
        >>> # Create grooves on inner radius
        >>> grooves = Groove(
        ...     name="cooling_grooves",
        ...     gtype="rint",
        ...     n=8,
        ...     eps=2.5
        ... )
        >>>
        >>> # Create empty/default groove (no grooves)
        >>> no_grooves = Groove()
        >>>
        >>> # Load from YAML
        >>> grooves = Groove.from_yaml("grooves.yaml")
    """

    yaml_tag = "Groove"

    def __init__(self, name: str = "", gtype: str = None, n: int = 0, eps: float = 0) -> None:
        """
        Initialize a Groove object.

        Creates a groove specification with the given parameters. All parameters
        have defaults, allowing creation of an empty groove specification (no grooves).

        Args:
            name: Unique identifier for the groove set (default: '').
                  Empty string is allowed for default/no-groove cases.
            gtype: Groove radial position (default: None):
                   - "rint": Grooves on inner radius
                   - "rext": Grooves on outer radius
                   - None: No grooves defined
            n: Number of grooves distributed evenly around the circumference
               (default: 0). Must be non-negative. Zero means no grooves.
            eps: Depth of each groove in millimeters (default: 0). Must be
                 non-negative. This is the radial depth of the square groove.

        Example:
            >>> # Full specification
            >>> g1 = Groove("cooling", "rint", 8, 2.5)
            >>>
            >>> # Default (no grooves)
            >>> g2 = Groove()
            >>>
            >>> # Partial specification
            >>> g3 = Groove(name="test_grooves", gtype="rext", n=4, eps=1.5)

        Notes:
            The grooves are assumed to:
            - Have square cross-sections (width ≈ depth = eps)
            - Be evenly distributed around the circumference (360°/n spacing)
            - Extend along the full axial length of the conductor
        """
        self.name = name
        self.gtype = gtype
        self.n = n
        self.eps: float = eps

    def __repr__(self):
        """
        Return string representation of the Groove object.

        Returns:
            str: String showing class name and all attribute values

        Example:
            >>> g = Groove("test", "rint", 4, 2.0)
            >>> repr(g)
            "Groove(name=test, gtype=rint, n=4, eps=2)"
        """
        return f"{self.__class__.__name__}(name={self.name}, gtype={self.gtype}, n={self.n}, eps={self.eps:g})"

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create a Groove object from a dictionary.

        This method is used for deserialization from YAML/JSON formats.
        The 'name' field is optional and defaults to empty string if not present.

        Args:
            values: Dictionary containing groove specification with keys:
                    - 'name': str (optional, defaults to '')
                    - 'gtype': str ("rint" or "rext")
                    - 'n': int (number of grooves)
                    - 'eps': float (groove depth in mm)
            debug: Enable debug output (default: False)

        Returns:
            Groove: New instance created from the dictionary data

        Raises:
            KeyError: If required keys are missing ('gtype', 'n', 'eps')

        Example:
            >>> # Full specification
            >>> data = {
            ...     "name": "inner_grooves",
            ...     "gtype": "rint",
            ...     "n": 8,
            ...     "eps": 2.5
            ... }
            >>> groove = Groove.from_dict(data)
            >>>
            >>> # Without name (uses default empty string)
            >>> data2 = {
            ...     "gtype": "rext",
            ...     "n": 4,
            ...     "eps": 1.5
            ... }
            >>> groove2 = Groove.from_dict(data2)
            >>> print(groove2.name)  # ''
        """
        name = values.get("name", "")
        gtype = values["gtype"]
        n = values["n"]
        eps = values["eps"]
        return Groove(name, gtype, n, eps)
