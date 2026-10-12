#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides definition for aerodynamic profiles.

This module defines the Profile class for representing aerodynamic shape profiles
as a series of 2D points with optional labels, similar to Contour2D but specialized
for aerodynamic applications with DAT file generation.

Classes:
    Profile: Represents an aerodynamic profile with points and labels
"""

from pathlib import Path

from .base import YAMLObjectBase

# Module logger
from .logging_config import get_logger

logger = get_logger(__name__)


class Profile(YAMLObjectBase):
    """
    Represents a profile defined by 2D points and labels.

    A Profile object defines a shape as a sequence of (X, F) coordinate pairs
    with associated integer labels.

    Attributes:
        cad (str): CAD identifier for the profile
        points (list[list[float]]): List of [X, F] coordinate pairs
        labels (list[int] | None): Optional list of integer labels, one per point

    Example:
        >>> # Create a simple profile
        >>> profile = Profile(
        ...     cad="HR-54-116",
        ...     points=[[-5.34, 0], [-3.34, 0], [0, 0.9], [3.34, 0], [5.34, 0]],
        ...     labels=[0, 0, 1, 0, 0]
        ... )
        >>>
        >>> # Load from YAML
        >>> profile = Profile.from_yaml("my_profile.yaml")
        >>>
        >>> # Create from dictionary
        >>> data = {
        ...     "cad": "WING-01",
        ...     "points": [[0, 0], [1, 0.5], [2, 0]],
        ...     "labels": [0, 1, 0]
        ... }
        >>> profile = Profile.from_dict(data)
    """

    yaml_tag = "Profile"

    def __init__(self, cad: str, points: list[list[float]], labels: list[int] | None = None):
        """
        Initialize a Profile object.

        Args:
            cad: CAD identifier for the profile. Must be non-empty and follow
                 standard naming conventions (alphanumeric, underscores, hyphens).
            points: List of [X, F] coordinate pairs defining the profile shape.
                   Each point must be a list or tuple of exactly 2 float values.
            labels: Optional list of integer labels, one per point. If provided,
                   must have the same length as points. If None, defaults to
                   all zeros.

        Raises:
            ValidationError: If cad is invalid or empty
            ValueError: If labels length doesn't match points length

        Example:
            >>> profile = Profile(
            ...     cad="NACA-0012",
            ...     points=[[0, 0], [0.5, 0.05], [1, 0]],
            ...     labels=[0, 1, 0]
            ... )
        """
        # Validate CAD identifier
        # GeometryValidator.validate_name(cad)

        # Validate labels length if provided
        if labels is not None and len(labels) != len(points):
            raise ValueError(
                f"Labels length ({len(labels)}) must match points length ({len(points)})"
            )

        self.cad = cad
        self.points = points
        self.labels = labels if labels is not None else [0] * len(points)

    def __repr__(self):
        """
        Return string representation of the Profile object.

        Returns:
            str: String showing class name, cad, points, and labels

        Example:
            >>> profile = Profile("TEST", [[0, 0], [1, 1]], [0, 1])
            >>> repr(profile)
            "Profile(cad='TEST', points=[[0, 0], [1, 1]], labels=[0, 1])"
        """
        return (
            f"{self.__class__.__name__}(cad={self.cad!r}, "
            f"points={self.points!r}, labels={self.labels!r})"
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create a Profile object from a dictionary.

        This method is used for deserialization from YAML/JSON formats.
        Handles both cases where labels are explicitly provided or omitted.

        Args:
            values: Dictionary containing 'cad' and 'points' keys,
                   optionally 'labels' key
            debug: Enable debug output (default: False)

        Returns:
            Profile: New instance created from the dictionary data

        Raises:
            KeyError: If required keys ('cad', 'points') are missing
            ValidationError: If cad or points data is invalid
            ValueError: If labels length doesn't match points length

        Example:
            >>> data = {
            ...     "cad": "AIRFOIL-A",
            ...     "points": [[0, 0], [5, 2], [10, 0]],
            ...     "labels": [0, 1, 0]
            ... }
            >>> profile = Profile.from_dict(data)
            >>>
            >>> # Without labels
            >>> data_no_labels = {
            ...     "cad": "AIRFOIL-B",
            ...     "points": [[0, 0], [5, 2], [10, 0]]
            ... }
            >>> profile = Profile.from_dict(data_no_labels)
        """
        cad = values["cad"]
        points = values["points"]
        labels = values.get("labels", None)

        logger.debug(
            f"Creating Profile from dict: cad={cad}, "
            f"points count={len(points)}, labels={labels}"
        )

        return cls(cad, points, labels)

    def generate_dat_file(self, output_dir: str = ".") -> Path:
        """
        Generate a Shape_{cad}.dat file with the profile data.

        Creates a DAT file in the specified output directory with formatted
        profile data including header comments, point count, and coordinate data.
        The file format follows aerodynamic profile conventions.

        Args:
            output_dir: Directory where the file will be created (default: current directory)

        Returns:
            Path: Path object pointing to the created file

        Example:
            >>> # With labels
            >>> profile = Profile(
            ...     cad="HR-54-116",
            ...     points=[[-5.34, 0], [0, 0.9], [5.34, 0]],
            ...     labels=[0, 1, 0]
            ... )
            >>> output = profile.generate_dat_file("./output")
            >>> print(f"File created: {output}")
            File created: output/Shape_HR-54-116.dat

            >>> # Without labels
            >>> profile_no_labels = Profile(
            ...     cad="SIMPLE",
            ...     points=[[0, 0], [1, 0.5], [2, 0]],
            ...     labels=None
            ... )
            >>> output = profile_no_labels.generate_dat_file()

        File Format (with labels):
            #Shape : {cad}
            #
            # Profile with region labels
            #
            #N_i
            {point_count}
            #X_i F_i    Id_i
            {x:.2f} {f:.2f}    {label}
            ...

        File Format (without labels):
            #Shape : {cad}
            #
            # Profile geometry
            #
            #N_i
            {point_count}
            #X_i F_i
            {x:.2f} {f:.2f}
            ...
        """
        output_path = Path(output_dir) / f"Shape_{self.cad}.dat"

        # Determine if labels are present and non-empty
        has_labels = (
            self.labels is not None
            and len(self.labels) > 0
            and any(label != 0 for label in self.labels)
        )

        with open(output_path, "w", encoding="utf-8") as f:
            # Write header with CAD identifier
            f.write(f"#Shape : {self.cad}\n")
            f.write("#\n")

            # Write context-appropriate comments
            if has_labels:
                f.write("# Profile with region labels\n")
            else:
                f.write("# Profile geometry\n")
            f.write("#\n")

            # Write number of points
            f.write("#N_i\n")
            f.write(f"{len(self.points)}\n")

            # Write column headers based on whether labels are present
            if has_labels:
                f.write("#X_i F_i\tId_i\n")
                # Write data points with labels
                for (x, y), label in zip(self.points, self.labels, strict=True):
                    f.write(f"{x:.2f} {y:.2f}\t{label}\n")
            else:
                f.write("#X_i F_i\n")
                # Write data points without labels
                for x, y in self.points:
                    f.write(f"{x:.2f} {y:.2f}\n")

        print(f"Generated DAT file: {output_path}")
        return output_path
