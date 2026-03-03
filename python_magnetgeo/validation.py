#!/usr/bin/env python3

"""
Validation framework for geometry objects.

Provides comprehensive input validation for all geometry classes in python_magnetgeo.
The validation system ensures data integrity and provides clear, actionable error
messages when invalid configurations are detected.

Architecture:
- ValidationError: Exception for critical validation failures (must fix)
- ValidationWarning: Warning for non-critical issues (should review)
- GeometryValidator: Static validation methods used by all geometry classes

The validator is used throughout the codebase to ensure:
- Names are valid non-empty strings
- Numeric values are positive when required
- Lists have correct lengths and types
- Values are in proper order (ascending/descending)
- Geometry bounds are physically valid

Example Usage:
    >>> from python_magnetgeo.validation import GeometryValidator, ValidationError
    >>>
    >>> # Validate object name
    >>> try:
    ...     GeometryValidator.validate_name("")
    ... except ValidationError as e:
    ...     print(f"Error: {e}")
    Error: Name must be a non-empty string
    >>>
    >>> # Validate radial bounds
    >>> GeometryValidator.validate_numeric_list([10.0, 20.0], "r", expected_length=2)
    >>> GeometryValidator.validate_ascending_order([10.0, 20.0], "r")
    >>>
    >>> # Validate positive values
    >>> GeometryValidator.validate_positive(5.0, "radius")

Integration with Geometry Classes:
    All geometry class constructors use the validator:

    >>> class Helix(YAMLObjectBase):
    ...     def __init__(self, name: str, r: list[float], z: list[float], ...):
    ...         # Validate all inputs before assignment
    ...         GeometryValidator.validate_name(name)
    ...         GeometryValidator.validate_numeric_list(r, "r", expected_length=2)
    ...         GeometryValidator.validate_ascending_order(r, "r")
    ...         GeometryValidator.validate_numeric_list(z, "z", expected_length=2)
    ...         GeometryValidator.validate_ascending_order(z, "z")
    ...
    ...         self.name = name
    ...         self.r = r
    ...         self.z = z
"""

from .logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class ValidationWarning(UserWarning):
    """Warning for non-critical validation issues"""

    pass


class ValidationError(ValueError):
    """Error for critical validation issues"""

    pass


class GeometryValidator:
    """
    Static validator class providing validation methods for geometry objects.

    All validation methods are static and raise ValidationError on failure.
    Used throughout python_magnetgeo to ensure data integrity before object
    creation.

    Validation Categories:
        - Name validation: Non-empty strings
        - Numeric validation: Type checking and sign constraints
        - List validation: Length and element type checking
        - Order validation: Ascending/descending sequences
        - Geometry validation: Physical constraints (r_inner < r_outer, etc.)

    Design Philosophy:
        - Fail fast: Detect problems at object creation time
        - Clear messages: Explain what's wrong and what's expected
        - Type safe: Validate types match expectations
        - Consistent: Same validation logic across all classes

    Example:
        >>> from python_magnetgeo.validation import GeometryValidator, ValidationError
        >>>
        >>> # All methods are static - no instantiation needed
        >>> GeometryValidator.validate_name("my_magnet")  # OK
        >>> GeometryValidator.validate_positive(10.5, "radius")  # OK
        >>>
        >>> # Validation errors provide clear messages
        >>> try:
        ...     GeometryValidator.validate_name("")
        ... except ValidationError as e:
        ...     print(e)
        Name must be a non-empty string
    """

    @staticmethod
    def validate_name(name: str) -> None:
        """Validate that a name is a non-empty string"""
        if not name or not isinstance(name, str):
            logger.error(f"Validation failed: Name must be a non-empty string, got {type(name)}")
            raise ValidationError("Name must be a non-empty string")

        # Check for whitespace-only names
        if not name.strip():
            logger.error("Validation failed: Name cannot be whitespace only")
            raise ValidationError("Name cannot be whitespace only")
        
        logger.debug(f"Name validation passed: '{name}'")

    @staticmethod
    def validate_positive(r: float, name: str) -> None:
        """Validate that a numeric value is positive or zero"""
        if not isinstance(r, float) and not isinstance(r, int):
            logger.error(f"Validation failed: {name} must be numeric, got {type(r)}")
            raise ValidationError(f"{name} must be either a float or an integer")
        if r < 0:
            logger.error(f"Validation failed: {name}={r} must be positive or null")
            raise ValidationError(f"{name} must be positive or null")
        
        logger.debug(f"Positive validation passed: {name}={r}")

    @staticmethod
    def validate_integer(n: int, name: str) -> None:
        """Validate that a value is an integer type"""
        if not isinstance(n, int):
            logger.error(f"Validation failed: {name} must be an integer, got {type(n)}")
            raise ValidationError(f"{name} must be an integer")
        
        logger.debug(f"Integer validation passed: {name}={n}")

    @staticmethod
    def validate_numeric(n: int | float, name: str) -> None:
        """Validate that a value is numeric (int or float)"""
        if not isinstance(n, (int, float)):
            logger.error(f"Validation failed: {name} must be numeric, got {type(n)}")
            raise ValidationError(f"{name} must be an integer or a float")
        
        logger.debug(f"Numeric validation passed: {name}={n}")

    @staticmethod
    def validate_numeric_list(values: list[float], name: str, expected_length: int = None) -> None:
        """Validate that a list contains only numeric values with optional length check"""
        if not isinstance(values, (list, tuple)):
            logger.error(f"Validation failed: {name} must be a list, got {type(values)}")
            raise ValidationError(f"{name} must be a list")

        if not all(isinstance(x, (int, float)) for x in values):
            logger.error(f"Validation failed: All elements in {name} must be numeric")
            raise ValidationError(f"All elements in {name} must be numeric")

        if expected_length and len(values) != expected_length:
            logger.error(f"Validation failed: {name} has {len(values)} values, expected {expected_length}")
            raise ValidationError(
                f"{name} must have exactly {expected_length} values, got {len(values)}"
            )
        
        logger.debug(f"Numeric list validation passed: {name} with {len(values)} elements")

    @staticmethod
    def validate_ascending_order(values: list[float], name: str) -> None:
        """Validate that numeric values are in strictly ascending order"""
        for i in range(1, len(values)):
            if values[i] <= values[i - 1]:
                logger.error(f"Validation failed: {name} values not in ascending order at index {i}: {values}")
                raise ValidationError(f"{name} values must be in ascending order: {values}")
        
        logger.debug(f"Ascending order validation passed: {name}={values}")
