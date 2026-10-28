#!/usr/bin/env python3

"""
Provides tools to un/serialize data from json
"""

from .base import YAMLObjectBase

# Module logger
from .logging_config import get_logger

# Import all classes to ensure they're registered
# (importing triggers __init_subclass__ which registers them)

logger = get_logger(__name__)

# From : http://chimera.labs.oreilly.com/books/1230000000393/ch06.html#_discussion_95
# Dictionary mapping names to known classes

# Get class registry from base class
# This is automatically populated by __init_subclass__
classes = YAMLObjectBase.get_all_classes()


def serialize_instance(obj):
    """
    Serialize instance of an object to dictionary for JSON.

    Handles:
    - Enum values: converts to their string values
    - Private attributes: filters out attributes starting with _ (like _basedir)

    Args:
        obj: Object to serialize

    Returns:
        dict: Dictionary representation with __classname__ and public attributes
    """
    from enum import Enum

    d = {"__classname__": type(obj).__name__}

    # Get object attributes
    obj_dict = vars(obj)

    # Filter and convert attributes
    for key, value in obj_dict.items():
        # Skip private attributes (starting with _)
        if key.startswith('_'):
            continue

        # Convert Enum values to their string representation
        if isinstance(value, Enum):
            d[key] = value.value
        else:
            d[key] = value

    return d


def unserialize_object(d, debug: bool = False):
    """
    Unserialize object from dictionary.

    Args:
        d: Dictionary with __classname__ and object attributes
        debug: Enable debug output

    Returns:
        Reconstructed object instance

    Raises:
        ValueError: If __classname__ refers to unknown class
    """
    logger.debug(f"unserialize_object: d={d}")

    # Remove __classname__ key
    clsname = d.pop("__classname__", None)
    logger.debug(f"clsname: {clsname}")

    if clsname:
        # Use auto-registered class
        cls = YAMLObjectBase.get_class(clsname)

        if cls is None:
            raise ValueError(
                f"Unknown class '{clsname}'. "
                f"Available classes: {list(classes.keys())}"
            )

        # Create instance without calling __init__
        obj = cls.__new__(cls)

        # Set attributes (lowercase keys for compatibility)
        for key, value in d.items():
            logger.debug(f"key={key}, value={value} type={type(value)}")
            # Recursively deserialize nested objects
            deserialized_value = _deserialize_value(value)
            setattr(obj, key.lower(), deserialized_value)

        logger.debug(f"obj={obj}")

        return obj
    else:
        logger.debug(f"no classname: {d}")
        return d


def _deserialize_value(value):
    """
    Recursively deserialize a value that may contain nested objects.

    Args:
        value: Value to deserialize (can be dict, list, or primitive)

    Returns:
        Deserialized value with nested objects converted to class instances
    """
    if isinstance(value, dict):
        # Check if it's a serialized object
        if "__classname__" in value:
            # Make a copy to avoid modifying the original
            value_copy = value.copy()
            return unserialize_object(value_copy)
        else:
            # Regular dict - recursively process values
            return {k: _deserialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        # Recursively process list items
        return [_deserialize_value(item) for item in value]
    else:
        # Primitive value - return as is
        return value
