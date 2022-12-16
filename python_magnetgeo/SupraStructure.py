"""
Define HTS insert geometry
"""

import os
import sys
import gmsh

def flatten(S: list):
    from pandas.core.common import flatten
    return list(flatten(S))

class tape:
    """
    HTS tape

    w: width
    h: height
    e: thickness of co-wound durnomag
    """

    def __init__(self, w: float=0, h: float=0, e: float=0):
        self.w = w
        self.h = h
        self.e = e


    @classmethod
    def from_data(cls, data={}):
        if "w" in data:
            w = data["w"]
        if "h" in data:
            h = data["h"]
        if "e" in data:
            e = data["e"]
        return cls(w, h, e)

    def __str__(self) -> str:
        msg = "\n"
        msg += f"width: {self.w} [mm]\n"
        msg += f"height: {self.h} [mm]\n"
        msg += f"e: {self.e} [mm]\n"
        return msg
        pass

    def getH(self):
        """
        get tape height
        """
        return self.h

    def getW(self):
        """
        get total width
        """
        return (self.w + self.e)

    def getW_Sc(self):
        """
        get Sc width
        """
        return self.w

    def getW_Isolation(self):
        """
        get Isolation width
        """
        return self.e

    def getArea(self):
        """
        get tape cross section surface
        """
        return ((self.w + self.e) * self.h)

    def getFillingFactor(self):
        """
        get tape filling factor (aka ratio of superconductor over tape section)
        """
        return  (self.w * self.h) / self.getArea()

    def gmsh(self, x0: float, y0: float, detail: str):
        """
        create tape for gmsh

        inputs:
        x0, y0: coordinates of lower left point

        returns gmsh ids
        ie. [tape,isolation]
        """

        # print("gmsh/tape", x0, y0, self.w, self.e, self.h)

        # TODO return either whole tape or details

        _tape = gmsh.model.occ.addRectangle(x0, y0, 0, self.w, self.h)
        _e =gmsh.model.occ.addRectangle(x0+self.w, y0, 0, self.e, self.h)

        """
        lcar = self.getW()/3.
        gmsh.model.mesh.setSize(gmsh.model.getBoundary([(2, _tape)], False, False, True), lcar)
        gmsh.model.mesh.setSize(gmsh.model.getBoundary([(2, _e)], False, False, True), lcar)
        """

        # gmsh.model.occ.synchronize()
        return [_tape, _e]


class pancake:
    """
    Pancake structure

    r0:
    mandrin: mandrin (only for mesh purpose)
    tape: tape used for pancake
    n: number of tapes
    """

    def __init__(self, r0: float=0, tape: tape =tape(), n: int=0, mandrin=0):
        self.mandrin = mandrin
        self.tape = tape
        self.n = n
        self.r0 = r0

    @classmethod
    def from_data(cls, data={}):
        if "r0" in data:
            r0 = data["r0"]
        if "mandrin" in data:
            mandrin = data["mandrin"]
        if "tape" in data:
            t_ = tape.from_data(data["tape"])
        if "ntapes" in data:
            n = data["ntapes"]
        return cls(r0, t_, n, mandrin)
    
    def __str__(self) -> str:
        msg = "\n"
        msg += f"r0: {self.r0} [m]\n"
        msg += f"mandrin: {self.mandrin} [m]\n"
        msg += f"ntapes: {self.n} \n"
        msg += f"tape: {self.tape}***\n"
        return msg
        pass

    def getN(self) -> int:
        """
        get number of tapes
        """
        return self.n

    def getTape(self):
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
        return self.n * (self.tape.w+self.tape.e) + self.r0

    def getR(self):
        """
        get list of tapes inner radius
        """
        r = []
        ri = self.getR0()
        dr = self.tape.w + self.tape.e
        for i in range(self.n):
            # print(f"r[{i}]={ri}, {ri+self.tape.w + self.tape.e/2.}")
            r.append(ri)
            ri += dr
        # print(f"r[-1]: {r[0]}, {r[-1]}, {r[-1]+self.tape.w + self.tape.e/2.}, {self.n}, {self.getR1()}")
        return r

    def getFillingFactor(self) -> float:
        """
        ratio of the surface occupied by the tapes / total surface
        """
        S_tapes = self.n * self.tape.w * self.tape.h
        return S_tapes / self.getArea()

    def getW(self) -> float:
        return (self.getR1() - self.getR0())

    def getH(self) -> float:
        return self.tape.getH()

    def getArea(self) -> float:
        return (self.getR1() - self.getR0()) * self.getH()

    def gmsh(self, x0: float, y0: float, detail: str):
        """
        create pancake for gmsh

        inputs:
        x0, y0: coordinates of lower left point
        tag: for tape
        tag_e: for insulation

        returns gmsh ids
        ie. [_mandrin, [tape_id]]
        """
        #print("gmsh/pancake")

        # TODO return either pancake as a whole or detailed
        if detail == "pancake":
            _id = gmsh.model.occ.addRectangle(self.getR0(), y0, 0, self.getW(), self.getH())
            
            """
            lcar = (self.getR1()-self.getR1())/10.
            gmsh.model.mesh.setSize(gmsh.model.getBoundary([(2, _id)], False, False, True), lcar)
            """
            return _id
        else:
            _mandrin = gmsh.model.occ.addRectangle(self.r0-self.mandrin, y0, 0, self.mandrin, self.getH())
            # print("pancake/gmsh: create mandrin {_mandrin}")
            x0 = self.r0
            tape_ids = []
            for i in range(self.n):
                tape_id = self.tape.gmsh(x0, y0, detail)
                x0 = x0 + self.tape.getW()
                tape_ids.append(tape_id)

            #gmsh.model.occ.synchronize()
            return [_mandrin, tape_ids]

