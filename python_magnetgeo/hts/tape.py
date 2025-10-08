# Import DetailLevel from Supra module
from typing import Self, Optional, Union

from ..enums import DetailLevel

class tape:
    """
    HTS tape

    w: width
    h: height
    e: thickness of co-wound durnomag
    """

    def __init__(self, w: float = 0, h: float = 0, e: float = 0) -> None:
        self.w: float = w
        self.h: float = h
        self.e: float = e

    @classmethod
    def from_data(cls, data: dict) -> Self:
        w = h = e = 0
        if "w" in data:
            w: float = data["w"]
        if "h" in data:
            h: float = data["h"]
        if "e" in data:
            e: float = data["e"]
        return cls(w, h, e)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"tape(w={self.w}, h={self.h}, e={self.e})"

    def __str__(self) -> str:
        msg = "\n"
        msg += f"width: {self.w} [mm]\n"
        msg += f"height: {self.h} [mm]\n"
        msg += f"e: {self.e} [mm]\n"
        return msg

    def get_names(
        self, 
        name: str, 
        detail: Union[str, DetailLevel], 
        verbose: bool = False
    ) -> list[str]:
        """
        Get marker names for tape elements.
        
        Args:
            name: Base name for markers
            detail: Detail level (DetailLevel enum or string)
            verbose: Enable verbose output
        
        Returns:
            list[str]: List of marker names for superconductor and duromag
        """
        _tape = f"{name}_SC"
        _e = f"{name}_Duromag"
        return [_tape, _e]

    def getH(self) -> float:
        """
        get tape height
        """
        return self.h

    def getW(self) -> float:
        """
        get total width
        """
        return self.w + self.e

    def getW_Sc(self) -> float:
        """
        get Sc width
        """
        return self.w

    def getW_Isolation(self) -> float:
        """
        get Isolation width
        """
        return self.e

    def getArea(self) -> float:
        """
        get tape cross section surface
        """
        return (self.w + self.e) * self.h

    def getFillingFactor(self) -> float:
        """
        get tape filling factor (aka ratio of superconductor over tape section)
        """
        return (self.w * self.h) / self.getArea()


