"""Console script for python_magnetgeo."""
import argparse
import sys
import os
import yaml

from . import Insert
from . import SupraStructure

def main():
    """Console script for python_magnetgeo."""
    parser = argparse.ArgumentParser()
    
    parser.add_argument("filename", help="name of the model to be loaded", type=str, nargs='?' )
    parser.add_argument("--tojson", help="convert to json", action='store_true')
    
    parser.add_argument("--wd", help="set a working directory", type=str, default="data")
    parser.add_argument("--air", help="activate air generation", action="store_true")
    parser.add_argument("--gmsh", help="save to gmsh geofile", action="store_true")
    parser.add_argument("--gmsh_api", help="use gmsh api to create geofile", action="store_true")
    parser.add_argument("--mesh", help="create gmsh mesh ", action="store_true")
    parser.add_argument("--detail", help="select representation mode of HTS", choices=['None', 'dblepancake', 'pancake', 'tape'], default='None')
    parser.add_argument("--show", help="display gmsh geofile when api is on", action="store_true")
    
    args = parser.parse_args()

    print("Arguments: " + str(args))
    
    cwd = os.getcwd()
    if args.wd:
        os.chdir(args.wd)

    # TODO extract extension
    (name, ext) = args.filename.split(".")
    print(name, ext)

    site = None
    if ext == "yaml":
        with open(args.filename, 'r') as f:
            site = yaml.load(f, Loader=yaml.FullLoader)
            print("site=",site)

    elif ext == "json":
        with open(args.filename, 'r') as f:
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

    if args.gmsh:
        if isinstance(site, Insert):
            site.Create_AxiGeo(args.air)
        if isinstance(site, SupraStructure.HTSinsert):
            site.template_gmsh(name, args.detail)
    
    if args.gmsh_api:
        import gmsh
        gmsh.initialize()
        gmsh.model.add(name)
        gmsh.logger.start()

        if not isinstance(site, SupraStructure.HTSinsert):
            ids = site.gmsh(args.air)
        else:
            ids = site.gmsh(args.detail, args.air)
        gmsh.model.occ.synchronize()

        # TODO create Physical here
        if not isinstance(site, SupraStructure.HTSinsert):
            site.gmsh_bcs(ids)
        else:
            site.gmsh_bcs(args.detail, ids)
        # TODO set mesh characteristics here
        if args.mesh:
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