class isolation:
    """
    Isolation

    r0: inner radius of isolation structure
    w: widths of the different layers
    h: heights of the different layers
    """

    def __init__(self, r0: float=0, w: list =[], h: list =[]):
        self.r0 = r0
        self.w = w
        self.h = h

    @classmethod
    def from_data(cls, data={}):
        if "r0" in data:
            r0 = data["r0"]
        if "w" in data:
            w = data["w"]
        if "h" in data:
            h = data["h"]
        return cls(r0, w, h)

    def __str__(self) -> str:
        msg = "\n"
        msg += f'r0: {self.r0} [mm]\n'
        msg += f'w: {self.w} \n'
        msg += f'h: {self.h} \n'
        return msg
        pass

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

    def gmsh(self, x0: float, y0: float, detail: str):
        """
        create isolation for gmsh

        inputs:
        x0, y0: coordinates of lower left point

        returns gmsh id
        """

        # print("gmsh/isolation")
        # TODO: return either isolation as a whole or detail
        _id = gmsh.model.occ.addRectangle(self.r0, y0, 0, self.getW(), self.getH())
        return _id
        """
        _ids = []
        for i in range(self.getLayer()):
            _id = gmsh.model.occ.addRectangle(self.r0, y0, 0, self.getW_Layer(i), self.getH_Layer(i))
            _ids.append(_id)
        # gmsh.model.occ.synchronize()
        # return _ids
        """

class dblpancake:
    """
    Double Pancake structure

    z0: position of the double pancake (centered on isolation)
    pancake: pancake structure (assume that both pancakes have the same structure)
    isolation: isolation between pancakes
    """

    def __init__(self, z0: float, pancake: pancake=pancake(), isolation: isolation=isolation()):
        self.z0 = z0
        self.pancake = pancake
        self.isolation = isolation

    def __str__(self) -> str:
        msg = f'r0={self.pancake.getR0()}, '
        msg += f'r1={self.pancake.getR1()}, '
        msg += f'z1={self.getZ0() - self.getH()/2.}, '
        msg += f'z2={self.getZ0() + self.getH()/2.}'
        msg += f'(z0={self.getZ0()}, h={self.getH()})'
        return msg

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

    def setZ0(self, z0) -> float:
        self.z0 = z0

    def setPancake(self, pancake):
        self.pancake = pancake

    def setIsolation(self, isolation):
        self.isolation = isolation

    def getFillingFactor(self) -> float:
        """
        ratio of the surface occupied by the tapes / total surface
        """
        S_tapes = 2. * self.pancake.n * self.pancake.tape.w * self.pancake.tape.h
        return (S_tapes / self.getArea())

    def getR0(self) -> float:
        return self.pancake.getR0()

    def getZ0(self) -> float:
        return self.z0

    def getW(self) -> float:
        return self.pancake.getW()

    def getH(self) -> float:
        return ( 2.*self.pancake.getH() + self.isolation.getH() )

    def getArea(self) -> float:
        return ((self.pancake.getR1() - self.pancake.getR0()) * self.getH())

    def gmsh(self, x0: float, y0: float, detail: str):
        """
        create dbl pancake for gmsh

        inputs:
        x0, y0: coordinates of lower left point

        returns tuple of gmsh ids
        ie. (m_id, t_id, e_id, i_id)
        """
        # print("gmsh/dblpancake")

        #TODO if detail="pancake" return the pancake as a whole
        #     otherwise do like bellow
        if detail == "dblpancake":
            _id = gmsh.model.occ.addRectangle(self.getR0(), y0, 0, self.getW(), self.getH())
            """
            lcar = self.getW() / 10.
            gmsh.model.mesh.setSize(gmsh.model.getBoundary([(2, _id)], False, False, True), lcar)
            """
            return _id
        else:
            p_ids = []
            
            _id = self.pancake.gmsh(x0, y0, detail)
            p_ids.append(_id)

            y0 += self.pancake.getH()
            _isolation_id = self.isolation.gmsh(x0, y0, detail)
    
            y0 += self.isolation.getH()
            _id = self.pancake.gmsh(x0, y0, detail)
            p_ids.append(_id)

            #gmsh.model.occ.synchronize()
            return [p_ids, _isolation_id]

