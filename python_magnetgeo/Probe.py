#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides definition for Probe:

* name: Identifier for this probe collection
* type: Type of probes (e.g., "voltage_taps", "temperature", "magnetic_field")
* labels: List of probe identifiers
* points: List of 3D coordinates [x, y, z] for each probe location
"""

from .base import YAMLObjectBase


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
        labels: list[str | int],
        points: list[list[float]],
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
            raise ValueError(
                f"Probe {name}: labels and points must have the same length. "
                f"Got {len(self.labels)} indices and {len(self.points)} points."
            )

        # Validate that each point has exactly 3 coordinates
        for i, loc in enumerate(self.points):
            if len(loc) != 3:
                raise ValueError(
                    f"Probe {name}: point {i} must have exactly 3 coordinates [x, y, z]. "
                    f"Got {len(loc)} coordinates: {loc}"
                )

    def __repr__(self):
        """
        representation of object
        """
        return f"{self.__class__.__name__}(name={self.name!r}, type={self.type!r}, labels={self.labels!r}, points={self.points!r})"

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

    def get_probe_by_labels(self, probe_label: str | int) -> dict:
        """
        return probe information by its labels
        """
        try:
            idx = self.labels.index(probe_label)
            return {"labels": self.labels[idx], "points": self.points[idx], "type": self.type}
        except ValueError as e:
            raise ValueError(f"Probe labels {probe_label} not found in {self.name}") from e

    def get_points_by_type(self, type: str = None) -> list[list[float]]:
        """
        return all points, optionally filtered by probe type
        """
        if type is None or type == self.type:
            return self.points.copy()
        else:
            return []

    def add_probe(self, probe_labels: str | int, point: list[float]) -> None:
        """
        add a new probe to the collection
        """
        if len(point) != 3:
            raise ValueError(
                f"Point must have exactly 3 coordinates [x, y, z]. Got {len(point)}: {point}"
            )

        if probe_labels in self.labels:
            raise ValueError(f"Probe labels {probe_labels} already exists in {self.name}")

        self.labels.append(probe_labels)
        self.points.append(point)

    def remove_probe(self, probe_label: str | int) -> None:
        """
        remove a probe from the collection
        """
        try:
            idx = self.labels.index(probe_label)
            del self.labels[idx]
            del self.points[idx]
        except ValueError as e:
            raise ValueError(f"Probe labels {probe_label} not found in {self.name}") from e
