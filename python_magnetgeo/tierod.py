
from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Tierod(YAMLObjectBase):
    yaml_tag = "Tierod"

    def __init__(
        self, name: str, r: float, n: int, dh: float, sh: float, contour2d
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
        self.contour2d = contour2d
        

    def __repr__(self):
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"r={self.r!r}, n={self.n!r}, "
                f"dh={self.dh!r}, sh={self.sh!r}, "
                f"contour2d={self.contour2d!r})")
            
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        # Smart nested object handling
        contour2d = cls._load_nested_contour2d(values.get('contour2d'), debug=debug)
        return cls(
            name=values["name"], 
            r=values["r"], 
            n=values["n"], 
            dh=values.get("dh", 0.0), 
            sh=values.get("sh", 0.0), 
            contour2d=contour2d
        )

    @classmethod  
    def _load_nested_contour2d(cls, contour2d_data, debug=False):
        if isinstance(contour2d_data, str):
            # String reference → load from "contour2d_data.yaml"
            from .utils import loadObject
            from .Contour2D import Contour2D
            return loadObject("contour2d", contour2d_data, Contour2D, Contour2D.from_yaml)
        elif isinstance(contour2d_data, dict):
            # Inline object → create from dict
            from .Contour2D import Contour2D
            return Contour2D.from_dict(contour2d_data)
        else:
            # None or already instantiated
            return contour2d_data
        
    
    