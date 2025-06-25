import os
import yaml

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
 

def loadYaml(comment, filename, supported_type=None, debug: bool = True):
    cwd = os.getcwd()

    (basedir, basename) = os.path.split(filename)
    if debug:
        print(f"basedir={basedir}, basename={basename}, cwd={cwd}")

    if basedir and basedir != ".":
        os.chdir(basedir)
        print(f"cwd={cwd} -> {basedir}")

    try:
        with open(basename, "r") as istream:
            object = yaml.load(stream=istream, Loader=yaml.FullLoader)
    except Exception as e:
        raise Exception(f"Failed to load {comment} data {filename}: {e}")
    finally:
        if basedir and basedir != ".":
            os.chdir(cwd)

    if debug:
        print(f"loadYaml: {comment} from {filename} done - {type(object)}")
    if supported_type:
        if not isinstance(object, supported_type):
            raise Exception(f"{comment}: unsupported type {type(object)}")    
    return object

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
    """
    for item in objects:
        if isinstance(item, supported_type):
            return True
    return False
    
def check_type(object, lTypes):
    for item in lTypes:
        if isinstance(object, item):
            return True
    return False
    
def loadObject(comment: str, data, supported_type, constructor):
    if isinstance(data, str):
        YAMLFile = os.path.join(f"{data}.yaml")
        with open(YAMLFile, "r") as istream:
            Object  = yaml.load(istream, Loader=yaml.FullLoader)
        return Object
    elif isinstance(data, supported_type):
        return data
    else:
        raise Exception(f"{comment}: unsupported type {type(data)}")

def loadList(comment: str, objects: list, supported_types: list, dict_objects: dict):
    """
    load objets from yaml files into a list

    otype:
    objects:

    return targets
    """
    
    targets = []
    if isinstance(objects, str):
        YAMLFile = os.path.join(f"{objects}.yaml")
        with open(YAMLFile, "r") as istream:
            Object = yaml.load(istream, Loader=yaml.FullLoader)
        targets = Object

    elif isinstance(objects, list):
        for mname in objects:
            if isinstance(mname, str):
                YAMLFile = os.path.join(f"{mname}.yaml")
                with open(YAMLFile, "r") as istream:
                    Object = yaml.load(istream, Loader=yaml.FullLoader)
                    if check_type(Object, supported_types[1:]):
                        targets.append(Object)
                        print(f"{comment}: {mname}.yaml - loaded {type(Object)}: {Object}")
                    else:
                        raise Exception(f"{comment}: {mname}.yaml - unsupported type {type(Object)}")
                    
            elif check_type(mname, supported_types[1:]):
                targets.append(mname)
                
    elif isinstance(objects, dict):
        for key, value in objects.items():
            if check_type(value, supported_types[1:]):
                targets.append(value)
            elif isinstance(value, str):
                YAMLFile = os.path.join(f"{value}.yaml")
                with open(YAMLFile, "r") as istream:
                    Object = yaml.load(istream, Loader=yaml.FullLoader)
                    targets.append(Object)

            elif isinstance(value, list):
                for mname in value:
                    if check_type(mname, supported_types[1:]):
                        targets.append(value)
                    elif isinstance(mname, str):
                        YAMLFile = os.path.join(f"{mname}.yaml")
                        with open(YAMLFile, "r") as istream:
                            Object = yaml.load(istream, Loader=yaml.FullLoader)
                            targets.append(Object)
            else:
                raise Exception(
                    f"{comment}: unsupported type {type(value)}"
                )
    else:
        raise Exception(f"{comment}: unsupported type {type(objects)}")

    return targets

