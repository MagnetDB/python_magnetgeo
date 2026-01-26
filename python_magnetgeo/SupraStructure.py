#!/usr/bin/env python3
# encoding: UTF-8

"""
Define HTS insert geometry with DetailLevel enum support
"""
from typing import Optional

from .enums import DetailLevel
from .hts.dblpancake import dblpancake
from .hts.isolation import isolation
from .hts.pancake import pancake
from .hts.tape import tape
from .utils import flatten

# Module logger
from .logging_config import get_logger
logger = get_logger(__name__)

class HTSInsert:
    """
    HTS insert

    dblpancakes: stack of double pancakes
    isolation: stack of isolations between double pancakes

    TODO: add possibility to use 2 different pancake
    """

    def __init__(
        self,
        name: str = "",
        z0: float = 0,
        h: float = 0,
        r0: float = 0,
        r1: float = 0,
        z1: float = 0,
        n: int = 0,
        dblpancakes: list[dblpancake] = None,
        isolations: list[isolation] = None,
    ):
        self.name = name
        self.z0 = z0
        self.h = h
        self.r0 = r0
        self.r1 = r1
        self.z1 = z1
        self.n = n
        self.dblpancakes = dblpancakes if dblpancakes is not None else []
        self.isolations = isolations if isolations is not None else []

    @classmethod
    def fromcfg(
        cls,
        inputcfg: str,
        directory: Optional[str] = None,
        debug: Optional[bool] = False,
    ):
        """create from a file"""
        import json

        filename = inputcfg
        if directory is not None:
            filename = f"{directory}/{filename}"
        print(f"SupraStructure:fromcfg({filename}, directory={directory})", flush=True)

        with open(filename) as f:
            data = json.load(f)
            logger.debug(f"HTSinsert data: {data}")

            mytape = None
            if "tape" in data:
                mytape = tape.from_data(data["tape"])

            mypancake = pancake()
            if "pancake" in data:
                mypancake = pancake.from_data(data["pancake"])

            myisolation = isolation()
            if "isolation" in data:
                myisolation = isolation.from_data(data["isolation"])

            z = 0
            r0 = r1 = z0 = z1 = h = 0
            n = 0
            dblpancakes = []
            isolations = []
            if "dblpancakes" in data:
                logger.debug(f"DblPancake data: {data['dblpancakes']}")

                # if n defined use the same pancakes and isolations
                # else loop to load pancake and isolation structure definitions
                if "n" in data["dblpancakes"]:
                    n = data["dblpancakes"]["n"]
                    logger.debug(f"Loading {n} similar dblpancakes, z={z}")
                    if "isolation" in data["dblpancakes"]:
                        dpisolation = isolation.from_data(data["dblpancakes"]["isolation"])
                    else:
                        dpisolation = myisolation
                    logger.debug(f"dpisolation={dpisolation}")

                    for i in range(n):
                        dp = dblpancake(z, mypancake, myisolation)
                        logger.debug(f"dp={dp}")
                        dblpancakes.append(dp)
                        isolations.append(dpisolation)

                        logger.debug(f"dblpancake[{i}]: {dp}")

                        z += dp.getH()
                        # print(f'z={z} dp_H={dp.getH()}')
                        if i != n - 1:
                            z += dpisolation.getH()  # isolation between D
                        # print(f'z={z} dp_i={dpisolation.getH()}')

                    h = z
                    # print(f"h= {self.h} [mm] = {z}")

                    r0 = dblpancakes[0].getR0()
                    r1 = dblpancakes[0].getR0() + dblpancakes[0].getW()
                else:
                    logger.debug(f"Loading different dblpancakes, z={z}")
                    n = 0
                    for dp in data["dblpancakes"]:
                        n += 1
                        logger.debug(f"dp: {dp}, pancake: {data['dblpancakes'][dp]['pancake']}")
                        mypancake = pancake.from_data(data["dblpancakes"][dp]["pancake"])

                        if "isolation" in data["isolations"][dp]:
                            dpisolation = isolation.from_data(data["isolations"][dp]["isolation"])
                        else:
                            dpisolation = myisolation
                        isolations.append(dpisolation)

                        dp_ = dblpancake(z, mypancake, myisolation)
                        r0 = min(r0, dp_.getR0())
                        r1 = max(r1, dp_.pancake.getR1())
                        dblpancakes.append(dp_)
                        logger.debug(f"mypancake: {mypancake}")
                        logger.debug(f"dpisolation: {dpisolation}")
                        logger.debug(f"dp: {dp_}")

                        z += dp_.getH()
                        z += myisolation.getH()  # isolation between DP

                    h = z - myisolation.getH()
                    # print(f"h= {self.h} [mm] = {z}-{myisolation.getH()} ({self.n} dblpancakes)")

            # shift insert by z0-z/2.
            z1 = z0 - h / 2.0
            z = z1
            # print(f'shift insert by {z} = {self.z0}-{self.h}/2.')
            for i in range(len(dblpancakes)):
                _h = dblpancakes[i].getH()
                dblpancakes[i].setZ0(z + _h / 2.0)
                # print(f'dp[{i}]: z0={z+_h/2.}, z1={z}, z2={z+_h}')
                z += _h + myisolation.getH()

            logger.debug("=== Load cfg:")
            logger.debug(f"r0= {r0} [mm]")
            logger.debug(f"r1= {r1} [mm]")
            logger.debug(f"z1= {z0-h/2.} [mm]")
            logger.debug(f"z2= {z0+h/2.} [mm]")
            logger.debug(f"z0= {z0} [mm]")
            logger.debug(f"h= {h} [mm]")
            logger.debug(f"n= {len(dblpancakes)}")

            for i, dp in enumerate(dblpancakes):
                logger.debug(f"dblpancakes[{i}]: {dp}")
            logger.debug("===")

            name = inputcfg.replace(".json", "")
            return cls(name, z0, h, r0, r1, z1, n, dblpancakes, isolations)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"htsinsert(name={self.name}, r0={self.r0!r}, r1={self.r1!r}, z0={self.z0!r}, h={self.h!r}, n={self.n!r}, dblpancakes={self.dblpancakes!r}, isolations={self.isolations!r})"

    def get_names(self, mname: str, detail: str | DetailLevel, verbose: bool = False) -> list[str]:
        """
        Get marker names for HTS insert elements.

        Args:
            mname: Base name prefix
            detail: Detail level (DetailLevel enum or string)
            verbose: Enable verbose output

        Returns:
            list[str]: Flattened list of all marker names
        """
        # Convert enum to string for comparison
        if isinstance(detail, str):
            detail = DetailLevel[detail.upper()]

        dp_ids = []
        i_ids = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        n_dp = len(self.dblpancakes)
        for i, dp in enumerate(self.dblpancakes):
            if verbose:
                print(f"HTSInsert.names: dblpancakes[{i}]: dp={dp}")

            dp_name = f"{prefix}dp{i}"
            dp_id = dp.get_names(dp_name, detail, verbose)
            dp_ids.append(dp_id)

            if i != n_dp - 1:
                dp_i = self.isolations[i]

                _name = f"{prefix}i{i}"
                _id = dp_i.get_names(_name, detail, verbose)
                i_ids.append(_id)

        if detail == DetailLevel.DBLPANCAKE:
            return flatten([dp_ids, i_ids])
        else:
            return flatten([flatten(dp_ids), i_ids])

    def setDblpancake(self, dblpancake):
        self.dblpancakes.append(dblpancake)

    def setIsolation(self, isolation):
        self.isolations.append(isolation)

    def getR0(self) -> float:
        """
        get insert inner radius
        """
        return self.r0

    def getR1(self) -> float:
        """
        get insert outer radius
        """
        return self.r1

    def getZ0(self) -> float:
        """
        get insert center position
        """
        return self.z0

    def getH(self) -> float:
        """
        get insert total height
        """
        return self.h

    def get_lc(self) -> float:
        """
        get characteristic length for mesh
        """
        return self.dblpancakes[0].pancake.tape.getH()

    def getNtapes(self) -> list[int]:
        """
        returns the number of tapes per dblpancake as a list
        """
        n_ = []
        for dp in self.dblpancakes:
            n_.append(2 * dp.getPancake().getN())
        return n_

    def getWMandrin(self) -> list:
        """
        returns the width of Mandrin as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getPancake().getMandrin())
        return w_

    def getWPancake(self) -> list:
        """
        returns the width of pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getPancake().getW())
        return w_

    def getWPancake_Isolation(self) -> list:
        """
        returns the width of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.isolation.getW())
        return w_

    def getR0Pancake_Isolation(self) -> list:
        """
        returns the inner radius of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getIsolation().getR0())
        return w_

    def getR1Pancake_Isolation(self) -> list:
        """
        returns the external radius of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getIsolation().getR0() + dp.getIsolation().getW())
        return w_

    def getHPancake_Isolation(self) -> list:
        """
        returns the height of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getIsolation().getH())
        return w_

    def getWDblPancake(self) -> list:
        """
        returns the width of dblpancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getW())
        return w_

    def getHDblPancake(self) -> list:
        """
        returns the height of dblpancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getH())
        return w_

    def getR0_Isolation(self) -> list:
        """
        returns the inner radius of the isolation between dblpancake as a list
        """
        w_ = []
        for dp_i in self.isolations:
            w_.append(dp_i.getR0())
        return w_

    def getR1_Isolation(self) -> list:
        """
        returns the external radius of the isolation between dblpancake as a list
        """
        w_ = []
        for dp_i in self.isolations:
            w_.append(dp_i.getR0() + dp_i.getW())
        return w_

    def getW_Isolation(self) -> list:
        """
        returns the width of the isolation between dblpancake as a list
        """
        w_ = []
        for dp_i in self.isolations:
            w_.append(dp_i.getW())
        return w_

    def getH_Isolation(self) -> list:
        """
        returns the height of the isolation between dblpancake as a list
        """
        w_ = []
        for dp_i in self.isolations:
            w_.append(dp_i.getH())
        return w_
