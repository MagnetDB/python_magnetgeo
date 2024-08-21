from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo.tierod import Tierod
from python_magnetgeo.Shape2D import Shape2D

import yaml
import pytest


def test_create():

    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    dh = 4 * 1
    sh = 1 * 1
    tierod = Tierod(2, 20, dh, sh, Square)

    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    slit1 = CoolingSlit(2, 5, 20, 0.1, 0.2, Square)
    slit2 = CoolingSlit(10, 5, 20, 0.1, 0.2, Square)
    coolingSlits = [slit1, slit2]

    Axi = ModelAxi("test", 0.9, [2], [0.9])

    innerbore = 1 - 0.01
    outerbore = 2 + 0.01
    bitter = Bitter(
        "Bitter", [1, 2], [-1, 1], True, Axi, coolingSlits, tierod, innerbore, outerbore
    )
    bitter.dump()
    assert bitter.r[0] == 1

    """    
    with open("Bitter.yaml", "r") as f:
        bitter = yaml.load(f, Loader=yaml.FullLoader)

    print(bitter)
    for i, slit in enumerate(bitter.coolingslits):
        print(f"slit[{i}]: {slit}, shape={slit.shape}")
    """

def test_load():
    object = yaml.load(open("Bitter.yaml", "r"), Loader=yaml.FullLoader)
    assert object.r[0] == 1


def test_json():
    object = yaml.load(open("Bitter.yaml", "r"), Loader=yaml.FullLoader)
    object.write_to_json()

    # load from json
    jsondata = Bitter.from_json('Bitter.json')
    assert jsondata.name == "Bitter" and jsondata.r[0] == 1
