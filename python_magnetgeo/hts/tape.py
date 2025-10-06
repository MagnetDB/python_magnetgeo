#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Tape - HTS Tape Geometry

Defines the geometry of High-Temperature Superconductor (HTS) tape including
width, height, and optional co-wound duromag thickness.
"""

from dataclasses import dataclass
from typing import Union, Optional
from ..base import YAMLObjectBase
from ..validation import GeometryValidator


@dataclass
class Tape(YAMLObjectBase):
    """
    HTS tape geometry with rectangular cross-section.
    
    Represents a High-Temperature Superconductor tape with defined dimensions.
    Used as the fundamental building block for pancake coils.
    
    Attributes:
        w (float): Tape width in millimeters [mm]
        h (float): Tape thickness/height in millimeters [mm]
        e (float): Co-wound duromag thickness in millimeters [mm] (default: 0.0)
    
    Units:
        All dimensions in millimeters (mm).
    
    Example:
        >>> # Standard 12mm HTS tape
        >>> tape = Tape(w=12.0, h=0.1, e=0.05)
        >>> print(f"Tape area: {tape.area} mm²")
        
        >>> # From dictionary
        >>> tape = Tape.from_dict({'w': 12.0, 'h': 0.1, 'e': 0.05})
        
        >>> # YAML serialization
        >>> tape.dump("my_tape.yaml")
        >>> loaded = Tape.from_yaml("my_tape.yaml")
    
    Notes:
        - Width (w) typically ranges from 4-12mm for commercial HTS tapes
        - Height (h) typically 0.1-0.2mm
        - Duromag (e) is optional insulation/protection layer
        - All values must be non-negative
    """
    
    yaml_tag = "!Tape"
    
    w: float = 0.0  # width [mm]
    h: float = 0.0  # height/thickness [mm]
    e: float = 0.0  # duromag thickness [mm]
    
    def __post_init__(self):
        """Validate tape dimensions after initialization."""
        if self.w < 0:
            raise ValueError(f"Tape width must be non-negative, got w={self.w}")
        if self.h < 0:
            raise ValueError(f"Tape height must be non-negative, got h={self.h}")
        if self.e < 0:
            raise ValueError(f"Duromag thickness must be non-negative, got e={self.e}")
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Tape from dictionary.
        
        Args:
            values: Dictionary with 'w', 'h', and optionally 'e' keys
            debug: Enable debug output (unused)
            
        Returns:
            New Tape instance
            
        Example:
            >>> tape = Tape.from_dict({'w': 12.0, 'h': 0.1, 'e': 0.05})
        """
        return cls(
            w=values.get('w', 0.0),
            h=values.get('h', 0.0),
            e=values.get('e', 0.0)
        )
    
    @property
    def width(self) -> float:
        """Tape width in millimeters [mm]."""
        return self.w
    
    @property
    def height(self) -> float:
        """Tape height/thickness in millimeters [mm]."""
        return self.h
    
    @property
    def duromag_thickness(self) -> float:
        """Co-wound duromag thickness in millimeters [mm]."""
        return self.e
    
    @property
    def area(self) -> float:
        """
        Cross-sectional area of tape in square millimeters [mm²].
        
        Returns:
            Area = w × h
        """
        return self.w * self.h
    
    def get_names(self, name: str, detail: Union[str, 'DetailLevel'], 
                  verbose: bool = False) -> list[str]:
        """
        Get marker names for tape elements.
        
        Args:
            name: Base name for marker
            detail: Detail level (not used for tape - leaf node)
            verbose: Enable verbose output
            
        Returns:
            List containing single marker name
        """
        return [name]
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Tape:\n"
            f"  width: {self.w} mm\n"
            f"  height: {self.h} mm\n"
            f"  duromag: {self.e} mm\n"
            f"  area: {self.area} mm²"
        )