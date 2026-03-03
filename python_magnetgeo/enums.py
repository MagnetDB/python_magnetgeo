from enum import Enum

class DetailLevel(str, Enum):
    """
    Level of detail for structural modeling of Supra components.
    
    Attributes:
        NONE: Simplified single-region model
        DBLPANCAKE: Model at double-pancake level
        PANCAKE: Model individual pancakes
        TAPE: Model individual tape windings
    
    Notes:
        Inherits from str to maintain YAML serialization compatibility.
        Higher detail levels increase mesh complexity and solve time.
    """
    NONE = "NONE"
    DBLPANCAKE = "DBLPANCAKE"
    PANCAKE = "PANCAKE"
    TAPE = "TAPE"

