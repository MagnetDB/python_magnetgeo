from typing import Self

# Import DetailLevel from Supra module
from ..enums import DetailLevel
from ..utils import flatten
from .tape import tape


class pancake:
    """
    Pancake structure

    r0: inner radius
    mandrin: mandrin (only for mesh purpose)
    tape: tape used for pancake
    n: number of tapes
    """

    def __init__(self, r0: float = 0, tape: tape = tape(), n: int = 0, mandrin: int = 0) -> None:
        self.mandrin = mandrin
        self.tape = tape
        self.n = n
        self.r0 = r0

    @classmethod
    def from_data(cls, data={}) -> Self:
        r0 = 0
        n = 0
        t_ = tape()
        mandrin = 0
        if "r0" in data:
            r0 = data["r0"]
        if "mandrin" in data:
            mandrin = data["mandrin"]
        if "tape" in data:
            t_ = tape.from_data(data["tape"])
        if "ntapes" in data:
            n = data["ntapes"]
        return cls(r0, t_, n, mandrin)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return "pancake(r0=%r, n=%r, tape=%r, mandrin=%r)" % (
            self.r0,
            self.n,
            self.tape,
            self.mandrin,
        )

    def __str__(self) -> str:
        msg = "\n"
        msg += f"r0: {self.r0} [m]\n"
        msg += f"mandrin: {self.mandrin} [m]\n"
        msg += f"ntapes: {self.n} \n"
        msg += f"tape: {self.tape}***\n"
        return msg

    def get_names(
        self, name: str, detail: str | DetailLevel, verbose: bool = False
    ) -> str | list[str]:
        """
        Get marker names for pancake elements.

        Args:
            name: Base name for markers
            detail: Detail level (DetailLevel enum or string)
            verbose: Enable verbose output

        Returns:
            str | list[str]: Marker name(s) depending on detail level
        """
        # Convert enum to string for comparison
        if isinstance(detail, str):
            detail = DetailLevel[detail.upper()]

        if detail == DetailLevel.PANCAKE:
            return name
        else:
            _mandrin = f"{name}_Mandrin"
            tape_ = self.tape
            tape_ids = []
            for i in range(self.n):
                tape_id = tape_.get_names(f"{name}_t{i}", detail)
                tape_ids.append(tape_id)

            if verbose:
                print(f"pancake: mandrin (1), tapes ({len(tape_ids)})")
            return flatten([[_mandrin], flatten(tape_ids)])

    def getN(self) -> int:
        """
        get number of tapes
        """
        return self.n

    def getTape(self) -> tape:
        """
        return tape object
        """
        return self.tape

    def getR0(self) -> float:
        """
        get pancake inner radius
        """
        return self.r0

    def getMandrin(self) -> float:
        """
        get pancake mandrin inner radius
        """
        return self.mandrin

    def getR1(self) -> float:
        """
        get pancake outer radius
        """
        return self.n * (self.tape.w + self.tape.e) + self.r0

    def getR(self) -> list[float]:
        """
        get list of tapes inner radius
        """
        r = []
        ri = self.getR0()
        dr = self.tape.w + self.tape.e
        for i in range(self.n):
            r.append(ri)
            ri += dr
        return r

    def getFillingFactor(self) -> float:
        """
        ratio of the surface occupied by the tapes / total surface
        """
        S_tapes = self.n * self.tape.w * self.tape.h
        return S_tapes / self.getArea()

    def getW(self) -> float:
        return self.getR1() - self.getR0()

    def getH(self) -> float:
        return self.tape.getH()

    def getArea(self) -> float:
        return (self.getR1() - self.getR0()) * self.getH()
