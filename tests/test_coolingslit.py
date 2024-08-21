from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo.coolingslit import Shape2D

import yaml
import pytest


def test_create():
    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    slit = CoolingSlit(2, 5, 20, 0.1, 0.2, Square)
    slit.dump("slit")
