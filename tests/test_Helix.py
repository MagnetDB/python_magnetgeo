import yaml
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Helix import Helix



def test_helix():
    ofile = open("Helix.yaml", "w")
    r = [38.6 / 2.0, 48.4 / 2.0]
    z = []
    cutwidth = 0.2
    odd = True
    dble = True
    axi = ModelAxi()
    m3d = Model3D(cad="test")
    shape = Shape("", "")
    helix = Helix("Helix", r, z, cutwidth, odd, dble, axi, m3d, shape)
    yaml.dump(helix, ofile)


def test_loadhelix():
    helix = yaml.load(open("Helix.yaml", "r"), Loader=yaml.FullLoader)
    assert helix.r[0] == 19.3


def test_jsonhelix():
    helix = yaml.load(open("Helix.yaml", "r"), Loader=yaml.FullLoader)
    helix.write_to_json()

    # load from json
    jsondata = Helix.from_json('Helix.json')
    assert jsondata.name == "Helix" and jsondata.r[0] == 19.3
