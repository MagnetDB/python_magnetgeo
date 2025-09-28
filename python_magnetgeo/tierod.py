
from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Tierod(YAMLObjectBase):
    yaml_tag = "Tierod"

    def __init__(
        self, name: str, r: float, n: int, dh: float, sh: float, shape
    ) -> None:
        # validation
        GeometryValidator.validate_name(name)      # Must be non-empty string
        GeometryValidator.validate_positive(r)     # Must be positive number
        GeometryValidator.validate_integer(n)      # Must be integer
    
        self.name = name
        self.r = r
        self.n = n
        self.dh: float = dh
        self.sh: float = sh
        self.shape = shape
        

    def __repr__(self):
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"r={self.r!r}, n={self.n!r}, "
                f"dh={self.dh!r}, sh={self.sh!r}, "
                f"shape={self.shape!r})")
            
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        # Smart nested object handling
        shape = cls._load_nested_shape(values.get('shape'), debug=debug)
        return cls(
            name=values["name"], 
            r=values["r"], 
            n=values["n"], 
            dh=values.get("dh", 0.0), 
            sh=values.get("sh", 0.0), 
            shape=shape
        )

    @classmethod  
    def _load_nested_shape(cls, shape_data, debug=False):
        if isinstance(shape_data, str):
            # String reference → load from "shape_data.yaml"
            from .utils import loadObject
            from .Contour2D import Contour2D
            return loadObject("shape", shape_data, Contour2D, Contour2D.from_yaml)
        elif isinstance(shape_data, dict):
            # Inline object → create from dict
            from .Contour2D import Contour2D
            return Contour2D.from_dict(shape_data)
        else:
            # None or already instantiated
            return shape_data
        
    
    