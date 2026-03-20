#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides definition for magnetic screening geometry.

This module defines the Screen class for representing magnetic shielding
or screening elements in magnet assemblies. Screens are typically cylindrical
shells used to shape or redirect magnetic fields.

Classes:
    Screen: Represents a magnetic screening element with cylindrical geometry
"""

from .base import YAMLObjectBase


class Screen(YAMLObjectBase):
    """
    Represents a magnetic screening element in axisymmetric geometry.

    A Screen is a cylindrical shell structure used for magnetic field shaping,
    shielding, or redirection. It is defined by its radial extent (inner and
    outer radius) and axial extent (bottom and top z-coordinates).

    Common uses:
    - Magnetic field shaping
    - Flux return paths
    - Magnetic shielding
    - Structural support with magnetic properties

    Attributes:
        name (str): Unique identifier for the screen
        r (list[float]): Radial bounds [r_inner, r_outer] in millimeters
        z (list[float]): Axial bounds [z_bottom, z_top] in millimeters

    Example:
        >>> # Create a simple screen
        >>> screen = Screen(
        ...     name="outer_screen",
        ...     r=[100.0, 120.0],
        ...     z=[0.0, 500.0]
        ... )
        >>>
        >>> # Load from YAML
        >>> screen = Screen.from_yaml("screen.yaml")
        >>>
        >>> # Check characteristic length scale
        >>> lc = screen.get_lc()
        >>>
        >>> # Get bounding box
        >>> r_bounds, z_bounds = screen.boundingBox()
    """

    yaml_tag = "Screen"

    def __init__(
        self,
        name: str,
        r: list[float],
        z: list[float],
    ):
        """
        Initialize a Screen object.

        Creates a cylindrical screening element with the specified geometry.

        Args:
            name: Unique identifier for the screen. Must follow standard naming
                  conventions (alphanumeric, underscores, hyphens).
            r: Radial bounds as [r_inner, r_outer] in millimeters.
               Must be a list of exactly 2 positive values with r_inner < r_outer.
            z: Axial bounds as [z_bottom, z_top] in millimeters.
               Must be a list of exactly 2 values with z_bottom < z_top.

        Example:
            >>> # Screen from r=50mm to r=60mm, z=0 to z=200mm
            >>> screen = Screen("shield_1", [50.0, 60.0], [0.0, 200.0])
            >>>
            >>> # Screen with negative z-coordinates (symmetric about z=0)
            >>> screen2 = Screen("shield_2", [40.0, 45.0], [-100.0, 100.0])
        """
        self.name = name
        self.r = r
        self.z = z

    def get_lc(self):
        """
        Calculate characteristic length scale for mesh generation.

        Returns a length scale suitable for finite element mesh sizing,
        based on the radial thickness of the screen.

        Returns:
            float: Characteristic length in millimeters (radial thickness / 10)

        Example:
            >>> screen = Screen("test", [100.0, 120.0], [0.0, 500.0])
            >>> lc = screen.get_lc()  # Returns 2.0 mm

        Notes:
            This is used as a hint for automatic mesh generation algorithms
            to create appropriately sized elements for this geometry.
        """
        return (self.r[1] - self.r[0]) / 10.0

    def get_channels(self, mname: str, hideIsolant: bool = True, debug: bool = False) -> list:
        """
        Get cooling channels for the screen.

        Currently returns an empty list as screens typically do not have
        internal cooling channels in the standard implementation.

        Args:
            mname: Parent magnet name for hierarchical naming
            hideIsolant: If True, hide insulation in the output (default: True)
            debug: Enable debug output (default: False)

        Returns:
            list: Empty list (screens have no cooling channels in current implementation)

        Example:
            >>> screen = Screen("shield", [100.0, 110.0], [0.0, 500.0])
            >>> channels = screen.get_channels("Insert1")
            >>> print(len(channels))  # 0

        Notes:
            This method exists for interface compatibility with other conductor
            classes (Helix, Bitter) that do have cooling channels. It may be
            extended in future versions if screen cooling becomes necessary.
        """
        return []

    def get_isolants(self, mname: str, debug: bool = False):
        """
        Get electrical isolation elements for the screen.

        Currently returns an empty list as screens are typically single
        conducting elements without internal insulation layers.

        Args:
            mname: Parent magnet name for hierarchical naming
            debug: Enable debug output (default: False)

        Returns:
            list: Empty list (screens have no isolants in current implementation)

        Example:
            >>> screen = Screen("shield", [100.0, 110.0], [0.0, 500.0])
            >>> isolants = screen.get_isolants("Insert1")
            >>> print(len(isolants))  # 0

        Notes:
            This method exists for interface compatibility with other conductor
            classes that may have insulation. Screens are typically modeled as
            single homogeneous conducting shells.
        """
        return []

    def get_names(self, mname: str, is2D: bool = False, verbose: bool = False) -> list[str]:
        """
        Get list of geometry part names for CAD/mesh markers.

        Returns a list of names used to identify this screen's geometry
        in CAD models, meshes, or visualization. Typically used for
        setting material properties or boundary conditions.

        Args:
            mname: Parent magnet name to prepend to part names.
                   If empty, no prefix is added.
            is2D: If True, generate names for 2D (axisymmetric) geometry.
                  If False, generate names for 3D geometry (default: False).
                  Currently this parameter is not used.
            verbose: If True, print debug information about generated names
                    (default: False)

        Returns:
            list[str]: List containing the single screen part name

        Example:
            >>> screen = Screen("outer_shield", [100.0, 110.0], [0.0, 500.0])
            >>>
            >>> # With parent magnet name
            >>> names = screen.get_names("M1")
            >>> print(names)  # ['M1_outer_shield_Screen']
            >>>
            >>> # Without parent magnet name
            >>> names = screen.get_names("")
            >>> print(names)  # ['outer_shield_Screen']
            >>>
            >>> # With verbose output
            >>> names = screen.get_names("M1", verbose=True)
            # Prints: Bitter/get_names: solid_names 1
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        solid_names.append(f"{prefix}{self.name}_Screen")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return f"{self.__class__.__name__}(name={self.name!r}, r={self.r!r}, z={self.z!r})"

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]

        return cls(name, r, z)

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not
        return False if empty, True otherwise
        """
        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])
        return r_overlap and z_overlap

    def _plot_geometry(self, ax, show_labels: bool = True, **kwargs):
        """
        Plot Screen geometry in 2D axisymmetric coordinates.

        Screens are typically displayed with distinct styling to differentiate
        them from active conductor elements.

        Args:
            ax: Matplotlib axes to draw on
            show_labels: If True, display screen name at center
            **kwargs: Styling options (color, alpha, linewidth, etc.)

        Example:
            >>> import matplotlib.pyplot as plt
            >>> screen = Screen("outer_shield", [100, 110], [0, 500])
            >>> fig, ax = plt.subplots()
            >>> screen._plot_geometry(ax, color='gray', alpha=0.4)
        """
        from matplotlib.patches import Rectangle

        # Get bounding box
        r_bounds, z_bounds = self.boundingBox()
        r_min, r_max = r_bounds[0], r_bounds[1]
        z_min, z_max = z_bounds[0], z_bounds[1]

        # Extract styling parameters with defaults (gray for screens)
        color = kwargs.get('color', 'lightgray')
        alpha = kwargs.get('alpha', 0.5)
        edgecolor = kwargs.get('edgecolor', 'dimgray')
        linewidth = kwargs.get('linewidth', 2.0)
        label = kwargs.get('label', self.name if show_labels else None)
        hatch = kwargs.get('hatch', '///')  # Hatching to distinguish screens

        # Create rectangle patch for screen
        width = r_max - r_min
        height = z_max - z_min
        rect = Rectangle(
            (r_min, z_min),
            width,
            height,
            facecolor=color,
            alpha=alpha,
            edgecolor=edgecolor,
            linewidth=linewidth,
            hatch=hatch,
            label=label
        )
        ax.add_patch(rect)

        # Update axis limits to include this geometry with some padding
        current_xlim = ax.get_xlim()
        current_ylim = ax.get_ylim()
        
        # Calculate padding (5% of geometry size)
        r_padding = width * 0.05
        z_padding = height * 0.05
        
        # Expand limits if needed (check if limits are default)
        if current_xlim == (0.0, 1.0):
            # Default limits, set based on geometry
            ax.set_xlim(r_min - r_padding, r_max + r_padding)
        else:
            # Expand existing limits
            ax.set_xlim(
                min(current_xlim[0], r_min - r_padding),
                max(current_xlim[1], r_max + r_padding)
            )
        
        if current_ylim == (0.0, 1.0):
            # Default limits, set based on geometry
            ax.set_ylim(z_min - z_padding, z_max + z_padding)
        else:
            # Expand existing limits
            ax.set_ylim(
                min(current_ylim[0], z_min - z_padding),
                max(current_ylim[1], z_max + z_padding)
            )

        # Add text label at center if requested
        if show_labels and 'label' not in kwargs:
            center_r = (r_min + r_max) / 2
            center_z = (z_min + z_max) / 2
            ax.text(
                center_r,
                center_z,
                self.name,
                ha='center',
                va='center',
                fontsize=9,
                style='italic',
                color='black'
            )
