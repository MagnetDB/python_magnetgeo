#!/usr/bin/env python3

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

from .base import YAMLObjectBase


class Model3D(YAMLObjectBase):
    """
    name:
    cad :
    with_shapes :
    with_channels :
    """

    yaml_tag = "Model3D"

    def __init__(
        self, name: str, cad: str, with_shapes: bool = False, with_channels: bool = False
    ) -> None:
        """
        Initialize a 3D CAD model configuration.

        A Model3D specifies parameters for generating actual 3D CAD representations
        of magnet geometries. It defines which CAD system to use and what geometric
        features to include in the generated model (shapes, channels, etc.).

        Args:
            name: Unique identifier for this 3D model configuration. Can be empty
                string "" if the model doesn't require a specific name.
            cad: CAD system identifier. Specifies which CAD ID in Catia/Smarteam
            with_shapes: If True, include additional geometric shapes/features
                        (such as those defined in Shape objects) in the 3D model.
                        These are typically cooling channels, ventilation holes,
                        or other secondary geometric features. Default: False
            with_channels: If True, include cooling/flow channels explicitly in
                        the 3D model geometry. Channels may be modeled as solid
                        voids or separate geometric entities. Default: False

        Notes:
            - Name can be empty string (no validation required)
            - CAD identifier determines the export format and methodology
            - with_shapes and with_channels control model complexity/detail
            - More detailed models (True flags) take longer to generate
            - Balance between model detail and computational efficiency
            - Used in conjunction with Helix, Bitter, or other magnet classes

        Example:
            >>> # Simple model without extra features
            >>> model1 = Model3D(
            ...     name="basic_model",
            ...     cad="SALOME",
            ...     with_shapes=False,
            ...     with_channels=False
            ... )

        """
        self.name = name
        self.cad = cad
        self.with_shapes = with_shapes
        self.with_channels = with_channels

    def __repr__(self):
        """
        Return string representation of Model3D instance.

        Provides a detailed string showing all attributes and their values,
        useful for debugging, logging, and interactive inspection.

        Returns:
            str: String representation in constructor-like format showing:
                - name: Model identifier (may be empty string)
                - cad: CAD identifier
                - with_shapes: Shape inclusion flag
                - with_channels: Channel inclusion flag

        Example:
            >>> model = Model3D(
            ...     name="helix_cad",
            ...     cad="SALOME",
            ...     with_shapes=True,
            ...     with_channels=False
            ... )
            >>> print(repr(model))
            Model3D(name='helix_cad', cad='SALOME', with_shapes=True, with_channels=False)

        """
        return f"{self.__class__.__name__}(name={self.name!r}, cad={self.cad!r}, with_shapes={self.with_shapes!r}, with_channels={self.with_channels!r})"

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """
        Create Model3D instance from dictionary representation.

        Standard deserialization method with default values for optional parameters.

        Args:
            values: Dictionary containing Model3D configuration with keys:
                - name (str, optional): Model identifier. Default: ""
                - cad (str): Catia/SmarTeam CAD identifier (required)
                - with_shapes (bool, optional): Include shapes flag. Default: False
                - with_channels (bool, optional): Include channels flag. Default: False
            debug: Enable debug output (currently unused)

        Returns:
            Model3D: New Model3D instance created from dictionary

        Raises:
            KeyError: If required 'cad' key is missing from dictionary

        Notes:
            - Name defaults to empty string if not provided
            - Boolean flags default to False if not provided
            - CAD identifier is the only required field

        Example:
            >>> # Full specification
            >>> data = {
            ...     "name": "helix_model",
            ...     "cad": "SALOME",
            ...     "with_shapes": True,
            ...     "with_channels": True
            ... }
            >>> model = Model3D.from_dict(data)
        """
        name = values.get("name", "")
        cad = values["cad"]
        with_shapes = values.get("with_shapes", False)
        with_channels = values.get("with_channels", False)

        return cls(name, cad, with_shapes, with_channels)
