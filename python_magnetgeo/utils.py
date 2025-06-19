import os
import yaml


def load(comment: str, objects, supported_types: list, dict_objects: dict):
    """
    load objets from yaml files into a list

    otype:
    objects:

    return targets
    """
    
    def check_type(object, lTypes):
        for item in lTypes:
            if isinstance(object, item):
                return True
        return False
    
    targets = []
    if isinstance(objects, str):
        YAMLFile = os.path.join(f"{objects}.yaml")
        with open(YAMLFile, "r") as istream:
            data, otype  = yaml.load(istream, Loader=yaml.FullLoader)
            Object = dict_objects[otype](data)
        targets = Object

    elif isinstance(objects, list):
        for mname in objects:
            if isinstance(mname, str):
                YAMLFile = os.path.join(f"{mname}.yaml")
                with open(YAMLFile, "r") as istream:
                    data, otype = yaml.load(istream, Loader=yaml.FullLoader)
                    Object = dict_objects[otype](data)
                    targets.append(Object)
            elif check_type(mname, supported_types[1:]):
                targets.append(mname)
                
    elif isinstance(objects, dict):
        for key, value in objects.items():
            if check_type(value, supported_types[1:]):
                targets.append(value)
            elif isinstance(value, str):
                YAMLFile = os.path.join(f"{value}.yaml")
                with open(YAMLFile, "r") as istream:
                    data, otype = yaml.load(istream, Loader=yaml.FullLoader)
                    Object = dict_objects[otype](data)
                    targets.append(Object)

            elif isinstance(value, list):
                for mname in value:
                    if check_type(mname, supported_types[1:]):
                        targets.append(value)
                    elif isinstance(mname, str):
                        YAMLFile = os.path.join(f"{mname}.yaml")
                        with open(YAMLFile, "r") as istream:
                            data, otype = yaml.load(istream, Loader=yaml.FullLoader)
                            Object = dict_objects[otype](data)
                            targets.append(Object)
            else:
                raise Exception(
                    f"{comment}: unsupported type {type(value)}"
                )
    else:
        raise Exception(f"{comment}: unsupported type {type(objects)}")

    return targets

