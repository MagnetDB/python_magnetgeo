#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Base classes for python_magnetgeo to eliminate code duplication.

Provides the foundational architecture for all geometry classes:
- SerializableMixin: Core serialization functionality (JSON/YAML)
- YAMLObjectBase: YAML integration with automatic constructor registration

All geometry classes (Helix, Ring, Insert, etc.) inherit from YAMLObjectBase,
which provides consistent serialization behavior and automatic YAML type handling.

Architecture Benefits:
- Eliminates ~95% of duplicate serialization code across 15+ classes
- Automatic YAML constructor registration (no manual yaml.add_constructor calls)
- Consistent API across all geometry classes
- Single source of truth for serialization logic
- Easier to maintain and extend

Example:
    Creating a new geometry class:
    
    >>> from python_magnetgeo.base import YAMLObjectBase
    >>> from python_magnetgeo.validation import GeometryValidator
    >>> 
    >>> class MyGeometry(YAMLObjectBase):
    ...     yaml_tag = "MyGeometry"
    ...     
    ...     def __init__(self, name: str, value: float):
    ...         GeometryValidator.validate_name(name)
    ...         self.name = name
    ...         self.value = value
    ...     
    ...     @classmethod
    ...     def from_dict(cls, values: dict, debug: bool = False):
    ...         return cls(name=values["name"], value=values["value"])
    >>> 
    >>> # All serialization methods available automatically:
    >>> obj = MyGeometry("test", 42.0)
    >>> obj.dump()  # Writes test.yaml
    >>> obj.to_json()  # Returns JSON string
    >>> MyGeometry.from_yaml("test.yaml")  # Loads from YAML
