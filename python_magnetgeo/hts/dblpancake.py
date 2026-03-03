# Import DetailLevel from Supra module
from ..enums import DetailLevel
from ..utils import flatten
from .isolation import isolation
from .pancake import pancake


class dblpancake:
    """
    Double Pancake structure

    z0: position of the double pancake (centered on isolation)
    pancake: pancake structure (assume that both pancakes have the same structure)
    isolation: isolation between pancakes
    """

    def __init__(
        self,
        z0: float,
        pancake: pancake = pancake(),
        isolation: isolation = isolation(),
    ):
        self.z0 = z0
        self.pancake = pancake
        self.isolation = isolation

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"dblpancake(z0={self.z0}, pancake={self.pancake}, isolation={self.isolation})"

    def __str__(self) -> str:
        msg = f"r0={self.pancake.getR0()}, "
        msg += f"r1={self.pancake.getR1()}, "
        msg += f"z1={self.getZ0() - self.getH()/2.}, "
        msg += f"z2={self.getZ0() + self.getH()/2.}"
        msg += f"(z0={self.getZ0()}, h={self.getH()})"
        return msg

    def get_names(
        self, name: str, detail: str | DetailLevel, verbose: bool = False
    ) -> str | list[str]:
        """
        Get marker names for double pancake elements.

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

        if detail == DetailLevel.DBLPANCAKE:
            return name
        else:
            p_ids = []

            p_ = self.pancake
            _id = p_.get_names(f"{name}_p0", detail)
            p_ids.append(_id)

            dp_i = self.isolation
            if verbose:
                print(f"dblpancake: isolation={dp_i}")
            _isolation_id = dp_i.get_names(f"{name}_i", detail)

            _id = p_.get_names(f"{name}_p1", detail)
            p_ids.append(_id)

            if verbose:
                print(f"dblpancake: pancakes ({len(p_ids)}, {type(p_ids[0])}), isolations (1)")
            if isinstance(p_ids[0], list):
                return flatten([flatten(p_ids), [_isolation_id]])
            else:
                return flatten([p_ids, [_isolation_id]])

    def getPancake(self):
        """
        return pancake object
        """
        return self.pancake

    def getIsolation(self):
        """
        return isolation object
        """
        return self.isolation

    def setZ0(self, z0) -> None:
        self.z0 = z0

    def setPancake(self, pancake) -> None:
        self.pancake = pancake

    def setIsolation(self, isolation) -> None:
        self.isolation = isolation

    def getFillingFactor(self) -> float:
        """
        ratio of the surface occupied by the tapes / total surface
        """
        S_tapes = 2.0 * self.pancake.n * self.pancake.tape.w * self.pancake.tape.h
        return S_tapes / self.getArea()

    def getR0(self) -> float:
        return self.pancake.getR0()

    def getR1(self) -> float:
        return self.pancake.getR1()

    def getZ0(self) -> float:
        return self.z0

    def getW(self) -> float:
        return self.pancake.getW()

    def getH(self) -> float:
        return 2.0 * self.pancake.getH() + self.isolation.getH()

    def getArea(self) -> float:
        return (self.pancake.getR1() - self.pancake.getR0()) * self.getH()
