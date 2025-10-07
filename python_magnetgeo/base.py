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
from pathlib import Path

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
        # Get absolute path
        yaml_path = Path(filename).resolve()
        
        if debug:
            print(f"{cls.__name__}.from_yaml: Loading from {yaml_path}")
        
        # Load using standard mechanism
        instance = loadYaml(cls.__name__, str(yaml_path), cls, debug)
        
        # Store directory for nested file resolution
        # This is used by _load_nested_* methods
        instance._basedir = str(yaml_path.parent)
        
        if debug:
            print(f"SerializableMixin.load_from_yaml: Loading {cls.__name__} from {filename}: Set _basedir to {instance._basedir}", flush=True)
        
        return instance

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
    # Class registry - shared across all subclasses
    _class_registry = {}

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register YAML constructors for all subclasses.
        
        This is called whenever a class inherits from YAMLObjectBase.
        """
        super().__init_subclass__(**kwargs)
        
        # Register the class by its name
        class_name = cls.__name__
        cls._class_registry[class_name] = cls
        
        # Also register by yaml_tag if it exists
        if hasattr(cls, 'yaml_tag') and cls.yaml_tag:
            cls._class_registry[cls.yaml_tag] = cls
            
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
        import os
        if os.getenv('SPHINX_BUILD') != '1':
            print(f"Auto-registered YAML constructor and representer for {cls.__name__}")

    @classmethod
    def get_class(cls, name: str):
        """
        Get a registered class by name.
        
        Args:
            name: Class name or yaml_tag
            
        Returns:
            The class object, or None if not found
            
        Example:
            >>> Ring_class = YAMLObjectBase.get_class('Ring')
            >>> ring = Ring_class.from_dict(data)
        """
        return cls._class_registry.get(name)
    
    @classmethod
    def get_all_classes(cls):
        """
        Get all registered classes.
        
        Returns:
            Dictionary of {name: class} for all registered classes
        """
        return cls._class_registry.copy()

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

    @classmethod
    def _load_nested_list(cls, data, object_class, debug=False):
        """
        Generic loader for lists of nested objects.
        
        Handles three input formats:
        1. String: loads from file "{string}.yaml"
        2. Dict: creates object from dictionary
        3. Object: returns as-is (already instantiated)
        
        Args:
            data: List of strings/dicts/objects, or None
            object_class: The class to instantiate (e.g., Helix) OR tuple/list of classes to try
            debug: Enable debug output
            
        Returns:
            List of instantiated objects
            
        Example:
            helices = cls._load_nested_list(data, Helix, debug)
            leads = cls._load_nested_list(data, (InnerCurrentLead, OuterCurrentLead), debug)
        """
        if data is None:
            return []
        
        if not isinstance(data, list):
            raise TypeError(
                f"Expected list for nested objects, got {type(data).__name__}"
            )
        
        # Normalize object_class to tuple
        classes_to_try = (object_class,) if not isinstance(object_class, (list, tuple)) else tuple(object_class)
        
        objects = []
        
        for i, item in enumerate(data):
            if isinstance(item, str):
                # String reference → load from file
                if debug:
                    print(f"Loading object[{i}] from file: {item}")
                from .utils import getObject
                filename = f"{data}.yaml"
                
                # Check if path is absolute
                path_obj = Path(filename)
                
                if path_obj.is_absolute():
                    # Absolute path - use as-is
                    resolved_path = filename
                else:
                    # Relative path - resolve relative to parent's basedir
                    basedir = getattr(cls, '_basedir', None) if hasattr(cls, '_basedir') else None
                    
                    if basedir:
                        resolved_path = str(Path(basedir) / filename)
                    else:
                        # No basedir - use relative to current directory
                        resolved_path = filename
                
                if debug:
                    print(f"  Loading nested {object_class.__name__} from {resolved_path}")
                obj = getObject(filename)
                objects.append(obj)
                
            elif isinstance(item, dict):
                # Inline dictionary → try each class until one works
                if debug:
                    print(f"Creating object[{i}] from inline dict")
                
                obj = None
                last_error = None
                
                for candidate_class in classes_to_try:
                    try:
                        obj = candidate_class.from_dict(item, debug=debug)
                        break
                    except (KeyError, TypeError, ValueError) as e:
                        last_error = e
                        continue
                
                if obj is None:
                    class_names = [c.__name__ for c in classes_to_try]
                    raise TypeError(
                        f"Could not create object at index {i} using any of {class_names}. "
                        f"Last error: {last_error}"
                    )
                
                objects.append(obj)
                
            elif item is None:
                # Skip None values
                if debug:
                    print(f"Skipping None value at index {i}")
                continue
                
            else:
                # Already instantiated object - verify it's one of the expected types
                if not any(isinstance(item, cls) for cls in classes_to_try):
                    class_names = [c.__name__ for c in classes_to_try]
                    raise TypeError(
                        f"Expected one of {class_names}, str, or dict, "
                        f"got {type(item).__name__} at index {i}"
                    )
                objects.append(item)
        
        return objects

    @classmethod
    def _load_nested_single(cls, data, object_class, debug=False):
        """
        Generic loader for single nested object.
        
        Handles three input formats:
        1. String: loads from file "{string}.yaml"
        2. Dict: creates object from dictionary
        3. Object: returns as-is (already instantiated)
        4. None: returns None
        
        Args:
            data: String/dict/object, or None
            object_class: The class to instantiate OR tuple/list of classes to try
            debug: Enable debug output
            
        Returns:
            Instantiated object or None
            
        Example:
            modelaxi = cls._load_nested_single(data, ModelAxi, debug)
            lead = cls._load_nested_single(data, (InnerCurrentLead, OuterCurrentLead), debug)
        """
        if data is None:
            return None
        
        # Normalize object_class to tuple
        classes_to_try = (object_class,) if not isinstance(object_class, (list, tuple)) else tuple(object_class)
        
        if isinstance(data, str):
            # String reference → load from file
            if debug:
                print(f"Loading object from file: {data}")
            from .utils import getObject
            
            filename = f"{data}.yaml"
            # Check if path is absolute
            path_obj = Path(filename)
            
            if path_obj.is_absolute():
                # Absolute path - use as-is
                resolved_path = filename
            else:
                # Relative path - resolve relative to parent's basedir
                basedir = getattr(cls, '_basedir', None) if hasattr(cls, '_basedir') else None
                
                if basedir:
                    resolved_path = str(Path(basedir) / filename)
                else:
                    # No basedir - use relative to current directory
                    resolved_path = filename
            
            if debug:
                print(f"  Loading nested {object_class.__name__} from {resolved_path}")
            return getObject(filename)
            
        elif isinstance(data, dict):
            # Inline dictionary → try each class until one works
            if debug:
                print(f"Creating object from inline dict")
            
            last_error = None
            
            for candidate_class in classes_to_try:
                try:
                    return candidate_class.from_dict(data, debug=debug)
                except (KeyError, TypeError, ValueError) as e:
                    last_error = e
                    continue
            
            # If we get here, none of the classes worked
            class_names = [c.__name__ for c in classes_to_try]
            raise TypeError(
                f"Could not create object using any of {class_names}. "
                f"Last error: {last_error}"
            )
            
        else:
            # Already instantiated - verify it's one of the expected types
            if not any(isinstance(data, cls) for cls in classes_to_try):
                class_names = [c.__name__ for c in classes_to_try]
                raise TypeError(
                    f"Expected one of {class_names}, str, dict, or None, "
                    f"got {type(data).__name__}"
                )
            return data
