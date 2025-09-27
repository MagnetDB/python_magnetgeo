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
        Initialize Ring object.
        
        Args:
            name: Ring identifier
            r: [inner_radius, outer_radius] 
            z: [lower_z, upper_z]
            n: Number parameter
            angle: Angular position in degrees
            bpside: Boolean parameter side
            fillets: Whether to include fillets
            cad: CAD identifier
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
        
        print(f"Ring.__init__: name={name}, r={r}, z={z}", flush=True)
        
        
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
        Create Ring from dictionary.
        
        Args:
            values: Dictionary containing ring data
            debug: Enable debug output
            
        Returns:
            New Ring instance
        """
        print(f"Ring.fromdict: values={values}")
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
        """Calculate characteristic length"""
        return (self.r[1] - self.r[0]) / 10.0

    def __repr__(self) -> str:
        """String representation of Ring"""
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"r={self.r!r}, z={self.z!r}, n={self.n!r}, "
                f"angle={self.angle!r}, bpside={self.bpside!r}, "
                f"fillets={self.fillets!r}, cad={self.cad!r})")

# Note: No manual YAML constructor needed!
# YAMLObjectBase automatically registers it via __init_subclass__
