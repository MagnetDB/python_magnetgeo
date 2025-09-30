#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides tools to un/serialize data from json
"""

from .Probe import Probe
from .Shape import Shape
from .ModelAxi import ModelAxi
from .Model3D import Model3D
from .Helix import Helix
from .Ring import Ring
from .InnerCurrentLead import InnerCurrentLead
from .OuterCurrentLead import OuterCurrentLead
from .Insert import Insert
from .Bitter import Bitter
from .Supra import Supra
from .Screen import Screen
from .MSite import MSite
from .Bitters import Bitters
from .Supras import Supras
from .Contour2D import Contour2D
from .Chamfer import Chamfer
from .Groove import Groove
from .tierod import Tierod
from .coolingslit import CoolingSlit


# From : http://chimera.labs.oreilly.com/books/1230000000393/ch06.html#_discussion_95
# Dictionary mapping names to known classes

classes = {
    "Probe": Probe,
    "Shape": Shape,
    "ModelAxi": ModelAxi,
    "Model3D": Model3D,
    "Helix": Helix,
    "Ring": Ring,
    "InnerCurrentLead": InnerCurrentLead,
    "OuterCurrentLead": OuterCurrentLead,
    "Insert": Insert,
    "Bitter": Bitter,
    "Supra": Supra,
    "Screen": Screen,
    "Bitters": Bitters,
    "Supras": Supras,
    "MSite": MSite,
    "Contour2D": Contour2D,
    "Chamfer": Chamfer,
    "Groove": Groove,
    "Tierod": Tierod,
    "CoolingSlit": CoolingSlit,
}


def serialize_instance(obj):
    """
    serialize_instance of an obj
    
    Handles Enum values by converting them to their string values.
    """
    from enum import Enum
    
    d = {"__classname__": type(obj).__name__}
    
    # Get object attributes
    obj_dict = vars(obj)
    
    # Convert any Enum values to their string representation
    for key, value in obj_dict.items():
        if isinstance(value, Enum):
            d[key] = value.value
        else:
            d[key] = value
    
    return d

def unserialize_object(d, debug: bool = True):
    """
    unserialize_instance of an obj
    """
    if debug:
        print(f"unserialize_object: d={d}", flush=True)

    # remove all __classname__ keys
    clsname = d.pop("__classname__", None)
    if debug:
        print(f"clsname: {clsname}", flush=True)
    if clsname:
        cls = classes[clsname]
        obj = cls.__new__(cls)  # Make instance without calling __init__
        for key, value in d.items():
            if debug:
                print(f"key={key}, value={value} type={type(value)}", flush=True)
            setattr(obj, key.lower(), value)
        if debug:
            print(f"obj={obj}", flush=True)
        return obj
    else:
        if debug:
            print(f"no classname: {d}", flush=True)
        return d
