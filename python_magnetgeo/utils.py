from typing import Union, List, Dict, Callable, Any, Type, Optional
from pathlib import Path
import yaml
import os

class ObjectLoadError(Exception):
    """Raised when object loading fails"""
    pass

class UnsupportedTypeError(Exception):
    """Raised when object type is not supported"""
    pass

def load_yaml_object(filename: str, expected_type: Type = None) -> Any:
    """
    Load a single YAML object - compatible replacement for loadYaml.
    
    Args:
        filename: YAML file path
        expected_type: Expected object type for validation
        
    Returns:
        Loaded and updated object
    """
    cwd = os.getcwd()
    basedir, basename = os.path.split(filename)
    
    if basedir and basedir != ".":
        os.chdir(basedir)
    
    try:
        with open(basename, 'r') as f:
            obj = yaml.load(f, Loader=yaml.FullLoader)
        
        # Type validation if expected_type provided
        if expected_type and not isinstance(obj, expected_type):
            raise UnsupportedTypeError(f"Expected {expected_type.__name__}, got {type(obj).__name__}")
        
        # Auto-update if supported
        if hasattr(obj, 'update'):
            obj.update()
            
        return obj
        
    except (IOError, yaml.YAMLError) as e:
        raise ObjectLoadError(f"Failed to load YAML from {filename}: {e}")
    finally:
        if basedir and basedir != ".":
            os.chdir(cwd)

def load_objects(items: Union[str, List[str], Dict[str, str]], 
                loader_registry: Dict[str, Callable]) -> List[Any]:
    """
    Load objects from YAML files or return existing objects.
    Compatible replacement for loadList.
    
    Args:
        items: String filename, list of strings/objects, or dict mapping names to filenames
        loader_registry: Dict mapping class names to their from_dict constructors
        
    Returns:
        List of loaded objects
        
    Raises:
        ObjectLoadError: When file loading fails
        UnsupportedTypeError: When object type is not supported
    """
    if isinstance(items, str):
        # Single file case - return single object for compatibility
        filepath = f"{items}.yaml"
        obj = load_yaml_object(filepath)
        return obj  # Return object directly like old loadList for single string
    
    elif isinstance(items, list):
        # List case - mix of strings (filenames) and objects
        results = []
        for item in items:
            if isinstance(item, str):
                filepath = f"{item}.yaml"
                obj = load_yaml_object(filepath)
                results.append(obj)
            else:
                # Already an object, add directly
                results.append(item)
        return results
    
    elif isinstance(items, dict):
        # Dict case - values are filenames or nested lists
        results = []
        for key, value in items.items():
            if isinstance(value, str):
                filepath = f"{value}.yaml"
                obj = load_yaml_object(filepath)
                results.append(obj)
            elif isinstance(value, list):
                # Recursively handle nested lists
                nested_results = load_objects(value, loader_registry)
                results.extend(nested_results)
            else:
                # Already an object
                results.append(value)
        return results
    
    else:
        raise UnsupportedTypeError(f"Unsupported items type: {type(items)}")

# Compatibility function to maintain old API
def loadYaml(comment: str, filename: str, supported_type: Type = None, debug: bool = False) -> Any:
    """Backward compatibility wrapper for load_yaml_object"""
    if debug:
        print(f"Loading {comment} from {filename}")
    return load_yaml_object(filename, supported_type)

# Updated loadList with backward compatibility
def loadList(comment: str, objects, supported_types: list, dict_objects: dict):
    """
    Backward compatibility wrapper for load_objects.
    Maintains exact same behavior as original.
    """
    # For single string input, return the object directly (not in a list)
    if isinstance(objects, str):
        result = load_objects(objects, dict_objects)
        return result  # load_objects returns single object for string input
    
    # For other cases, return list as before
    return load_objects(objects, dict_objects)


def writeYaml(comment, object, debug: bool = True):        
    oname = comment
    if hasattr(object, "name"):
        oname = object.name

    try:
        with open(f"{oname}.yaml", "w") as ostream:
            yaml.dump(object, stream=ostream)
    except Exception as e:
        raise Exception(f"Failed to {comment} dump - {oname}.yaml - {e}")

def writeJson(comment, object, debug: bool = True):        
    oname = comment
    if hasattr(object, "name"):
        oname = object.name

    try:
        with open(f"{oname}.json", "w") as ostream:
            jsondata = object.to_json()
            ostream.write(str(jsondata))
    except Exception as e:
        raise Exception(f"Failed to {comment} dump - {oname}.json - {e}")
 


def loadJson(comment, filename, debug: bool = False):
    from . import deserialize
    import json
    cwd = os.getcwd()

    (basedir, basename) = os.path.split(filename)
    if debug:
        print(f"basedir={basedir}, basename={basename}, cwd={cwd}")

    if basedir and basedir != ".":
        os.chdir(basedir)
        if debug:
            print(f"cwd={cwd} -> {basedir}")

    try:
        if debug:
            print(f"loadJson: filename={basename}")
        with open(basename, "r") as istream:
            object = json.loads(
                istream.read(), object_hook=deserialize.unserialize_object
            )
    except Exception as e:
        raise Exception(f"Failed to load {comment} data {filename}: {e}")
    finally:
        if basedir and basedir != ".":
            os.chdir(cwd)
    
    if debug:
        print(f"loadJson: {comment} from {filename} done - {type(object)}")
    
    return object

def check_objects(objects, supported_type):
    """
    check if objects are of supported type
    Handle None and empty cases gracefully
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
    
def check_type(object, lTypes):
    for item in lTypes:
        if isinstance(object, item):
            return True
    return False
    
def loadObject(comment: str, data, supported_type, constructor):
    if isinstance(data, str):
        YAMLFile = os.path.join(f"{data}.yaml")
        Object = load_yaml_object(YAMLFile, expected_type=supported_type)
        """
        with open(YAMLFile, "r") as istream:
            Object  = yaml.load(istream, Loader=yaml.FullLoader)
            if check_objects([Object], supported_type):
                if hasattr(Object, 'update'):
                    Object.update()
            else:
                raise Exception(f"{comment}: {data}.yaml - unsupported type {type(Object)}")
        """
        return Object
    elif isinstance(data, supported_type):
        return data
    else:
        raise Exception(f"{comment}: unsupported type {type(data)}")


def getObject(filename: str):
    """
    Load an object from a YAML file and update it if necessary.
    """
    # import yaml
    from . import Helix
    from . import Insert
    from . import Bitter
    from . import Bitters
    from . import Supra
    from . import Supras
    from . import Screen
    from . import MSite

    Object = load_yaml_object(filename)
    return Object
    with open(filename, "r") as f:
        object = yaml.load(f, Loader=yaml.FullLoader)
        if hasattr(object, 'update'):
            object.update()
        return object