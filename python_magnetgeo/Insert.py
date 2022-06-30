#!/usr/bin/env python3
# encoding: UTF-8

"""defines Insert structure"""

import datetime
import json
import yaml
from . import deserialize

class Insert(yaml.YAMLObject):
    """
    name :
    Helices :
    Rings :
    CurrentLeads :

    HAngles :
    RAngles :

    innerbore:
    outerbore:
    """

    yaml_tag = 'Insert'

    def __init__(self, name, Helices=[], Rings=[], CurrentLeads=[], HAngles=[], RAngles=[], innerbore=None, outerbore=None):
        """constructor"""
        self.name = name
        self.Helices = Helices
        self.HAngles = HAngles
        for Angle in self.HAngles:
            print ("Angle: ", Angle)
        self.Rings = Rings
        self.RAngles = RAngles
        self.CurrentLeads = CurrentLeads
        self.innerBore = innerbore
        self.outerBore = outerbore

    def __repr__(self):
        """representation"""
        return "%s(name=%r, Helices=%r, Rings=%r, CurrentLeads=%r, HAngles=%r, RAngles=%r, innerbore=%r, outerbore=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.Helices,
                self.Rings,
                self.CurrentLeads,
                self.HAngles,
                self.RAngles,
                self.innerbore,
                self.outerbore)

    def dump(self):
        """dump to a yaml file name.yaml"""
        try:
            ostream = open(self.name + '.yaml', 'w')
            yaml.dump(self, stream=ostream)
        except:
            print ("Failed to Insert dump")

    def load(self):
        """load from a yaml file"""
        data = None
        try:
            istream = open(self.name + '.yaml', 'r')
            data = yaml.load(stream=istream)
        except:
            raise Exception("Failed to load Insert data %s" % (self.name+".yaml"))

        self.name = data.name
        self.Helices = data.Helices
        self.HAngles = data.HAngles
        self.RAngles = data.RAngles
        self.Rings = data.Rings
        self.CurrentLeads = data.CurrentLeads

        self.innerbore = data.innerbore
        self.outerbore = data.outerbore

    def to_json(self):
        """convert from yaml to json"""
        return json.dumps(self, default=deserialize.serialize_instance, \
            sort_keys=True, indent=4)

    def from_json(self, string):
        """get from json"""
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """write to a json file"""
        ostream = open(self.name + '.json', 'w')
        jsondata = self.to_json()
        ostream.write(str(jsondata))
        ostream.close()

    def read_from_json(self):
        """read from a json file"""
        istream = open(self.name + '.json', 'r')
        jsondata = self.from_json(istream.read())
        print (type(jsondata))
        istream.close()

    ###################################################################
    #
    #
    ###################################################################

    def boundingBox(self):
        """
        return Bounding as r[], z[]
        
        so far exclude Leads
        """

        rb = [0,0]
        zb = [0,0]
        
        for i, name in enumerate(self.Helices):
            Helix = None
            with open(name+".yaml", 'r') as f:
                Helix = yaml.load(f, Loader=yaml.FullLoader)

            if i == 0:
                rb = Helix.r
                zb = Helix.z
                
            rb[0] = min(rb[0], Helix.r[0])
            zb[0] = min(zb[0], Helix.z[0])
            rb[1] = max(rb[1], Helix.r[1])
            zb[1] = max(zb[1], Helix.z[1])

        ring_dz_max = 0
        for i, name in enumerate(self.Rings):
            Ring = None
            with open(name+".yaml", 'r') as f:
                Ring = yaml.load(f, Loader = yaml.FullLoader)

            ring_dz_max = abs(Ring.z[-1]-Ring.z[0])

        zb[0] -= ring_dz_max
        zb[1] += ring_dz_max
        
        return (rb, zb)

    def intersect(self, r, z):
        """
        Check if intersection with rectangle defined by r,z is empty or not
        
        return False if empty, True otherwise
        """

        (r_i, z_i) = self.boundingbox()

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(r_i[0] - r[0]) < abs(r_i[1]-r_i[0] + r[0] + r[1]) /2.
        isZ = abs(z_i[0] - z[0]) < abs(z_i[1]-z_i[0] + z[0] + z[1]) /2.
        if isR and isZ:
            collide = True
        return collide

    def gmsh(self, AirData=None, debug=False):
        """
        create gmsh geometry
        """
        import gmsh

        # loop over Helices
        z0 = []
        z1 = []
        z = []
        r = []
        H_ids = []
        for i, name in enumerate(self.Helices):
            Helix = None
            with open(name+".yaml", 'r') as f:
                Helix = yaml.load(f, Loader=yaml.FullLoader)

            H_ids.append(Helix.gmsh())
            if i%2 == 0:
                z.append(Helix.z[1])
            else:
                z.append(Helix.z[0])

            r.append(Helix.r[1])
            z0.append(Helix.z[0])
            

        # loop over Rings
        R_ids = []
        for i, name in enumerate(self.Rings):
            Ring = None
            with open(name+".yaml", 'r') as f:
                Ring = yaml.load(f, Loader = yaml.FullLoader)

            x = 0
            y = z[i]
            z1.append(y+(Ring.z[-1]-Ring.z[0]))
            
            if i%2 != 0:
                y -= (Ring.z[-1]-Ring.z[0])
                z1.append(y)

            R_id = Ring.gmsh(x, y)
            R_ids.append(R_id)
            # fragment
            if i%2 != 0:
                ov, ovv = gmsh.model.occ.fragment([(2, R_id)], [(2, H_ids[i][0]), (2, H_ids[i+1][0])] )    
            else:
                ov, ovv = gmsh.model.occ.fragment([(2, R_id)], [(2, H_ids[i][-1]), (2, H_ids[i+1][-1])] )

            if debug:
                print("Insert/Ring[%d]:" % i, "R_id=%d" % R_id, " fragment produced volumes:", len(ov), len(ovv))
                for e in ov:
                    print(e)
        
        # Now create air
        if AirData:
            r0_air = 0
            dr_air = max(r) * 2
            z0_air = min(z0) * 1.2
            dz_air = max(z1) * 1.2 - z0_air
            _id = gmsh.model.occ.addRectangle(r0_air, z0_air, 0, dr_air, dz_air)
        
            flat_list = []
            for sublist in H_ids:
                for item in sublist:
                    flat_list.append(item)
            flat_list += R_ids
            print("flat_list:", flat_list)
            ov, ovv = gmsh.model.occ.fragment([(2, _id)], [(2, i) for i in flat_list] )
            return (H_ids, R_ids, (_id, dr_air, z0_air, dz_air))

        # TODO return ids
        return (H_ids, R_ids, None)

    def gmsh_bcs(self, ids: tuple, debug: bool =False):
        """
        retreive ids for bcs in gmsh geometry
        """
        import gmsh

        (H_ids, R_ids, Air_data) = ids

        eps =1.e-3
        defs = {}
        
        # loop over Helices
        z = []
        H_Bc_ids = []
        NHelices = len(self.Helices)
        for i, name in enumerate(self.Helices):
            Helix = None
            with open(name+".yaml", 'r') as f:
                Helix = yaml.load(f, Loader=yaml.FullLoader)

            hname = "H%d" % (i+1)
            (r0_ids, r1_ids, hdefs) = Helix.gmsh_bcs(hname, H_ids[i], debug)
            if i%2 == 0:
                z.append(Helix.z[1])
            else:
                z.append(Helix.z[0])
            H_Bc_ids.append((r0_ids, r1_ids))
            for key in hdefs:
                defs[key] = hdefs[key]
            
            if i == 0:
                ov = gmsh.model.getEntitiesInBoundingBox(Helix.r[0]-eps, Helix.z[0]-eps, 0, Helix.r[1]+eps, Helix.z[0]+eps, 0, 1)
                print("ov:", len(ov))
                ps = gmsh.model.addPhysicalGroup(1, [tag for (dim,tag) in ov])
                gmsh.model.setPhysicalName(1, ps, "H1_HP")
                defs["H1_HP"] = ps

        # loop over Rings
        R_Bc_ids = []
        NRings = len(self.Rings)
        for i, name in enumerate(self.Rings):
            Ring = None
            with open(name+".yaml", 'r') as f:
                Ring = yaml.load(f, Loader = yaml.FullLoader)

            y = z[i]
            if i%2 != 0:
                y -= (Ring.z[-1]-Ring.z[0])
            
            rname = "R%d" % (i+1)
            (r0_ids, r1_ids, slit_ids) = Ring.gmsh_bcs(rname, (i%2 != 0), y, R_ids[i], debug)
            R_Bc_ids.append((r0_ids, r1_ids, slit_ids))
        print("R_bcs %d " % len(R_Bc_ids), ":" , R_Bc_ids)

        # TODO group bcs by Channels
        num = 0
        NChannels = NHelices+1
        for i in range(NChannels):
            print("Channel%d" % i)
            Channel_id = []
            if i == 0:
                # names.append("R%d_R0n" % (i+1)) # check Ring nummerotation
                Channel_id += R_Bc_ids[i][0]
            if i >= 1:
                # names.append("H%d_rExt" % (i))
                Channel_id += H_Bc_ids[i-1][1]
            if i >= 2:
                # names.append("R%d_R1n" % (i-1))
                Channel_id += R_Bc_ids[i-2][1]
            if i < NChannels:
                # names.append("H%d_rInt" % (i+1))
                if i < NHelices:
                    Channel_id += H_Bc_ids[i][0]
                if i != 0 and i+1 < NChannels:
                    # names.append("R%d_CoolingSlits" % (i))
                    print("R_Bc_ids[%d]" % i, R_Bc_ids[i-1])
                    Channel_id += R_Bc_ids[i-1][2]
                    #names.append("R%d_R0n" % (i+1))
                    if i < NRings:
                        Channel_id += R_Bc_ids[i][0]
            
            ps = gmsh.model.addPhysicalGroup(1, Channel_id)
            gmsh.model.setPhysicalName(1, ps, "Channel%d" % i)
            defs["Channel%d" % i] = ps
        
        # TODO: Air
        if Air_data:
            (Air_id, dr_air, z0_air, dz_air) = Air_data

            ps = gmsh.model.addPhysicalGroup(2, [Air_id])
            gmsh.model.setPhysicalName(2, ps, "Air")
            defs["ZAxis" % self.name] = ps

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
            defs["Infty" % self.name] = ps        

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
    

    def Create_AxiGeo(self, AirData):
        """
        create Axisymetrical Geo Model for gmsh

        return
        H_ids, R_ids, BC_ids, Air_ids, BC_Air_ids
        """
        import getpass
        UserName = getpass.getuser()

        geofilename = self.name + "_axi.geo"
        geofile = open(geofilename, "w")

        # Preambule
        geofile.write("//%s\n" % self.name)
        geofile.write("// AxiSymetrical Geometry Model\n")
        geofile.write("//%s\n" % UserName)
        geofile.write("//%s\n" % (datetime.datetime.now().strftime("%y-%m-%d %Hh%M")))
        geofile.write("\n")

        # Mesh Preambule
        geofile.write("// Mesh Preambule\n")
        geofile.write("Mesh.Algorithm=3;\n")
        geofile.write("Mesh.RecombinationAlgorithm=0; // Deactivate Blossom support\n")
        geofile.write("Mesh.RemeshAlgorithm=1; //(0=no split, 1=automatic, 2=automatic only with metis)\n")
        geofile.write("Mesh.RemeshParametrization=0; //\n\n")

        # Define Parameters
        geofile.write("//Geometric Parameters\n")
        onelab_r0 = "DefineConstant[ r0_H%d = {%g, Name \"Geom/H%d/Rint\"} ];\n" # should add a min and a max
        onelab_r1 = "DefineConstant[ r1_H%d = {%g, Name \"Geom/H%d/Rext\"} ];\n"
        onelab_z0 = "DefineConstant[ z0_H%d = {%g, Name \"Geom/H%d/Zinf\"} ];\n" #  should add a min and a max
        onelab_z1 = "DefineConstant[ z1_H%d = {%g, Name \"Geom/H%d/Zsup\"} ];\n"
        onelab_lc = "DefineConstant[ lc_H%d = {%g, Name \"Geom/H%d/lc\"} ];\n"
        onelab_z_R = "DefineConstant[ dz_R%d = {%g, Name \"Geom/R%d/dz\"} ];\n"
        onelab_lc_R = "DefineConstant[ lc_R%d = {%g, Name \"Geom/R%d/lc\"} ];\n"

        # Define Geometry
        onelab_point = "Point(%d)= {%s,%g, 0.0, lc_H%d};\n"
        onelab_pointx = "Point(%d)= {%s,%s, 0.0, lc_H%d};\n"
        onelab_point_gen = "Point(%d)= {%s,%s, 0.0, %s};\n"
        onelab_line = "Line(%d)= {%d, %d};\n"
        onelab_circle = "Circle(%d)= {%d, %d, %d};\n"
        onelab_lineloop = "Line Loop(%d)= {%d, %d, %d, %d};\n"
        onelab_lineloop_R = "Line Loop(%d)= {%d, %d, %d, %d, %d, %d, %d, %d};\n"
        onelab_planesurf = "Plane Surface(%d)= {%d};\n"
        onelab_phys_surf = "Physical Surface(%d) = {%d};\n"

        H_ids = [] # gsmh ids for Helix
        Rint_ids = []
        Rext_ids = []
        BP_ids = []
        HP_ids = []
        dH_ids = []

        point = 1
        line = 1
        lineloop = 1
        planesurf = 1

        for i, name in enumerate(self.Helices):
            H = []
            Rint = []
            Rext = []
            BP = []
            HP = []
            dH = []

            Helix = None
            with open(name+".yaml", 'r') as f:
                Helix = yaml.load(f)
            geofile.write("// H%d : %s\n" % (i+1, Helix.name))
            geofile.write(onelab_r0 % (i+1, Helix.r[0], i+1))
            geofile.write(onelab_r1 % (i+1, Helix.r[1], i+1))
            geofile.write(onelab_z0 % (i+1, Helix.z[0], i+1))
            geofile.write(onelab_z1 % (i+1, Helix.z[1], i+1))
            geofile.write(onelab_lc % (i+1, (Helix.r[1]-Helix.r[0])/5., i+1))

            axi = Helix.axi # h, turns, pitch

            geofile.write(onelab_pointx % (point, "r0_H%d"%(i+1), "z0_H%d"%(i+1), i+1))
            geofile.write(onelab_pointx % (point+1, "r1_H%d"%(i+1), "z0_H%d"%(i+1), i+1))
            geofile.write(onelab_point % (point+2, "r1_H%d"%(i+1), -axi.h, i+1))
            geofile.write(onelab_point % (point+3, "r0_H%d"%(i+1), -axi.h, i+1))

            geofile.write(onelab_line % (line, point, point+1))
            geofile.write(onelab_line % (line+1, point+1, point+2))
            geofile.write(onelab_line % (line+2, point+2, point+3))
            geofile.write(onelab_line % (line+3, point+3, point))
            BP_ids.append(line)
            Rint.append(line+3)
            Rext.append(line+1)
            dH.append([line+3, line, line+1])

            geofile.write(onelab_lineloop % (lineloop, line, line+1, line+2, line+3))
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            H.append(planesurf)
            dH.append(lineloop)

            point += 4
            line += 4
            lineloop += 1
            planesurf += 1

            z = Helix.z[0]
            dz = 2* axi.h / float(len(axi.pitch))
            z = -axi.h
            for n, p in enumerate(axi.pitch):
                geofile.write(onelab_point % (point, "r0_H%d"%(i+1), z, i+1))
                geofile.write(onelab_point % (point+1, "r1_H%d"%(i+1), z, i+1))
                geofile.write(onelab_point % (point+2, "r1_H%d"%(i+1), z+dz, i+1))
                geofile.write(onelab_point % (point+3, "r0_H%d"%(i+1), z+dz, i+1))

                geofile.write(onelab_line % (line, point, point+1))
                geofile.write(onelab_line % (line+1, point+1, point+2))
                geofile.write(onelab_line % (line+2, point+2, point+3))
                geofile.write(onelab_line % (line+3, point+3, point))
                Rint.append(line+3)
                Rext.append(line+1)

                geofile.write(onelab_lineloop % (lineloop, line, line+1, line+2, line+3))
                geofile.write(onelab_planesurf % (planesurf, lineloop))
                geofile.write(onelab_phys_surf % (planesurf, planesurf))
                H.append(planesurf)
                dH.append(lineloop)

                point += 4
                line += 4
                lineloop += 1
                planesurf += 1

                z += dz

            geofile.write(onelab_point % (point, "r0_H%d"%(i+1), axi.h, i+1))
            geofile.write(onelab_point % (point+1, "r1_H%d"%(i+1), axi.h, i+1))
            geofile.write(onelab_pointx % (point+2, "r1_H%d"%(i+1), "z1_H%d"%(i+1), i+1))
            geofile.write(onelab_pointx % (point+3, "r0_H%d"%(i+1), "z1_H%d"%(i+1), i+1))

            geofile.write(onelab_line % (line, point, point+1))
            geofile.write(onelab_line % (line+1, point+1, point+2))
            geofile.write(onelab_line % (line+2, point+2, point+3))
            geofile.write(onelab_line % (line+3, point+3, point))

            geofile.write(onelab_lineloop % (lineloop, line, line+1, line+2, line+3))
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            H.append(planesurf)
            Rint.append(line+3)
            Rext.append(line+1)

            # dH.append(Rext)
            # dH.append([line+1,line+2, line+3])
            # for id in reversed(Rint):
            #     dH.append([id])
            dH.append(lineloop)

            H_ids.append(H)
            HP_ids.append(line+2)
            Rint_ids.append(Rint)
            Rext_ids.append(Rext)

            dH_ids.append(dH) #### append(reduce(operator.add, dH)) #other way to flatten dH : list(itertools.chain(*dH))
            geofile.write("\n")

            point += 4
            line += 4
            lineloop += 1
            planesurf += 1

        # Add Rings
        Ring_ids = []
        HP_Ring_ids = []
        BP_Ring_ids = []
        dR_ids = []

        H0 = 0
        H1 = 1
        for i, name in enumerate(self.Rings):
            R = []
            Rint = []
            Rext = []
            BP = []
            HP = []

            Ring = None
            with open(name+".yaml", 'r') as f:
                Ring = yaml.load(f)
            geofile.write("// R%d [%d, H%d] : %s\n"%(i+1, H0+1, H1+1, Ring.name))
            geofile.write(onelab_z_R%(i+1, (Ring.z[1]-Ring.z[0]), i+1))
            geofile.write(onelab_lc_R%(i+1, (Ring.r[3]-Ring.r[0])/5., i+1))

            if Ring.BPside:
                geofile.write(onelab_pointx % (point, "r0_H%d"%(H0+1), "z1_H%d"%(H0+1), i+1))
                geofile.write(onelab_pointx % (point+1, "r1_H%d"%(H0+1), "z1_H%d"%(H0+1), i+1))
                geofile.write(onelab_pointx % (point+2, "r0_H%d"%(H1+1), "z1_H%d"%(H1+1), i+1))
                geofile.write(onelab_pointx % (point+3, "r1_H%d"%(H1+1), "z1_H%d"%(H1+1), i+1))

                geofile.write(onelab_pointx % (point+4, "r1_H%d"%(H1+1), "z1_H%d+dz_R%d"%(H1+1, i+1), i+1))
                geofile.write(onelab_pointx % (point+5, "r0_H%d"%(H1+1), "z1_H%d+dz_R%d"%(H1+1, i+1), i+1))
                geofile.write(onelab_pointx % (point+6, "r1_H%d"%(H0+1), "z1_H%d+dz_R%d"%(H0+1, i+1), i+1))
                geofile.write(onelab_pointx % (point+7, "r0_H%d"%(H0+1), "z1_H%d+dz_R%d"%(H0+1, i+1), i+1))
            else:
                geofile.write(onelab_pointx % (point, "r0_H%d"%(H0+1), "z0_H%d-dz_R%d"%(H0+1, i+1), i+1))
                geofile.write(onelab_pointx % (point+1, "r1_H%d"%(H0+1), "z0_H%d-dz_R%d"%(H0+1, i+1), i+1))
                geofile.write(onelab_pointx % (point+2, "r0_H%d"%(H1+1), "z0_H%d-dz_R%d"%(H1+1, i+1), i+1))
                geofile.write(onelab_pointx % (point+3, "r1_H%d"%(H1+1), "z0_H%d-dz_R%d"%(H1+1, i+1), i+1))

                geofile.write(onelab_pointx % (point+4, "r1_H%d"%(H1+1), "z0_H%d"%(H1+1), i+1))
                geofile.write(onelab_pointx % (point+5, "r0_H%d"%(H1+1), "z0_H%d"%(H1+1), i+1))
                geofile.write(onelab_pointx % (point+6, "r1_H%d"%(H0+1), "z0_H%d"%(H0+1), i+1))
                geofile.write(onelab_pointx % (point+7, "r0_H%d"%(H0+1), "z0_H%d"%(H0+1), i+1))

            geofile.write(onelab_line % (line, point, point+1))
            geofile.write(onelab_line % (line+1, point+1, point+2))
            geofile.write(onelab_line % (line+2, point+2, point+3))
            geofile.write(onelab_line % (line+3, point+3, point+4))
            geofile.write(onelab_line % (line+4, point+4, point+5))
            geofile.write(onelab_line % (line+5, point+5, point+6))
            geofile.write(onelab_line % (line+6, point+6, point+7))
            geofile.write(onelab_line % (line+7, point+7, point))

            if Ring.BPside:
                HP_Ring_ids.append([line+4, line+5, line+6])
            else:
                BP_Ring_ids.append([line+4, line+5, line+6])

            geofile.write(onelab_lineloop_R % (lineloop, line, line+1, line+2, line+3, line+4, line+5, line+6, line+7))
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            Ring_ids.append(planesurf)

            Rint_ids[H0].append(line+7)
            Rext_ids[H1].append(line+3)
            dR_ids.append(lineloop)

            H0 = H1
            H1 += 1

            point += 8
            line += 8
            lineloop += 1
            planesurf += 1

        # create physical lines
        for i, r_ids in enumerate(Rint_ids):
            geofile.write("Physical Line(\"H%dChannel0\") = {" % (i+1))
            for id in r_ids:
                geofile.write("%d"%id)
                if id != r_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        for i, r_ids in enumerate(Rext_ids):
            geofile.write("Physical Line(\"H%dChannel1\") = {" % (i+1))
            for id in r_ids:
                geofile.write("%d"%id)
                if id != r_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        geofile.write("Physical Line(\"HP_H%d\") = " % (0))
        geofile.write("{%d};\n"%HP_ids[0])

        if len(self.Helices)%2 == 0:
            geofile.write("Physical Line(\"HP_H%d\") = " % (len(self.Helices)))
            geofile.write("{%d};\n" % HP_ids[-1])
        else:
            geofile.write("Physical Line(\"BP_H%d\") = " % (len(self.Helices)))
            geofile.write("{%d};\n" % BP_ids[-1])

        for i, _ids in enumerate(HP_Ring_ids):
            geofile.write("Physical Line(\"HP_R%d\") =  {" % (i+1))
            for id in _ids:
                geofile.write("%d" % id)
                if id != _ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        for i, _ids in enumerate(BP_Ring_ids):
            geofile.write("Physical Line(\"BP_R%d\") =  {" % (i+1))
            for id in _ids:
                geofile.write("%d" % id)
                if id != _ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        # BC_ids should contains "H%dChannel%d", "HP_R%d" and "BP_R%d"
        BC_ids = []

        #Air
        Air_ids = []
        BC_Air_ids = []
        if AirData:
            Axis_ids = []
            Infty_ids = []

            geofile.write("// Define Air\n")
            onelab_r_air = "DefineConstant[ r_Air = {%g, Name \"Geom/Air/factor_R\"} ];\n"
            onelab_z_air = "DefineConstant[ z_Air = {%g, Name \"Geom/Air/factor_Z\"} ];\n" #  should add a min and a max
            onelab_lc_air = "DefineConstant[ lc_Air = {%g, Name \"Geom/Air/lc\"} ];\n"
            geofile.write(onelab_r_air % (1.2))
            geofile.write(onelab_z_air % (1.2))
            geofile.write(onelab_lc_air % (2))

            H0 = 0
            Hn = len(self.Helices)-1

            geofile.write(onelab_pointx % (point, "0", "z_Air * z0_H%d"%(H0+1), i+1))
            geofile.write(onelab_pointx % (point+1, "r_Air * r1_H%d"%(Hn+1), "z_Air * z0_H%d"%(H0+1), i+1))
            geofile.write(onelab_pointx % (point+2, "r_Air * r1_H%d"%(Hn+1), "z_Air * z1_H%d"%(Hn+1), i+1))
            geofile.write(onelab_pointx % (point+3, "0", "z_Air * z1_H%d"%(Hn+1), i+1))

            geofile.write(onelab_line % (line, point, point+1))
            geofile.write(onelab_line % (line+1, point+1, point+2))
            geofile.write(onelab_line % (line+2, point+2, point+3))
            geofile.write(onelab_line % (line+3, point+3, point))
            Axis_ids.append(line+3)

            geofile.write(onelab_lineloop % (lineloop, line, line+1, line+2, line+3))
            geofile.write("Plane Surface(%d)= {%d, " % (planesurf, lineloop))
            for _ids in H_ids:
                for _id in _ids:
                    geofile.write("%d," % (-_id))
            for _id in dR_ids:
                geofile.write("%d" % (-_id))
                if _id != dR_ids[-1]:
                    geofile.write(",")
            Air_ids.append(planesurf)

            geofile.write("};\n")
            #geofile.write(onelab_planesurf%(planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))

            dAir = lineloop
            axis_HP = point
            axis_BP = point+3
            Air_line = line

            point += 4
            line += 4
            lineloop += 1
            planesurf += 1

            # Define Infty
            geofile.write("// Define Infty\n")
            onelab_rint_infty = "DefineConstant[ Val_Rint = {%g, Name \"Geom/Infty/Val_Rint\"} ];\n"
            onelab_rext_infty = "DefineConstant[ Val_Rext = {%g, Name \"Geom/Infty/Val_Rext\"} ];\n"
            onelab_lc_infty = "DefineConstant[ lc_infty = {%g, Name \"Geom/Infty/lc_inft\"} ];\n"
            onelab_point_infty = "Point(%d)= {%s,%s, 0.0, %s};\n"
            geofile.write(onelab_rint_infty % (4))
            geofile.write(onelab_rext_infty % (5))
            geofile.write(onelab_lc_infty % (100))

            center = point
            geofile.write(onelab_point_gen % (center, "0", "0", "lc_Air"))
            point += 1

            Hn = len(self.Helices)

            geofile.write(onelab_point_gen % (point, "0", "-Val_Rint * r1_H%d" % Hn, "lc_infty"))
            geofile.write(onelab_point_gen % (point+1, "Val_Rint * r1_H%d" % Hn, "0", "lc_infty"))
            geofile.write(onelab_point_gen % (point+2, "0", "Val_Rint * r1_H%d" % Hn, "lc_infty"))

            geofile.write(onelab_circle % (line, point, center, point+1))
            geofile.write(onelab_circle % (line+1, point+1, center, point+2))
            geofile.write(onelab_line % (line+2, point+2, axis_BP))
            geofile.write(onelab_line % (line+3, axis_HP, point))
            Axis_ids.append(line+2)
            Axis_ids.append(line+3)

            geofile.write("Line Loop(%d) = {" % lineloop)
            geofile.write("%d, " % line)
            geofile.write("%d, " % (line+1))
            geofile.write("%d, " % (line+2))
            geofile.write("%d, " % (-(Air_line+2)))
            geofile.write("%d, " % (-(Air_line+1)))
            geofile.write("%d, " % (-(Air_line)))
            geofile.write("%d};\n " % (line+3))

            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            Air_ids.append(planesurf)

            axis_HP = point
            axis_BP = point+2
            Air_line = line

            point += 3
            line += 4
            lineloop += 1
            planesurf += 1

            geofile.write(onelab_point_gen % (point, "0", "-Val_Rext * r1_H%d" % Hn, "lc_infty"))
            geofile.write(onelab_point_gen % (point+1, "Val_Rext * r1_H%d" % Hn, "0", "lc_infty"))
            geofile.write(onelab_point_gen % (point+2, "0", "Val_Rext * r1_H%d" % Hn, "lc_infty"))

            geofile.write(onelab_circle % (line, point, center, point+1))
            geofile.write(onelab_circle % (line+1, point+1, center, point+2))
            geofile.write(onelab_line % (line+2, point+2, axis_BP))
            geofile.write(onelab_line%(line+3, axis_HP, point))
            Axis_ids.append(line+2)
            Axis_ids.append(line+3)
            Infty_ids.append(line)
            Infty_ids.append(line+1)

            geofile.write("Line Loop(%d) = {" % lineloop)
            geofile.write("%d, " % line)
            geofile.write("%d, " % (line+1))
            geofile.write("%d, " % (line+2))
            geofile.write("%d, " % (-(Air_line+1)))
            geofile.write("%d, " % (-(Air_line)))
            geofile.write("%d};\n " % (line+3))
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            Air_ids.append(planesurf)

            # Add Physical Lines
            geofile.write("Physical Line(\"Axis\") =  {")
            for id in Axis_ids:
                geofile.write("%d" % id)
                if id != Axis_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

            geofile.write("Physical Line(\"Infty\") =  {")
            for id in Infty_ids:
                geofile.write("%d" % id)
                if id != Infty_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

            # BC_Airs_ids should contains "Axis" and "Infty"

        # coherence
        geofile.write("\nCoherence;\n")
        geofile.close()

        return (H_ids, Ring_ids, BC_ids, Air_ids, BC_Air_ids)

def Insert_constructor(loader, node):
    print ("Insert_constructor")
    values = loader.construct_mapping(node)
    name = values["name"]
    Helices = values["Helices"]
    HAngles = values["HAngles"]
    RAngles = values["RAngles"]
    Rings = values["Rings"]
    CurrentLeads = values["CurrentLeads"]
    innerbore = values["innerbore"]
    outerbore = values["outerbore"]
    return Insert(name, Helices, Rings, CurrentLeads, HAngles, RAngles, innerbore, outerbore)

yaml.add_constructor(u'!Insert', Insert_constructor)

