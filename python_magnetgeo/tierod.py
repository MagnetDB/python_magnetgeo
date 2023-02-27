from typing import Union

import yaml

from .Shape2D import Shape2D


class Tierod:
    yaml_tag = "Tierod"

    def __init__(self, r: float, n: int, shape: Union[Shape2D, str]) -> None:
        self.r = r
        self.n = n
        if isinstance(shape, Shape2D):
            self.shape = shape
        else:
            with open(f"{shape}.yaml", "r") as f:
                self.shape = yaml.load(f, Loader=yaml.FullLoader)

    def __repr__(self):
        return "r=%r, n=%r, shape=%r" % (self.r, self.n, self.shape)

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Tierod dump")

    def load(self, name: str):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Bitter data {name}.yaml")

        self.r = data.r
        self.n = data.n
        self.shape = data.shape


def Tierod_constructor(loader, node):
    """
    build an Tierod object
    """
    values = loader.construct_mapping(node)
    r = values["r"]
    n = values["n"]
    shape = values["shape"]

    return Tierod(r, n, shape)


yaml.add_constructor("!TieRod", Tierod_constructor)

if __name__ == "__main__":
    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    tierod = Tierod(2, 20, Square)
    tierod.dump("tierod")
