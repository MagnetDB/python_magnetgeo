from python_magnetgeo.tierod import Tierod
from python_magnetgeo.Shape2D import Shape2D

import yaml
import pytest


def test_tierod():
    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    tierod = Tierod(2, 20, 1, 4, Square)
    tierod.dump("tierod")
