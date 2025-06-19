import yaml
import json

"""
Provides definition for Groove
!!! groove are supposed to be "square" like !!!

gtype: rint or rext
n: number of grooves
eps: depth of groove
"""


class Groove(yaml.YAMLObject):
    yaml_tag = "Groove"

    def __init__(self, gtype: str=None, n: int=0, eps: float=0) -> None:
        self.gtype = gtype
        self.n = n
        self.eps: float = eps

    def __repr__(self):
        return "%s(gtype=%s, n=%d, eps=%g)" % (
            self.__class__.__name__,
            self.gtype,
            self.n,
            self.eps,
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
            raise Exception(f"Failed to load Groove data {filename}")
        
        if basedir and basedir != ".":
            os.chdir(cwd)

        gtype = values["gtype"]
        n = values["n"]
        eps = values["eps"]
        return cls(gtype, n, eps)

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f"Groove.from_json: filename={filename}")
        with open(filename, "r") as istream:
            return json.loads(
                istream.read(), object_hook=deserialize.unserialize_object
            )


def Groove_constructor(loader, node):
    """
    build an Groove object
    """
    values = loader.construct_mapping(node)
    return values, "Groove"

yaml.add_constructor(Groove.yaml_tag, Groove_constructor)
