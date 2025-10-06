#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTSInsert - Complete HTS Insert Structure

Defines a complete HTS insert consisting of multiple double pancakes
stacked vertically with isolation layers between them.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Optional, Self
from ..base import YAMLObjectBase
from ..utils import flatten
from .double_pancake import DoublePancake
from .isolation import Isolation
from .pancake import Pancake
from .tape import Tape


@dataclass
class HTSInsert(YAMLObjectBase):
    """
    Complete HTS insert with multiple double pancakes.
    
    Represents a full High-Temperature Superconductor insert consisting of
    a vertical stack of double pancakes separated by isolation layers.
    
    Attributes:
        name (str): Insert identifier
        z0 (float): Axial center position in millimeters [mm]
        h (float): Total height in millimeters [mm]
        r0 (float): Inner radius in millimeters [mm]
        r1 (float): Outer radius in millimeters [mm]
        z1 (float): Bottom axial position in millimeters [mm]
        n (int): Number of double pancakes
        dblpancakes (list[DoublePancake]): Stack of double pancakes
        isolations (list[Isolation]): Isolation layers between double pancakes
    
    Units:
        All dimensions in millimeters (mm).
    
    Example:
        >>> # Build from components
        >>> tape = Tape(w=12.0, h=0.1, e=0.05)
        >>> pancake = Pancake(r0=50.0, n=100, mandrin=2.0, tape=tape)
        >>> isolation = Isolation(r0=50.0, w=[10.0], h=[0.3])
        >>> 
        >>> # Create insert (simplified constructor)
        >>> insert = HTSInsert.from_yaml("my_insert.yaml")
        >>> 
        >>> print(f"Insert has {insert.n} double pancakes")
        >>> print(f"Total height: {insert.h} mm")
        >>> print(f"Characteristic length: {insert.lc} mm")
    
    Notes:
        - Double pancakes are stacked with isolation between them
        - First double pancake starts at z1 (bottom)
        - Last double pancake ends at z1 + h (top)
        - Number of isolations = n - 1 (no isolation after last double pancake)
        - z0 should be at geometric center: z0 = z1 + h/2
    """
    
    yaml_tag = "!HTSInsert"
    
    name: str = ""
    z0: float = 0.0
    h: float = 0.0
    r0: float = 0.0
    r1: float = 0.0
    z1: float = 0.0
    n: int = 0
    dblpancakes: list[DoublePancake] = field(default_factory=list)
    isolations: list[Isolation] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate HTS insert structure after initialization."""
        if not self.name:
            raise ValueError("HTSInsert must have a name")
        
        if self.n < 0:
            raise ValueError(f"Number of double pancakes must be non-negative, got n={self.n}")
        
        if self.n > 0:
            if len(self.dblpancakes) != self.n:
                raise ValueError(
                    f"Number of double pancakes ({len(self.dblpancakes)}) "
                    f"must match n={self.n}"
                )
            
            if len(self.isolations) != self.n - 1:
                raise ValueError(
                    f"Number of isolations ({len(self.isolations)}) "
                    f"must be n-1={self.n-1}"
                )
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create HTSInsert from dictionary.
        
        Args:
            values: Dictionary with insert parameters
            debug: Enable debug output
            
        Returns:
            New HTSInsert instance
        """
        # Load double pancakes
        dblpancakes = []
        for dp_data in values.get('dblpancakes', []):
            if isinstance(dp_data, DoublePancake):
                dblpancakes.append(dp_data)
            elif isinstance(dp_data, dict):
                dblpancakes.append(DoublePancake.from_dict(dp_data, debug))
            else:
                raise ValueError(f"Invalid double pancake data: {dp_data}")
        
        # Load isolations
        isolations = []
        for iso_data in values.get('isolations', []):
            if isinstance(iso_data, Isolation):
                isolations.append(iso_data)
            elif isinstance(iso_data, dict):
                isolations.append(Isolation.from_dict(iso_data, debug))
            else:
                raise ValueError(f"Invalid isolation data: {iso_data}")
        
        return cls(
            name=values.get('name', ''),
            z0=values.get('z0', 0.0),
            h=values.get('h', 0.0),
            r0=values.get('r0', 0.0),
            r1=values.get('r1', 0.0),
            z1=values.get('z1', 0.0),
            n=values.get('n', 0),
            dblpancakes=dblpancakes,
            isolations=isolations
        )
    
    @classmethod
    def from_yaml(cls, filepath: str, directory: Optional[str] = None, 
                  debug: bool = False) -> Self:
        """
        Load HTSInsert from YAML configuration file.
        
        This replaces the old fromcfg() JSON method with YAML support.
        
        Args:
            filepath: Path to YAML file
            directory: Optional directory prefix
            debug: Enable debug output
            
        Returns:
            New HTSInsert instance loaded from YAML
            
        Example:
            >>> insert = HTSInsert.from_yaml("my_insert.yaml")
            >>> insert = HTSInsert.from_yaml("insert.yaml", directory="configs")
        """
        full_path = Path(directory or ".") / filepath
        
        if debug:
            print(f"HTSInsert.from_yaml({full_path})")
        
        with open(full_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if debug:
            print("HTSInsert data:", data)
        
        # Extract base components if specified at top level
        base_tape = None
        if 'tape' in data:
            tape_data = data['tape']
            base_tape = Tape.from_dict(tape_data) if isinstance(tape_data, dict) else tape_data
        
        base_pancake = Pancake()
        if 'pancake' in data:
            pancake_data = data['pancake']
            base_pancake = Pancake.from_dict(pancake_data) if isinstance(pancake_data, dict) else pancake_data
        
        base_isolation = Isolation()
        if 'isolation' in data:
            iso_data = data['isolation']
            base_isolation = Isolation.from_dict(iso_data) if isinstance(iso_data, dict) else iso_data
        
        # Get parameters
        z0 = data.get('z0', 0.0)
        h = data.get('h', 0.0)
        n = data.get('n', 0)
        
        # Calculate geometry
        r0 = base_pancake.r0
        r1 = base_pancake.r1
        z1 = z0 - h / 2.0
        
        # Build double pancakes and isolations
        dblpancakes = []
        isolations = []
        
        # Create n identical double pancakes
        base_dblpancake = DoublePancake(z0=z1, pancake=base_pancake, isolation=base_isolation)
        
        for i in range(n):
            dblpancakes.append(base_dblpancake)
            if i != n - 1:
                isolations.append(base_isolation)
        
        # Set z0 positions for each double pancake
        z_current = z1
        for i, dp in enumerate(dblpancakes):
            dp_height = dp.height
            dp.z0 = z_current + dp_height / 2.0
            z_current += dp_height + base_isolation.height
        
        if debug:
            print("=== Loaded configuration ===")
            print(f"r0 = {r0} mm")
            print(f"r1 = {r1} mm")
            print(f"z1 = {z1} mm")
            print(f"z2 = {z0 + h/2.0} mm")
            print(f"z0 = {z0} mm")
            print(f"h = {h} mm")
            print(f"n = {n}")
            for i, dp in enumerate(dblpancakes):
                print(f"dblpancakes[{i}]: {dp}")
            print("============================")
        
        name = filepath.replace('.yaml', '').replace('.yml', '')
        name = Path(name).stem
        
        return cls(
            name=name,
            z0=z0,
            h=h,
            r0=r0,
            r1=r1,
            z1=z1,
            n=n,
            dblpancakes=dblpancakes,
            isolations=isolations
        )
    
    @property
    def inner_radius(self) -> float:
        """Inner radius in millimeters [mm]."""
        return self.r0
    
    @property
    def outer_radius(self) -> float:
        """Outer radius in millimeters [mm]."""
        return self.r1
    
    @property
    def height(self) -> float:
        """Total height in millimeters [mm]."""
        return self.h
    
    @property
    def lc(self) -> float:
        """
        Characteristic length for meshing in millimeters [mm].
        
        Returns:
            Tape height from first double pancake
        """
        if self.dblpancakes:
            return self.dblpancakes[0].pancake.tape.h
        return 0.0
    
    def get_names(self, mname: str, detail: Union[str, 'DetailLevel'], 
                  verbose: bool = False) -> list[str]:
        """
        Get marker names for HTS insert elements.
        
        Args:
            mname: Base name prefix
            detail: Detail level (DetailLevel enum or string)
            verbose: Enable verbose output
            
        Returns:
            Flattened list of all marker names
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
        
        dp_ids = []
        i_ids = []
        
        prefix = f"{mname}_" if mname else ""
        
        n_dp = len(self.dblpancakes)
        for i, dp in enumerate(self.dblpancakes):
            if verbose:
                print(f"HTSInsert.get_names: dblpancakes[{i}]: dp={dp}")
            
            dp_name = f"{prefix}dp{i}"
            dp_id = dp.get_names(dp_name, detail, verbose)
            dp_ids.append(dp_id)
            
            # Add isolation between double pancakes (not after last one)
            if i != n_dp - 1:
                iso = self.isolations[i]
                iso_name = f"{prefix}i{i}"
                iso_id = iso.get_names(iso_name, detail, verbose)
                i_ids.append(iso_id)
        
        if detail_str == "DBLPANCAKE":
            return flatten([dp_ids, i_ids])
        else:
            return flatten([flatten(dp_ids), i_ids])
    
    def get_ntapes(self) -> list[int]:
        """
        Get number of tapes per double pancake.
        
        Returns:
            List of tape counts for each double pancake
        """
        return [2 * dp.pancake.n for dp in self.dblpancakes]
    
    def get_mandrin_widths(self) -> list[float]:
        """
        Get mandrin widths for each double pancake.
        
        Returns:
            List of mandrin widths in millimeters [mm]
        """
        return [dp.pancake.mandrin for dp in self.dblpancakes]
    
    def get_pancake_widths(self) -> list[float]:
        """
        Get pancake widths for each double pancake.
        
        Returns:
            List of pancake widths in millimeters [mm]
        """
        return [dp.pancake.width for dp in self.dblpancakes]
    
    def get_pancake_isolation_widths(self) -> list[float]:
        """
        Get isolation widths between pancakes in each double pancake.
        
        Returns:
            List of isolation widths in millimeters [mm]
        """
        return [dp.isolation.width for dp in self.dblpancakes]
    
    def get_pancake_isolation_r0(self) -> list[float]:
        """
        Get inner radii of isolations between pancakes.
        
        Returns:
            List of inner radii in millimeters [mm]
        """
        return [dp.isolation.r0 for dp in self.dblpancakes]
    
    def get_pancake_isolation_r1(self) -> list[float]:
        """
        Get outer radii of isolations between pancakes.
        
        Returns:
            List of outer radii in millimeters [mm]
        """
        return [dp.isolation.r0 + dp.isolation.width for dp in self.dblpancakes]
    
    def get_dblpancake_isolation_widths(self) -> list[float]:
        """
        Get isolation widths between double pancakes.
        
        Returns:
            List of isolation widths in millimeters [mm]
        """
        return [iso.width for iso in self.isolations]
    
    def get_dblpancake_isolation_r0(self) -> list[float]:
        """
        Get inner radii of isolations between double pancakes.
        
        Returns:
            List of inner radii in millimeters [mm]
        """
        return [iso.r0 for iso in self.isolations]
    
    def get_dblpancake_isolation_r1(self) -> list[float]:
        """
        Get outer radii of isolations between double pancakes.
        
        Returns:
            List of outer radii in millimeters [mm]
        """
        return [iso.r0 + iso.width for iso in self.isolations]
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"HTSInsert '{self.name}':\n"
            f"  Position (z0): {self.z0} mm\n"
            f"  Z bounds: [{self.z1}, {self.z1 + self.h}] mm\n"
            f"  Inner radius (r0): {self.r0} mm\n"
            f"  Outer radius (r1): {self.r1} mm\n"
            f"  Total height: {self.h} mm\n"
            f"  Number of double pancakes: {self.n}\n"
            f"  Characteristic length: {self.lc} mm"
        )