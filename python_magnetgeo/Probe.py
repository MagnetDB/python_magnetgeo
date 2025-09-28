#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Probe:

* name: Identifier for this probe collection
* probe_type: Type of probes (e.g., "voltage_taps", "temperature", "magnetic_field")
* index: List of probe identifiers
* locations: List of 3D coordinates [x, y, z] for each probe location
"""

from typing import List, Union
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Probe(YAMLObjectBase):
    """
    name: Identifier for this probe collection
    probe_type: Type of probes (e.g., "voltage_taps", "temperature", "magnetic_field")
    index: List of probe identifiers
    locations: List of 3D coordinates [x, y, z] for each probe location
    """

    yaml_tag = "Probe"

    def __init__(
        self,
        name: str,
        probe_type: str,
        index: List[Union[str, int]],
        locations: List[List[float]],
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.probe_type = probe_type
        self.index = index
        self.locations = locations
        
        # Validate that index and locations have the same length
        if len(self.index) != len(self.locations):
            raise ValueError(f"Probe {name}: index and locations must have the same length. "
                           f"Got {len(self.index)} indices and {len(self.locations)} locations.")
        
        # Validate that each location has exactly 3 coordinates
        for i, loc in enumerate(self.locations):
            if len(loc) != 3:
                raise ValueError(f"Probe {name}: location {i} must have exactly 3 coordinates [x, y, z]. "
                               f"Got {len(loc)} coordinates: {loc}")

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, probe_type=%r, index=%r, locations=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.probe_type,
                self.index,
                self.locations,
            )
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        probe_type = values["probe_type"]
        index = values["index"]
        locations = values["locations"]

        return cls(name, probe_type, index, locations)

    def get_probe_count(self) -> int:
        """
        return the number of probes in this collection
        """
        return len(self.index)

    def get_probe_by_index(self, probe_index: Union[str, int]) -> dict:
        """
        return probe information by its index
        """
        try:
            idx = self.index.index(probe_index)
            return {
                "index": self.index[idx],
                "location": self.locations[idx],
                "probe_type": self.probe_type
            }
        except ValueError:
            raise ValueError(f"Probe index {probe_index} not found in {self.name}")

    def get_locations_by_type(self, probe_type: str = None) -> List[List[float]]:
        """
        return all locations, optionally filtered by probe type
        """
        if probe_type is None or probe_type == self.probe_type:
            return self.locations.copy()
        else:
            return []

    def add_probe(self, probe_index: Union[str, int], location: List[float]) -> None:
        """
        add a new probe to the collection
        """
        if len(location) != 3:
            raise ValueError(f"Location must have exactly 3 coordinates [x, y, z]. Got {len(location)}: {location}")
        
        if probe_index in self.index:
            raise ValueError(f"Probe index {probe_index} already exists in {self.name}")
        
        self.index.append(probe_index)
        self.locations.append(location)

    def remove_probe(self, probe_index: Union[str, int]) -> None:
        """
        remove a probe from the collection
        """
        try:
            idx = self.index.index(probe_index)
            del self.index[idx]
            del self.locations[idx]
        except ValueError:
            raise ValueError(f"Probe index {probe_index} not found in {self.name}")

