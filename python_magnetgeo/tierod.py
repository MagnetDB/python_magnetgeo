import yaml
import json


class Tierod(yaml.YAMLObject):
    yaml_tag = "Tierod"

    def __init__(
        self, name: str, r: float, n: int, dh: float, sh: float, shape
    ) -> None:
        self.name = name
        self.r = r
        self.n = n
        self.dh: float = dh
        self.sh: float = sh
        self.shape = shape
        

    def __repr__(self):
        return "%s(name=%s, r=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.n,
            self.dh,
            self.sh,
            self.shape,
        )
    
    def update(self):
        from .utils import check_objects, loadObject
        from .Shape2D import Shape2D
        if isinstance(self.shape, str):
            self.shape = loadObject("shape", self.shape, Shape2D, Shape2D.from_yaml)

    def dump(self):
        """
        dump object to file
        """
        from .utils import writeYaml
        writeYaml("Tierod", self, Tierod)

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values.get("name", "")
        r = values["r"]
        n = values["n"]
        dh = values["dh"]
        sh = values["sh"]
        shape = values["shape"]

        object = cls(name, r, n, dh, sh, shape)
        object.update()
        return object
    
    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        object = loadYaml("Tierod", filename, Tierod, debug)
        object.update()
        return object

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        object = loadJson("Tierod", filename, debug)
        object.update()
        return object


def Tierod_constructor(loader, node):
    """
    build an Tierod object
    """
    values = loader.construct_mapping(node)
    return Tierod.from_dict(values)

yaml.add_constructor(Tierod.yaml_tag, Tierod_constructor)
