#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pancake - Single Pancake Coil

Defines a single pancake coil structure with HTS tape windings,
including mandrin (inner former) and radial build.
"""

from dataclasses import dataclass
from typing import Union, Optional
from ..base import YAMLObjectBase
from .tape import Tape


@dataclass
class Pancake(YAMLObjectBase):
    """
    Single pancake coil with HTS tape windings.
    
    Represents one pancake coil with specified inner radius, number of turns,
    mandrin thickness, and tape geometry.
    
    Attributes:
        r0 (float): Inner radius (bore) in millimeters [mm]
        n (int): Number of tape turns
        mandrin (float): Mandrin (inner former) thickness in millimeters [mm]
        tape (Tape): HTS tape geometry
    
    Units:
        All dimensions in millimeters (mm).
    
    Example:
        >>> # Create tape first
        >>> tape = Tape(w=12.0, h=0.1, e=0.05)
        
        >>> # Create pancake
        >>> pancake = Pancake(r0=50.0, n=100, mandrin=2.0, tape=tape)
        >>> print(f"Outer radius: {pancake.r1} mm")
        >>> print(f"Radial build: {pancake.width} mm")
        >>> print(f"Pancake height: {pancake.height} mm")
        
        >>> # From dictionary
        >>> pancake = Pancake.from_dict({
        ...     'r0': 50.0,
        ...     'n': 100,
        ...     'mandrin': 2.0,
        ...     'tape': {'w': 12.0, 'h': 0.1, 'e': 0.05}
        ... })
    
    Notes:
        - Outer radius r1 = r0 + mandrin + n * tape.w
        - Pancake height = n * tape.h
        - Width (radial build) = mandrin + n * tape.w
        - Area is radial build × height
    """
    
    yaml_tag = "!Pancake"
    
    r0: float = 0.0      # inner radius [mm]
    n: int = 0           # number of turns
    mandrin: float = 0.0 # mandrin thickness [mm]
    tape: Tape = None    # HTS tape
    
    def __post_init__(self):
        """Validate pancake structure after initialization."""
        if self.r0 < 0:
            raise ValueError(f"Inner radius must be non-negative, got r0={self.r0}")
        
        if self.n < 0:
            raise ValueError(f"Number of turns must be non-negative, got n={self.n}")
        
        if self.mandrin < 0:
            raise ValueError(f"Mandrin thickness must be non-negative, got mandrin={self.mandrin}")
        
        if self.tape is None:
            raise ValueError("Pancake must have a tape specification")
        
        if not isinstance(self.tape, Tape):
            raise TypeError(f"tape must be a Tape instance, got {type(self.tape)}")
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Pancake from dictionary.
        
        Args:
            values: Dictionary with 'r0', 'n', 'mandrin', 'tape' keys
            debug: Enable debug output (unused)
            
        Returns:
            New Pancake instance
            
        Example:
            >>> pancake = Pancake.from_dict({
            ...     'r0': 50.0,
            ...     'n': 100,
            ...     'mandrin': 2.0,
            ...     'tape': {'w': 12.0, 'h': 0.1, 'e': 0.05}
            ... })
        """
        # Handle tape: can be Tape instance or dict
        tape_data = values.get('tape')
        if isinstance(tape_data, Tape):
            tape = tape_data
        elif isinstance(tape_data, dict):
            tape = Tape.from_dict(tape_data)
        else:
            raise ValueError(f"Invalid tape specification: {tape_data}")
        
        return cls(
            r0=values.get('r0', 0.0),
            n=values.get('n', 0),
            mandrin=values.get('mandrin', 0.0),
            tape=tape
        )
    
    @property
    def inner_radius(self) -> float:
        """Inner radius (bore) in millimeters [mm]."""
        return self.r0
    
    @property
    def r1(self) -> float:
        """
        Outer radius in millimeters [mm].
        
        Returns:
            r1 = r0 + mandrin + n * tape.w
        """
        return self.r0 + self.mandrin + self.n * self.tape.w
    
    @property
    def outer_radius(self) -> float:
        """Outer radius in millimeters [mm] (alias for r1)."""
        return self.r1
    
    @property
    def width(self) -> float:
        """
        Radial build (width) in millimeters [mm].
        
        Returns:
            Radial build = mandrin + n * tape.w
        """
        return self.mandrin + self.n * self.tape.w
    
    @property
    def height(self) -> float:
        """
        Pancake height (axial build) in millimeters [mm].
        
        Returns:
            Height = n * tape.h
        """
        return self.n * self.tape.h
    
    @property
    def area(self) -> float:
        """
        Cross-sectional area in square millimeters [mm²].
        
        Returns:
            Area = width × height
        """
        return self.width * self.height
    
    @property
    def filling_factor(self) -> float:
        """
        Tape filling factor (ratio of tape area to total area).
        
        Returns:
            Filling factor = (n * tape.area) / total_area
        """
        if self.area == 0:
            return 0.0
        tape_area = self.n * self.tape.area
        return tape_area / self.area
    
    def get_names(self, name: str, detail: Union[str, 'DetailLevel'], 
                  verbose: bool = False) -> Union[str, list[str]]:
        """
        Get marker names for pancake elements.
        
        Args:
            name: Base name for markers
            detail: Detail level (DetailLevel enum or string)
            verbose: Enable verbose output
            
        Returns:
            - If detail == "PANCAKE": single name string
            - If detail == "TAPE": list of tape names
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
        
        if detail_str == "PANCAKE":
            return name
        elif detail_str == "TAPE":
            # Generate individual tape names
            tape_names = []
            for i in range(self.n):
                tape_names.append(f"{name}_t{i}")
            return tape_names
        else:
            return name
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Pancake:\n"
            f"  Inner radius (r0): {self.r0} mm\n"
            f"  Outer radius (r1): {self.r1} mm\n"
            f"  Radial build: {self.width} mm\n"
            f"  Height: {self.height} mm\n"
            f"  Number of turns: {self.n}\n"
            f"  Mandrin: {self.mandrin} mm\n"
            f"  Filling factor: {self.filling_factor:.3f}\n"
            f"  Tape: {self.tape.w}×{self.tape.h} mm"
        )
