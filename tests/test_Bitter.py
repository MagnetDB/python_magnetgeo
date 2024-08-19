from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo.tierod import Tierod
from python_magnetgeo.Shape2D import Shape2D

import yaml
import pytest


def test_create_Bitter():

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
        "B", [1, 2], [-1, 1], True, Axi, coolingSlits, tierod, innerbore, outerbore
    )
    bitter.dump()

    with open("B.yaml", "r") as f:
        bitter = yaml.load(f, Loader=yaml.FullLoader)

    print(bitter)
    for i, slit in enumerate(bitter.coolingslits):
        print(f"slit[{i}]: {slit}, shape={slit.shape}")
