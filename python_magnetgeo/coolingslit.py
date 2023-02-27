import yaml

from .Shape2D import Shape2D


class CoolingSlit:
    yaml_tag = "Slit"

    def __init__(
        self, r: float, angle: float, n: int, dh: float, sh: float, shape: Shape2D
    ) -> None:
        self.r = r
        self.angle = angle
        self.n = n
        self.dh = dh
        self.sh = sh
        self.shape = shape

    def __repr__(self):
        return "r=%r, angle=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.r,
            self.angle,
            self.n,
            self.dh,
            self.sh,
            self.sh,
            self.shape,
        )

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to CoolingSlit dump")

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
        self.angle = data.angle
        self.n = data.n
        self.dh = data.dh
        self.sh = data.sh
        self.shape = data.shape


def CoolingSlit_constructor(loader, node):
    """
    build an coolingslit object
    """
    values = loader.construct_mapping(node)
    r = values["r"]
    angle = values["angle"]
    n = values["n"]
    dh = values["dh"]
    sh = values["sh"]
    shape = values["shape"]

    return CoolingSlit(r, angle, n, dh, sh, shape)


yaml.add_constructor("!Slit", CoolingSlit_constructor)

if __name__ == "__main__":
    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    slit = CoolingSlit(2, 5, 20, 0.1, 0.2, Square)
    slit.dump("slit")
