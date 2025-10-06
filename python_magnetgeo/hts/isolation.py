#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Isolation - Multi-layer Isolation Structure

Defines isolation layers between pancake coils with configurable
radial position, widths, and heights for each layer.
"""

from dataclasses import dataclass, field
from typing import Union, Optional
from ..base import YAMLObjectBase


@dataclass
class Isolation(YAMLObjectBase):
    """
    Multi-layer isolation structure for HTS inserts.
    
    Represents isolation material between pancakes or double pancakes.
    Supports multiple layers with individual widths and heights.
    
    Attributes:
        r0 (float): Inner radius in millimeters [mm]
        w (list[float]): Width of each isolation layer [mm]
        h (list[float]): Height of each isolation layer [mm]
    
    Units:
        All dimensions in millimeters (mm).
    
    Example:
        >>> # Single layer isolation
        >>> iso = Isolation(r0=50.0, w=[10.0], h=[0.3])
        
        >>> # Multi-layer isolation
        >>> iso = Isolation(
        ...     r0=50.0,
        ...     w=[10.0, 5.0],  # Two layers with different widths
        ...     h=[0.3, 0.2]    # Two layers with different heights
        ... )
        >>> print(f"Total height: {iso.height} mm")
        >>> print(f"Number of layers: {iso.n_layers}")
        
        >>> # From dictionary
        >>> iso = Isolation.from_dict({
        ...     'r0': 50.0,
        ...     'w': [10.0, 5.0],
        ...     'h': [0.3, 0.2]
        ... })
    
    Notes:
        - Lists w and h must have the same length (number of layers)
        - Each layer can have different width and height
        - Total height is sum of all layer heights
        - Maximum width is max(w)
    """
    
    yaml_tag = "!Isolation"
    
    r0: float = 0.0
    w: list[float] = field(default_factory=lambda: [0.0])
    h: list[float] = field(default_factory=lambda: [0.0])
    
    def __post_init__(self):
        """Validate isolation structure after initialization."""
        # Ensure lists
        if not isinstance(self.w, list):
            self.w = [self.w]
        if not isinstance(self.h, list):
            self.h = [self.h]
        
        # Validation
        if self.r0 < 0:
            raise ValueError(f"Inner radius must be non-negative, got r0={self.r0}")
        
        if len(self.w) != len(self.h):
            raise ValueError(
                f"Width and height lists must have same length: "
                f"len(w)={len(self.w)}, len(h)={len(self.h)}"
            )
        
        if not self.w:
            raise ValueError("Isolation must have at least one layer")
        
        for i, (w_val, h_val) in enumerate(zip(self.w, self.h)):
            if w_val < 0:
                raise ValueError(f"Layer {i} width must be non-negative, got w={w_val}")
            if h_val < 0:
                raise ValueError(f"Layer {i} height must be non-negative, got h={h_val}")
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Isolation from dictionary.
        
        Args:
            values: Dictionary with 'r0', 'w', 'h' keys
            debug: Enable debug output (unused)
            
        Returns:
            New Isolation instance
            
        Example:
            >>> iso = Isolation.from_dict({
            ...     'r0': 50.0,
            ...     'w': [10.0],
            ...     'h': [0.3]
            ... })
        """
        w = values.get('w', [0.0])
        h = values.get('h', [0.0])
        
        # Handle single values
        if not isinstance(w, list):
            w = [w]
        if not isinstance(h, list):
            h = [h]
        
        return cls(
            r0=values.get('r0', 0.0),
            w=w,
            h=h
        )
    
    @property
    def inner_radius(self) -> float:
        """Inner radius in millimeters [mm]."""
        return self.r0
    
    @property
    def width(self) -> float:
        """
        Maximum width across all layers in millimeters [mm].
        
        Returns:
            max(w) - the widest layer width
        """
        return max(self.w) if self.w else 0.0
    
    @property
    def height(self) -> float:
        """
        Total height of all isolation layers in millimeters [mm].
        
        Returns:
            sum(h) - sum of all layer heights
        """
        return sum(self.h)
    
    @property
    def n_layers(self) -> int:
        """Number of isolation layers."""
        return len(self.w)
    
    @property
    def layer_widths(self) -> list[float]:
        """List of layer widths in millimeters [mm]."""
        return self.w.copy()
    
    @property
    def layer_heights(self) -> list[float]:
        """List of layer heights in millimeters [mm]."""
        return self.h.copy()
    
    def get_layer_width(self, i: int) -> float:
        """
        Get width of specific layer.
        
        Args:
            i: Layer index (0-based)
            
        Returns:
            Width of layer i in millimeters [mm]
            
        Raises:
            IndexError: If layer index out of range
        """
        return self.w[i]
    
    def get_layer_height(self, i: int) -> float:
        """
        Get height of specific layer.
        
        Args:
            i: Layer index (0-based)
            
        Returns:
            Height of layer i in millimeters [mm]
            
        Raises:
            IndexError: If layer index out of range
        """
        return self.h[i]
    
    def get_names(self, name: str, detail: Union[str, 'DetailLevel'], 
                  verbose: bool = False) -> str:
        """
        Get marker name for isolation.
        
        Args:
            name: Base name for marker
            detail: Detail level (not used for isolation - always single marker)
            verbose: Enable verbose output
            
        Returns:
            Marker name for isolation
        """
        return name
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        layers_str = "\n".join([
            f"    Layer {i}: w={w} mm, h={h} mm"
            for i, (w, h) in enumerate(zip(self.w, self.h))
        ])
        return (
            f"Isolation:\n"
            f"  Inner radius: {self.r0} mm\n"
            f"  Total height: {self.height} mm\n"
            f"  Max width: {self.width} mm\n"
            f"  Layers ({self.n_layers}):\n"
            f"{layers_str}"
        )
