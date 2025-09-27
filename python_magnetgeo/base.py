#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Base classes for python_magnetgeo to eliminate code duplication.
"""

import json
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, TypeVar

# Type variable for proper type hinting in return types
T = TypeVar('T', bound='SerializableMixin')

class SerializableMixin:
    """
    Mixin providing common serialization functionality.
    
    This eliminates duplicate serialization code across all geometry classes.
    """
    
    def dump(self, filename: Optional[str] = None) -> None:
        """
        Dump object to YAML file.
        
        Args:
            filename: Optional custom filename. If None, uses object name.
        """
        from .utils import writeYaml
        
        # Use the class name for writeYaml's comment parameter
        class_name = self.__class__.__name__
        writeYaml(class_name, self)

    def to_json(self) -> str:
        """
        Convert object to JSON string.
        
        Returns:
            JSON string representation of the object
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
        
        Args:
            filename: Optional custom filename. If None, uses object name.
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
        
        Note: Using 'load_from_yaml' instead of 'from_yaml' to avoid 
        conflicts with yaml.YAMLObject.from_yaml()
        
        Args:
            filename: Path to YAML file
            debug: Enable debug output
            
        Returns:
            Instance of the class loaded from YAML
        """
        from .utils import loadYaml
        if debug:
            print(f"SerializableMixin.load_from_yaml: Loading {cls.__name__} from {filename}", flush=True)
        return loadYaml(cls.__name__, filename, cls, debug)

    @classmethod  
    def load_from_json(cls: Type[T], filename: str, debug: bool = False) -> T:
        """
        Load object from JSON file.
        
        Note: Using 'load_from_json' instead of 'from_json' to avoid 
        potential conflicts.
        
        Args:
            filename: Path to JSON file  
            debug: Enable debug output
            
        Returns:
            Instance of the class loaded from JSON
        """
        from .utils import loadJson
        return loadJson(cls.__name__, filename, debug)

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], values: Dict[str, Any], debug: bool = False) -> T:
        """
        Create instance from dictionary.
        
        This method must be implemented by each subclass.
        
        Args:
            values: Dictionary containing object data
            debug: Enable debug output
            
        Returns:
            New instance of the class
        """
        raise NotImplementedError(f"{cls.__name__} must implement from_dict method")


class YAMLObjectBase(SerializableMixin):
    """
    Base class for all YAML serializable geometry objects.
    
    This class automatically handles YAML constructor registration and provides
    serialization functionality without inheriting from yaml.YAMLObject
    (which causes conflicts with the constructor registration).
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
            data = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
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

