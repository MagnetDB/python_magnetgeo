    # Create cut files
"""
Utils for generating cut
"""

def lncmi_cut(object, filename: str, append: bool = False, z0: float = 0):
    """
    for lncmi CAM
    see: MagnetTools/MagnetField/Stack.cc write_lncmi_paramfile L136
    """
    print(f'lncmi_cut: filename={filename}')
    from math import pi

    sign = 1
    if not object.odd:
        sign *= -1

    # force units (mm, deg)
    units = 1.e+3
    angle_units = 180 / pi

    z = z0
    theta = 0
    shape_id = 0
    tab = "\t"

    # 'x' create file, 'a' append to file, Append and Read (‘a+’)
    flag = "x"
    if append:
        flag = "a"
    with open(filename, flag) as f:
        sens = "droite"
        if sign > 0:
            sens = "gauche"
        f.write(f"%decoupe double helice {filename} {sens}\n")
        f.write("%Origin ")
        f.write(f"X {-z * units:12.4f}\t")
        f.write(f"W {-sign * theta * angle_units:12.3f}\n")

        f.write("O****(*****)\n")
        f.write("G0G90X0.0Y0.0\n")
        f.write("G0A-0.\n")
        f.write("G92\n")
        f.write("G40G50\n")
        f.write("M61\nM60\n")
        f.write("G0X-0.000\n")
        f.write("G0A0.\n")

        # TODO use compact to reduce size of cuts
        for i, (turn, pitch) in enumerate(zip(object.modelaxi.turns, object.modelaxi.pitch)):
            theta += turn * (2 * pi) * sign
            z -= turn * pitch
            f.write(f"N{i+1}")
            if i == len(object.modelaxi.turns)-1:
                f.write("G01")

            f.write("\t");
            f.write(f"X {-z * units:12.4f}\t")
            f.write(f"W {-sign * theta * angle_units:12.3f}\n")

        f.write("M50\nM29\nM30")
        f.write("%")
    
def salome_cut(object, filename: str, append: bool = False, z0: float = 0):
    """
    for salome
    see: MagnetTools/MagnetField/Stack.cc write_salome_paramfile L1011

    """
    print(f'salome_cut: filename={filename}')
    from math import pi

    sign = 1
    if object.odd:
        sign = -1

    z = object.modelaxi.h
    theta = 0
    shape_id = 0
    tab = "\t"

    # 'x' create file, 'a' append to file, Append and Read (‘a+’)
    flag = "x"
    if append:
        flag = "a"
    print(f'flag={flag}')
    with open(filename, flag) as f:
        f.write(f"#theta[rad]{tab}Shape_id[]{tab}tZ[mm]\n")
        f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")

        # TODO use compact to reduce size of cuts
        for i, (turn, pitch) in enumerate(zip(object.modelaxi.turns, object.modelaxi.pitch)):
            theta += turn * (2 * pi) * sign
            z -= turn * pitch
            f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")


def create_cut(
    object, format: str, name: str, append: bool = False, z0: float=0 
):
    """
    create cut file
    """

    dformat = {
        "lncmi": {"run": lncmi_cut, "extension": "_lncmi.iso"},
        "salome": {"run": salome_cut, "extension": "_cut_salome.dat"},
    }

    try:
        format_cut = dformat[format.lower()]
    except:
        raise RuntimeError(
            f"create_cut: format={format} unsupported\nallowed formats are: {dformat.keys()}"
        )

    write_cut = format_cut["run"]
    ext = format_cut["extension"]
    filename = f"{name}{ext}"
    write_cut(object, filename, append, z0)

