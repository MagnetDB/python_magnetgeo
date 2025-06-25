#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Ring:

"""

import json
import yaml


class Ring(yaml.YAMLObject):
    """
    name :
    r :
    z :
    angle :
    bpside :
    fillets :
    cad :
    """

    yaml_tag = "Ring"

    def __setstate__(self, state):
        """
        This method is called during deserialization (when loading from YAML or pickle)
        We use it to ensure the optional attributes always exist
        """
        self.__dict__.update(state)
        
        # Ensure these attributes always exist
        if not hasattr(self, 'cad'):
            self.cad = ''

    def __init__(
        self,
        name: str,
        r: list[float],
        z: list[float],
        n: int = 0,
        angle: float = 0,
        bpside: bool = True,
        fillets: bool = False,
        cad: str = None
    ) -> None:
        """
        initialize object
        """
        
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.bpside = bpside
        self.fillets = fillets
        self.cad = cad

    def __repr__(self):
        """
        representation of object
        """
        msg = "%s(name=%r, r=%r, z=%r, n=%r, angle=%r, bpside=%r, fillets=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
            self.n,
            self.angle,
            self.bpside,
            self.fillets)
        if hasattr(self, 'cad'):
            msg += ", cad=%r" % self.cad
        else:
            msg += ", cad=None"
        return msg

    def get_lc(self):
        return (self.r[1] - self.r[0]) / 10.0

    def dump(self):
        """
        dump object to file
        """
        from .utils import writeYaml
        writeYaml("Ring", self, Ring)

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self):
        """
        write from json file
        """
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        r = values["r"]
        z = values["z"]
        n = values["n"]
        angle = values["angle"]
        bpside = values["bpside"]
        fillets = values["fillets"]
        cad = values.get("cad", '')

        return  cls(name, r, z, n, angle, bpside, fillets, cad)


    @classmethod
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("Ring", filename, Ring, debug)

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("Ring", filename, debug)


def Ring_constructor(loader, node):
    """
    build an ring object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    n = values["n"]
    angle = values["angle"]
    bpside = values["bpside"]
    fillets = values["fillets"]
    cad = values.get("cad", '') 

    return  Ring(name, r, z, n, angle, bpside, fillets, cad)

yaml.add_constructor(Ring.yaml_tag, Ring_constructor)
