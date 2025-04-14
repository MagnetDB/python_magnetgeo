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
    BPside :
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
        BPside: bool = True,
        fillets: bool = False,
        cad: str|None = None
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.BPside = BPside
        self.fillets = fillets
        self.cad = cad

    def __repr__(self):
        """
        representation of object
        """
        msg = "%s(name=%r, r=%r, z=%r, n=%r, angle=%r, BPside=%r, fillets=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
            self.n,
            self.angle,
            self.BPside,
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
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception as e:
            raise Exception("Failed to dump Ring data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception as e:
            raise Exception(f"Failed to load Ring data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.n = data.n
        self.angle = data.angle
        self.BPside = data.BPside
        self.fillets = data.fillets
        self.data = None
        self.cad = getattr(data, 'cad', '')

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
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f"Ring.from_json: filename={filename}")
        with open(filename, "r") as istream:
            return json.loads(
                istream.read(), object_hook=deserialize.unserialize_object
            )


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
    BPside = values["BPside"]
    fillets = values["fillets"]
    cad = values.get("cad", '')
    
    ring = Ring(name, r, z, n, angle, BPside, fillets, cad)
    if not hasattr(ring, 'cad'):
        ring.cad = ''
    return cad

yaml.add_constructor("!Ring", Ring_constructor)
