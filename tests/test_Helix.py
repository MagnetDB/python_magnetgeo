import yaml
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Chamfer import Chamfer


def test_helix():
    r = [38.6 / 2.0, 48.4 / 2.0]
    z = []
    cutwidth = 0.2
    odd = True
    dble = True
    axi = ModelAxi()
    m3d = Model3D(cad="test")
    shape = Shape("", "")
    helix = Helix("Helix", r, z, cutwidth, odd, dble, axi, m3d, shape)
    ofile = open("Helix.yaml", "w")
    yaml.dump(helix, ofile)


def test_printhelix_oldformat():
    helix = yaml.load(open("tests/Helix-v0.yaml", "r"), Loader=yaml.FullLoader)
    print(helix)

def test_loadhelix_oldformat():
    helix = yaml.load(open("tests/Helix-v0.yaml", "r"), Loader=yaml.FullLoader)
    assert helix.r[0] == 19.3

def test_loadhelix():
    helix = yaml.load(open("Helix.yaml", "r"), Loader=yaml.FullLoader)
    assert helix.r[0] == 19.3

def test_jsonhelix():
    helix = yaml.load(open("Helix.yaml", "r"), Loader=yaml.FullLoader)
    helix.write_to_json()

    # load from json
    jsondata = Helix.from_json('Helix.json')
    assert jsondata.name == "Helix" and jsondata.r[0] == 19.3

def test_chamfer():
    r = [38.6 / 2.0, 48.4 / 2.0]
    z = []
    cutwidth = 0.2
    odd = True
    dble = True
    axi = ModelAxi()
    m3d = Model3D(cad="test")
    shape = Shape("", "")
    chamfers = [Chamfer("HP", "rint", 4, 9)]
    helix = Helix("Helix", r, z, cutwidth, odd, dble, axi, m3d, shape, chamfers)
    ofile = open("Helix-w-chamfer.yaml", "w")
    yaml.dump(helix, ofile)

def test_loadchamfer():
    helix = yaml.load(open("Helix-w-chamfer.yaml", "r"), Loader=yaml.FullLoader)
    print(helix.chamfers)
    chamfers = helix.chamfers
    chamfer0 = chamfers[0]
    assert chamfer0.side == "HP"
