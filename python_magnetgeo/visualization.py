#!/usr/bin/env python3
# encoding: UTF-8

"""
Visualization mixin for geometry classes.

Provides optional matplotlib-based 2D axisymmetric plotting functionality
for all geometry classes through a mixin pattern.

This module can be safely imported even if matplotlib is not installed.
The ImportError will only be raised when attempting to actually plot.

Classes:
    VisualizableMixin: Mixin class providing plot_axisymmetric() method

Example:
    >>> class MyGeometry(YAMLObjectBase, VisualizableMixin):
    ...     def _plot_geometry(self, ax, show_labels=True, **kwargs):
    ...         # Custom plotting implementation
    ...         pass
    ...
    >>> obj = MyGeometry(...)
    >>> ax = obj.plot_axisymmetric()  # Creates plot
    >>> plt.show()
"""

from abc import abstractmethod
from typing import Any, Optional

from .logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class VisualizableMixin:
    """
    Mixin class providing 2D axisymmetric visualization capabilities.

    This mixin adds matplotlib-based plotting functionality to geometry classes.
    Matplotlib is an optional dependency - it's only required when actually
    calling plot methods, not when importing the class.

    The mixin provides a high-level plot_axisymmetric() method that handles
    matplotlib setup and delegates to a class-specific _plot_geometry() method
    for rendering the actual geometry.

    Methods:
        plot_axisymmetric: Main plotting method (public API)
        _plot_geometry: Abstract method for class-specific rendering (protected)

    Design Pattern:
        - Template Method pattern: plot_axisymmetric() is the template,
          _plot_geometry() is the customization point
        - Subclasses must implement _plot_geometry() to define their rendering

    Usage:
        Classes should inherit from this mixin and implement _plot_geometry():

        >>> class Ring(YAMLObjectBase, VisualizableMixin):
        ...     def _plot_geometry(self, ax, show_labels=True, **kwargs):
        ...         r, z = self.boundingBox()
        ...         # Draw rectangle representing ring
        ...         from matplotlib.patches import Rectangle
        ...         rect = Rectangle((r[0], z[0]), r[1]-r[0], z[1]-z[0])
        ...         ax.add_patch(rect)

    Notes:
        - Matplotlib import is deferred until plot time
        - Graceful error message if matplotlib not installed
        - All kwargs are passed through to _plot_geometry() for customization
        - Supports both standalone plotting and subplot integration
    """

    def plot_axisymmetric(
        self,
        ax: Optional[Any] = None,
        show_labels: bool = True,
        show_legend: bool = True,
        title: Optional[str] = None,
        figsize: tuple[float, float] = (10, 12),
        **kwargs
    ) -> Any:
        """
        Plot geometry in 2D axisymmetric coordinates (r, z).

        Creates a matplotlib visualization of the geometry in cylindrical
        coordinates, showing the r-z plane cross-section. Suitable for
        axisymmetric geometries like magnets, coils, and rings.

        Args:
            ax: Optional matplotlib Axes object to plot on. If None, creates
                new figure and axes. Use this to create subplot layouts or
                overlay multiple geometries.
            show_labels: If True, display component names/labels on the plot.
                Default: True
            show_legend: If True, display legend for plotted components.
                Default: True
            title: Optional custom title for the plot. If None, uses class
                name and object name (if available). Default: None
            figsize: Figure size as (width, height) in inches, only used when
                creating new figure (ax=None). Default: (10, 12)
            **kwargs: Additional keyword arguments passed to _plot_geometry()
                for customization. Common options:
                - color: Line/fill color
                - alpha: Transparency (0-1)
                - linewidth: Line width
                - linestyle: Line style ('-', '--', '-.', ':')
                - facecolor: Fill color
                - edgecolor: Edge color
                - label: Custom label for legend

        Returns:
            matplotlib.axes.Axes: The axes object containing the plot.
                Can be used for further customization or to add more elements.

        Raises:
            ImportError: If matplotlib is not installed. Install with:
                pip install matplotlib

        Example:
            >>> # Simple standalone plot
            >>> ring = Ring("R1", [10, 20], [0, 50])
            >>> ax = ring.plot_axisymmetric()
            >>> plt.show()
            >>>
            >>> # Custom styling
            >>> ax = ring.plot_axisymmetric(
            ...     color='blue',
            ...     alpha=0.5,
            ...     linewidth=2,
            ...     title="Ring Geometry"
            ... )
            >>>
            >>> # Multiple geometries on same axes
            >>> fig, ax = plt.subplots()
            >>> ring1.plot_axisymmetric(ax=ax, color='red', label='Ring 1')
            >>> ring2.plot_axisymmetric(ax=ax, color='blue', label='Ring 2')
            >>> plt.legend()
            >>> plt.show()
            >>>
            >>> # Subplot layout
            >>> fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            >>> insert.plot_axisymmetric(ax=ax1, title='Insert')
            >>> bitter.plot_axisymmetric(ax=ax2, title='Bitter')
            >>> plt.tight_layout()
            >>> plt.show()

        Notes:
            - Coordinate system: r (horizontal) = radial, z (vertical) = axial
            - Aspect ratio is set to 'equal' for correct geometry representation
            - Grid is enabled by default for easier reading
            - For collection classes (Insert, MSite, etc.), plots all components
        """
        # Import matplotlib only when needed (optional dependency)
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            raise ImportError(
                "Matplotlib is required for visualization functionality.\n"
                "Install it with: pip install matplotlib\n"
                "Or install with visualization support: pip install python_magnetgeo[viz]"
            ) from e

        # Create new figure and axes if not provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            logger.debug(f"Created new figure with size {figsize}")
        else:
            logger.debug("Using provided axes for plotting")

        # Set title
        if title is None and hasattr(self, 'name'):
            title = f"{self.__class__.__name__}: {self.name}"
        elif title is None:
            title = f"{self.__class__.__name__}"
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')

        # Delegate to class-specific plotting implementation
        logger.debug(f"Plotting {self.__class__.__name__} geometry")
        self._plot_geometry(ax, show_labels=show_labels, **kwargs)

        # Configure axes
        ax.set_xlabel('Radius r (mm)', fontsize=12)
        ax.set_ylabel('Axial Position z (mm)', fontsize=12)
        
        # Set aspect ratio after plotting (when limits are established)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        # Add legend if requested and there are labeled elements
        if show_legend:
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(loc='best', fontsize=10)

        logger.info(f"Successfully plotted {self.__class__.__name__}")
        return ax

    @abstractmethod
    def _plot_geometry(self, ax: Any, show_labels: bool = True, **kwargs) -> None:
        """
        Abstract method for class-specific geometry rendering.

        This method must be implemented by each class that uses VisualizableMixin.
        It should add the appropriate matplotlib artists (patches, lines, etc.)
        to the provided axes to represent the geometry.

        Args:
            ax: Matplotlib Axes object to draw on
            show_labels: Whether to show labels/annotations for this geometry
            **kwargs: Additional styling parameters (color, alpha, linewidth, etc.)

        Implementation Guidelines:
            1. Use self.boundingBox() or similar methods to get geometry data
            2. Create matplotlib patches/lines to represent the shape
            3. Add artists to ax using ax.add_patch(), ax.plot(), etc.
            4. Respect show_labels to conditionally add text annotations
            5. Use kwargs for customization (color, alpha, linewidth, etc.)
            6. For collections, iterate and plot each component
            7. Set appropriate default colors/styles if kwargs not provided

        Example Implementation (Ring):
            >>> def _plot_geometry(self, ax, show_labels=True, **kwargs):
            ...     from matplotlib.patches import Rectangle
            ...     r, z = self.boundingBox()
            ...     width = r[1] - r[0]
            ...     height = z[1] - z[0]
            ...     
            ...     # Default styling
            ...     color = kwargs.get('color', 'steelblue')
            ...     alpha = kwargs.get('alpha', 0.6)
            ...     
            ...     # Create and add rectangle
            ...     rect = Rectangle(
            ...         (r[0], z[0]), width, height,
            ...         facecolor=color, alpha=alpha,
            ...         edgecolor='black', linewidth=1
            ...     )
            ...     ax.add_patch(rect)
            ...     
            ...     # Add label if requested
            ...     if show_labels:
            ...         ax.text(
            ...             (r[0] + r[1]) / 2,
            ...             (z[0] + z[1]) / 2,
            ...             self.name,
            ...             ha='center', va='center'
            ...         )

        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _plot_geometry() method "
            "to provide visualization functionality"
        )
