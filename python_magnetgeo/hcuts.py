#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Utilities for generating helical cut files for magnet manufacturing.

This module provides functions to create cut files in different formats
for CNC machining of helical conductor geometries. The cut files define
the toolpath for creating helical grooves in conductor blocks.

Functions:
    lncmi_cut: Generate cut file in LNCMI CAM format
    salome_cut: Generate cut file in SALOME format
    create_cut: Main interface for creating cut files in specified format
    
The cut files contain a sequence of (theta, z) coordinates that define
the helical toolpath, where theta is the angular position and z is the
axial position.
"""

from math import pi


def lncmi_cut(object, filename: str, append: bool = False, z0: float = 0):
    """
    Generate helical cut file in LNCMI CAM format.
    
    Creates a cut file compatible with LNCMI's computer-aided manufacturing
    system. The file includes G-code commands and toolpath coordinates for
    CNC machining of helical grooves.
    
    Args:
        object: Helix or Bitter object containing the geometry definition.
                Must have attributes:
                - modelaxi: ModelAxi object with turns and pitch lists
                - odd: bool indicating helix handedness
        filename: Output filename for the cut file
        append: If True, append to existing file; if False, create new file 
                (default: False)
        z0: Initial z-coordinate offset in millimeters (default: 0)
        
    Raises:
        FileExistsError: If file exists and append=False
        AttributeError: If object missing required attributes
        
    Example:
        >>> from python_magnetgeo import Helix, ModelAxi
        >>> modelaxi = ModelAxi("test", 50.0, [10.0, 15.0], [5.0, 5.0])
        >>> helix = Helix("H1", [10, 30], [0, 100], 2.5, True, False, 
        ...               modelaxi, None, None)
        >>> lncmi_cut(helix, "helix_lncmi.iso")
        
    Output Format:
        The file contains:
        - Header with helix direction (droite/gauche = right/left hand)
        - Origin coordinates (X, W) in mm and degrees
        - G-code setup commands
        - Sequence of move commands (N1, N2, ...) with X (axial) and 
          W (angular) coordinates
        - Footer with M-codes for machine control
        
    Notes:
        - Units: millimeters for distance, degrees for angles
        - Coordinate system: X is axial position (multiplied by 1000 for μm),
          W is angular position
        - Sign convention depends on helix handedness (odd parameter)
        - The last move uses G01 (linear interpolation) while others use G0 (rapid)
        
    See Also:
        MagnetTools/MagnetField/Stack.cc write_lncmi_paramfile L136
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

    # 'x' create file, 'a' append to file
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

        # Generate toolpath points from helix geometry
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
    Generate helical cut file in SALOME format.
    
    Creates a cut file compatible with SALOME platform for 3D CAD modeling
    and geometry definition. The file contains tabulated (theta, z) coordinates
    defining the helical curve.
    
    Args:
        object: Helix or Bitter object containing the geometry definition.
                Must have attributes:
                - modelaxi: ModelAxi object with h (half-height), turns and pitch lists
                - odd: bool indicating helix handedness (affects sign)
        filename: Output filename for the cut file
        append: If True, append to existing file; if False, create new file
                (default: False)
        z0: Initial z-coordinate offset in millimeters (default: 0, unused in
            current implementation as starting point is modelaxi.h)
            
    Raises:
        FileExistsError: If file exists and append=False
        AttributeError: If object missing required attributes
        
    Example:
        >>> from python_magnetgeo import Helix, ModelAxi
        >>> modelaxi = ModelAxi("test", 50.0, [10.0, 15.0], [5.0, 5.0])
        >>> helix = Helix("H1", [10, 30], [0, 100], 2.5, True, False,
        ...               modelaxi, None, None)
        >>> salome_cut(helix, "helix_salome.dat")
        
    Output Format:
        Tab-delimited text file with columns:
        - Column 1: theta in radians
        - Column 2: Shape_id (always 0 in current implementation)
        - Column 3: z coordinate in millimeters
        
        Header line: #theta[rad]    Shape_id[]    tZ[mm]
        
    Notes:
        - Units: radians for angles, millimeters for distances
        - Starting point: z = modelaxi.h (half-height of the helix)
        - Sign convention: depends on helix handedness
          - If odd=True: sign = -1 (left-hand helix)
          - If odd=False: sign = +1 (right-hand helix)
        - Each row represents one point along the helical curve
        - Number of points = number of turn segments + 1 (initial point)
        
    Coordinate System:
        - theta: cumulative angular rotation from starting point
        - z: axial position, decreasing from modelaxi.h
        - For each segment: theta += turns * 2π * sign, z -= turns * pitch
        
    See Also:
        MagnetTools/MagnetField/Stack.cc write_salome_paramfile L1011
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

    # 'x' create file, 'a' append to file
    flag = "x"
    if append:
        flag = "a"
    print(f'flag={flag}')
    with open(filename, flag) as f:
        # Write header
        f.write(f"#theta[rad]{tab}Shape_id[]{tab}tZ[mm]\n")
        
        # Write initial point
        f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")

        # Generate subsequent points from helix geometry
        for i, (turn, pitch) in enumerate(zip(object.modelaxi.turns, object.modelaxi.pitch)):
            theta += turn * (2 * pi) * sign
            z -= turn * pitch
            f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")


def create_cut(
    object, format: str, name: str, append: bool = False, z0: float = 0
):
    """
    Create helical cut file in the specified format.
    
    Main interface function for generating cut files. Dispatches to the
    appropriate format-specific function (lncmi_cut or salome_cut) based
    on the format parameter.
    
    Args:
        object: Helix or Bitter object containing the geometry definition.
                Must have attributes:
                - modelaxi: ModelAxi object with geometry parameters
                - odd: bool indicating helix handedness
        format: Output format specification (case-insensitive):
                - "lncmi": LNCMI CAM format (G-code)
                - "salome": SALOME platform format (tabulated data)
        name: Base name for the output file (extension added automatically)
        append: If True, append to existing file; if False, create new file
                (default: False)
        z0: Initial z-coordinate offset in millimeters (default: 0)
        
    Returns:
        None: File is written to disk
        
    Raises:
        RuntimeError: If format is not supported
        FileExistsError: If file exists and append=False
        AttributeError: If object missing required attributes
        
    Example:
        >>> from python_magnetgeo import Helix, ModelAxi, Model3D, Shape
        >>> modelaxi = ModelAxi("axi", 50.0, [10.0, 15.0], [5.0, 5.0])
        >>> model3d = Model3D("3d", "SALOME", True, False)
        >>> shape = Shape("shape", "rect", [15.0], [90.0], [1], "ABOVE")
        >>> helix = Helix("H1", [10, 30], [0, 100], 2.5, True, False,
        ...               modelaxi, model3d, shape)
        >>> 
        >>> # Create SALOME format cut file
        >>> create_cut(helix, "salome", "H1")
        >>> # Creates file: H1_cut_salome.dat
        >>> 
        >>> # Create LNCMI format cut file
        >>> create_cut(helix, "lncmi", "H1")
        >>> # Creates file: H1_lncmi.iso
        
    Output Files:
        - LNCMI format: {name}_lncmi.iso
        - SALOME format: {name}_cut_salome.dat
        
    Notes:
        The format string is case-insensitive (e.g., "SALOME", "Salome", 
        and "salome" are all valid).
        
    See Also:
        lncmi_cut: For LNCMI format details
        salome_cut: For SALOME format details
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

