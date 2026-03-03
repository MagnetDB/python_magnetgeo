#!/usr/bin/env python3

"""
Provides definition for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
* Chamfers:
* Grooves:
"""

import math
import os

from .base import YAMLObjectBase
from .Chamfer import Chamfer
from .Groove import Groove
from .hcuts import create_cut
from .Model3D import Model3D
from .ModelAxi import ModelAxi
from .Shape import Shape
from .validation import GeometryValidator, ValidationError

from .logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

class Helix(YAMLObjectBase):
    """
    Helix geometry class representing a helical magnet coil.

    Attributes:
        name (str): Unique identifier for the helix
        r (list[float]): Radial bounds [r_inner, r_outer] in mm
        z (list[float]): Axial bounds [z_bottom, z_top] in mm
        cutwidth (float): Width of helical cut in mm
        odd (bool): Odd layer indicator
        dble (bool): Double layer indicator
        modelaxi (ModelAxi): Axisymmetric model definition
        model3d (Model3D): 3D CAD model configuration
        shape (Shape): Cross-sectional shape definition
        chamfers (list): List of Chamfer objects for edge modifications
        grooves (Groove): Groove configuration for cooling channels

    """

    yaml_tag = "Helix"

    def __init__(
        self,
        name: str,
        r: list[float],
        z: list[float],
        cutwidth: float,
        odd: bool,
        dble: bool,
        modelaxi: ModelAxi = None,
        model3d: Model3D = None,
        shape: Shape = None,
        chamfers: list = None,
        grooves: Groove = None,
        start_hole_diameter: float = 0.0,
    ) -> None:
        """
        Initialize a Helix object with validation.

        Args:
            name: Unique identifier for the helix
            r: Radial bounds [r_inner, r_outer] in mm, must be ascending
            z: Axial bounds [z_bottom, z_top] in mm, must be ascending
            cutwidth: Width of helical cut in mm
            odd: True if odd layer, False otherwise
            dble: True if double layer, False otherwise
            modelaxi: Axisymmetric model definition for helical cut
            model3d: 3D CAD model configuration
            shape: Cross-sectional shape definition
            chamfers: Optional list of Chamfer objects for edge modifications
            grooves: Optional Groove object for cooling channel definition

        Raises:
            ValidationError: If validation fails for name, r, z, or modelaxi.h constraint
        """
        # General validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
        GeometryValidator.validate_ascending_order(r, "r")

        GeometryValidator.validate_numeric_list(z, "z", expected_length=2)
        GeometryValidator.validate_ascending_order(z, "z")

        self.name = name
        self.dble = dble
        self.odd = odd
        self.r = r
        self.z = z
        self.cutwidth = cutwidth
        self.start_diameter_hole = start_hole_diameter

        if modelaxi is not None and isinstance(modelaxi, str):
            self.modelaxi = ModelAxi.from_yaml(f"{modelaxi}.yaml")
        else:
            self.modelaxi = modelaxi

        if model3d is not None and isinstance(model3d, str):
            self.model3d = Model3D.from_yaml(f"{model3d}.yaml")
        else:
            self.model3d = model3d

        if shape is not None and isinstance(shape, str) and shape.strip():
            self.shape = Shape.from_yaml(f"{shape}.yaml")
        elif isinstance(shape, str) and not shape.strip():
            self.shape = None
        else:
            self.shape = shape

        self.chamfers = []
        if chamfers is not None:
            for chamfer in chamfers:
                if isinstance(chamfer, str):
                    self.chamfers.append(Chamfer.from_yaml(f"{chamfer}.yaml"))
                else:
                    self.chamfers.append(chamfer)

        if grooves is not None and isinstance(grooves, str):
            if isinstance(grooves, str):
                self.grooves = Groove.from_yaml(f"{grooves}.yaml")
        else:
            self.grooves = grooves

        # validation for groove
        if self.grooves is not None:
            if self.grooves.gtype == "rint":
                if self.grooves.n * self.grooves.eps > 2 * math.pi * self.r[0]:
                    raise ValidationError(
                        f"Groove: {self.grooves.n} of eps={self.grooves.eps} exceed circumference on rint"
                    )
            if self.grooves.gtype == "rext":
                if self.grooves.n * self.grooves.eps > 2 * math.pi * self.r[1]:
                    raise ValidationError(
                        f"Groove: {self.grooves.n} of eps={self.grooves.eps} exceed circumference on rext"
                    )

        self.start_hole_diameter = start_hole_diameter

        # add check for self.modelaxi.h must be less than (z[1]-z[0])/2.
        if self.modelaxi is not None and self.modelaxi.h > (z[1] - z[0]) / 2.0:
            raise ValidationError(
                f"modelaxi.h ({self.modelaxi.h}) must be less than half the helix height ({(z[1]-z[0])/2.0})"
            )

        # Store the directory context for resolving struct paths
        self._basedir = os.getcwd()

    def get_type(self) -> str:
        """
        Determine the helix type based on 3D model configuration.

        Returns:
            str: "HR" if model has both shapes and channels, "HL" otherwise

        Notes:
            - HR (Helix with Reinforcement): Includes shaped channels
            - HL (Helix Layer): Standard helical layer
        """
        if self.model3d.with_shapes and self.model3d.with_channels:
            return "HR"
        return "HL"

    def get_lc(self) -> float:
        """
        Calculate characteristic length for mesh generation.

        Returns:
            float: Characteristic length computed as radial thickness / 10

        Notes:
            Used by mesh generators to determine appropriate element size
        """
        return (self.r[1] - self.r[0]) / 10.0

    def get_names(self, mname: str, is2D: bool, verbose: bool = False) -> list[str]:
        """
        Generate marker names for mesh identification.

        Args:
            mname: Prefix for marker names (typically parent magnet name)
            is2D: True for 2D axisymmetric mesh, False for 3D mesh
            verbose: Enable verbose output for debugging

        Returns:
            list[str]: List of marker names for conductor and insulator regions

        Notes:
            - 2D mesh: Returns section-wise names (Cu0, Cu1, ..., CuN)
            - 3D mesh: Returns single Cu conductor and insulator names
            - Insulator type depends on helix type (Glue for HL, Kapton for HR)
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        sInsulator = "Glue"
        nInsulators = 0
        nturns = self.get_Nturns()
        htype = self.get_type()
        if htype == "HR":
            sInsulator = "Kapton"
            angle = self.shape.angle
            nshapes = nturns * (360 / float(angle[0]))  # only one angle to be checked
            if verbose:
                logger.info("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

            nshapes = (
                lambda x: (math.ceil(x) if math.ceil(x) - x < x - math.floor(x) else math.floor(x))
            )(nshapes)
            nInsulators = int(nshapes)
            logger.info("nKaptons=", nInsulators)
        else:
            nInsulators = 1
            if self.dble:
                nInsulators = 2
            if verbose:
                logger.info("helix:", self.name, htype, nturns)

        if is2D:
            nsection = len(self.modelaxi.turns)
            solid_names.append(f"{prefix}Cu{0}")  # HP
            for j in range(nsection):
                solid_names.append(f"{prefix}Cu{j+1}")
            solid_names.append(f"{prefix}Cu{nsection+1}")  # BP
        else:
            solid_names.append("Cu")
            # TODO tell HR from HL
            for j in range(nInsulators):
                solid_names.append(f"{sInsulator}{j}")

        if verbose:
            logger.info(f"Helix_Gmsh[{htype}]: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        Generate string representation of Helix object.

        Returns:
            str: String representation including all parameters
        """
        msg = f"{self.__class__.__name__}(name={self.name},odd={self.odd},dble={self.dble},r={self.r},z={self.z},cutwidth={self.cutwidth},modelaxi={self.modelaxi},model3d={self.model3d},shape={self.shape}"
        if hasattr(self, "chamfers"):
            msg += f",chamfers={self.chamfers}"
        else:
            msg += ",chamfers=None"
        if hasattr(self, "grooves"):
            msg += f",grooves={self.grooves}"
        else:
            msg += ",grooves=None"
        msg += ")"
        return msg

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Helix instance from dictionary representation.

        Args:
            values: Dictionary containing helix parameters
            debug: Enable debug output during deserialization

        Returns:
            Helix: New Helix instance

        Notes:
            Handles nested objects (modelaxi, model3d, shape, chamfers, grooves)
            by loading from files or instantiating from dicts
        """
        logger.debug(f"Helix.from_dict: values keys={list(values.keys())}")
        modelaxi = cls._load_nested_single(values.get("modelaxi"), ModelAxi, debug=debug)
        model3d = cls._load_nested_single(values.get("model3d"), Model3D, debug=debug)
        shape = cls._load_nested_single(values.get("shape"), Shape, debug=debug)
        chamfers = cls._load_nested_list(values.get("chamfers"), Chamfer, debug=debug)
        grooves = cls._load_nested_single(values.get("grooves"), Groove, debug=debug)

        name = values["name"]
        r = values["r"]
        z = values["z"]
        odd = values["odd"]
        dble = values["dble"]
        cutwidth = values["cutwidth"]
        start_diameter_hole = values.get("start_diameter_hole", 0.0)

        object = cls(
            name,
            r,
            z,
            cutwidth,
            odd,
            dble,
            modelaxi,
            model3d,
            shape,
            chamfers,
            grooves,
            start_diameter_hole,
        )
        # object.update()
        return object

    @classmethod
    def _analyze_nested_dependencies(cls, values: dict, required_files: set, debug: bool = False):
        """
        Analyze nested dependencies specific to Helix class.

        Identifies files that would be loaded for modelaxi, model3d, shape,
        chamfers, and grooves nested objects.

        Args:
            values: Dictionary containing helix parameters
            required_files: Set to populate with file paths (modified in place)
            debug: Enable debug output
        """
        if debug:
            logger.info("  Analyzing Helix nested dependencies...")

        # Analyze single nested objects
        cls._analyze_single_dependency(
            values.get("modelaxi"), ModelAxi, required_files, debug=debug
        )
        cls._analyze_single_dependency(values.get("model3d"), Model3D, required_files, debug=debug)
        cls._analyze_single_dependency(values.get("shape"), Shape, required_files, debug=debug)
        cls._analyze_single_dependency(values.get("grooves"), Groove, required_files, debug=debug)

        # Analyze list of nested objects
        cls._analyze_list_dependency(values.get("chamfers"), Chamfer, required_files, debug=debug)

    def getModelAxi(self):
        """
        Get the axisymmetric model definition.

        Returns:
            ModelAxi: Axisymmetric model object
        """
        return self.modelaxi

    def getModel3D(self):
        """
        Get the 3D CAD model configuration.

        Returns:
            Model3D: 3D model configuration object
        """
        return self.model3d

    def get_Nturns(self) -> float:
        """
        Get the number of turns in the helix.

        Returns:
            float: Number of turns from the axisymmetric model

        Notes:
            Delegates to modelaxi.get_Nturns() method
        """
        return self.modelaxi.get_Nturns()

    def generate_cut(self, format: str = "SALOME"):
        """
        Generate helical cut geometry file for CAD system.

        Args:
            format: Target CAD format (default: "SALOME")

        Notes:
            Creates helical cut definition file and optionally adds shapes
            if model3d.with_shapes is enabled. Uses external MagnetTools utilities.
        """

        create_cut(self, format, self.name)
        if self.model3d.with_shapes:

            # if Profile class is used: self.shape.profile.generate_dat_file()
            if self.shape is not None and self.shape.profile is not None:
                    self.shape.profile.generate_dat_file(self._basedir)
                    shape_profile = f"{self._basedir}/Shape_{self.shape.cad}.dat"
            else:
                return

            if self.get_type() == "HL":
                angles = " ".join(f"{t:4.2f}" for t in self.shape.angle if t != 0)
                cmd = f'add_shape --angle="{angles}" --shape_angular_length={self.shape.length} --shape={shape_profile} --format={format} --position="{self.shape.position} {self.name}"'
                logger.info(f"create_cut: with_shapes not implemented - shall run {cmd}")
            else:
                angles = " ".join(f"{t:4.2f}" for t in self.shape.angle if t != 0)
                cmd = f'add_shape --angle="{angles[0]}" --shape_angular_length={self.shape.length[0]} --shape={shape_profile} --format={format} --position="{self.shape.position} {self.name}"'
                logger.info(f"create_cut: with_shapes not implemented - shall run {cmd}")
            try:
                import subprocess

                subprocess.run(cmd, shell=True, check=True)
            except RuntimeError as e:
                raise Exception(f"cannot run add_shape properly: {e}") from e

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if this helix intersects with a given rectangular region.

        Args:
            r: Radial bounds [r_min, r_max] of test region
            z: Axial bounds [z_min, z_max] of test region

        Returns:
            bool: True if regions overlap, False if no intersection

        Notes:
            Uses axis-aligned bounding box intersection test
        """

        r_overlap = max(self.r[0], r[0]) < min(self.r[1], r[1])
        z_overlap = max(self.z[0], z[0]) < min(self.z[1], z[1])

        return r_overlap and z_overlap

    def boundingBox(self) -> tuple:
        """
        Get the bounding box of the helix geometry.

        Returns:
            tuple: (r_bounds, z_bounds) where each is [min, max]

        Notes:
            Currently excludes current leads from bounding box calculation
        """
        return (self.r, self.z)

    def insulators(self):
        """
        Determine insulator material and count based on helix type.

        Returns:
            tuple: (insulator_name, count) where:
                - insulator_name: "Glue" for HL type, "Kapton" for HR type
                - count: Number of insulator regions

        Notes:
            - HL type: 1 or 2 insulators depending on dble flag
            - HR type: Calculated based on shape angular coverage and turns
        """

        sInsulator = "Glue"
        nInsulators = 0
        htype = self.get_type()
        if htype == "HL":
            nInsulators = 2 if self.dble else 1
        else:
            sInsulator = "Kapton"
            angle = self.shape.angle
            nshapes = self.get_Nturns() * (360 / float(angle[0]))
            # logger.info("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

            nshapes = (
                lambda x: (math.ceil(x) if math.ceil(x) - x < x - math.floor(x) else math.floor(x))
            )(nshapes)
            nInsulators = int(nshapes)
            # logger.info("nKaptons=", nInsulators)

        return (sInsulator, nInsulators)

    def _plot_geometry(self, ax, show_labels: bool = True, **kwargs):
        """
        Plot Helix geometry in 2D axisymmetric coordinates.

        Renders the helix as a rectangle in the r-z plane, with an optional
        modelaxi zone showing the helical cut region centered at z=0.

        Args:
            ax: Matplotlib axes to draw on
            show_labels: If True, display helix name at center
            **kwargs: Styling options (color, alpha, linewidth, etc.)
                Special kwargs:
                - show_modelaxi: If True, display modelaxi zone (default: True)
                - modelaxi_color: Color for modelaxi zone (default: 'orange')
                - modelaxi_alpha: Transparency for modelaxi zone (default: 0.3)

        Example:
            >>> import matplotlib.pyplot as plt
            >>> helix = Helix("H1", [50, 60], [0, 100], 5.0, True, False, modelaxi)
            >>> fig, ax = plt.subplots()
            >>> helix._plot_geometry(ax, color='green', alpha=0.5)
        """
        from matplotlib.patches import Rectangle

        # Get bounding box
        r_bounds, z_bounds = self.r, self.z
        r_min, r_max = r_bounds[0], r_bounds[1]
        z_min, z_max = z_bounds[0], z_bounds[1]

        # Extract styling parameters with defaults
        color = kwargs.get('color', 'darkgreen')
        alpha = kwargs.get('alpha', 0.6)
        edgecolor = kwargs.get('edgecolor', 'black')
        linewidth = kwargs.get('linewidth', 1.5)
        label = kwargs.get('label', self.name if show_labels else None)
        
        # ModelAxi zone parameters
        show_modelaxi = kwargs.get('show_modelaxi', True)
        modelaxi_color = kwargs.get('modelaxi_color', 'orange')
        modelaxi_alpha = kwargs.get('modelaxi_alpha', 0.3)

        # Create rectangle patch for main helix
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
            label=label
        )
        ax.add_patch(rect)

        # Plot modelaxi zone if requested and available
        if show_modelaxi and self.modelaxi is not None and hasattr(self.modelaxi, 'h'):
            h = self.modelaxi.h
            # ModelAxi zone: from -h to +h on z-axis, same r dimensions
            modelaxi_rect = Rectangle(
                (r_min, -h),
                width,
                2 * h,  # Total height from -h to +h
                facecolor=modelaxi_color,
                alpha=modelaxi_alpha,
                edgecolor='darkorange',
                linewidth=1.0,
                linestyle='--',
                label=f'{self.name}_modelaxi' if show_labels else None
            )
            ax.add_patch(modelaxi_rect)

        # Update axis limits to include this geometry with some padding
        current_xlim = ax.get_xlim()
        current_ylim = ax.get_ylim()
        
        # Calculate padding (5% of geometry size)
        r_padding = width * 0.05
        z_padding = height * 0.05
        
        # Also consider modelaxi zone for y limits
        if show_modelaxi and self.modelaxi is not None and hasattr(self.modelaxi, 'h'):
            z_min_total = min(z_min, -self.modelaxi.h)
            z_max_total = max(z_max, self.modelaxi.h)
        else:
            z_min_total = z_min
            z_max_total = z_max
        
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
            ax.set_ylim(z_min_total - z_padding, z_max_total + z_padding)
        else:
            # Expand existing limits
            ax.set_ylim(
                min(current_ylim[0], z_min_total - z_padding),
                max(current_ylim[1], z_max_total + z_padding)
            )

        # Add text label at center if requested and no custom label
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
                fontweight='bold',
                color='white' if alpha > 0.5 else 'black'
            )