class HTSinsert:
    """
    HTS insert

    dblpancakes: stack of double pancakes
    isolation: stack of isolations between double pancakes

    TODO: add possibility to use 2 different pancake
    """

    def __init__(self, z0: float=0, h: float=0, r0: float=0, r1: float=0, z1: float=0, n: int=0, dblpancakes: list=[], isolations: list=[]):
        self.z0 = z0
        self.h = h
        self.r0 = r0
        self.r1 = r1
        self.z1 = z1
        self.n = n
        self.dblpancakes = dblpancakes
        self.isolations = isolations

    def setDblpancake(self, dblpancake):
        self.dblpancakes.append(dblpancake)

    def setIsolation(self, isolation):
        self.isolations.append(isolation)

    def setZ0(self, z0: float):
        self.z0 = z0

    def getZ0(self) -> float:
        """
        returns the bottom altitude of de SuperConductor insert
        """
        return self.z0

    def getZ1(self) -> float:
        """
        returns the top altitude of de SuperConductor insert
        """
        return self.z1

    def getH(self) -> float:
        """
        returns the height of de SuperConductor insert
        """

        return self.h

    def getR0(self) -> float:
        """
        returns the inner radius of de SuperConductor insert
        """
        return self.r0

    def getR1(self) -> float:
        """
        returns the outer radius of de SuperConductor insert
        """
        return self.r1

    def getN(self) -> int:
        """
        returns the number of dbl pancakes
        """
        return self.n

    def getNtapes(self) -> list:
        """
        returns the number of tapes as a list
        """
        n_ = []
        for dp in self.dblpancakes:
            n_.append( dp.getPancake().getN() )
        return n_

    def getHtapes(self) -> list:
        """
        returns the width of SC tapes
        either as an float or a list
        """
        w_tapes = []
        for dp in self.dblpancakes:
            w_tapes.append( dp.pancake.getTape().getH() )
        return w_tapes

    def getWtapes_SC(self) -> list:
        """
        returns the width of SC tapes as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.pancake.getTape().getW_Sc() )
        return w_

    def getWtapes_Isolation(self) -> list:
        """
        returns the width of isolation between tapes as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.pancake.getTape().getW_Isolation() )
        return w_

    def getMandrinPancake(self) -> list:
        """
        returns the width of Mandrin as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getPancake().getMandrin() )
        return w_

    def getWPancake(self) -> list:
        """
        returns the width of pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getPancake().getW() )
        return w_

    def getWPancake_Isolation(self) -> list:
        """
        returns the width of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.isolation.getW() )
        return w_

    def getR0Pancake_Isolation(self) -> list:
        """
        returns the inner radius of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getIsolation().getR0() )
        return w_

    def getR1Pancake_Isolation(self) -> list:
        """
        returns the external radius of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getIsolation().getR0() + dp.getIsolation().getW() )
        return w_

    def getHPancake_Isolation(self) -> list:
        """
        returns the height of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getIsolation().getH() )
        return w_


    def getWDblPancake(self) -> list:
        """
        returns the width of dblpancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getW() )
        return w_

    def getHDblPancake(self) -> list:
        """
        returns the height of dblpancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append( dp.getH() )
        return w_

    def getR0_Isolation(self) -> list:
        """
        returns the inner radius of isolation between dbl pancake as a list
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getR0() )
        return w_

    def getR1_Isolation(self) -> list:
        """
        returns the external radius of isolation between dbl pancake as a list
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getR0() +  isolant.getH() )
        return w_

    def getW_Isolation(self) -> list:
        """
        returns the width of isolation between dbl pancakes
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getW() )
        return w_

    def getH_Isolation(self) -> list:
        """
        returns the height of isolation between dbl pancakes
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getH() )
        return w_

    def getFillingFactor(self) -> float:
        S_tapes = 0
        for dp in self.dblpancakes:
            S_tapes += dp.pancake.n * 2 * dp.pancake.tape.w * dp.pancake.tape.h
        return S_tapes / self.getArea()

    def getArea(self) -> float:
        return (self.getR1() - self.getR0()) * self.getH()

    def loadCfg(self, inputcfg: str, debug: bool=False):
        """
        Load insert params from json
        """
        import json

        with open(inputcfg) as f:
            data = json.load(f)
            if debug:
                print("HTSinsert data:", data)

            """
            print("List main keys:")
            for key in data:
                print("key:", key)
            """

            mytape = None
            if "tape" in data:
                mytape = tape.from_data(data["tape"])

            mypancake = None
            if "pancake" in data:
                mypancake = pancake.from_data(data["pancake"])
                if debug:
                    print(f'mypancake={mypancake}')

            myisolation = None
            if "isolation" in data:
                myisolation = isolation.from_data(data["isolation"])
                if debug:
                    print(f'myisolation={myisolation}')

            z = 0
            if "dblpancakes" in data:
                if debug:
                    print(f"DblPancake data:", data["dblpancakes"])

                # if n defined use the same pancakes and isolations
                # else loop to load pancake and isolation structure definitions
                if "n" in data["dblpancakes"]:
                    self.n = data["dblpancakes"]["n"]
                    if debug: 
                        print(f"Loading {self.n} similar dblpancakes, z={z}")
                    if "isolation" in data["dblpancakes"]:
                        dpisolation = isolation.from_data(data["dblpancakes"]["isolation"])
                    else:
                        dpisolation = myisolation
                    if debug:
                        print(f'dpisolation={dpisolation}')
                        print(f'dp={dp}')

                    for i in range(self.n):
                        dp = dblpancake(z, mypancake, myisolation)

                        self.setDblpancake(dp)
                        self.setIsolation(dpisolation)

                        if debug:
                            print(f'dblpancake[{i}]:')

                        z += dp.getH()
                        # print(f'z={z} dp_H={dp.getH()}')
                        if i != self.n-1:
                            z += dpisolation.getH() # isolation between D
                        # print(f'z={z} dp_i={dpisolation.getH()}')
                    
                    self.h = z
                    # print(f"h= {self.h} [mm] = {z}")

                    self.r0 = self.dblpancakes[0].getR0()
                    self.r1 = self.dblpancakes[0].getR0() + self.dblpancakes[0].getW()
                else:
                    if debug:
                        print(f"Loading different dblpancakes, z={z}")
                    self.n = 0
                    for dp in data['dblpancakes']:
                        self.n += 1
                        if debug:
                            print("dp:", dp, data['dblpancakes'][dp]["pancake"])
                        mypancake = pancake.from_data(data['dblpancakes'][dp]["pancake"])

                        if "isolation" in data['isolations'][dp]:
                            dpisolation = isolation.from_data(data['isolations'][dp]["isolation"])
                        else:
                            dpisolation = myisolation
                        self.setIsolation(dpisolation)

                        dp_ = dblpancake(z, mypancake, myisolation)
                        self.r0 = min(self.r0, dp_.getR0())
                        self.r1 = max(self.r1, dp_.pancake.getR1())
                        self.setDblpancake(dp_)
                        if debug:
                            print(f'mypancake: {mypancake}')
                            print(f'dpisolant: {dpisolation}')
                            print(f'dp: {dp_}')

                        z += dp_.getH()
                        z += myisolation.getH() # isolation between DP

                    self.h = z - myisolation.getH()
                    # print(f"h= {self.h} [mm] = {z}-{myisolation.getH()} ({self.n} dblpancakes)")
                    
            # shift insert by z0-z/2.
            self.z1 = self.z0 - self.h/2.
            z = self.z1
            # print(f'shift insert by {z} = {self.z0}-{self.h}/2.')
            for i in range(len(self.dblpancakes)):
                _h =  self.dblpancakes[i].getH()
                self.dblpancakes[i].setZ0(z + _h/2.)
                # print(f'dp[{i}]: z0={z+_h/2.}, z1={z}, z2={z+_h}')
                z += _h + myisolation.getH()

            if debug:
                print("=== Load cfg:")
                print(f"r0= {self.r0} [mm]")
                print(f"r1= {self.r1} [mm]")
                print(f"z1= {self.getZ0()-self.getH()/2.} [mm]")
                print(f"z2= {self.getZ0()+self.getH()/2.} [mm]")
                print(f"z0= {self.z0} [mm]")
                print(f"h= {self.h} [mm]")
                print(f"n= {len(self.dblpancakes)}")

                for i,dp in enumerate(self.dblpancakes):
                    print(f"dblpancakes[{i}]: {dp}")
                print("===")

    def gmsh(self, detail: str, AirData: tuple =(), debug: bool = False):
        """
        create insert for gmsh

        inputs:
        x0, y0: coordinates of lower left point
        detail: level of precision

        returns gmsh ids depending on detail value
        ie. [dp_ids, isolation_ids]
        """

        x0 = self.r0
        y0 = self.z0-self.getH()/2.
        n_dp = len(self.dblpancakes)

        if detail == "None":
            #
            id = gmsh.model.occ.addRectangle(self.r0, y0, 0, (self.r1-self.r0), self.getH())
            
            # Now create air
            if AirData:
                r0_air = 0
                dr_air = (self.r1-self.r0) * AirData[0]
                z0_air = y0 * AirData[1]
                dz_air = (2 * abs(y0) ) * AirData[1]
                _id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
                ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, id)] )
                return (id, (_id, dr_air, z0_air, dz_air))
            return (id, None)

        else:
            dp_ids = []
            i_ids = []
                    
            for i,dp in enumerate(self.dblpancakes):
                dp_id = dp.gmsh(x0, y0, detail)
                dp_ids.append(dp_id)
                y0 += dp.getH()
                if i != n_dp-1 :
                    _id = self.isolations[i].gmsh(x0, y0, detail)
                    y0 += self.isolations[i].getH()
                    i_ids.append(_id)

            #for i,ids in enumerate(i_ids):
            #    print(f"i_ids[{i}]={ids}")
        
            # Perform BooleanFragment
            print(f"Create BooleanFragments (detail={detail})")
            for j,dp in enumerate(dp_ids):
                print(f"HTSInsert gmsh: dp[{j}]")
                if isinstance(dp, list):
                    for p in dp:
                        # print(f"HTSInsert gmsh: dp[{j}] p={p}")
                        # dp = [ [p0, p1], isolation ]
                        if isinstance(p, list):
                            # print(f"HTSInsert gmsh: dp[{j}] len(p)={len(p)}, {type(p[0])}, dp[-1]={dp[-1]}" )
                            if len(p) == 2 and isinstance(p[0], int):
                                # detail == pancake 
                                # print(f"HTSInsert gmsh: dp[{j}] len(p)={len(p)}, p={p}, i_ids={len(i_ids)}")
                                
                                if j >= 1:
                                    ov, ovv = gmsh.model.occ.fragment([(2, p[0])], [(2, i_ids[j-1])])
                                if j < n_dp-1:
                                    ov, ovv = gmsh.model.occ.fragment([(2, p[1])], [(2, i_ids[j])])
                                ov, ovv = gmsh.model.occ.fragment([(2, dp[-1])], [(2, p[0]), (2, p[1])] )
                                
                            else:
                                # detail == tape
                                # p = [ mandrin, [[SC, duromag], [SC, duromag], ...] ]
                                # print(f"HTSInsert gmsh: dp[{j}] len(p)={len(p)}, p={p}")
                                flat_p0 = flatten(p[0])
                                flat_p1 = flatten(p[1])
                                if j >= 1:
                                    ov, ovv = gmsh.model.occ.fragment([(2, i_ids[j-1])], [(2, l) for l in flat_p0])
                                if j < n_dp-1:
                                    ov, ovv = gmsh.model.occ.fragment([(2, i_ids[j])], [(2, l) for l in flat_p1])
                                ov, ovv = gmsh.model.occ.fragment([(2, dp[-1])], [(2, l) for l in flat_p0] + [(2, l) for l in flat_p1] )
                                
                                """
                                for t in p:    
                                    # print("flatten:", flat_list)
                                    flat_list = flatten(t[1])
                                    ov, ovv = gmsh.model.occ.fragment([(2, dp[-1])], [(2, l) for l in flat_list])
                                    if j < n_dp-1:
                                        ov, ovv = gmsh.model.occ.fragment([(2, i_ids[j])], [(2, l) for l in flat_list] )
                                """
                else:
                    # detail == dblpancake 
                    if j >= 1:
                        ov, ovv = gmsh.model.occ.fragment([(2, dp)], [(2, i_ids[j-1])])
                    if j < n_dp-1:
                        ov, ovv = gmsh.model.occ.fragment([(2, dp)], [(2, i_ids[j])])

            # Now create air
            if AirData:
                y0 = self.z0-self.getH()/2. # need to force y0 to init value
                r0_air = 0
                dr_air = (self.r1-self.r0) * 2
                z0_air = y0 * 1.2
                dz_air = (2 * abs(y0) ) * 1.2    
                _id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
                # TODO fragment _id with dp_ids, i_ids
                for j,i_dp in enumerate(i_ids):
                    ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, i_dp)])

                for j,dp in enumerate(dp_ids):
                    # dp = [ [p0, p1], isolation ]
                    print(f"HTSInsert with Air: dp[{j}] detail={detail} dp={dp}")
                    if isinstance(dp, list):
                        # detail == pancake|tape
                        # print(_id, flatten(dp))
                        ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, l) for l in flatten(dp)])               
                    else:
                        # detail == dblpancake 
                        ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, dp)])
                        # ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, i) for i in i_ids])
                
                # print("dp_ids:", dp_ids)
                # print("i_ids:", i_ids)
                return ([dp_ids, i_ids], (_id, dr_air, z0_air, dz_air))

            return ([dp_ids, i_ids], None)

    def gmsh_bcs(self, name: str,  detail: str, ids: tuple, debug=False):
        """
        create bcs groups for gmsh

        inputs:
        

        returns
        """

        defs = {}
        (gmsh_ids, Air_data) = ids

        print("Set Physical Volumes")
        if isinstance(gmsh_ids, list):
            dp_ids = gmsh_ids[0]
            i_ids = gmsh_ids[1]
            for i,isol in enumerate(i_ids):
                ps = gmsh.model.addPhysicalGroup(2, [isol])
                gmsh.model.setPhysicalName(2, ps, f"{name}_i_dp{i}")
                defs[f"{name}_i_dp{i}"] = ps
            for i,dp in enumerate(dp_ids):
                print(f"dp[{i}")
                if detail == "dblpancake":
                    ps = gmsh.model.addPhysicalGroup(2, [dp])
                    gmsh.model.setPhysicalName(2, ps, f"{name}_dp{i}")
                    defs[f"{name}_dp{i}"] = ps
                elif detail == "pancake":
                    # print("dp:", dp)
                    ps = gmsh.model.addPhysicalGroup(2, [dp[0][0]])
                    gmsh.model.setPhysicalName(2, ps, f"{name}_p{0}_dp{i}")
                    defs[f"{name}_p{0}_dp{i}"] = ps
                    ps = gmsh.model.addPhysicalGroup(2, [dp[0][1]])
                    gmsh.model.setPhysicalName(2, ps, f"{name}_p{1}_dp{i}")
                    defs[f"{name}_p{1}_dp{i}"] = ps
                    ps = gmsh.model.addPhysicalGroup(2, [dp[1]])
                    gmsh.model.setPhysicalName(2, ps, f"{name}_i_dp{i}")
                    defs[f"{name}_i_p{i}"] = ps
                elif detail == "tape":
                    # print("HTSInsert/gsmh_bcs (tape):", dp)
                    ps = gmsh.model.addPhysicalGroup(2, [dp[1]])
                    gmsh.model.setPhysicalName(2, ps, f"{name}_i_p{i}")
                    defs[f"{name}_i_p{i}"] = ps
                    for t in dp[0][0]:
                        # print("p0:", t)
                        if isinstance(t, list):
                            for l,t_id in enumerate(t):
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[0]])
                                gmsh.model.setPhysicalName(2, ps, f"{name}_sc{l}_p{0}_dp{i}")
                                defs[f"{name}_sc{l}_p{0}_dp{i}"] = ps
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[1]])
                                gmsh.model.setPhysicalName(2, ps, f"{name}_du{l}_p{0}_dp{i}")
                                defs[f"{name}_du{l}_p{0}_dp{i}"] = ps
                        else:
                            ps = gmsh.model.addPhysicalGroup(2, [t])
                            gmsh.model.setPhysicalName(2, ps, f"{name}_mandrin_p{0}_dp{i}")
                            defs[f"{name}_mandrin_p{0}_dp{i}"] = ps
                            print(f"HTSInsert/gmsh_bcs: mandrin {t}: {ps}")
                    for t in dp[0][1]:
                        # print("p1:", t)
                        if isinstance(t, list):
                            for l,t_id in enumerate(t):
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[0]])
                                gmsh.model.setPhysicalName(2, ps, f"{name}_sc{l}_p{1}_dp{i}")
                                defs[ f"{name}_sc{l}_p{1}_dp{i}"] = ps
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[1]])
                                gmsh.model.setPhysicalName(2, ps,  f"{name}_du{l}_p{1}_dp{i}")
                                defs[ f"{name}_du{l}_p{1}_dp{i}"] = ps
                        else:
                            ps = gmsh.model.addPhysicalGroup(2, [t])
                            gmsh.model.setPhysicalName(2, ps, f"{name}_mandrin_p{1}_dp{i}")
                            defs[f"{name}_mandrin_p{1}_dp{i}"] = ps
                            print(f"HTSInsert/gmsh_bcs: mandrin {t}: {ps}")
        else:   
            ps = gmsh.model.addPhysicalGroup(2, [gmsh_ids])
            gmsh.model.setPhysicalName(2, ps, f"{name}_S")

        # TODO set lc charact on Domains
        # TODO retreive BCs group for Rint, Rext, Top, Bottom

        print("TODO: Set Physical Surfaces")
        # Select the corner point by searching for it geometrically:
        eps = 1e-3
        gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)
        ov = gmsh.model.getEntitiesInBoundingBox(self.getR0()* (1-eps), (self.z0-self.getH()/2.)* (1-eps), 0,
                                                 self.getR1()* (1+eps), (self.z0-self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Bottom:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, f"{name}_Bottom")
        defs[f"{name}_Bottom"] = ps

        ov = gmsh.model.getEntitiesInBoundingBox(self.getR0()* (1-eps), (self.z0+self.getH()/2.)* (1-eps), 0,
                                                 self.getR1()* (1+eps), (self.z0+self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Top:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, f"{name}_Top")
        defs[f"{name}_Top"] = ps
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.getR0()* (1-eps), (self.z0-self.getH()/2.)* (1-eps), 0,
                                                 self.getR0()* (1+eps), (self.z0+self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Rint:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, f"{name}_Rint")
        defs[f"{name}_Rint"] = ps

        ov = gmsh.model.getEntitiesInBoundingBox(self.getR1()* (1-eps), (self.z0-self.getH()/2.)* (1-eps), 0,
                                                 self.getR1()* (1+eps), (self.z0+self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Rext:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, f"{name}_Rext")
        defs[f"{name}_Rext"] = ps

        # TODO: Air
        if Air_data:
            (Air_id, dr_air, z0_air, dz_air) = Air_data

            ps = gmsh.model.addPhysicalGroup(2, [Air_id])
            gmsh.model.setPhysicalName(2, ps, "Air")
            defs["Air"] = ps

            # TODO: Axis, Inf
            gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)
            
            eps = 1.e-6
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, +eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Axis")
            defs["Axis"] = ps
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, dr_air+eps, z0_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(dr_air-eps, z0_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(-eps, z0_air+dz_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Infty")
            defs["Infty"] = ps

        return defs

    def gmsh_msh(self, defs: dict = {}, lc: list=[]):
        print("TODO: set characteristic lengths")
        """
        lcar = (nougat.getR1() - nougat.R(0) ) / 10.
        lcar_dp = nougat.dblpancakes[0].getW() / 10.
        lcar_p = nougat.dblpancakes[0].getPancake().getW() / 10.
        lcar_tape = nougat.dblpancakes[0].getPancake().getW()/3.

        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar)
        # Override this constraint on the points of the tapes:

        gmsh.model.mesh.setSize(gmsh.model.getBoundary(tapes, False, False, True), lcar_tape)
        """
        pass
    
    # TODO move the template in a well defined directory (defined in config file for magnetgeo)
    def template_gmsh(self, name: str, detail: str) -> None:
        """
        generate a geo gmsh file

        option = dblpancake|pancake|tape control the precision of the model
        """

        details= {
            "tape" : 0,
            "pancake" : 1,
            "dblpancake" : 2,
            "None" : 3
        }
        
        print("ISolations:", len(self.isolations))
        print("=== Save to geo gmsh: NB use gmsh 4.9 or later")
        import getpass
        UserName = getpass.getuser()

        max_mandrin = max(self.getMandrinPancake())
        min_r_ = min(self.getR0Pancake_Isolation())
        min_r_dp = min(self.getR0_Isolation())
        xmin = min(self.getR0()-max_mandrin, min_r_dp, min_r_)


        rmin = min(self.getR0()-max_mandrin, min_r_dp, min_r_)
        rmax = 0
        for i, dp in enumerate(self.dblpancakes):
            r_dp = self.isolations[i].getR0()
            r_ = dp.getIsolation().getR0()
            rmax = max(rmax, dp.getPancake().getR0(), r_dp, r_)
        if rmax > self.getR0():
            print(f"ATTENTION rmax={rmax} > r0={self.getRO()}")
        """
        # To be checked if r_ and/or r_dp > r0
        for r in r_dp:
            if r > r0:
                ...
        for r in r_:
            if r > r0:
                ...
        """

        xmax = 0
        for i, dp in enumerate(self.dblpancakes):
            r_dp = self.isolations[i].getR0() + self.isolations[i].getW()
            r_ = dp.getIsolation().getR0() + dp.getIsolation().getW()
            xmax = max(xmax, r_dp, r_)

        # Some data will be stored as list (str(...)
        data_dict = {
            'detail': details[detail],
            'z0':self.getZ0()-self.getH()/2.,
            'r0':self.getR0(),
            'z1':self.getZ0()+self.getH()/2.,
            'r1':self.getR1(),
            'n_dp':self.getN(),
            'e_dp':str(self.getWDblPancake()).replace('[','{').replace(']','}'),
            'h_dp':str(self.getHDblPancake()).replace('[','{').replace(']','}'),
            'h_dp_isolation':str(self.getH_Isolation()).replace('[','{').replace(']','}'),
            'r_dp':str(self.getR0_Isolation()).replace('[','{').replace(']','}'),
            'e_p':str(self.getWPancake()).replace('[','{').replace(']','}'),
            'e_dp_isolation':str(self.getW_Isolation()).replace('[','{').replace(']','}'),
            'mandrin':str(self.getMandrinPancake()).replace('[','{').replace(']','}'),
            'h_tape':str(self.getHtapes()).replace('[','{').replace(']','}'),
            'h_isolation':str(self.getHPancake_Isolation()).replace('[','{').replace(']','}'),
            'r_':str(self.getR0Pancake_Isolation()).replace('[','{').replace(']','}'),
            'e_isolation':str(self.getWPancake_Isolation()).replace('[','{').replace(']','}'),
            'n_t':str(self.getNtapes()).replace('[','{').replace(']','}'),
            'e_t':str(self.getWtapes_Isolation()).replace('[','{').replace(']','}'),
            'w_t':str(self.getWtapes_SC()).replace('[','{').replace(']','}'),
            'emin':min(self.getWtapes_Isolation()),
            'xmin':xmin,
            'rmin':rmin,
            'rmax':rmax,
            'xmax':xmax,
        }

        # Load template file (TODO use jinja2 instead? or chevron)
        import chevron
        geofile = chevron.render("template-hts.mustache", data_dict)
        
        # print("geofile:", geofile)
        geofilename = name + "_hts_axi.geo"
        with open(geofilename, "x") as f:
            f.write(geofile)

        return

