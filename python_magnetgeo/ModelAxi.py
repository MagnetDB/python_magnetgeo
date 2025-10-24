#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""


from .base import YAMLObjectBase
from .validation import GeometryValidator, ValidationError


class ModelAxi(YAMLObjectBase):
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
        Initialize an axisymmetric helical cut model.

        A ModelAxi defines the geometric parameters for a helical cut pattern in
        resistive magnet conductors (Helix or Bitter). The helical pattern allows
        coolant flow through the conductor while maintaining structural integrity.

        The model describes the helix in sections, where each section can have a
        different number of turns and pitch. The total axial extent covered by all
        sections must equal 2*h.

        Args:
            name: Unique identifier for this helical cut model. Default: ""
            h: Half-height of the helical pattern in mm. The pattern extends from
            -h to +h along the z-axis, for a total height of 2*h. Default: 0.0
            turns: List of turn counts for each helical section. Each element
                represents the number of complete turns in that section.
                For example, [10.0, 20.0, 15.0] means three sections with
                10, 20, and 15 turns respectively. Default: []
            pitch: List of pitch values for each helical section in mm. Pitch is
                the axial distance traveled per complete turn. Must have the
                same length as turns list. For example, [5.0, 5.0, 5.0] means
                all sections have 5mm pitch. Default: []

        Raises:
            ValidationError: If name is invalid (empty when required)
            ValidationError: If len(pitch) != len(turns) (must be equal)
            ValidationError: If sum(pitch[i] * turns[i]) != 2*h (within tolerance 1e-6)
                            This ensures the helical pattern fits exactly in the
                            available axial space.

        Notes:
            - Helical pattern extends from z = -h to z = +h
            - Each section i contributes height = pitch[i] * turns[i]
            - Total height constraint: Σ(pitch[i] * turns[i]) = 2*h
            - Empty lists for turns/pitch are valid (no helical pattern)
            - Turn count can be non-integer (fractional turns)
            - Pitch can vary between sections for optimized cooling/performance

        Example:
            >>> # Simple uniform helix
            >>> model1 = ModelAxi(
            ...     name="uniform_helix",
            ...     h=112.5,             # ±112.5mm (225mm total height)
            ...     turns=[45.0],        # Single section with 45 turns
            ...     pitch=[5.0]          # 5mm pitch
            ... )
            >>> # 45 turns * 5mm = 225mm = 2 * 112.5mm ✓

            >>> # Multi-section helix with variable pitch
            >>> model2 = ModelAxi(
            ...     name="variable_helix",
            ...     h=100.0,             # ±100mm (200mm total height)
            ...     turns=[10.0, 20.0, 10.0],   # 3 sections
            ...     pitch=[4.0, 6.0, 4.0]       # Variable pitch
            ... )
            >>> # (10*4) + (20*6) + (10*4) = 40 + 120 + 40 = 200mm = 2*100mm ✓

            >>> # No helical pattern (empty lists)
            >>> model3 = ModelAxi(
            ...     name="no_helix",
            ...     h=50.0,
            ...     turns=[],
            ...     pitch=[]
            ... )
        """
        GeometryValidator.validate_name(name)
        if pitch and turns:
            if len(pitch) != len(turns):
                raise ValidationError(
                    f"Number of pitch ({len(pitch)}) must be equal to number of turns ({len(turns)})"
                )

        self.name = name
        self.h = h
        self.turns = turns
        self.pitch = pitch

        # sum of pitch*turns must be equal to 2*h
        if pitch:
            total_height = sum(p * t for p, t in zip(pitch, turns))
            if abs(total_height - 2 * self.h) > 1.0e-6:
                raise ValidationError(
                    f"Sum of pitch*turns ({total_height}) must be equal to 2*h ({2*self.h})"
                )

    def __repr__(self):
        """
        Return string representation of ModelAxi instance.

        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.

        Returns:
            str: String representation in constructor-like format showing:
                - name: Model identifier
                - h: Half-height value
                - turns: List of turn counts
                - pitch: List of pitch values

        Example:
            >>> model = ModelAxi(
            ...     name="helix_model",
            ...     h=112.5,
            ...     turns=[10.0, 20.0, 15.0],
            ...     pitch=[5.0, 5.0, 5.0]
            ... )
            >>> print(repr(model))
            ModelAxi(name='helix_model', h=112.5, turns=[10.0, 20.0, 15.0],
                    pitch=[5.0, 5.0, 5.0])
            >>>
            >>> # In Python REPL
            >>> model
            ModelAxi(name='helix_model', h=112.5, ...)
            >>>
            >>> # Empty model
            >>> empty = ModelAxi(name="empty", h=50.0, turns=[], pitch=[])
            >>> print(repr(empty))
            ModelAxi(name='empty', h=50.0, turns=[], pitch=[])
        """
        return "%s(name=%r, h=%r, turns=%r, pitch=%r)" % (
            self.__class__.__name__,
            self.name,
            self.h,
            self.turns,
            self.pitch,
        )

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create ModelAxi instance from dictionary representation.

        Standard deserialization method for creating ModelAxi from configuration data.

        Args:
            values: Dictionary containing ModelAxi configuration with keys:
                - name (str): Model identifier
                - h (float): Half-height in mm
                - turns (list[float]): Turn counts for each section
                - pitch (list[float]): Pitch values for each section in mm
            debug: Enable debug output (currently unused)

        Returns:
            ModelAxi: New ModelAxi instance created from dictionary

        Raises:
            KeyError: If required keys are missing from dictionary
            ValidationError: If validation constraints are violated

        Example:
            >>> data = {
            ...     "name": "helix_pattern",
            ...     "h": 112.5,
            ...     "turns": [10.0, 20.0, 15.0],
            ...     "pitch": [5.0, 5.0, 5.0]
            ... }
            >>> model = ModelAxi.from_dict(data)
            >>> assert model.name == "helix_pattern"
            >>> assert model.get_Nturns() == 45.0
        """
        name = values["name"]
        h = values["h"]
        turns = values["turns"]
        pitch = values["pitch"]

        return cls(name, h, turns, pitch)

    def get_Nturns(self) -> float:
        """
        Calculate the total number of turns across all helical sections.

        Sums the turn counts from all sections to give the total number of
        complete helical turns in the pattern.

        Returns:
            float: Total number of turns (sum of all elements in self.turns)

        Notes:
            - Returns 0.0 if turns list is empty
            - Turn count can be fractional (e.g., 45.5 turns)
            - Used for electrical resistance and inductance calculations
            - Used for determining number of geometric sections in meshing

        Example:
            >>> model = ModelAxi(
            ...     name="test",
            ...     h=112.5,
            ...     turns=[10.0, 20.0, 15.0],
            ...     pitch=[5.0, 5.0, 5.0]
            ... )
            >>> total_turns = model.get_Nturns()
            >>> print(total_turns)  # 45.0 (10 + 20 + 15)

            >>> # With fractional turns
            >>> model2 = ModelAxi(
            ...     name="fractional",
            ...     h=56.25,
            ...     turns=[10.5, 12.0],
            ...     pitch=[5.0, 5.0]
            ... )
            >>> print(model2.get_Nturns())  # 22.5

            >>> # Empty model
            >>> model3 = ModelAxi(name="empty", h=50.0, turns=[], pitch=[])
            >>> print(model3.get_Nturns())  # 0.0
        """
        return sum(self.turns)

    def compact(self, tol: float = 1.0e-6):
        """
        Consolidate consecutive sections with similar pitch values.

        Merges adjacent helical sections that have nearly identical pitch values
        (within specified tolerance) by summing their turns. This simplifies the
        helical pattern representation while maintaining geometric equivalence.

        Args:
            tol: Relative tolerance for pitch comparison. Two pitch values p1 and p2
                are considered similar if :math: ``|1 - p1/p2|`` <= tol. Default: 1e-6

        Returns:
            tuple: (new_turns, new_pitch) where:
                - new_turns (list[float]): Compacted turn counts
                - new_pitch (list[float]): Compacted pitch values
                Both lists have length <= original length

        Notes:
            - Does not modify the object (returns new lists)
            - Preserves total height: Σ(new_turns[i] * new_pitch[i]) = Σ(turns[i] * pitch[i])
            - Empty pitch list returns copies of original lists
            - Consecutive sections with similar pitch are merged
            - Useful for optimizing CAM operations and reducing complexity

        Algorithm:
            1. Group consecutive sections with similar pitch (within tolerance)
            2. For each group, sum the turns and keep the first pitch value
            3. Result has fewer sections but same total geometry

        Example:
            >>> # Three sections with same pitch
            >>> model = ModelAxi(
            ...     name="test",
            ...     h=112.5,
            ...     turns=[10.0, 20.0, 15.0],
            ...     pitch=[5.0, 5.0, 5.0]
            ... )
            >>> new_turns, new_pitch = model.compact()
            >>> print(new_turns)  # [45.0] - all merged
            >>> print(new_pitch)  # [5.0]
            >>> # Total height preserved: 45*5 = 225mm = original sum

            >>> # Mixed pitches
            >>> model2 = ModelAxi(
            ...     name="mixed",
            ...     h=100.0,
            ...     turns=[10.0, 10.0, 10.0, 5.0, 5.0],
            ...     pitch=[5.0, 5.0, 5.0, 3.0, 3.0]
            ... )
            >>> new_turns, new_pitch = model2.compact()
            >>> print(new_turns)  # [30.0, 10.0] - two groups
            >>> print(new_pitch)  # [5.0, 3.0]

            >>> # With tolerance
            >>> model3 = ModelAxi(
            ...     name="similar",
            ...     h=75.0,
            ...     turns=[10.0, 10.0],
            ...     pitch=[5.0, 5.00001]  # Very similar
            ... )
            >>> new_turns, new_pitch = model3.compact(tol=1e-4)
            >>> print(new_turns)  # [20.0] - merged due to similarity
            >>> print(new_pitch)  # [5.0]

            >>> # Empty pitch
            >>> model4 = ModelAxi(name="empty", h=50.0, turns=[10.0], pitch=[])
            >>> new_turns, new_pitch = model4.compact()
            >>> print(new_turns)  # [10.0] - unchanged
            >>> print(new_pitch)  # [] - unchanged
        """

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