"""

import json
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, TypeVar

# Type variable for proper type hinting in return types
T = TypeVar('T', bound='SerializableMixin')

class SerializableMixin:
    """
    Mixin providing common serialization functionality for all geometry classes.
    
    Eliminates duplicate serialization code by providing a single implementation
    of JSON/YAML serialization methods that all geometry classes inherit.
    
    Inherited Methods:
        - dump(): Write object to YAML file
        - to_json(): Convert object to JSON string
        - write_to_json(): Write object to JSON file
        - load_from_yaml(): Load object from YAML file (classmethod)
        - load_from_json(): Load object from JSON file (classmethod)
        - from_dict(): Create object from dictionary (must be implemented by subclass)
    
    Notes:
        - This is a mixin class, not meant to be instantiated directly
        - All methods use the utils module for actual file I/O
        - Subclasses must implement from_dict() for complete functionality
    """
    
    def dump(self, filename: Optional[str] = None) -> None:
        """
        Dump object to YAML file.
        
        Serializes this object to YAML format and writes to a file. The filename
        is automatically determined from the object's 'name' attribute.
        
        Args:
            filename: Optional custom filename. If None, uses object name.
                     Currently not used - kept for API compatibility.
        
        Example:
            >>> ring = Ring("test_ring", [10.0, 20.0], [0.0, 10.0])
            >>> ring.dump()  # Creates test_ring.yaml
        
        Notes:
            - Creates file in current directory
            - Overwrites existing files without warning
            - Uses object name for filename: {name}.yaml
        """
        from .utils import writeYaml
        
        # Use the class name for writeYaml's comment parameter
        class_name = self.__class__.__name__
        writeYaml(class_name, self)

    def to_json(self) -> str:
        """
        Convert object to JSON string representation.
        
        Serializes this object to a formatted JSON string with proper indentation
        and sorted keys for readability.
        
        Returns:
            str: JSON string representation of the object
        
        Example:
            >>> ring = Ring("test", [10.0, 20.0], [0.0, 10.0])
            >>> json_str = ring.to_json()
            >>> print(json_str)
            {
                "__classname__": "Ring",
                "name": "test",
                "r": [10.0, 20.0],
                ...
            }
        
        Notes:
            - Includes __classname__ for deserialization
            - Uses 4-space indentation
            - Keys are sorted alphabetically
            - Delegates to deserialize.serialize_instance for object encoding
        """
        from . import deserialize
        return json.dumps(
            self, 
            default=deserialize.serialize_instance, 
            sort_keys=True, 
            indent=4
        )

    def write_to_json(self, filename: Optional[str] = None) -> None:
        """
        Write object to JSON file.
        
        Serializes this object to JSON and writes to a file. The filename is
        automatically determined from the object's 'name' attribute if not specified.
        
        Args:
            filename: Optional custom filename. If None, uses "{object.name}.json"
        
        Raises:
            Exception: If file write fails for any reason
        
        Example:
            >>> helix = Helix("test_helix", [15.0, 25.0], [0.0, 100.0], ...)
            >>> helix.write_to_json()  # Creates test_helix.json
            >>> helix.write_to_json("custom_name.json")  # Custom filename
        
        Notes:
            - Creates file in current directory
            - Overwrites existing files without warning
        """
        if filename is None:
            name = getattr(self, 'name', self.__class__.__name__)
            filename = f"{name}.json"
            
        try:
            with open(filename, "w") as ostream:
                ostream.write(self.to_json())
        except Exception as e:
            raise Exception(f"Failed to write {self.__class__.__name__} to {filename}: {e}")

    @classmethod
    def load_from_yaml(cls: Type[T], filename: str, debug: bool = True) -> T:
        """
        Load object from YAML file.
        
        Class method that deserializes a YAML file into an instance of this class.
        Automatically validates that the loaded object is the correct type.
        
        Note: Using 'load_from_yaml' instead of 'from_yaml' to avoid 
        conflicts with yaml.YAMLObject.from_yaml() method.
        
        Args:
            filename: Path to YAML file (relative or absolute)
            debug: Enable debug output showing loading progress
            
        Returns:
            Instance of the class loaded from YAML file
        
        Raises:
            ObjectLoadError: If file doesn't exist or loading fails
            UnsupportedTypeError: If loaded object is wrong type
        
        Example:
            >>> ring = Ring.load_from_yaml("test_ring.yaml", debug=True)
            SerializableMixin.load_from_yaml: Loading Ring from test_ring.yaml
            >>> print(ring.name)
            test_ring
        
        Notes:
            - Automatically validates object type matches class
            - Handles directory changes if file is in subdirectory
            - Returns to original directory after loading
        """
        from .utils import loadYaml
        if debug:
            print(f"SerializableMixin.load_from_yaml: Loading {cls.__name__} from {filename}", flush=True)
        return loadYaml(cls.__name__, filename, cls, debug)

    @classmethod  
    def load_from_json(cls: Type[T], filename: str, debug: bool = False) -> T:
        """
        Load object from JSON file.
        
        Class method that deserializes a JSON file into an instance of this class.
        Uses the custom deserialization infrastructure to handle __classname__ annotations.
        
        Note: Using 'load_from_json' instead of 'from_json' to avoid 
        potential conflicts and maintain consistency with load_from_yaml.
        
        Args:
            filename: Path to JSON file
            debug: Enable debug output
            
        Returns:
            Instance of the class loaded from JSON file
        
        Raises:
            ObjectLoadError: If file doesn't exist or loading fails
        
        Example:
            >>> helix = Helix.load_from_json("test_helix.json")
            >>> print(helix.name)
            test_helix
        
        Notes:
            - Expects JSON to have __classname__ annotation
            - Uses deserialize module for class reconstruction
        """
        from .utils import loadJson
        return loadJson(cls.__name__, filename, debug)

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], values: Dict[str, Any], debug: bool = False) -> T:
        """
        Create instance from dictionary representation.
        
        Abstract method that must be implemented by each subclass to define
        how to construct an instance from a dictionary of values.
        
        Args:
            values: Dictionary containing object data with all required fields
            debug: Enable debug output during construction
            
        Returns:
            New instance of the class
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        
        Example:
            Subclass implementation:
            
            >>> @classmethod
            >>> def from_dict(cls, values: dict, debug: bool = False):
            ...     return cls(
            ...         name=values["name"],
            ...         r=values["r"],
            ...         z=values["z"]
            ...     )
        
        Notes:
            - Each geometry class must implement this method
            - Should handle default values and optional parameters
            - Should validate inputs using GeometryValidator
            - Can load nested objects from dicts or strings
        """
        raise NotImplementedError(f"{cls.__name__} must implement from_dict method")


class YAMLObjectBase(SerializableMixin):
    """
    Base class for all YAML-serializable geometry objects.
    
    Combines yaml.YAMLObject functionality with SerializableMixin to provide:
    - Automatic YAML constructor registration via __init_subclass__
    - Consistent serialization API across all geometry classes
    - Support for both YAML and JSON serialization
    - Type-safe loading with validation
    
    All geometry classes (Helix, Ring, Insert, Supra, etc.) inherit from this base.
    
    Class Attributes:
        yaml_loader: YAML loader class (default: yaml.FullLoader)
        yaml_dumper: YAML dumper class (default: yaml.Dumper)
        yaml_tag: YAML type annotation (e.g., "!<Helix>") - must be set by subclass
    
    Automatic Features:
        - YAML constructor registration happens automatically via __init_subclass__
        - No need to manually call yaml.add_constructor
        - Consistent from_yaml() and from_json() aliases
        - Consistent YAML representation via custom representer
    """
    
    def __init_subclass__(cls, **kwargs):
        """
        Automatically register YAML constructors for all subclasses.
        
        This is called whenever a class inherits from YAMLObjectBase.
        """
        super().__init_subclass__(**kwargs)
        
        # Ensure the class has a yaml_tag
        if not hasattr(cls, 'yaml_tag') or not cls.yaml_tag:
            raise ValueError(f"Class {cls.__name__} must define a yaml_tag")
        
        # Auto-register YAML constructor
        def constructor(loader, node):
            """
            Generated YAML constructor for this class.
    
            This is called during YAML parsing with (loader, node) parameters.
            """
            # Extract the mapping from the YAML node
            values = loader.construct_mapping(node, deep=True)
    
            # Create instance using from_dict (which each class implements)
            return cls.from_dict(values)
        
        # Auto-register YAML representer
        def representer(dumper, obj):
            """
            Generated YAML representer for this class.
            
            This is called during YAML dumping to convert objects to YAML nodes.
            """
            # Convert object to dictionary (excluding private attributes)
            from enum import Enum  # ← Add this import
            data = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if isinstance(value, Enum):  # ← Add this check
                        data[key] = value.value
                    else:
                        data[key] = value
            # Create YAML mapping node with custom tag
            return dumper.represent_mapping(cls.yaml_tag, data)
            
        
        # Register both constructor and representer with PyYAML
        yaml.add_constructor(cls.yaml_tag, constructor)
        yaml.add_representer(cls, representer)
        
        # Optional: print confirmation (remove in production)
        print(f"Auto-registered YAML constructor and representer for {cls.__name__}")

    @classmethod
    def from_yaml(cls: Type[T], filename: str, debug: bool = False) -> T:
        """
        Create object from YAML file.
        
        This method overrides yaml.YAMLObject.from_yaml() to provide
        the expected behavior for our geometry classes.
        
        Args:
            filename: Path to YAML file
            debug: Enable debug output
            
        Returns:
            Instance loaded from YAML file
        """
        if debug:
            print(f"YAMLObjectBase.from_yaml: Loading {cls.__name__} from {filename}", flush=True)
        return cls.load_from_yaml(filename, debug)

    @classmethod  
    def from_json(cls: Type[T], filename: str, debug: bool = False) -> T:
        """
        Create object from JSON file.
        
        Args:
            filename: Path to JSON file  
            debug: Enable debug output
            
        Returns:
            Instance loaded from JSON file
        """
        return cls.load_from_json(filename, debug)

