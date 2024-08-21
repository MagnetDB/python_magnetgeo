"""
Template for Gmsh
"""    
from python_magnetgeo.SupraStructure in SupraStructure

# TODO move the template in a well defined directory (defined in config file for magnetgeo)
def template_gmsh(struct: SupraStructure, name: str, detail: str) -> None:
    """
    generate a geo gmsh file

    option = dblpancake|pancake|tape control the precision of the model
    """

    details = {"tape": 0, "pancake": 1, "dblpancake": 2, "None": 3}

    print("ISolations:", len(struct.isolations))
    print("=== Save to geo gmsh: NB use gmsh 4.9 or later")
    import getpass

    UserName = getpass.getuser()

    max_mandrin = max(struct.getMandrinPancake())
    min_r_ = min(struct.getR0Pancake_Isolation())
    min_r_dp = min(struct.getR0_Isolation())
    xmin = min(struct.getR0() - max_mandrin, min_r_dp, min_r_)

    rmin = min(struct.getR0() - max_mandrin, min_r_dp, min_r_)
    rmax = 0
    for i, dp in enumerate(struct.dblpancakes):
        r_dp = struct.isolations[i].getR0()
        r_ = dp.getIsolation().getR0()
        rmax = max(rmax, dp.getPancake().getR0(), r_dp, r_)
    if rmax > struct.getR0():
        print(f"ATTENTION rmax={rmax} > r0={struct.getR0()}")
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
    for i, dp in enumerate(struct.dblpancakes):
        r_dp = struct.isolations[i].getR0() + struct.isolations[i].getW()
        r_ = dp.getIsolation().getR0() + dp.getIsolation().getW()
        xmax = max(xmax, r_dp, r_)

    # Some data will be stored as list (str(...)
    data_dict = {
        "detail": details[detail],
        "z0": struct.getZ0() - struct.getH() / 2.0,
        "r0": struct.getR0(),
        "z1": struct.getZ0() + struct.getH() / 2.0,
        "r1": struct.getR1(),
        "n_dp": struct.getN(),
        "e_dp": str(struct.getWDblPancake()).replace("[", "{").replace("]", "}"),
        "h_dp": str(struct.getHDblPancake()).replace("[", "{").replace("]", "}"),
        "h_dp_isolation": str(struct.getH_Isolation())
        .replace("[", "{")
        .replace("]", "}"),
        "r_dp": str(struct.getR0_Isolation()).replace("[", "{").replace("]", "}"),
        "e_p": str(struct.getWPancake()).replace("[", "{").replace("]", "}"),
        "e_dp_isolation": str(struct.getW_Isolation())
        .replace("[", "{")
        .replace("]", "}"),
        "mandrin": str(struct.getMandrinPancake())
        .replace("[", "{")
        .replace("]", "}"),
        "h_tape": str(struct.getHtapes()).replace("[", "{").replace("]", "}"),
        "h_isolation": str(struct.getHPancake_Isolation())
        .replace("[", "{")
        .replace("]", "}"),
        "r_": str(struct.getR0Pancake_Isolation())
        .replace("[", "{")
        .replace("]", "}"),
        "e_isolation": str(struct.getWPancake_Isolation())
        .replace("[", "{")
        .replace("]", "}"),
        "n_t": str(struct.getNtapes()).replace("[", "{").replace("]", "}"),
        "e_t": str(struct.getWtapes_Isolation()).replace("[", "{").replace("]", "}"),
        "w_t": str(struct.getWtapes_SC()).replace("[", "{").replace("]", "}"),
        "emin": min(struct.getWtapes_Isolation()),
        "xmin": xmin,
        "rmin": rmin,
        "rmax": rmax,
        "xmax": xmax,
    }

    # Load template file (TODO use jinja2 instead? or chevron)
    import chevron

    geofile = chevron.render("template-hts.mustache", data_dict)

    # print("geofile:", geofile)
    geofilename = name + "_hts_axi.geo"
    with open(geofilename, "x") as f:
        f.write(geofile)

        return
