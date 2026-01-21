from typing import Self

# Import DetailLevel from Supra module
from ..enums import DetailLevel


class isolation:
    """
    Isolation

    r0: inner radius of isolation structure
    w: widths of the different layers
    h: heights of the different layers
    """

    def __init__(self, r0: float = 0, w: list = [], h: list = []):
        self.r0 = r0
        self.w = w
        self.h = h

    @classmethod
    def from_data(cls, data: dict) -> Self:
        r0 = 0
        w = []
        h = []
        if "r0" in data:
            r0 = data["r0"]
        if "w" in data:
            w = data["w"]
        if "h" in data:
            h = data["h"]
        return cls(r0, w, h)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"isolation(r0={self.r0}, w={self.w}, h={self.h})"

    def __str__(self) -> str:
        msg = "\n"
        msg += f"r0: {self.r0} [mm]\n"
        msg += f"w: {self.w} \n"
        msg += f"h: {self.h} \n"
        return msg

    def get_names(self, name: str, detail: str | DetailLevel, verbose: bool = False) -> str:
        """
        Get marker name for isolation element.

        Args:
            name: Base name for marker
            detail: Detail level (DetailLevel enum or string) - not used for isolation
            verbose: Enable verbose output

        Returns:
            str: Marker name for isolation
        """
        return name

    def getR0(self) -> float:
        """
        return the inner radius of isolation
        """
        return self.r0

    def getW(self) -> float:
        """
        return the width of isolation
        """
        return max(self.w)

    def getH_Layer(self, i: int) -> float:
        """
        return the height of isolation layer i
        """
        return self.h[i]

    def getW_Layer(self, i: int) -> float:
        """
        return the width of isolation layer i
        """
        return self.w[i]

    def getH(self) -> float:
        """
        return the total heigth of isolation
        """
        return sum(self.h)

    def getLayer(self) -> int:
        """
        return the number of layer
        """
        return len(self.w)
