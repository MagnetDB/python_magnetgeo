#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Validation framework for geometry objects.
"""

from typing import List, Any
import warnings

class ValidationWarning(UserWarning):
    """Warning for non-critical validation issues"""
    pass

class ValidationError(ValueError):
    """Error for critical validation issues"""
    pass

class GeometryValidator:
    @staticmethod
    def validate_name(name: str) -> None:
        """General name validation - same for all geometries"""
        if not name or not isinstance(name, str):
            raise ValidationError("Name must be a non-empty string")
        
        # Check for whitespace-only names
        if not name.strip():
            raise ValidationError("Name cannot be whitespace only")
 
    @staticmethod
    def validate_positive(r: float, name: str) -> None:
        """Must be positive or null number"""
        if not isinstance(r, float) and not isinstance(r, int):
            raise ValidationError(f"{name} must be either a float or an integer")
        if r < 0:
            raise ValidationError(f"{name} must be positive or null")
    
    @staticmethod
    def validate_integer(n: int, name: str)  -> None:
        """Must be integer"""
        if not isinstance(n, int):
            raise ValidationError(f"{name} must be an integer")

    @staticmethod
    def validate_numeric(n: int|float, name: str)  -> None:
        """Must be integer or float"""
        if not isinstance(n, (int, float)):
            raise ValidationError(f"{name} must be an integer or a float")

    @staticmethod
    def validate_numeric_list(values: List[float], name: str, expected_length: int = None) -> None:
        """General validation for numeric lists"""
        if not isinstance(values, list):
            raise ValidationError(f"{name} must be a list")
        
        if expected_length and len(values) != expected_length:
            raise ValidationError(f"{name} must have exactly {expected_length} values, got {len(values)}")
        
        if not all(isinstance(val, (int, float)) for val in values):
            raise ValidationError(f"All {name} values must be numeric")
    
    @staticmethod
    def validate_ascending_order(values: List[float], name: str) -> None:
        """Validate that values are in ascending order"""
        for i in range(1, len(values)):
            if values[i] <= values[i-1]:
                raise ValidationError(f"{name} values must be in ascending order: {values}")


