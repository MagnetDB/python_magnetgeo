import yaml
import json

from .Shape2D import Shape2D
from .utils import loadObject

class Tierod(yaml.YAMLObject):
    yaml_tag = "Tierod"

    def __init__(
        self, r: float, n: int, dh: float, sh: float, shape: Shape2D | str
    ) -> None:
        self.r = r
        self.n = n
        self.dh: float = dh
        self.sh: float = sh
        self.shape = shape
        

    def __repr__(self):
        return "%s(r=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.__class__.__name__,
            self.r,
            self.n,
            self.dh,
            self.sh,
            self.shape,
        )
    def update(self):
        from .utils import check_objects
        if isinstance(self.shape, str):
            self.shape = loadObject("shape", self.shape, Shape2D, Shape2D.from_yaml)

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception("Failed to Tierod dump")

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("Tierod", filename, Tierod, debug)



    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("Tierod", filename, debug)


def Tierod_constructor(loader, node):
    """
    build an Tierod object
    """
    values = loader.construct_mapping(node)
    r = values["r"]
    n = values["n"]
    dh = values["dh"]
    sh = values["sh"]
    shape = values["shape"]
    return Tierod(r, n, dh, sh, shape)

yaml.add_constructor(Tierod.yaml_tag, Tierod_constructor)
