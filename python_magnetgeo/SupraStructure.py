"""
Define HTS insert geometry
"""

# from typing import SupportsFloat

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

    def __init__(self, w=0, h=0, e=0):
        self.w = w
        self.h = h
        self.e = e


    def __init__(self, data={}):
        if "w" in data:
            self.w = data["w"]
        if "h" in data:
            self.h = data["h"]
        if "e" in data:
            self.e = data["e"]

    def __str__(self) -> str:
        msg = "\n"
        msg += "width: %g [mm]\n" % self.w
        msg += "height: %g [mm]\n" % self.h
        msg += "e: %g [mm]\n" % self.e
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

    def __init__(self, r0=0, tape=tape(), n=0, mandrin=0) -> None:
        self.mandrin = mandrin
        self.tape = tape
        self.n = n
        self.r0 = r0
        pass

    def __init__(self, data={}):
        if "r0" in data:
            self.r0 = data["r0"]
        if "mandrin" in data:
            self.mandrin = data["mandrin"]
        if "tape" in data:
            self.tape = tape(data["tape"])
        if "ntapes" in data:
            self.n = data["ntapes"]

    def __str__(self) -> str:
        msg = "\n"
        msg += "r0: %g [m]\n" % self.r0
        msg += "mandrin: %g [m]\n" % self.mandrin
        msg += "ntapes: %d \n" % self.n
        msg += "tape: %s***\n" % self.tape
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
            # print("r[%d]=%g,%g" % (i, ri, ri+self.tape.w + self.tape.e/2.))
            r.append(ri)
            ri += dr
        # print("r[-1]:", r[0], r[-1], r[-1]+self.tape.w + self.tape.e/2., self.n, self.getR1())
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
            # print("pancake/gmsh: create mandrin %d" % _mandrin)
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

    def __init__(self, r0=0, w=[], h=[]) -> None:
        self.r0 = r0
        self.w = w
        self.h = h
        pass

    def __init__(self, data={}):
        if "r0" in data:
            self.r0 = data["r0"]
        if "w" in data:
            self.w = data["w"]
        if "h" in data:
            self.h = data["h"]

    def __str__(self) -> str:
        msg = "\n"
        msg += "r0: %g [mm]\n" % self.r0
        msg += "w:" + str(self.w) + "\n"
        msg += "h:" + str(self.h) + "\n"
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

    def __init__(self) -> None:
        self.z0 = 0
        self.pancake = pancake()
        self.isolation = isolation()
        pass

    def __init__(self, data={}):
        if "z0" in data:
            self.z0 = data["z0"]
        if "pancake" in data:
            self.pancake = pancake(data["pancake"])
        if "isolation" in data:
            self.isolation = data["isolation"]
            print(self.isolation)

    def __str__(self) -> str:
        msg = str(self.pancake.getR0()) + ", "
        msg += str(self.pancake.getR1()) + ", "
        msg += str(self.z0 - self.getH()) + ", "
        msg += str(self.z0 + self.getH())
        return msg
        pass

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
        S_tapes = 2 * self.pancake.n * self.pancake.tape.w * self.pancake.tape.h
        return S_tapes / self.getArea()

    def getR0(self) -> float:
        return self.pancake.r0

    def getZ0(self) -> float:
        return self.z0

    def getW(self) -> float:
        return self.pancake.getW()

    def getH(self) -> float:
        return 2*self.pancake.getH() + self.isolation.getH()

    def getArea(self) -> float:
        return (self.pancake.getR1() - self.pancake.getR0()) * self.getH()

    def gmsh(self, x0: float, y0: float, detail: str):
        """
        create dble pancake for gmsh

        inputs:
        x0, y0: coordinates of lower left point

        returns tuple of gmsh ids
        ie. (m_id, t_id, e_id, i_id)
        """
        # print("gmsh/dblepancake")

        #TODO if detail="pancake" return the pancake as a whole
        #     otherwise do like bellow
        if detail == "dblepancake":
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

    dblepancakes: stack of double pancakes
    isolation: stack of isolations between double pancakes

    TODO: add possibility to use 2 different pancake
    """

    def __init__(self) -> None:
        self.z0 = 0
        self.h = 0
        self.r0 = 0
        self.r1 = 0
        self.z1 = 0
        self.n = 0
        self.dblepancakes = []
        self.isolations = []
        pass

    def setDblepancake(self, dblepancake):
        self.dblepancakes.append(dblepancake)

    def setIsolation(self, isolation):
        self.isolations.append(isolation)

    def setZ0(self, z0):
        self.z0 = 0

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
        returns the number of dble pancakes
        """
        return self.n

    def getNtapes(self) -> list:
        """
        returns the number of tapes as a list
        """
        n_ = []
        for dp in self.dblepancakes:
            n_.append( dp.getPancake().getN() )
        return n_

    def getHtapes(self) -> list:
        """
        returns the width of SC tapes
        either as an float or a list
        """
        w_tapes = []
        for dp in self.dblepancakes:
            w_tapes.append( dp.pancake.getTape().getH() )
        return w_tapes

    def getWtapes_SC(self) -> list:
        """
        returns the width of SC tapes as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.pancake.getTape().getW_Sc() )
        return w_

    def getWtapes_Isolation(self) -> list:
        """
        returns the width of isolation between tapes as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.pancake.getTape().getW_Isolation() )
        return w_

    def getMandrinPancake(self) -> list:
        """
        returns the width of Mandrin as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.getPancake().getMandrin() )
        return w_

    def getWPancake(self) -> list:
        """
        returns the width of pancake as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.getPancake().getW() )
        return w_

    def getWPancake_Isolation(self) -> list:
        """
        returns the width of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.isolation.getW() )
        return w_

    def getR0Pancake_Isolation(self) -> list:
        """
        returns the height of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.getIsolation().getR0() )
        return w_

    def getHPancake_Isolation(self) -> list:
        """
        returns the height of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.getIsolation().getH() )
        return w_


    def getWDblePancake(self) -> list:
        """
        returns the width of dblepancake as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.getW() )
        return w_

    def getHDblePancake(self) -> list:
        """
        returns the height of dblepancake as a list
        """
        w_ = []
        for dp in self.dblepancakes:
            w_.append( dp.getH() )
        return w_

    def getR0_Isolation(self) -> list:
        """
        returns the height of isolation between dble pancake as a list
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getR0() )
        return w_

    def getW_Isolation(self) -> list:
        """
        returns the width of isolation between dble pancakes
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getW() )
        return w_

    def getH_Isolation(self) -> list:
        """
        returns the height of isolation between dble pancakes
        """
        w_ = []
        for isolant in self.isolations:
            w_.append( isolant.getH() )
        return w_

    def getFillingFactor(self) -> float:
        S_tapes = 0
        for dp in self.dblepancakes:
            S_tapes += dp.pancake.n * 2 * dp.pancake.tape.w * dp.pancake.tape.h
        return S_tapes / self.getArea()

    def getArea(self) -> float:
        return (self.getR1() - self.getR0()) * self.getH()

    def loadCfg(self, inputcfg: str):
        """
        Load insert params from json
        """
        import json

        with open(inputcfg) as f:
            data = json.load(f)
            print("HTSinsert data:", data)

            """
            print("List main keys:")
            for key in data:
                print("key:", key)
            """

            mytape = None
            if "tape" in data:
                mytape = tape(data["tape"])

            mypancake = None
            if "pancake" in data:
                mypancake = pancake(data["pancake"])

            myisolation = None
            if "isolation" in data:
                myisolation = isolation(data["isolation"])

            if "dblepancakes" in data:
                print("DblePancake data:", data["dblepancakes"])

                # if n defined use the same pancakes and isolations
                # else loop to load pancake and isolation structure definitions
                if "n" in data["dblepancakes"]:
                    z = 0
                    if "isolation" in data["dblepancakes"]:
                        dpisolation = isolation(data["dblepancakes"]["isolation"])
                    else:
                        dpisolation = myisolation

                    self.n = data["dblepancakes"]["n"]
                    for i in range(self.n):
                        # print("dblepancake[%d]" % i, "z0= %g [mm]" % z)
                        dblepancake = dblpancake()
                        dblepancake.setZ0(z)
                        dblepancake.setPancake(mypancake)
                        dblepancake.setIsolation(myisolation)
                        self.setDblepancake(dblepancake)
                        self.setIsolation(dpisolation)

                        z += dblepancake.getH()
                        z += dpisolation.getH() # isolation between DP

                    self.h = z - dpisolation.getH()
                    self.r0 = mypancake.getR0()
                    self.r1 = mypancake.getR1()

                    # shift insert by z0-z/2.
                    z = self.z0 - self.h/2.
                    for i in range(self.n):
                        h = self.dblepancakes[i].getH()
                        self.dblepancakes[i].setZ0(z + h/2.)
                        z += h
                        z += dpisolation.getH()

                else:
                    z = 0
                    print("Loading different dblepancakes")
                    for dp in data['dblepancakes']:
                        print("dp:", dp, data['dblepancakes'][dp]["pancake"])
                        mypancake = pancake(data['dblepancakes'][dp]["pancake"])
                        print(mypancake)

                        print("isolant:", dp, data['isolations'][dp])
                        myisolation = isolation(data['isolations'][dp])
                        print(myisolation)
                        self.setIsolation(myisolation)

                        dblepancake = dblpancake()
                        print(type(dblepancake))
                        dblepancake.setZ0(z)
                        dblepancake.setPancake(mypancake)
                        isolant = isolation(data['dblepancakes'][dp]["isolation"])
                        dblepancake.setIsolation(isolant)
                        print(dblepancake)
                        self.setDblepancake(dblepancake)

                        z += dblepancake.getH()
                        z += myisolation.getH() # isolation between DP

                        self.h = z - myisolation.getH()
                        self.r0 = mypancake.getR0()
                        self.r1 = mypancake.getR1()

                        # shift insert by z0-z/2.
                        z = self.z0 - self.h/2.
                        for i in range(self.n):
                            h = self.dblepancakes[i].getH()
                            self.dblepancakes[i].setZ0(z + h/2.)
                            z += h
                            z += myisolation.getH()


            print("=== Load cfg:")
            print("z0= %g [mm]" % self.z0)
            print("r0= %g [mm]" % self.r0)
            print("r1= %g [mm]" % self.r1)
            print("h= %g [mm]" % self.h)
            if self.n:
                print("n= %d" % self.n)
            else:
                print("n= %d" % len(self.dblepancakes))

            for i in range(self.n):
                print("dlbpancake[%d]: " % i, self.dblepancakes[i])
            print("===")

    def gmsh(self, detail: str, Air: bool =False, debug: bool = False):
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
        n_dp = len(self.dblepancakes)

        if detail == "None":
            #
            id = gmsh.model.occ.addRectangle(self.r0, y0, 0, (self.r1-self.r0), self.getH())
            
            # Now create air
            if Air:
                r0_air = 0
                dr_air = (self.r1-self.r0) * 2
                z0_air = y0 * 1.2
                dz_air = (2 * abs(y0) ) * 1.2    
                _id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
                ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, id)] )
                return (id, (_id, dr_air, z0_air, dz_air))
            return (id, None)

        else:
            dp_ids = []
            i_ids = []
                    
            for i,dp in enumerate(self.dblepancakes):
                dp_id = dp.gmsh(x0, y0, detail)
                dp_ids.append(dp_id)
                y0 += dp.getH()
                if i != n_dp-1 :
                    _id = self.isolations[i].gmsh(x0, y0, detail)
                    y0 += self.isolations[i].getH()
                    i_ids.append(_id)

            #for i,ids in enumerate(i_ids):
            #    print("i_ids[%d]=" % i, ids)
        
            # Perform BooleanFragment
            print("Create BooleanFragments (detail=%s)" % detail)
            for j,dp in enumerate(dp_ids):
                print("HTSInsert gmsh: dp[%d]" % j)
                if isinstance(dp, list):
                    for p in dp:
                        # print("HTSInsert gmsh: dp[%d] p=" % j, p )
                        # dp = [ [p0, p1], isolation ]
                        if isinstance(p, list):
                            # print("HTSInsert gmsh: dp[%d] len(p)=" % j, len(p), type(p[0]), "dp[-1]=", dp[-1] )
                            if len(p) == 2 and isinstance(p[0], int):
                                # detail == pancake 
                                # print("HTSInsert gmsh: dp[%d] len(p)=" % j, len(p), "p=", p, "i_ids=", len(i_ids) )
                                
                                if j >= 1:
                                    ov, ovv = gmsh.model.occ.fragment([(2, p[0])], [(2, i_ids[j-1])])
                                if j < n_dp-1:
                                    ov, ovv = gmsh.model.occ.fragment([(2, p[1])], [(2, i_ids[j])])
                                ov, ovv = gmsh.model.occ.fragment([(2, dp[-1])], [(2, p[0]), (2, p[1])] )
                                
                            else:
                                # detail == tape
                                # p = [ mandrin, [[SC, duromag], [SC, duromag], ...] ]
                                # print("HTSInsert gmsh: dp[%d] len(p)=" % j, len(p), "p=", p)
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
                    # detail == dblepancake 
                    if j >= 1:
                        ov, ovv = gmsh.model.occ.fragment([(2, dp)], [(2, i_ids[j-1])])
                    if j < n_dp-1:
                        ov, ovv = gmsh.model.occ.fragment([(2, dp)], [(2, i_ids[j])])

            # Now create air
            if Air:
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
                    print("HTSInsert with Air: dp[%d]" % j, "detail=%s" % detail, dp) 
                    if isinstance(dp, list):
                        # detail == pancake|tape
                        # print(_id, flatten(dp))
                        ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, l) for l in flatten(dp)])               
                    else:
                        # detail == dblepancake 
                        ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, dp)])
                        # ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, i) for i in i_ids])
                
                # print("dp_ids:", dp_ids)
                # print("i_ids:", i_ids)
                return ([dp_ids, i_ids], (_id, dr_air, z0_air, dz_air))

            return ([dp_ids, i_ids], None)

    def gmsh_bcs(self, detail: str, ids: tuple, debug=False):
        """
        create bcs groups for gmsh

        inputs:
        

        returns
        """

        (gmsh_ids, Air_data) = ids

        print("Set Physical Volumes")
        if isinstance(gmsh_ids, list):
            dp_ids = gmsh_ids[0]
            i_ids = gmsh_ids[1]
            for i,isol in enumerate(i_ids):
                ps = gmsh.model.addPhysicalGroup(2, [isol])
                gmsh.model.setPhysicalName(2, ps, "i_dp%d" % i)
            for i,dp in enumerate(dp_ids):
                print("dp[%d]" % i)
                if detail == "dblepancake":
                    ps = gmsh.model.addPhysicalGroup(2, [dp])
                    gmsh.model.setPhysicalName(2, ps, "dp%d" % i)
                elif detail == "pancake":
                    # print("dp:", dp)
                    ps = gmsh.model.addPhysicalGroup(2, [dp[0][0]])
                    gmsh.model.setPhysicalName(2, ps, "p%d_dp%d" % (0,i))
                    ps = gmsh.model.addPhysicalGroup(2, [dp[0][1]])
                    gmsh.model.setPhysicalName(2, ps, "p%d_dp%d" % (1,i))
                    ps = gmsh.model.addPhysicalGroup(2, [dp[1]])
                    gmsh.model.setPhysicalName(2, ps, "i_p%d" % i)
                elif detail == "tape":
                    # print("HTSInsert/gsmh_bcs (tape):", dp)
                    ps = gmsh.model.addPhysicalGroup(2, [dp[1]])
                    gmsh.model.setPhysicalName(2, ps, "i_p%d" % i)
                    for t in dp[0][0]:
                        # print("p0:", t)
                        if isinstance(t, list):
                            for l,t_id in enumerate(t):
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[0]])
                                gmsh.model.setPhysicalName(2, ps, "sc%d_p%d_dp%d" % (l,0,i))
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[1]])
                                gmsh.model.setPhysicalName(2, ps, "du%d_p%d_dp%d" % (l,0,i))
                        else:
                            ps = gmsh.model.addPhysicalGroup(2, [t])
                            gmsh.model.setPhysicalName(2, ps, "mandrin_p%d_dp%d" % (0,i))
                            print("HTSInsert/gmsh_bcs: mandrin %d: %d" % (t, ps))
                    for t in dp[0][1]:
                        # print("p1:", t)
                        if isinstance(t, list):
                            for l,t_id in enumerate(t):
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[0]])
                                gmsh.model.setPhysicalName(2, ps, "sc%d_p%d_dp%d" % (l,1,i))
                                ps = gmsh.model.addPhysicalGroup(2, [t_id[1]])
                                gmsh.model.setPhysicalName(2, ps, "du%d_p%d_dp%d" % (l,1,i))
                        else:
                            ps = gmsh.model.addPhysicalGroup(2, [t])
                            gmsh.model.setPhysicalName(2, ps, "mandrin_p%d_dp%d" % (1,i))
                            print("HTSInsert/gmsh_bcs: mandrin %d: %d" % (t, ps))
        else:   
            ps = gmsh.model.addPhysicalGroup(2, [gmsh_ids])
            gmsh.model.setPhysicalName(2, ps, "Supra")

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
        gmsh.model.setPhysicalName(1, ps, "Bottom")

        ov = gmsh.model.getEntitiesInBoundingBox(self.getR0()* (1-eps), (self.z0+self.getH()/2.)* (1-eps), 0,
                                                 self.getR1()* (1+eps), (self.z0+self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Top:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "Top")
        
        ov = gmsh.model.getEntitiesInBoundingBox(self.getR0()* (1-eps), (self.z0-self.getH()/2.)* (1-eps), 0,
                                                 self.getR0()* (1+eps), (self.z0+self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Rint:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "Rint")

        ov = gmsh.model.getEntitiesInBoundingBox(self.getR1()* (1-eps), (self.z0-self.getH()/2.)* (1-eps), 0,
                                                 self.getR1()* (1+eps), (self.z0+self.getH()/2.)* (1+eps), 0, 1)
        print("BoundingBox Rext:", ov, type(ov))
        ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
        gmsh.model.setPhysicalName(1, ps, "Rext")

        # TODO: Air
        if Air_data:
            (Air_id, dr_air, z0_air, dz_air) = Air_data

            ps = gmsh.model.addPhysicalGroup(2, [Air_id])
            gmsh.model.setPhysicalName(2, ps, "Air")

            # TODO: Axis, Inf
            gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)
            
            eps = 1.e-6
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, +eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Axis")
            
            ov = gmsh.model.getEntitiesInBoundingBox(-eps, z0_air-eps, 0, dr_air+eps, z0_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(dr_air-eps, z0_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ov += gmsh.model.getEntitiesInBoundingBox(-eps, z0_air+dz_air-eps, 0, dr_air+eps, z0_air+dz_air+eps, 0, 1)
            print("ov:", len(ov))
            
            ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
            gmsh.model.setPhysicalName(1, ps, "Inf")            
        
        print("TODO: set characteristic lengths")
        """
        lcar = (nougat.getR1() - nougat.R(0) ) / 10.
        lcar_dp = nougat.dblepancakes[0].getW() / 10.
        lcar_p = nougat.dblepancakes[0].getPancake().getW() / 10.
        lcar_tape = nougat.dblepancakes[0].getPancake().getW()/3.

        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar)
        # Override this constraint on the points of the tapes:

        gmsh.model.mesh.setSize(gmsh.model.getBoundary(tapes, False, False, True), lcar_tape)
        """
        pass
    
    # TODO move the template in a well defined directory (defined in config file for magnetgeo)
    def template_gmsh(self, name: str, detail: str) -> None:
        """
        generate a geo gmsh file

        option = dblepancake|pancake|tape control the precision of the model
        """

        details= {
            "tape" : 0,
            "pancake" : 1,
            "dblepancake" : 2,
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
        for i, dp in enumerate(self.dblepancakes):
            r_dp = self.isolations[i].getR0()
            r_ = dp.getIsolation().getR0()
            rmax = max(rmax, dp.getPancake().getR0(), r_dp, r_)
        if rmax > self.getR0():
            print("ATTENTION rmax=%g > r0=%g" % (rmax, self.getRO()))
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
        for i, dp in enumerate(self.dblepancakes):
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
            'e_dp':str(self.getWDblePancake()).replace('[','{').replace(']','}'),
            'h_dp':str(self.getHDblePancake()).replace('[','{').replace(']','}'),
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

