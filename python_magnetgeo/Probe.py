#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Probe:

* name: Identifier for this probe collection
* type: Type of probes (e.g., "voltage_taps", "temperature", "magnetic_field")
* labels: List of probe identifiers
* points: List of 3D coordinates [x, y, z] for each probe location
"""

from typing import List, Union
from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError

class Probe(YAMLObjectBase):
    """
    name: Identifier for this probe collection
    type: Type of probes (e.g., "voltage_taps", "temperature", "magnetic_field")
    labels: List of probe identifiers
    points: List of 3D coordinates [x, y, z] for each probe location
    """

    yaml_tag = "Probe"

    def __init__(
        self,
        name: str,
        type: str,
        labels: List[Union[str, int]],
        points: List[List[float]],
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.type = type
        self.labels = labels
        self.points = points
        
        # Validate that labels and points have the same length
        if len(self.labels) != len(self.points):
            raise ValueError(f"Probe {name}: labels and points must have the same length. "
                           f"Got {len(self.labels)} indices and {len(self.points)} points.")
        
        # Validate that each location has exactly 3 coordinates
        for i, loc in enumerate(self.points):
            if len(loc) != 3:
                raise ValueError(f"Probe {name}: location {i} must have exactly 3 coordinates [x, y, z]. "
                               f"Got {len(loc)} coordinates: {loc}")

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, type=%r, labels=%r, points=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.type,
                self.labels,
                self.points,
            )
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        create from dict
        """
        name = values["name"]
        type = values["type"]
        labels = values["labels"]
        points = values["points"]

        return cls(name, type, labels, points)

    def get_probe_count(self) -> int:
        """
        return the number of probes in this collection
        """
        return len(self.labels)

    def get_probe_by_labels(self, probe_labels: Union[str, int]) -> dict:
        """
        return probe information by its labels
        """
        try:
            idx = self.labels.labels(probe_labels)
            return {
                "labels": self.labels[idx],
                "location": self.points[idx],
                "type": self.type
            }
        except ValueError:
            raise ValueError(f"Probe labels {probe_labels} not found in {self.name}")

    def get_points_by_type(self, type: str = None) -> List[List[float]]:
        """
        return all points, optionally filtered by probe type
        """
        if type is None or type == self.type:
            return self.points.copy()
        else:
            return []

    def add_probe(self, probe_labels: Union[str, int], location: List[float]) -> None:
        """
        add a new probe to the collection
        """
        if len(location) != 3:
            raise ValueError(f"Location must have exactly 3 coordinates [x, y, z]. Got {len(location)}: {location}")
        
        if probe_labels in self.labels:
            raise ValueError(f"Probe labels {probe_labels} already exists in {self.name}")
        
        self.labels.append(probe_labels)
        self.points.append(location)

    def remove_probe(self, probe_labels: Union[str, int]) -> None:
        """
        remove a probe from the collection
        """
        try:
            idx = self.labels.labels(probe_labels)
            del self.labels[idx]
            del self.points[idx]
        except ValueError:
            raise ValueError(f"Probe labels {probe_labels} not found in {self.name}")

