"""Main module."""

from .Insert import *

import math
import os

def get_main_characteristics(cad: Insert, MyEnv = None ):
    """
    return main characteristics for Insert
    NHelices
    NRings
    NChannels 
    R1
    R2
    Z1
    Z2
    Zmin, 
    Zmax, 
    Dh, 
    Sh
    """
    
    from python_magnetsetup.file_utils import MyOpen
    search_paths = [ os.getcwd() ]
    if MyEnv:
        default_paths={
            "geom" : MyEnv.yaml_repo,
            "cad" : MyEnv.cad_repo,
            "mesh" : MyEnv.mesh_repo
        }
        search_paths.append( default_paths["geom"]] )
    
    NHelices = len(cad.Helices)
    NRings = len(cad.Rings)
    NChannels = NHelices+1 # TODO check this value if insert contains HR 
    R1 = []
    R2 = []
    Z1 = []
    Z2 = []
    Nsections = []
    Nturns_h = []
    Zmin = [] 
    Zmax =  []
    Dh = []
    Sh = []
    for i,helix in enumerate(cad.Helices):
        hhelix = None
        with MyOpen(helix+".yaml", 'r', paths=search_paths) as f:
            hhelix = yaml.load(f, Loader = yaml.FullLoader)
        n_sections = len(hhelix.axi.turns)
        Nsections.append(n_sections)
        Nturns_h.append(hhelix.axi.turns)

        R1.append(hhelix.r[0])
        R2.append(hhelix.r[1])
        Z1.append(hhelix.z[0])
        Z2.append(hhelix.z[1])

    Ri = cad.innerbore
    Re = cad.outerbore
        
    zm1 = Z1[0]
    zm2 = Z2[0]
            
    for i in range(NHelices):

        Zmin.append(min(Z1[i],zm1))
        Zmax.append(min(Z2[i],zm2))

        Dh.append(2*(R1[i]-Ri))
        Sh.append(math.pi*(R1[i]-Ri)*(R1[i]+Ri))
            
        Ri = R1[i]
        zm1 = Z1[i]
        zm2 = Z2[i]

    Zmin.append(zm1)
    Zmax.append(zm2)

    Dh.append(2*(Re-Ri))
    Sh.append(math.pi*(Re-Ri)*(Re+Ri))

    return (NHelices, NRings, NChannels, Nsections, R1, R2, Z1, Z2, Zmin, Zmax, Dh, Sh)

def get_cut_characteristics(cad: Insert, MyEnv = None):
    """
    return cut characteristics for Insert
    Nturns
    NPitch
    """
    
    from python_magnetsetup.file_utils import MyOpen
    search_paths = [ os.getcwd() ]
    if MyEnv:
        default_paths={
            "geom" : MyEnv.yaml_repo,
            "cad" : MyEnv.cad_repo,
            "mesh" : MyEnv.mesh_repo
        }
        search_paths.append( default_paths["geom"]] )
    
    NHelices = len(cad.Helices)
    Nturns = []
    Pitch = [] 
    for i,helix in enumerate(cad.Helices):
        hhelix = None
        with MyOpen(helix+".yaml", 'r', paths=search_paths) as f:
            hhelix = yaml.load(f, Loader = yaml.FullLoader)
        Nturns.append(hhelix.axi.turns)
        Pitch.append(hhelix.axi.pitch)
    
    return (Nturns, Pitch)
