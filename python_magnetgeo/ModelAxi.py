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
    def from_yaml(cls, filename: str, debug: bool = False):
        """
        create from yaml
        """
        from .utils import loadYaml
        return loadYaml("ModelAxi", filename, ModelAxi, debug)


    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from .utils import loadJson
        return loadJson("ModelAxi", filename, debug)
    

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return sum(self.turns)

    def compact(self, tol: float = 1.0e-6):
        if not self.pitch:
            return self.turns.copy(), self.pitch.copy()
        
        def are_similar(a: float, b: float) -> bool:
            return abs(1 - a / b) <= tol if b != 0 else abs(a) <= tol
        
        new_turns = []
        new_pitch = []
        
        i = 0
        while i < len(self.pitch):
            current_pitch = self.pitch[i]
            current_turn = self.turns[i]
            
            # Look ahead for consecutive similar pitches
            j = i + 1
            while j < len(self.pitch) and are_similar(self.pitch[j], current_pitch):
                current_turn += self.turns[j]  # Sum the turns
                j += 1
            
            new_pitch.append(current_pitch)
            new_turns.append(current_turn)
            
            i = j  # Move to next non-duplicate group
        
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


yaml.add_constructor(ModelAxi.yaml_tag, ModelAxi_constructor)
