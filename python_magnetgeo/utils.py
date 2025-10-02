#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Utility functions for python_magnetgeo
Fixed version compatible with both original and refactored classes
"""

import os
import yaml
import json
from typing import Union, List, Dict, Callable, Any, Type, Optional
from pathlib import Path

class ObjectLoadError(Exception):
    """Raised when object loading fails"""
    pass

class UnsupportedTypeError(Exception):
    """Raised when object type is not supported"""
    pass

def writeYaml(comment: str, obj: Any, obj_class: Type = None, debug: bool = True):
    """
    Write object to YAML file.
    
    Args:
        comment: Comment/description for the operation
        obj: Object to write
        obj_class: Class type (for compatibility, not used)
        debug: Enable debug output
    """
    # Determine filename
    if hasattr(obj, "name") and obj.name:
        filename = f"{obj.name}.yaml"
    else:
        filename = f"{comment}.yaml"

    try:
        with open(filename, "w") as ostream:
            yaml.dump(obj, stream=ostream, default_flow_style=False)
        
        if debug:
            print(f"Written {comment} to {filename}")
            
    except Exception as e:
        raise Exception(f"Failed to {comment} dump - {filename} - {e}")

def writeJson(comment: str, obj: Any, debug: bool = True):
    """
    Write object to JSON file.
    
    Args:
        comment: Comment/description for the operation  
        obj: Object to write
        debug: Enable debug output
    """
    # Determine filename
    if hasattr(obj, "name") and obj.name:
        filename = f"{obj.name}.json"
    else:
        filename = f"{comment}.json"

    try:
        with open(filename, "w") as ostream:
            if hasattr(obj, 'to_json'):
                jsondata = obj.to_json()
            else:
                jsondata = json.dumps(obj, indent=4)
            ostream.write(str(jsondata))
            
        if debug:
            print(f"Written {comment} to {filename}")
            
    except Exception as e:
        raise Exception(f"Failed to {comment} dump - {filename} - {e}")

def loadYaml(comment: str, filename: str, supported_type: Type = None, debug: bool = False) -> Any:
    """
    Load object from YAML file.
    
    Args:
        comment: Comment/description for the operation
        filename: Path to YAML file
        supported_type: Expected object type for validation
        debug: Enable debug output
        
    Returns:
        Loaded object
        
    Raises:
        ObjectLoadError: When file loading fails
        UnsupportedTypeError: When object type is not supported
    """
    cwd = os.getcwd()
    
    # Handle path splitting
    basedir, basename = os.path.split(filename)
    
    if debug:
        print(f"utils.loadYaml: comment={comment}, filename={filename}")
        # print(f"  basedir={basedir}, basename={basename}, cwd={cwd}")

    # Change to target directory if needed
    if basedir and basedir != ".":
        os.chdir(basedir)
        if debug:
            print(f"  Changed directory: {cwd} -> {basedir}")

    try:
        # Load YAML file
        with open(basename, "r") as istream:
            obj = yaml.load(stream=istream, Loader=yaml.FullLoader)
        
        if debug:
            print(f"  Loaded object type: {type(obj)}")
            if hasattr(obj, 'name'):
                print(f"  Object name: {obj.name}")
        
        # Type validation if expected_type provided
        if supported_type and not isinstance(obj, supported_type):
            raise UnsupportedTypeError(
                f"{comment}: expected {supported_type.__name__}, got {type(obj).__name__}"
            )
        
        # Auto-update if object supports it
        if hasattr(obj, 'update'):
            if debug:
                print(f"  Calling update() on {type(obj).__name__}")
            obj.update()
            
        if debug:
            print(f"  loadYaml: {comment} from {filename} completed successfully")
            
        return obj
        
    except FileNotFoundError:
        raise ObjectLoadError(f"YAML file not found: {filename}")
    except yaml.YAMLError as e:
        raise ObjectLoadError(f"Failed to parse YAML in {filename}: {e}")
    except Exception as e:
        raise ObjectLoadError(f"Failed to load {comment} data from {filename}: {e}")
    finally:
        # Always restore original directory
        if basedir and basedir != ".":
            os.chdir(cwd)
            if debug:
                print(f"  Restored directory: {basedir} -> {cwd}")

def loadJson(comment: str, filename: str, debug: bool = False) -> Any:
    """
    Load object from JSON file.
    
    Args:
        comment: Comment/description for the operation
        filename: Path to JSON file
        debug: Enable debug output
        
    Returns:
        Loaded object
        
    Raises:
        ObjectLoadError: When file loading fails
    """
    from . import deserialize
    
    cwd = os.getcwd()
    basedir, basename = os.path.split(filename)
    
    if debug:
        print(f"loadJson: comment={comment}, filename={filename}")
        print(f"  basedir={basedir}, basename={basename}, cwd={cwd}")

    if basedir and basedir != ".":
        os.chdir(basedir)
        if debug:
            print(f"  Changed directory: {cwd} -> {basedir}")

    try:
        if debug:
            print(f"  Loading JSON from: {basename}")
            
        with open(basename, "r") as istream:
            obj = json.loads(
                istream.read(), 
                object_hook=deserialize.unserialize_object
            )
            
        if debug:
            print(f"  loadJson: {comment} from {filename} completed successfully")
            
        return obj
        
    except FileNotFoundError:
        raise ObjectLoadError(f"JSON file not found: {filename}")
    except json.JSONDecodeError as e:
        raise ObjectLoadError(f"Failed to parse JSON in {filename}: {e}")
    except Exception as e:
        raise ObjectLoadError(f"Failed to load {comment} data from {filename}: {e}")
    finally:
        if basedir and basedir != ".":
            os.chdir(cwd)

def check_objects(objects, supported_type):
    """
    Check if objects are of supported type.
    Handle None and empty cases gracefully.
    
    Args:
        objects: Object(s) to check
        supported_type: Expected type
        
    Returns:
        True if any object matches the supported type
    """
    if objects is None:
        return False
    if not objects:  # Empty list/dict/string
        return False
    
    if isinstance(objects, list):
        return any(isinstance(item, supported_type) for item in objects)
    elif isinstance(objects, dict):
        return any(isinstance(item, supported_type) for item in objects.values())
    else:
        return isinstance(objects, supported_type)

def check_type(obj, types_list):
    """
    Check if object is one of the types in the list.
    
    Args:
        obj: Object to check
        types_list: List of allowed types
        
    Returns:
        True if object matches any type in the list
    """
    for item in types_list:
        if isinstance(obj, item):
            return True
    return False

def loadObject(comment: str, data, supported_type, constructor):
    """
    Load object from string filename or return existing object.
    
    Args:
        comment: Description for error messages
        data: String filename or existing object
        supported_type: Expected object type
        constructor: Constructor function (for compatibility)
        
    Returns:
        Loaded or validated object
        
    Raises:
        ObjectLoadError: When loading fails
        UnsupportedTypeError: When object type is wrong
    """
    if isinstance(data, str):
        # Load from YAML file
        yaml_file = f"{data}.yaml"
        obj = loadYaml(comment, yaml_file, supported_type)
        return obj
        
    elif isinstance(data, supported_type):
        # Already the right type
        return data
        
    else:
        raise UnsupportedTypeError(f"{comment}: unsupported type {type(data)}")

def loadList(comment: str, objects, supported_types: list, dict_objects: dict):
    """
    Load list of objects from mixed string/object input.
    Maintains backward compatibility with original loadList.
    
    Args:
        comment: Description for error messages
        objects: String filename, list of strings/objects, or dict
        supported_types: List of supported types (first element is typically None)
        dict_objects: Dict mapping class names to their from_dict constructors
        
    Returns:
        List of loaded objects or single object for string input
    """
    # Extract actual supported types (skip None if present)
    actual_types = [t for t in supported_types if t is not None]
    
    if isinstance(objects, str):
        # Single file case - load and return object directly
        yaml_file = f"{objects}.yaml"
        obj = loadYaml(comment, yaml_file)
        
        # Validate type if we have supported types
        if actual_types and not any(isinstance(obj, t) for t in actual_types):
            type_names = [t.__name__ for t in actual_types]
            raise UnsupportedTypeError(
                f"{comment}: expected one of {type_names}, got {type(obj).__name__}"
            )
        
        return obj  # Return single object, not list
    
    elif isinstance(objects, list):
        # List case - mix of strings (filenames) and objects
        results = []
        for item in objects:
            if isinstance(item, str):
                yaml_file = f"{item}.yaml"
                obj = loadYaml(comment, yaml_file)
                results.append(obj)
            else:
                # Already an object, validate type if needed
                if actual_types and not any(isinstance(item, t) for t in actual_types):
                    type_names = [t.__name__ for t in actual_types]
                    raise UnsupportedTypeError(
                        f"{comment}: expected one of {type_names}, got {type(item).__name__}"
                    )
                results.append(item)
        return results
    
    elif isinstance(objects, dict):
        # Dict case - values are filenames or nested structures
        results = []
        for key, value in objects.items():
            if isinstance(value, str):
                yaml_file = f"{value}.yaml"
                obj = loadYaml(comment, yaml_file)
                results.append(obj)
            elif isinstance(value, list):
                # Recursively handle nested lists
                nested_results = loadList(f"{comment}.{key}", value, supported_types, dict_objects)
                if isinstance(nested_results, list):
                    results.extend(nested_results)
                else:
                    results.append(nested_results)
            else:
                # Already an object
                results.append(value)
        return results
    
    else:
        raise UnsupportedTypeError(f"{comment}: unsupported objects type: {type(objects)}")

def getObject(filename: str):
    """
    Load an object from a YAML file and update it if necessary.
    
    Args:
        filename: Path to YAML file
        
    Returns:
        Loaded and updated object
    """
    obj = loadYaml("getObject", filename)
    return obj

def flatten(S: list) -> list:
    from pandas.core.common import flatten as pd_flatten

    return list(pd_flatten(S))
