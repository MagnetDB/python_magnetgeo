import os

from .base import YAMLObjectBase
from .Contour2D import Contour2D
from .validation import GeometryValidator


class Tierod(YAMLObjectBase):
    yaml_tag = "Tierod"

    def __init__(
        self, name: str, r: float, n: int, dh: float, sh: float, contour2d: str | Contour2D
    ) -> None:
        """
        Initialize a tie rod configuration for Bitter disk magnets.

        A Tierod represents a circumferential array of structural reinforcement holes
        that pass axially through a stack of Bitter disks. These tie rods provide
        mechanical strength to hold the disk stack together under magnetic forces
        and coolant pressure.

        Args:
            name: Unique identifier for this tie rod configuration
            r: Radial position of the tie rod holes in mm. Measured from the
            magnet axis to the center of each tie rod hole.
            n: Number of tie rod holes distributed around the circumference.
            Holes are evenly spaced at intervals of 360/n degrees.
            dh: Hydraulic diameter in mm. For tie rods used as coolant channels,
                defined as dh = 4*Sh/Ph where:
                - Sh is the cross-sectional area of one hole
                - Ph is the wetted perimeter of one hole
                Set to 0.0 if tie rods are purely structural.
            sh: Cross-sectional area of a single tie rod hole in mm².
                Total structural area removed = n * sh.
                Set to 0.0 if tie rods are purely structural.
            contour2d: Contour2D object defining the tie rod hole cross-section,
                    or string reference to Contour2D YAML file, or None.
                    Describes the actual 2D shape of each hole (typically circular).

        Raises:
            ValidationError: If name is invalid (empty or None)
            ValidationError: If n is not a positive integer
            ValidationError: If r, dh, or sh are not positive numbers (or zero for dh/sh)

        Notes:
            - Tie rods are structural elements, not electrical conductors
            - Holes are typically circular but can have any cross-section shape
            - Evenly distributed around circumference at 360/n degree intervals
            - Can serve dual purpose: mechanical support + coolant flow path
            - dh and sh can be 0.0 for purely structural tie rods
            - The contour2d provides detailed geometry for stress analysis

        Example:
            >>> # Structural tie rods (no cooling function)
            >>> from python_magnetgeo.Contour2D import Contour2D
            >>> contour = Contour2D(
            ...     name="rod_circle",
            ...     points=[[0, 0], [10, 0]]  # Circular hole, 10mm diameter
            ... )
            >>> tierod = Tierod(
            ...     name="support_rods",
            ...     r=95.0,            # 95mm radius
            ...     n=6,               # 6 holes (spaced 60° apart)
            ...     dh=0.0,            # Not used for cooling
            ...     sh=0.0,            # Not used for cooling
            ...     contour2d=contour
            ... )

            >>> # Tie rods with coolant flow
            >>> tierod_cooling = Tierod(
            ...     name="cooling_rods",
            ...     r=110.0,
            ...     n=8,               # 8 holes (spaced 45° apart)
            ...     dh=12.0,           # 12mm hydraulic diameter
            ...     sh=113.1,          # ~113mm² area (10mm diameter circle)
            ...     contour2d=contour
            ... )

            >>> # Simplified without detailed contour
            >>> tierod_simple = Tierod(
            ...     name="simple_rods",
            ...     r=100.0,
            ...     n=12,
            ...     dh=0.0,
            ...     sh=0.0,
            ...     contour2d=None  # No detailed geometry
            ... )
        """
        # General validation
        # GeometryValidator.validate_name(name)

        # Ring-specific validation
        GeometryValidator.validate_integer(n, "n")
        GeometryValidator.validate_positive(n, "n")
        GeometryValidator.validate_positive(r, "r")
        GeometryValidator.validate_positive(dh, "dh")
        GeometryValidator.validate_positive(sh, "sh")

        self.name = name
        self.r = r
        self.n = n
        self.dh: float = dh
        self.sh: float = sh
        self.contour2d = contour2d

        # Store the directory context for resolving struct paths
        self._basedir = os.getcwd()

    def __repr__(self):
        """
        Return string representation of Tierod instance.

        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.

        Returns:
            str: String representation in constructor-like format showing:
                - name: Tie rod identifier
                - r: Radial position
                - n: Number of holes
                - dh: Hydraulic diameter
                - sh: Hole cross-section
                - contour2d: Contour2D object or None

        Example:
            >>> contour = Contour2D("circle", points=[[0, 0], [10, 0]])
            >>> tierod = Tierod("support_rods", r=95.0, n=6,
            ...                 dh=0.0, sh=0.0, contour2d=contour)
            >>> print(repr(tierod))
            Tierod(name='support_rods', r=95.0, n=6, dh=0.0, sh=0.0,
                contour2d=Contour2D(...))
            >>>
            >>> # In Python REPL
            >>> tierod
            Tierod(name='support_rods', r=95.0, n=6, ...)
            >>>
            >>> # With None contour
            >>> tierod_simple = Tierod("simple_rods", r=100.0, n=12,
            ...                        dh=0.0, sh=0.0, contour2d=None)
            >>> print(repr(tierod_simple))
            Tierod(name='simple_rods', r=100.0, n=12, dh=0.0, sh=0.0,
                contour2d=None)
        """
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"r={self.r!r}, n={self.n!r}, "
            f"dh={self.dh!r}, sh={self.sh!r}, "
            f"contour2d={self.contour2d!r})"
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Tierod instance from dictionary representation.

        Supports flexible input formats for the nested contour2d object,
        allowing inline definition, file reference, or pre-instantiated object.

        Args:
            values: Dictionary containing Tierod configuration with keys:
                - name (str): Tie rod identifier
                - r (float): Radial position in mm
                - n (int): Number of holes
                - dh (float, optional): Hydraulic diameter in mm (default: 0.0)
                - sh (float, optional): Hole cross-section in mm² (default: 0.0)
                - contour2d: Contour2D specification (string/dict/object/None)
            debug: Enable debug output showing object loading process

        Returns:
            Tierod: New Tierod instance created from dictionary

        Raises:
            KeyError: If required keys ('name', 'r', 'n') are missing from dictionary
            ValidationError: If values fail validation checks
            ValidationError: If contour2d data is malformed

        Notes:
            - dh and sh default to 0.0 if not provided (structural only)
            - contour2d is optional (can be None)

        Example:
            >>> # With inline contour definition
            >>> data = {
            ...     "name": "support_rods",
            ...     "r": 95.0,
            ...     "n": 6,
            ...     "dh": 0.0,
            ...     "sh": 0.0,
            ...     "contour2d": {
            ...         "name": "circle",
            ...         "points": [[0, 0], [10, 0]]
            ...     }
            ... }
            >>> tierod = Tierod.from_dict(data)

            >>> # With file reference
            >>> data2 = {
            ...     "name": "cooling_rods",
            ...     "r": 110.0,
            ...     "n": 8,
            ...     "dh": 12.0,
            ...     "sh": 113.1,
            ...     "contour2d": "rod_profile"  # Load from rod_profile.yaml
            ... }
            >>> tierod2 = Tierod.from_dict(data2)

            >>> # Minimal (structural only, no contour)
            >>> data3 = {
            ...     "name": "simple_rods",
            ...     "r": 100.0,
            ...     "n": 12
            ...     # dh, sh default to 0.0
            ...     # contour2d defaults to None
            ... }
            >>> tierod3 = Tierod.from_dict(data3)
        """
        # Smart nested object handling
        contour2d = cls._load_nested_single(values.get("contour2d"), Contour2D, debug=debug)
        return cls(
            name=values.get("name", "")
            r=values["r"],
            n=values["n"],
            dh=values.get("dh", 0.0),
            sh=values.get("sh", 0.0),
            contour2d=contour2d,
        )
