#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Ring
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Ring(YAMLObjectBase):
    """
    Ring geometry class.
    
    Represents a cylindrical ring with inner/outer radius and height bounds.
    All serialization functionality is inherited from YAMLObjectBase.
    """
    
    yaml_tag = "Ring"

    def __init__(self, name: str, r: List[float], z: List[float], 
                 n: int = 0, angle: float = 0, bpside: bool = True, 
                 fillets: bool = False, cad: str = None) -> None:
        """
        Initialize a Ring reinforcement structure connecting helical coils.
        
        A Ring is a cylindrical reinforcement element that mechanically connects
        two adjacent helical coils (Helix 0 and Helix 1) in an Insert assembly.
        Rings provide structural support, help distribute electromagnetic forces,
        and may include cooling slits for thermal management.
        
        Args:
            name: Unique identifier for the ring
            r: List of four radial values in mm defining ring boundaries:
            [r0_inner, r0_outer, r1_inner, r1_outer] where:
            - r0_inner: Inner radius at Helix 0 connection
            - r0_outer: Outer radius at Helix 0 connection  
            - r1_inner: Inner radius at Helix 1 connection
            - r1_outer: Outer radius at Helix 1 connection
            Must be in ascending order. The actual Helix radii assignment
            depends on the bpside parameter.
            z: [z_bottom, z_top] - Axial extent in mm. Must be in ascending order.
            n: Number of cooling slits in the ring. Default: 0 (no slits)
            angle: Angular width of each cooling slit in degrees. Default: 0
            bpside: Boolean indicating which side the ring connects to:
                - True: Normal connection orientation
                - False: Reversed connection orientation
                Determines how r values map to Helix 0 and Helix 1.
                Default: True
            fillets: If True, include fillet features at ring edges for stress
                    reduction and smoother geometry transitions. Default: False
            cad: CAD system identifier for this ring geometry. Can be None or
                empty string if not specified. Default: None (converted to '')
        
        Raises:
            ValidationError: If name is invalid (empty or None)
            ValidationError: If r does not have exactly 4 values
            ValidationError: If r values are not in ascending order
            ValidationError: If z does not have exactly 2 values
            ValidationError: If z values are not in ascending order
            ValidationError: If r[0] < 0 (negative inner radius)
            ValidationError: If n * angle > 360 (cooling slits would overlap)
        
        Notes:
            - Ring connects two adjacent helices in an Insert magnet assembly
            - Four radii needed to accommodate potentially different helix sizes
            - Cooling slits allow coolant flow through the ring structure
            - Total angular coverage of slits must not exceed 360 degrees
            - Fillets improve mechanical properties and reduce stress concentration
            - bpside determines orientation/connection topology
        
        Example:
            >>> # Simple ring without cooling slits
            >>> ring1 = Ring(
            ...     name="R1",
            ...     r=[100.0, 120.0, 110.0, 130.0],  # 4 radii
            ...     z=[250.0, 280.0],                 # 30mm height
            ...     n=0,                               # No cooling slits
            ...     angle=0.0,
            ...     bpside=True,
            ...     fillets=False,
            ...     cad="SALOME"
            ... )
            
            >>> # Ring with cooling slits
            >>> ring2 = Ring(
            ...     name="R2_cooled",
            ...     r=[105.0, 125.0, 105.0, 125.0],
            ...     z=[300.0, 330.0],
            ...     n=12,            # 12 cooling slits
            ...     angle=15.0,      # Each 15° wide
            ...     bpside=True,
            ...     fillets=True,    # Include fillets
            ...     cad="GMSH"
            ... )
            >>> # Total angular coverage: 12 * 15° = 180° < 360° ✓
            
            >>> # Ring with fillets and no CAD
            >>> ring3 = Ring(
            ...     name="R3_fillet",
            ...     r=[95.0, 115.0, 100.0, 120.0],
            ...     z=[350.0, 375.0],
            ...     fillets=True,
            ...     cad=None  # Will be converted to ''
            ... )
        """
        # General validation
        GeometryValidator.validate_name(name)
        
        # Ring-specific validation
        GeometryValidator.validate_numeric_list(r, "r", expected_length=4)
        GeometryValidator.validate_ascending_order(r, "r")
        
        GeometryValidator.validate_numeric_list(z, "z", expected_length=2) 
        GeometryValidator.validate_ascending_order(z, "z")
        
        # Additional Ring-specific checks
        if r[0] < 0:
            raise ValidationError("Inner radius cannot be negative")        
        
        # Check ring cooling slits
        if n * angle > 360:
            raise ValidationError(f"Ring: {n} coolingslits total angular length ({n * angle} cannot exceed 360 degrees")
        
        # Set all attributes
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.bpside = bpside
        self.fillets = fillets
        self.cad = cad or ''

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Ring instance from dictionary representation.
        
        Standard deserialization method with default values for optional parameters.
        Includes debug output to trace the deserialization process.
        
        Args:
            values: Dictionary containing Ring configuration with keys:
                - name (str): Ring identifier (required)
                - r (list[float]): Four radial values (required)
                - z (list[float]): Two axial values (required)
                - n (int, optional): Number of cooling slits. Default: 0
                - angle (float, optional): Slit angular width. Default: 0
                - bpside (bool, optional): Connection side. Default: True
                - fillets (bool, optional): Include fillets. Default: False
                - cad (str, optional): CAD identifier. Default: ''
            debug: Enable debug output showing dictionary values
        
        Returns:
            Ring: New Ring instance created from dictionary
        
        Raises:
            KeyError: If required keys ('name', 'r', 'z') are missing
            ValidationError: If validation constraints are violated
        
        Notes:
            - Debug mode prints the input dictionary values
            - All optional parameters have sensible defaults
            - CAD value defaults to empty string if not provided or None
        
        Example:
            >>> # Full specification
            >>> data = {
            ...     "name": "Ring-H1H2",
            ...     "r": [100.0, 120.0, 110.0, 130.0],
            ...     "z": [250.0, 280.0],
            ...     "n": 8,
            ...     "angle": 20.0,
            ...     "bpside": True,
            ...     "fillets": True,
            ...     "cad": "SALOME"
            ... }
            >>> ring = Ring.from_dict(data)
            
            >>> # Minimal specification (uses defaults)
            >>> minimal = {
            ...     "name": "SimpleRing",
            ...     "r": [95.0, 115.0, 100.0, 120.0],
            ...     "z": [300.0, 325.0]
            ... }
            >>> ring2 = Ring.from_dict(minimal)
            >>> assert ring2.n == 0
            >>> assert ring2.angle == 0
            >>> assert ring2.bpside == True
            >>> assert ring2.fillets == False
            >>> assert ring2.cad == ''
            
            >>> # With debug output
            >>> ring3 = Ring.from_dict(data, debug=True)
            >>> # Prints: Ring.fromdict: values={...}
        """
        return cls(
            name=values["name"],
            r=values["r"],
            z=values["z"],
            n=values.get("n", 0),
            angle=values.get("angle", 0),
            bpside=values.get("bpside", True),
            fillets=values.get("fillets", False),
            cad=values.get("cad", '')
        )

    def get_lc(self) -> float:
        """
        Calculate characteristic mesh length for the ring geometry.
        
        Computes an appropriate mesh element size based on the ring's radial
        thickness. Used for automatic mesh size determination in FEA.
        
        Returns:
            float: Characteristic length in mm, calculated as radial thickness / 10
        
        Notes:
            - Formula: lc = (r[1] - r[0]) / 10
            - Uses first two radial values (inner and outer at Helix 0)
            - Provides reasonable default mesh density
            - Smaller lc produces finer mesh with more elements
            - Can be overridden for specific meshing requirements
        
        Example:
            >>> ring = Ring(
            ...     name="R1",
            ...     r=[100.0, 120.0, 110.0, 130.0],
            ...     z=[250.0, 280.0]
            ... )
            >>> lc = ring.get_lc()
            >>> print(lc)  # 2.0 mm  (120 - 100) / 10
            
            >>> # Thicker ring gives larger lc
            >>> thick_ring = Ring(
            ...     name="R_thick",
            ...     r=[100.0, 150.0, 110.0, 160.0],
            ...     z=[250.0, 280.0]
            ... )
            >>> print(thick_ring.get_lc())  # 5.0 mm  (150 - 100) / 10
        """
        return (self.r[1] - self.r[0]) / 10.0

    def __repr__(self) -> str:
        """
        Return string representation of Ring instance.
        
        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.
        
        Returns:
            str: String representation in constructor-like format showing:
                - name: Ring identifier
                - r: Four radial values
                - z: Two axial values
                - n: Number of cooling slits
                - angle: Slit angular width
                - bpside: Connection side
                - fillets: Fillet inclusion flag
                - cad: CAD identifier
        
        Example:
            >>> ring = Ring(
            ...     name="R1",
            ...     r=[100.0, 120.0, 110.0, 130.0],
            ...     z=[250.0, 280.0],
            ...     n=8,
            ...     angle=20.0,
            ...     bpside=True,
            ...     fillets=True,
            ...     cad="SALOME"
            ... )
            >>> print(repr(ring))
            Ring(name='R1', r=[100.0, 120.0, 110.0, 130.0], z=[250.0, 280.0], 
                n=8, angle=20.0, bpside=True, fillets=True, cad='SALOME')
            >>>
            >>> # In Python REPL
            >>> ring
            Ring(name='R1', r=[100.0, 120.0, 110.0, 130.0], ...)
            >>>
            >>> # With defaults
            >>> simple = Ring(name="R_simple", r=[95, 115, 100, 120], z=[300, 325])
            >>> print(repr(simple))
            Ring(name='R_simple', r=[95, 115, 100, 120], z=[300, 325], 
                n=0, angle=0, bpside=True, fillets=False, cad='')
        """
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"r={self.r!r}, z={self.z!r}, n={self.n!r}, "
                f"angle={self.angle!r}, bpside={self.bpside!r}, "
                f"fillets={self.fillets!r}, cad={self.cad!r})")

# Note: No manual YAML constructor needed!
# YAMLObjectBase automatically registers it via __init_subclass__
