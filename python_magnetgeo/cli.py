"""Console script for python_magnetgeo."""
import argparse
import sys
import os
import yaml

from . import Insert
from . import SupraStructure

from python_magnetsetup.file_utils import MyOpen, search_paths

def main():
    """Console script for python_magnetgeo."""
    parser = argparse.ArgumentParser()
    
    parser.add_argument("filename", help="name of the model to be loaded", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    
    parser.add_argument("--env", help="load settings.env", action="store_true")
    parser.add_argument("--wd", help="set a working directory", type=str, default="")
    parser.add_argument("--air", help="activate air generation", nargs=2, type=float, metavar=('infty_Rratio', 'infty_Zratio'))
    parser.add_argument("--gmsh", help="save to gmsh geofile", action="store_true")
    parser.add_argument("--gmsh_api", help="use gmsh api to create geofile", action="store_true")
    parser.add_argument("--mesh", help="create gmsh mesh with lc charateristics (stored like bcs)", action="extend", nargs='+', type=float)
    parser.add_argument("--detail", help="select representation mode of HTS", choices=['None', 'dblepancake', 'pancake', 'tape'], default='None')
    parser.add_argument("--show", help="display gmsh geofile when api is on", action="store_true")
    
    args = parser.parse_args()

    print("Arguments: " + str(args))
    
    # load appenv
    from python_magnetsetup.config import appenv
    MyEnv = None
    if args.env:
        MyEnv = appenv()

    cwd = os.getcwd()
    if args.wd:
        os.chdir(args.wd)

    # TODO extract extension
    (name, ext) = args.filename.split(".")
    print(name, ext)

    site = None
    if ext == "yaml":
        with MyOpen(args.filename, 'r', paths=search_paths(MyEnv, "geom")) as f:
            site = yaml.load(f, Loader=yaml.FullLoader)
            print("site=",site)

    elif ext == "json":
        with MyOpen(args.filename, 'r', paths=search_paths(MyEnv, "geom")) as f:
            site = SupraStructure.HTSinsert()
            site.loadCfg(args.filename)

            print("HTS insert: ", "R0=%g m" % site.getR0(), 
                  "R1=%g m" % site.getR1(), 
                  "Z0=%g" % (site.getZ0()-site.getH()/2.),
                  "Z1=%g" % (site.getZ0()+site.getH()/2.))
    else:
        print("unsupported extension: %s" % ext)
        sys.exit(1)

    if args.tojson:
        if not isinstance(site, SupraStructure.HTSinsert):
            site.write_to_json()

    AirData = None
    if args.air:
        infty_Rratio = args.air[0] #1.5
        if infty_Rratio < 1:
            raise RuntimeError("Infty_Rratio=%g should be greater than 1"%infty_Rratio)
        infty_Zratio = args.air[1] #2.
        if infty_Zratio < 1:
            raise RuntimeError("Infty_Zratio=%g should be greater than 1"%infty_Zratio)
        AirData = (infty_Rratio, infty_Zratio)

    if args.gmsh:
        if isinstance(site, Insert):
            site.Create_AxiGeo(AirData)
        if isinstance(site, SupraStructure.HTSinsert):
            site.template_gmsh(name, args.detail)
    
    if args.gmsh_api:
        import gmsh
        gmsh.initialize()
        gmsh.model.add(name)
        gmsh.logger.start()

        if not isinstance(site, SupraStructure.HTSinsert):
            ids = site.gmsh(AirData)
        else:
            ids = site.gmsh(args.detail, args.air)
        gmsh.model.occ.synchronize()

        # TODO create Physical here
        if not isinstance(site, SupraStructure.HTSinsert):
            bcs = site.gmsh_bcs(ids)
        else:
            bcs = site.gmsh_bcs(site.name, args.detail, ids)

        # TODO set mesh characteristics here
        if args.mesh:
            print("msh:", type(args.mesh))
            site.gmsh_msh(bcs, args.mesh[0])
            gmsh.model.mesh.generate(2)
            gmsh.write(name + ".msh")        

        log = gmsh.logger.get()
        print("Logger has recorded " + str(len(log)) + " lines")
        gmsh.logger.stop()
        # Launch the GUI to see the results:
        if args.show:
            gmsh.fltk.run()
        gmsh.finalize()

    if args.wd:
        os.chdir(cwd)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
