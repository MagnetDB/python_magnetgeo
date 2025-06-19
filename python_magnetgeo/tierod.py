import yaml
import json

from .Shape2D import Shape2D


class Tierod(yaml.YAMLObject):
    yaml_tag = "Tierod"

    def __init__(
        self, r: float, n: int, dh: float, sh: float, shape: Shape2D | str
    ) -> None:
        self.r = r
        self.n = n
        self.dh: float = dh
        self.sh: float = sh
        if isinstance(shape, Shape2D):
            self.shape = shape
        else:
            with open(f"{shape}.yaml", "r") as f:
                self.shape = yaml.load(f, Loader=yaml.FullLoader)

    def __repr__(self):
        return "%s(r=%r, n=%r, dh=%r, sh=%r, shape=%r)" % (
            self.__class__.__name__,
            self.r,
            self.n,
            self.dh,
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
        import os
        cwd = os.getcwd()

        (basedir, basename) = os.path.split(filename)
        print(f"basedir={basedir}, basename={basename}, cwd={cwd}")

        if basedir and basedir != ".":
            os.chdir(basedir)
            print(f"-> cwd={cwd}")

        try:
            with open(basename, "r") as istream:
                values, otype = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Tierod data {filename}")
        if basedir and basedir != ".":
            os.chdir(cwd)

        r = values["r"]
        n = values["n"]
        dh = values["dh"]
        sh = values["sh"]
        shape = values["shape"]
        return cls(r, n, dh, sh, shape)


    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f"Tierod.from_json: filename={filename}")
        with open(filename, "r") as istream:
            return json.loads(
                istream.read(), object_hook=deserialize.unserialize_object
            )


def Tierod_constructor(loader, node):
    """
    build an Tierod object
    """
    values = loader.construct_mapping(node)
    return values, "Tierod"

yaml.add_constructor(Tierod.yaml_tag, Tierod_constructor)
