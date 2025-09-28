import yaml
import json

"""
Provides definition for Groove
!!! groove are supposed to be "square" like !!!

gtype: rint or rext
n: number of grooves
eps: depth of groove
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Groove(YAMLObjectBase):
    yaml_tag = "Groove"

    def __init__(self, name: str='', gtype: str=None, n: int=0, eps: float=0) -> None:
        self.name = name
        self.gtype = gtype
        self.n = n
        self.eps: float = eps

    def __repr__(self):
        return "%s(name=%s, gtype=%s, n=%d, eps=%g)" % (
            self.__class__.__name__,
            self.name,
            self.gtype,
            self.n,
            self.eps,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values.get("name", '')
        gtype = values["gtype"]
        n = values["n"]
        eps = values["eps"]
        return Groove(name, gtype, n, eps)
    
