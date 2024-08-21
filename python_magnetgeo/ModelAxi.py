#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

import json
import yaml


class ModelAxi(yaml.YAMLObject):
    """
    name :
    h :
    turns :
    pitch :
    """

    yaml_tag = "ModelAxi"

    def __init__(
        self,
        name: str = "",
        h: float = 0.0,
        turns: list[float] = [],
        pitch: list[float] = [],
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.h = h
        self.turns = turns
        self.pitch = pitch

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, h=%r, turns=%r, pitch=%r)" % (
            self.__class__.__name__,
            self.name,
            self.h,
            self.turns,
            self.pitch,
        )

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
            print(f'ModelAxi.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)
    

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return sum(self.turns)

    def compact(self, tol: float = 1.0e-6):
        def indices(lst: list, item: float):
            return [i for i, x in enumerate(lst) if abs(1 - item / x) <= tol]

        List = self.pitch
        duplicates = dict((x, indices(List, x)) for x in set(List) if List.count(x) > 1)
        # print(f"duplicates: {duplicates}")

        sum_index = {}
        for key in duplicates:
            index_fst = duplicates[key][0]
            sum_index[index_fst] = [index_fst]
            search_index = sum_index[index_fst]
            search_elem = search_index[-1]
            for index in duplicates[key]:
                # print(f"index={index}, search_elem={search_elem}")
                if index - search_elem == 1:
                    search_index.append(index)
                    search_elem = index
                else:
                    sum_index[index] = [index]
                    search_index = sum_index[index]
                    search_elem = search_index[-1]

        # print(f"sum_index: {sum_index}")

        remove_ids = []
        for i in sum_index:
            for item in sum_index[i]:
                if item != i:
                    remove_ids.append(item)

        new_pitch = [p for i, p in enumerate(self.pitch) if not i in remove_ids]
        # print(f"pitch={self.pitch}")
        # print(f"new_pitch={new_pitch}")

        new_turns = (
            self.turns
        )  # use deepcopy: import copy and copy.deepcopy(self.axi.turns)
        for i in sum_index:
            for item in sum_index[i]:
                new_turns[i] += self.turns[item]
        new_turns = [p for i, p in enumerate(self.turns) if not i in remove_ids]
        # print(f"turns={self.turns}")
        # print(f"new_turns={new_turns}")

        return new_turns, new_pitch


def ModelAxi_constructor(loader, node):
    """
    build an ModelAxi object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    h = values["h"]
    turns = values["turns"]
    pitch = values["pitch"]
    return ModelAxi(name, h, turns, pitch)


yaml.add_constructor("!ModelAxi", ModelAxi_constructor)
