#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
DoublePancake - Double Pancake Structure

Defines a double pancake structure consisting of two identical pancakes
separated by an isolation layer, with axial positioning.
"""

from dataclasses import dataclass
from typing import Union, Optional
from ..base import YAMLObjectBase
from ..utils import flatten
from .pancake import Pancake
from .isolation import Isolation


@dataclass
class DoublePancake(YAMLObjectBase):
    """
    Double pancake structure with two pancakes and isolation.
    
    Represents two identical pancake coils separated by an isolation layer,
    with defined axial position (z0 at center of isolation).
    
    Attributes:
        z0 (float): Axial position at center of structure in millimeters [mm]
        pancake (Pancake): Pancake coil structure (used for both pancakes)
        isolation (Isolation): Isolation between the two pancakes
    
    Units:
        All dimensions in millimeters (mm).
    
    Example:
        >>> # Create components
        >>> tape = Tape(w=12.0, h=0.1, e=0.05)
        >>> pancake = Pancake(r0=50.0, n=100, mandrin=2.0, tape=tape)
        >>> isolation = Isolation(r0=50.0, w=[10.0], h=[0.3])
        
        >>> # Create double pancake
        >>> dp = DoublePancake(z0=100.0, pancake=pancake, isolation=isolation)
        >>> print(f"Total height: {dp.height} mm")
        >>> print(f"Z bounds: [{dp.z_min}, {dp.z_max}] mm")
        
        >>> # From dictionary
        >>> dp = DoublePancake.from_dict({
        ...     'z0': 100.0,
        ...     'pancake': {...},
        ...     'isolation': {...}
        ... })
    
    Notes:
        - Structure is symmetric: pancake | isolation | pancake
        - Total height = 2 * pancake.height + isolation.height
        - z0 is at center of isolation layer
        - Both pancakes are identical (same geometry)
    """
    
    yaml_tag = "!DoublePancake"
    
    z0: float = 0.0
    pancake: Pancake = None
    isolation: Isolation = None
    
    def __post_init__(self):
        """Validate double pancake structure after initialization."""
        if self.pancake is None:
            raise ValueError("DoublePancake must have a pancake specification")
        
        if self.isolation is None:
            raise ValueError("DoublePancake must have an isolation specification")
        
        if not isinstance(self.pancake, Pancake):
            raise TypeError(f"pancake must be a Pancake instance, got {type(self.pancake)}")
        
        if not isinstance(self.isolation, Isolation):
            raise TypeError(f"isolation must be an Isolation instance, got {type(self.isolation)}")
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create DoublePancake from dictionary.
        
        Args:
            values: Dictionary with 'z0', 'pancake', 'isolation' keys
            debug: Enable debug output (unused)
            
        Returns:
            New DoublePancake instance
            
        Example:
            >>> dp = DoublePancake.from_dict({
            ...     'z0': 100.0,
            ...     'pancake': {'r0': 50.0, 'n': 100, ...},
            ...     'isolation': {'r0': 50.0, 'w': [10.0], ...}
            ... })
        """
        # Handle pancake
        pancake_data = values.get('pancake')
        if isinstance(pancake_data, Pancake):
            pancake = pancake_data
        elif isinstance(pancake_data, dict):
            pancake = Pancake.from_dict(pancake_data)
        else:
            raise ValueError(f"Invalid pancake specification: {pancake_data}")
        
        # Handle isolation
        isolation_data = values.get('isolation')
        if isinstance(isolation_data, Isolation):
            isolation = isolation_data
        elif isinstance(isolation_data, dict):
            isolation = Isolation.from_dict(isolation_data)
        else:
            raise ValueError(f"Invalid isolation specification: {isolation_data}")
        
        return cls(
            z0=values.get('z0', 0.0),
            pancake=pancake,
            isolation=isolation
        )
    
    @property
    def r0(self) -> float:
        """Inner radius in millimeters [mm] (from pancake)."""
        return self.pancake.r0
    
    @property
    def inner_radius(self) -> float:
        """Inner radius in millimeters [mm]."""
        return self.r0
    
    @property
    def r1(self) -> float:
        """Outer radius in millimeters [mm] (from pancake)."""
        return self.pancake.r1
    
    @property
    def outer_radius(self) -> float:
        """Outer radius in millimeters [mm]."""
        return self.r1
    
    @property
    def width(self) -> float:
        """Radial build in millimeters [mm]."""
        return self.pancake.width
    
    @property
    def height(self) -> float:
        """
        Total height of double pancake in millimeters [mm].
        
        Returns:
            height = 2 * pancake.height + isolation.height
        """
        return 2.0 * self.pancake.height + self.isolation.height
    
    @property
    def z_min(self) -> float:
        """
        Bottom axial position in millimeters [mm].
        
        Returns:
            z_min = z0 - height/2
        """
        return self.z0 - self.height / 2.0
    
    @property
    def z_max(self) -> float:
        """
        Top axial position in millimeters [mm].
        
        Returns:
            z_max = z0 + height/2
        """
        return self.z0 + self.height / 2.0
    
    @property
    def area(self) -> float:
        """
        Cross-sectional area in square millimeters [mm²].
        
        Returns:
            area = (r1 - r0) * height
        """
        return (self.r1 - self.r0) * self.height
    
    @property
    def filling_factor(self) -> float:
        """
        Tape filling factor for the double pancake.
        
        Returns:
            ratio = (2 * n_tapes * tape_area) / total_area
        """
        if self.area == 0:
            return 0.0
        n_tapes = 2 * self.pancake.n
        tape_area = self.pancake.tape.area
        total_tape_area = n_tapes * tape_area
        return total_tape_area / self.area
    
    def get_names(self, name: str, detail: Union[str, 'DetailLevel'], 
                  verbose: bool = False) -> Union[str, list[str]]:
        """
        Get marker names for double pancake elements.
        
        Args:
            name: Base name for markers
            detail: Detail level (DetailLevel enum or string)
            verbose: Enable verbose output
            
        Returns:
            - If detail == "DBLPANCAKE": single name string
            - Otherwise: list of pancake and isolation names
        """
        # Import here to avoid circular dependency
        try:
            from ..Supra import DetailLevel
            if isinstance(detail, DetailLevel):
                detail_str = detail.value
            else:
                detail_str = str(detail).upper()
        except ImportError:
            detail_str = str(detail).upper()
        
        if detail_str == "DBLPANCAKE":
            return name
        else:
            # Get names for both pancakes and isolation
            p_ids = []
            
            # First pancake
            p0_name = f"{name}_p0"
            p0_id = self.pancake.get_names(p0_name, detail, verbose)
            p_ids.append(p0_id)
            
            # Isolation
            iso_name = f"{name}_i"
            iso_id = self.isolation.get_names(iso_name, detail, verbose)
            
            # Second pancake
            p1_name = f"{name}_p1"
            p1_id = self.pancake.get_names(p1_name, detail, verbose)
            p_ids.append(p1_id)
            
            if verbose:
                print(f"DoublePancake: pancakes (2), isolation (1)")
            
            # Flatten if nested lists
            if isinstance(p_ids[0], list):
                return flatten([flatten(p_ids), [iso_id]])
            else:
                return flatten([p_ids, [iso_id]])
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"DoublePancake:\n"
            f"  Position (z0): {self.z0} mm\n"
            f"  Z bounds: [{self.z_min}, {self.z_max}] mm\n"
            f"  Inner radius (r0): {self.r0} mm\n"
            f"  Outer radius (r1): {self.r1} mm\n"
            f"  Total height: {self.height} mm\n"
            f"  Radial build: {self.width} mm\n"
            f"  Filling factor: {self.filling_factor:.3f}\n"
            f"  Pancake: {self.pancake.n} turns × {self.pancake.tape.w}×{self.pancake.tape.h} mm\n"
            f"  Isolation: {self.isolation.n_layers} layer(s), {self.isolation.height} mm"
        )
