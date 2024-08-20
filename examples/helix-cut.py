import yaml
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Helix import Helix

import json
import argparse

r = [38.6 / 2.0, 48.4 / 2.0]
z = []
cutwidth = 0.2
odd = True
dble = True
axi = ModelAxi()
m3d = Model3D(cad="test")
shape = Shape("", "")
helix = Helix("Helix", r, z, cutwidth, odd, dble, axi, m3d, shape)
# print object attribute
print("Helix attributes:", list(vars(helix).keys()), f'type={type(vars(helix))}')
print("Helix attributes:", [type(item) for item in vars(helix).items()], f'type={type(vars(helix))}')
# exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('jsonfiles', nargs='+')
args = parser.parse_args()

print(f"Arguments: {args}")

for file in args.jsonfiles:
    print(file, flush=True)
    ofile = file.replace('.json','')
    jsondata = helix.from_json(file)
    print(f'jsondata: {jsondata}')
    
    print('compact modelaxi: ')
    (turns, pitch) = jsondata.modelaxi.compact(1.e-6)
    jsondata.modelaxi.turns = turns
    jsondata.modelaxi.pitch = pitch

    with open(f"{ofile}.yaml", "w") as ostream:
        yaml.dump(jsondata, stream=ostream)

        jsondata.generate_cut('SALOME')
        jsondata.generate_cut('LNCMI')
#print(jsondata)
