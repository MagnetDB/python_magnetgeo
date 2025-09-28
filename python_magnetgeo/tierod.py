
from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class Tierod(YAMLObjectBase):
    yaml_tag = "Tierod"

    def __init__(
        self, name: str, r: float, n: int, dh: float, sh: float, shape
    ) -> None:
        self.name = name
        self.r = r
        self.n = n
        self.dh: float = dh
        self.sh: float = sh
        self.shape = shape
        

    def __repr__(self):
        return "%s(name=%s, r=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.n,
            self.dh,
            self.sh,
            self.shape,
        )
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """

        # Basic parameters
        _params = {
            'name': values.get("name", ""),
            'r': values["r"],
            'n': values["n"],
            'dh': values.get("dh", 0),
            'sh': values.get("sh", 0),
        }

        # Handle nested objects (they might be dicts or already instantiated)
        if 'shape' in values and values['shape']:
            shape_data = values['shape']
            if isinstance(shape_data, dict):
                from .Shape import Shape
                _params['shape'] = Shape.from_dict(shape_data)
            else:
                _params['shape'] = shape_data
        
        return cls(**_params)
    
    