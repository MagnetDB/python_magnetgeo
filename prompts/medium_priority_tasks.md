# Medium Priority Tasks - Step-by-Step Implementation Guide

## Overview

These tasks improve code maintainability, reduce duplication, and enhance type safety without breaking existing functionality. They should be tackled after High Priority tasks are complete.

---

## Task 5: Consolidate Nested Object Loading into Base Class

### Current Problem

Multiple classes have duplicated nested object loading code:

**In Insert.py:**
```python
@classmethod  
def _load_nested_helices(cls, data, debug=False):
    if data is None:
        return []
    objects = []
    for item in data:
        if isinstance(item, str):
            from .utils import loadObject
            obj = loadObject("helix", item, Helix, Helix.from_yaml)
            objects.append(obj)
        elif isinstance(item, dict):
            objects.append(Helix.from_dict(item, debug=debug))
        else:
            objects.append(item)
    return objects

@classmethod  
def _load_nested_rings(cls, data, debug=False):
    # Nearly identical code, just different class
    ...
```

**In Bitter.py:**
```python
@classmethod  
def _load_nested_coolingslits(cls, coolingslits_data, debug=False):
    # Same pattern again
    ...

@classmethod  
def _load_nested_tierod(cls, tierod_data, debug=False):
    # Single object version of same pattern
    ...
```

**In Helix.py:**
```python
@classmethod  
def _load_nested_modelaxi(cls, modelaxi_data, debug=False):
    # Same pattern
    ...
```

### Proposed Solution

**Step 1: Add Generic Loaders to YAMLObjectBase**

Add to `python_magnetgeo/base.py`:

```python
class YAMLObjectBase(SerializableMixin, yaml.YAMLObject):
    """Base class for all YAML-serializable geometry objects."""
    
    # ... existing code ...
    
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
            object_class: The class to instantiate (e.g., Helix, Ring)
            debug: Enable debug output
            
        Returns:
            List of instantiated objects
            
        Example:
            helices = cls._load_nested_list(data, Helix, debug)
        """
        if data is None:
            return []
        
        if not isinstance(data, list):
            raise TypeError(
                f"Expected list for nested objects, got {type(data).__name__}"
            )
        
        objects = []
        class_name = object_class.__name__.lower()
        
        for i, item in enumerate(data):
            if isinstance(item, str):
                # String reference → load from file
                if debug:
                    print(f"Loading {object_class.__name__}[{i}] from file: {item}")
                from .utils import loadObject
                obj = loadObject(
                    class_name, 
                    item, 
                    object_class, 
                    object_class.from_yaml
                )
                objects.append(obj)
                
            elif isinstance(item, dict):
                # Inline dictionary → create from dict
                if debug:
                    print(f"Creating {object_class.__name__}[{i}] from inline dict")
                obj = object_class.from_dict(item, debug=debug)
                objects.append(obj)
                
            elif item is None:
                # Skip None values
                if debug:
                    print(f"Skipping None value at index {i}")
                continue
                
            else:
                # Already instantiated object
                if not isinstance(item, object_class):
                    raise TypeError(
                        f"Expected {object_class.__name__}, str, or dict, "
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
            object_class: The class to instantiate
            debug: Enable debug output
            
        Returns:
            Instantiated object or None
            
        Example:
            modelaxi = cls._load_nested_single(data, ModelAxi, debug)
        """
        if data is None:
            return None
        
        if isinstance(data, str):
            # String reference → load from file
            if debug:
                print(f"Loading {object_class.__name__} from file: {data}")
            from .utils import loadObject
            return loadObject(
                object_class.__name__.lower(),
                data,
                object_class,
                object_class.from_yaml
            )
            
        elif isinstance(data, dict):
            # Inline dictionary → create from dict
            if debug:
                print(f"Creating {object_class.__name__} from inline dict")
            return object_class.from_dict(data, debug=debug)
            
        elif isinstance(data, object_class):
            # Already instantiated
            return data
            
        else:
            raise TypeError(
                f"Expected {object_class.__name__}, str, dict, or None, "
                f"got {type(data).__name__}"
            )
```

**Step 2: Refactor Insert.py**

Replace methods with generic loaders:

```python
# OLD - DELETE THESE:
@classmethod  
def _load_nested_helices(cls, data, debug=False):
    # ... 20+ lines of code ...

@classmethod  
def _load_nested_rings(cls, data, debug=False):
    # ... 20+ lines of code ...

@classmethod  
def _load_nested_currentleads(cls, data, debug=False):
    # ... 20+ lines of code ...

# NEW - USE GENERIC LOADERS:
@classmethod
def from_dict(cls, values: dict, debug: bool = False):
    """Create Insert from dictionary."""
    
    # Use inherited generic loaders
    helices = cls._load_nested_list(
        values.get('helices'), 
        Helix, 
        debug=debug
    )
    
    rings = cls._load_nested_list(
        values.get('rings'), 
        Ring, 
        debug=debug
    )
    
    # For currentleads, use getObject since they can be different types
    currentleads_data = values.get('currentleads', [])
    currentleads = []
    for lead in currentleads_data:
        if isinstance(lead, str):
            from .utils import getObject
            currentleads.append(getObject(f"{lead}.yaml"))
        else:
            currentleads.append(lead)
    
    probes = cls._load_nested_list(
        values.get('probes'), 
        Probe, 
        debug=debug
    )
    
    return cls(
        name=values["name"],
        helices=helices,
        rings=rings,
        currentleads=currentleads,
        hangles=values.get("hangles", []),
        rangles=values.get("rangles", []),
        innerbore=values.get("innerbore", 0),
        outerbore=values.get("outerbore", 0),
        probes=probes
    )
```

**Step 3: Refactor Bitter.py**

```python
# OLD - DELETE THESE:
@classmethod  
def _load_nested_modelaxi(cls, modelaxi_data, debug=False):
    # ... code ...

@classmethod  
def _load_nested_coolingslits(cls, coolingslits_data, debug=False):
    # ... code ...

@classmethod  
def _load_nested_tierod(cls, tierod_data, debug=False):
    # ... code ...

# NEW - USE GENERIC LOADERS:
@classmethod
def from_dict(cls, values: dict, debug: bool = False):
    """Create Bitter from dictionary."""
    
    modelaxi = cls._load_nested_single(
        values.get('modelaxi'),
        ModelAxi,
        debug=debug
    )
    
    coolingslits = cls._load_nested_list(
        values.get('coolingslits'),
        CoolingSlit,
        debug=debug
    )
    
    tierod = cls._load_nested_single(
        values.get('tierod'),
        Tierod,
        debug=debug
    )
    
    return cls(
        name=values["name"],
        r=values["r"],
        z=values["z"],
        odd=values["odd"],
        modelaxi=modelaxi,
        coolingslits=coolingslits,
        tierod=tierod,
        innerbore=values.get("innerbore", 0),
        outerbore=values.get("outerbore", 0)
    )
```

**Step 4: Refactor Helix.py**

```python
# Similar pattern - replace custom loaders with generic ones
@classmethod
def from_dict(cls, values: dict, debug: bool = False):
    """Create Helix from dictionary."""
    
    modelaxi = cls._load_nested_single(values.get('modelaxi'), ModelAxi, debug)
    model3d = cls._load_nested_single(values.get('model3d'), Model3D, debug)
    shape = cls._load_nested_single(values.get('shape'), Shape, debug)
    chamfers = cls._load_nested_list(values.get('chamfers'), Chamfer, debug)
    grooves = cls._load_nested_list(values.get('grooves'), Groove, debug)
    
    return cls(
        name=values["name"],
        r=values["r"],
        z=values["z"],
        cutwidth=values["cutwidth"],
        odd=values["odd"],
        dble=values["dble"],
        modelaxi=modelaxi,
        model3d=model3d,
        shape=shape,
        chamfers=chamfers,
        grooves=grooves
    )
```

**Step 5: Testing**

Create `tests/test_nested_loading.py`:

```python
import pytest
from python_magnetgeo import Insert, Helix, Ring, Bitter
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.coolingslit import CoolingSlit

def test_load_nested_list_from_dicts():
    """Test loading list of objects from inline dicts"""
    data = [
        {'name': 'H1', 'r': [10, 20], 'z': [0, 50], 'cutwidth': 0.2, 'odd': True, 'dble': False},
        {'name': 'H2', 'r': [25, 35], 'z': [0, 50], 'cutwidth': 0.2, 'odd': True, 'dble': False}
    ]
    
    helices = Insert._load_nested_list(data, Helix)
    
    assert len(helices) == 2
    assert all(isinstance(h, Helix) for h in helices)
    assert helices[0].name == 'H1'
    assert helices[1].name == 'H2'

def test_load_nested_single_from_dict():
    """Test loading single object from inline dict"""
    data = {'name': 'test_axi', 'h': 30.0, 'turns': [3.0], 'pitch': [10.0]}
    
    modelaxi = Bitter._load_nested_single(data, ModelAxi)
    
    assert isinstance(modelaxi, ModelAxi)
    assert modelaxi.name == 'test_axi'

def test_load_nested_list_none_handling():
    """Test that None input returns empty list"""
    result = Insert._load_nested_list(None, Helix)
    assert result == []

def test_load_nested_single_none_handling():
    """Test that None input returns None"""
    result = Bitter._load_nested_single(None, ModelAxi)
    assert result is None

def test_load_nested_list_invalid_type():
    """Test error on invalid input type"""
    with pytest.raises(TypeError, match="Expected list"):
        Insert._load_nested_list("not a list", Helix)

def test_load_nested_mixed_inputs():
    """Test loading with mix of dicts and objects"""
    h1_dict = {'name': 'H1', 'r': [10, 20], 'z': [0, 50], 'cutwidth': 0.2, 'odd': True, 'dble': False}
    h2_obj = Helix('H2', [25, 35], [0, 50], 0.2, True, False)
    
    data = [h1_dict, h2_obj]
    helices = Insert._load_nested_list(data, Helix)
    
    assert len(helices) == 2
    assert helices[0].name == 'H1'
    assert helices[1].name == 'H2'
```

### Benefits

- **Eliminates ~200+ lines** of duplicated code
- **Single source of truth** for nested object loading
- **Consistent behavior** across all classes
- **Easier to debug** and maintain
- **Better error messages** with type checking

### Estimated Time

- Implementation: 2-3 hours
- Testing: 1-2 hours
- **Total: 3-5 hours**

---

## Task 6: Add Auto-Registration for Class Registry

### Current Problem

In `deserialize.py`, classes must be manually registered:

```python
classes = {
    "Probe": Probe,
    "Shape": Shape,
    "ModelAxi": ModelAxi,
    "Model3D": Model3D,
    "Helix": Helix,
    "Ring": Ring,
    "InnerCurrentLead": InnerCurrentLead,
    "OuterCurrentLead": OuterCurrentLead,
    "Insert": Insert,
    "Bitter": Bitter,
    "Supra": Supra,
    "Screen": Screen,
    "Bitters": Bitters,
    "Supras": Supras,
    "MSite": MSite,
    "Contour2D": Contour2D,
    "Chamfer": Chamfer,
    "Groove": Groove,
    "Tierod": Tierod,
    "CoolingSlit": CoolingSlit,
}
```

**Problems:**
- Requires manual updates when adding new classes
- Easy to forget to register a class
- Prone to typos
- No compile-time checking

### Proposed Solution

**Step 1: Add Auto-Registration to YAMLObjectBase**

Update `python_magnetgeo/base.py`:

```python
class YAMLObjectBase(SerializableMixin, yaml.YAMLObject):
    """
    Base class for all YAML-serializable geometry objects.
    
    Automatically registers classes for deserialization.
    """
    
    # Class registry - shared across all subclasses
    _class_registry = {}
    
    def __init_subclass__(cls, **kwargs):
        """
        Automatically register subclasses when they're defined.
        
        This is called automatically when a class inherits from YAMLObjectBase.
        """
        super().__init_subclass__(**kwargs)
        
        # Register the class by its name
        class_name = cls.__name__
        cls._class_registry[class_name] = cls
        
        # Also register by yaml_tag if it exists
        if hasattr(cls, 'yaml_tag') and cls.yaml_tag:
            cls._class_registry[cls.yaml_tag] = cls
        
        # Register YAML constructor using yaml_tag
        if hasattr(cls, 'yaml_tag') and cls.yaml_tag:
            yaml.SafeLoader.add_constructor(
                f'!<{cls.yaml_tag}>',
                cls.from_yaml_constructor
            )
    
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
    def from_yaml_constructor(cls, loader, node):
        """
        YAML constructor called when loading objects.
        
        This is automatically registered for all subclasses.
        """
        # Get dictionary from YAML
        values = loader.construct_mapping(node, deep=True)
        
        # Create instance using from_dict
        return cls.from_dict(values, debug=False)
```

**Step 2: Update deserialize.py**

Replace hardcoded registry with dynamic lookup:

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides tools to un/serialize data from json
"""

from .base import YAMLObjectBase

# Import all classes to ensure they're registered
# (importing triggers __init_subclass__ which registers them)
from .Probe import Probe
from .Shape import Shape
from .ModelAxi import ModelAxi
from .Model3D import Model3D
from .Helix import Helix
from .Ring import Ring
from .InnerCurrentLead import InnerCurrentLead
from .OuterCurrentLead import OuterCurrentLead
from .Insert import Insert
from .Bitter import Bitter
from .Supra import Supra
from .Screen import Screen
from .MSite import MSite
from .Bitters import Bitters
from .Supras import Supras
from .Contour2D import Contour2D
from .Chamfer import Chamfer
from .Groove import Groove
from .tierod import Tierod
from .coolingslit import CoolingSlit

# Get class registry from base class
# This is automatically populated by __init_subclass__
classes = YAMLObjectBase.get_all_classes()


def serialize_instance(obj):
    """
    serialize_instance of an obj
    
    Handles Enum values by converting them to their string values.
    """
    from enum import Enum
    
    d = {"__classname__": type(obj).__name__}
    
    # Get object attributes
    obj_dict = vars(obj)
    
    # Convert any Enum values to their string representation
    for key, value in obj_dict.items():
        if isinstance(value, Enum):
            d[key] = value.value
        else:
            d[key] = value
    
    return d


def unserialize_object(d, debug: bool = True):
    """
    unserialize_instance of an obj
    """
    if debug:
        print(f"unserialize_object: d={d}", flush=True)

    # remove all __classname__ keys
    clsname = d.pop("__classname__", None)
    if debug:
        print(f"clsname: {clsname}", flush=True)
        
    if clsname:
        # Use auto-registered class
        cls = YAMLObjectBase.get_class(clsname)
        
        if cls is None:
            raise ValueError(
                f"Unknown class '{clsname}'. "
                f"Available classes: {list(classes.keys())}"
            )
        
        obj = cls.__new__(cls)  # Make instance without calling __init__
        for key, value in d.items():
            if debug:
                print(f"key={key}, value={value} type={type(value)}", flush=True)
            setattr(obj, key.lower(), value)
            
        if debug:
            print(f"obj={obj}", flush=True)
        return obj
    else:
        if debug:
            print(f"no classname: {d}", flush=True)
        return d
```

**Step 3: Add Verification Utilities**

Add to `python_magnetgeo/__init__.py`:

```python
def list_registered_classes():
    """
    List all registered geometry classes.
    
    Useful for debugging and documentation.
    
    Returns:
        Dictionary of {class_name: class_object}
    """
    from .base import YAMLObjectBase
    return YAMLObjectBase.get_all_classes()


def verify_class_registration():
    """
    Verify that all expected classes are registered.
    
    Raises:
        AssertionError: If expected classes are missing
    """
    from .base import YAMLObjectBase
    
    expected_classes = [
        'Insert', 'Helix', 'Ring', 'Bitter', 'Supra', 'Supras', 
        'Bitters', 'Screen', 'MSite', 'Probe', 'Shape', 'ModelAxi',
        'Model3D', 'InnerCurrentLead', 'OuterCurrentLead', 'Contour2D',
        'Chamfer', 'Groove', 'Tierod', 'CoolingSlit'
    ]
    
    registered = YAMLObjectBase.get_all_classes()
    missing = [cls for cls in expected_classes if cls not in registered]
    
    if missing:
        raise AssertionError(
            f"Missing registered classes: {missing}\n"
            f"Registered: {list(registered.keys())}"
        )
    
    return True
```

**Step 4: Testing**

Create `tests/test_auto_registration.py`:

```python
import pytest
from python_magnetgeo.base import YAMLObjectBase
from python_magnetgeo import (
    Insert, Helix, Ring, Bitter, Supra, Probe,
    list_registered_classes, verify_class_registration
)

def test_classes_auto_registered():
    """Test that classes are automatically registered"""
    registry = YAMLObjectBase.get_all_classes()
    
    # Check key classes are present
    assert 'Insert' in registry
    assert 'Helix' in registry
    assert 'Ring' in registry
    assert 'Bitter' in registry
    
    # Verify they're the correct classes
    assert registry['Insert'] is Insert
    assert registry['Helix'] is Helix

def test_get_class_by_name():
    """Test retrieving classes by name"""
    Ring_class = YAMLObjectBase.get_class('Ring')
    assert Ring_class is Ring
    
    # Can create instance
    ring = Ring_class(
        name="test",
        r=[10, 20, 30, 40],
        z=[0, 10]
    )
    assert isinstance(ring, Ring)

def test_list_registered_classes():
    """Test utility function"""
    classes = list_registered_classes()
    
    assert isinstance(classes, dict)
    assert len(classes) >= 15  # Should have at least 15 classes
    assert 'Insert' in classes

def test_verify_class_registration():
    """Test verification utility"""
    # Should not raise
    assert verify_class_registration() is True

def test_unknown_class_error():
    """Test error for unknown class"""
    from python_magnetgeo.deserialize import unserialize_object
    
    with pytest.raises(ValueError, match="Unknown class 'FakeClass'"):
        unserialize_object({'__classname__': 'FakeClass'}, debug=False)

def test_custom_class_auto_registers():
    """Test that custom classes auto-register"""
    
    class MyCustomGeometry(YAMLObjectBase):
        yaml_tag = "MyCustomGeometry"
        
        def __init__(self, name):
            self.name = name
        
        @classmethod
        def from_dict(cls, values, debug=False):
            return cls(values['name'])
    
    # Should be auto-registered
    registry = YAMLObjectBase.get_all_classes()
    assert 'MyCustomGeometry' in registry
    assert registry['MyCustomGeometry'] is MyCustomGeometry
```

### Benefits

- **No manual registration** - classes register themselves
- **Can't forget** to register new classes
- **No typos** in class names
- **Self-documenting** - can query what's registered
- **Extensible** - custom classes auto-register

### Estimated Time

- Implementation: 2-3 hours
- Testing: 1 hour
- **Total: 3-4 hours**

---

## Task 7: Improve Type Validation at Runtime

### Current Problem

Type hints are declared but not enforced at runtime:

```python
def __init__(self, name: str, r: List[float], z: List[float], ...):
    # No runtime check that r actually contains floats!
    # No runtime check that z is actually a list!
```

This can lead to subtle bugs when invalid data passes through.

### Proposed Solution

**Step 1: Add Runtime Type Validators**

Extend `python_magnetgeo/validation.py`:

```python
from typing import List, Any, get_origin, get_args
import inspect

class GeometryValidator:
    """Enhanced validation with runtime type checking"""
    
    # ... existing methods ...
    
    @staticmethod
    def validate_type(value: Any, expected_type: type, param_name: str) -> None:
        """
        Validate that value matches expected type at runtime.
        
        Supports:
        - Basic types: str, int, float, bool
        - List types: List[float], List[int]
        - Optional types: Optional[str]
        - Union types: Union[str, int]
        
        Args:
            value: Value to check
            expected_type: Expected type (can be type hint)
            param_name: Parameter name for error messages
            
        Raises:
            ValidationError: If type doesn't match
        """
        origin = get_origin(expected_type)
        args = get_args(expected_type)
        
        # Handle None for Optional types
        if value is None:
            if origin is not Union or type(None) not in args:
                raise ValidationError(
                    f"{param_name} cannot be None (expected {expected_type})"
                )
            return
        
        # Handle List[T]
        if origin is list:
            if not isinstance(value, list):
                raise ValidationError(
                    f"{param_name} must be a list, got {type(value).__name__}"
                )
            if args:  # Check element types
                expected_elem_type = args[0]
                for i, item in enumerate(value):
                    if not isinstance(item, expected_elem_type):
                        raise ValidationError(
                            f"{param_name}[{i}] must be {expected_elem_type.__name__}, "
                            f"got {type(item).__name__}"
                        )
        
        # Handle Union types
        elif origin is Union:
            if not any(isinstance(value, arg) for arg in args if arg is not type(None)):
                type_names = [arg.__name__ for arg in args if arg is not type(None)]
                raise ValidationError(
                    f"{param_name} must be one of {type_names}, "
                    f"got {type(value).__name__}"
                )
        
        # Handle basic types
        elif origin is None:
            if not isinstance(value, expected_type):
                raise ValidationError(
                    f"{param_name} must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    @staticmethod
    def validate_function_signature(func, kwargs: dict) -> None:
        """
        Validate that kwargs match function signature types.
        
        This can be used as a decorator or called manually.
        
        Args:
            func: Function to validate
            kwargs: Keyword arguments passed to function
            
        Raises:
            ValidationError: If any parameter has wrong type
        """
        sig = inspect.signature(func)
        
        for param_name, param in sig.parameters.items():
            if param_name in kwargs and param.annotation != inspect.Parameter.empty:
                value = kwargs[param_name]
                expected_type = param.annotation
                GeometryValidator.validate_type(value, expected_type, param_name)
    
    @staticmethod
    def validate_numeric_list_typed(
        values: Any,
        name: str,
        expected_length: int = None,
        allow_int: bool = True
    ) -> None:
        """
        Enhanced numeric list validation with type checking.
        
        Replaces validate_numeric_list with runtime type enforcement.
        """
        # First check it's a list
        if not isinstance(values, (list, tuple)):
            raise ValidationError(
                f"{name} must be a list or tuple, got {type(values).__name__}"
            )
        
        # Check length
        if expected_length and len(values) != expected_length:
            raise ValidationError(
                f"{name} must have exactly {expected_length} values, "
                f"got {len(values)}"
            )
        
        # Check each element is numeric
        allowed_types = (int, float) if allow_int else (float,)
        for i, val in enumerate(values):
            if not isinstance(val, allowed_types):
                raise ValidationError(
                    f"{name}[{i}] must be numeric, got {type(val).__name__}"
                )
```

**Step 2: Add Type-Checking Decorator**

```python
from functools import wraps

def validate_types(func):
    """
    Decorator to automatically validate parameter types at runtime.
    
    Reads type hints from function signature and validates all parameters.
    
    Usage:
        @validate_types
        def __init__(self, name: str, r: List[float], z: List[float]):
            # Types are automatically validated before this runs
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        # Validate each parameter
        for param_name, param in sig.parameters.items():
            if param_name == 'self' or param_name == 'cls':
                continue
                
            if param.annotation != inspect.Parameter.empty:
                value = bound.arguments.get(param_name)
                expected_type = param.annotation
                
                try:
                    GeometryValidator.validate_type(
                        value, 
                        expected_type, 
                        param_name
                    )
                except ValidationError as e:
                    # Add function context to error
                    raise ValidationError(
                        f"In {func.__name__}(): {e}"
                    ) from None
        
        return func(*args, **kwargs)
    
    return wrapper
```

**Step 3: Apply to Ring Class (Example)**

```python
from .validation import validate_types, GeometryValidator, ValidationError

class Ring(YAMLObjectBase):
    yaml_tag = "Ring"

    @validate_types  # <-- Add decorator for automatic type validation
    def __init__(
        self, 
        name: str, 
        r: List[float], 
        z: List[float],
        n: int = 0,
        angle: float = 0,
        bpside: bool = True,
        fillets: bool = False,
        cad: str = None
    ) -> None:
        """
        Initialize Ring object.
        
        Types are automatically validated by @validate_types decorator.
        """
        # Business logic validation (after type validation)
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, "r", expected_length=4)
        GeometryValidator.validate_ascending_order(r, "r")
        GeometryValidator.validate_numeric_list(z, "z", expected_length=2) 
        GeometryValidator.validate_ascending_order(z, "z")
        
        if r[0] < 0:
            raise ValidationError("Inner radius cannot be negative")        
        
        if n * angle > 360:
            raise ValidationError(
                f"Ring: {n} coolingslits total angular length "
                f"({n * angle}) cannot exceed 360 degrees"
            )
        
        # Set attributes
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.bpside = bpside
        self.fillets = fillets
        self.cad = cad or ''
```

**Step 4: Alternative - Explicit Validation**

For classes where decorator might be too magical:

```python
class Helix(YAMLObjectBase):
    yaml_tag = "Helix"

    def __init__(
        self,
        name: str,
        r: List[float],
        z: List[float],
        cutwidth: float,
        odd: bool,
        dble: bool,
        axi=None,
        model3d=None,
        shape=None,
        chamfers: List = None,
        grooves: List = None
    ):
        """Initialize Helix with explicit type validation."""
        
        # Explicit type validation
        GeometryValidator.validate_type(name, str, 'name')
        GeometryValidator.validate_type(r, List[float], 'r')
        GeometryValidator.validate_type(z, List[float], 'z')
        GeometryValidator.validate_type(cutwidth, float, 'cutwidth')
        GeometryValidator.validate_type(odd, bool, 'odd')
        GeometryValidator.validate_type(dble, bool, 'dble')
        
        # Business logic validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
        GeometryValidator.validate_ascending_order(r, 'r')
        
        # ... rest of initialization
```

**Step 5: Testing**

Create `tests/test_type_validation.py`:

```python
import pytest
from typing import List
from python_magnetgeo import Ring, Helix
from python_magnetgeo.validation import GeometryValidator, ValidationError

def test_validate_type_basic():
    """Test basic type validation"""
    # Valid cases
    GeometryValidator.validate_type("test", str, "name")
    GeometryValidator.validate_type(42, int, "count")
    GeometryValidator.validate_type(3.14, float, "radius")
    GeometryValidator.validate_type(True, bool, "flag")
    
    # Invalid cases
    with pytest.raises(ValidationError, match="name must be str"):
        GeometryValidator.validate_type(123, str, "name")

def test_validate_type_list():
    """Test list type validation"""
    # Valid
    GeometryValidator.validate_type([1.0, 2.0], List[float], "radii")
    GeometryValidator.validate_type([1, 2, 3], List[int], "counts")
    
    # Invalid - wrong container type
    with pytest.raises(ValidationError, match="radii must be a list"):
        GeometryValidator.validate_type((1.0, 2.0), List[float], "radii")
    
    # Invalid - wrong element type
    with pytest.raises(ValidationError, match=r"radii\[1\] must be float"):
        GeometryValidator.validate_type([1.0, "two"], List[float], "radii")

def test_ring_type_validation_success():
    """Test Ring with valid types"""
    ring = Ring(
        name="test_ring",
        r=[10.0, 20.0, 30.0, 40.0],  # List[float] ✓
        z=[0.0, 10.0],                # List[float] ✓
        n=5,                          # int ✓
        angle=45.0,                   # float ✓
        bpside=True,                  # bool ✓
        fillets=False                 # bool ✓
    )
    assert ring.name == "test_ring"

def test_ring_type_validation_failure_name():
    """Test Ring rejects non-string name"""
    with pytest.raises(ValidationError, match="name must be str"):
        Ring(
            name=123,  # Should be string!
            r=[10.0, 20.0, 30.0, 40.0],
            z=[0.0, 10.0]
        )

def test_ring_type_validation_failure_r():
    """Test Ring rejects non-list r"""
    with pytest.raises(ValidationError, match="r must be a list"):
        Ring(
            name="test",
            r=(10.0, 20.0, 30.0, 40.0),  # Tuple, not list!
            z=[0.0, 10.0]
        )

def test_ring_type_validation_failure_r_elements():
    """Test Ring rejects non-numeric r elements"""
    with pytest.raises(ValidationError, match=r"r\[1\] must be"):
        Ring(
            name="test",
            r=[10.0, "twenty", 30.0, 40.0],  # String in list!
            z=[0.0, 10.0]
        )

def test_ring_type_validation_failure_n():
    """Test Ring rejects non-integer n"""
    with pytest.raises(ValidationError, match="n must be int"):
        Ring(
            name="test",
            r=[10.0, 20.0, 30.0, 40.0],
            z=[0.0, 10.0],
            n=5.5  # Should be int, not float!
        )

def test_helix_type_validation():
    """Test Helix type validation"""
    # Valid
    helix = Helix(
        name="H1",
        r=[10.0, 20.0],
        z=[0.0, 50.0],
        cutwidth=0.2,
        odd=True,
        dble=False
    )
    assert helix.name == "H1"
    
    # Invalid - cutwidth as string
    with pytest.raises(ValidationError, match="cutwidth"):
        Helix(
            name="H1",
            r=[10.0, 20.0],
            z=[0.0, 50.0],
            cutwidth="0.2",  # Should be float!
            odd=True,
            dble=False
        )

def test_type_validation_error_messages():
    """Test that error messages are helpful"""
    try:
        Ring(
            name="test",
            r=[10.0, 20.0, "30.0", 40.0],  # String instead of float
            z=[0.0, 10.0]
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        error_msg = str(e)
        # Should mention parameter name, index, and types
        assert "r[2]" in error_msg or "r" in error_msg
        assert "float" in error_msg or "numeric" in error_msg
```

### Benefits

- **Catch type errors early** at construction time
- **Better error messages** showing exact parameter with wrong type
- **Prevents subtle bugs** from wrong types propagating
- **Self-documenting** - types are enforced, not just hints
- **IDE support** - type hints still work for autocomplete

### Estimated Time

- Implementation: 3-4 hours
- Testing: 2 hours
- **Total: 5-6 hours**

---

## Task 8: Add Negative Test Cases

### Current Problem

Test suite focuses on success cases but lacks negative testing:

```python
# tests/test_core_classes.py
def test_ring_initialization():
    """Test Ring object creation"""
    ring = Ring(name="test_ring", r=[10.0, 20.0, 30.0, 40.0], z=[0.0, 10.0])
    assert ring.name == "test_ring"
    # ✓ Tests success case
    # ✗ Doesn't test what happens with bad input
```

### Proposed Solution

**Step 1: Create Comprehensive Negative Test Suite**

Create `tests/test_validation_errors.py`:

```python
import pytest
from python_magnetgeo import Ring, Helix, Insert, Bitter
from python_magnetgeo.validation import ValidationError

class TestRingValidation:
    """Negative tests for Ring class"""
    
    def test_ring_empty_name(self):
        """Test Ring rejects empty name"""
        with pytest.raises(ValidationError, match="Name must be a non-empty string"):
            Ring(name="", r=[10.0, 20.0, 30.0, 40.0], z=[0.0, 10.0])
    
    def test_ring_whitespace_name(self):
        """Test Ring rejects whitespace-only name"""
        with pytest.raises(ValidationError, match="Name cannot be whitespace only"):
            Ring(name="   ", r=[10.0, 20.0, 30.0, 40.0], z=[0.0, 10.0])
    
    def test_ring_negative_radius(self):
        """Test Ring rejects negative inner radius"""
        with pytest.raises(ValidationError, match="Inner radius cannot be negative"):
            Ring(name="test", r=[-5.0, 20.0, 30.0, 40.0], z=[0.0, 10.0])
    
    def test_ring_descending_radii(self):
        """Test Ring rejects descending radius order"""
        with pytest.raises(ValidationError, match="must be in ascending order"):
            Ring(name="test", r=[40.0, 30.0, 20.0, 10.0], z=[0.0, 10.0])
    
    def test_ring_wrong_r_length(self):
        """Test Ring rejects wrong number of radius values"""
        with pytest.raises(ValidationError, match="must have exactly 4 values"):
            Ring(name="test", r=[10.0, 20.0], z=[0.0, 10.0])
    
    def test_ring_wrong_z_length(self):
        """Test Ring rejects wrong number of z values"""
        with pytest.raises(ValidationError, match="must have exactly 2 values"):
            Ring(name="test", r=[10.0, 20.0, 30.0, 40.0], z=[0.0, 5.0, 10.0])
    
    def test_ring_descending_z(self):
        """Test Ring rejects descending z order"""
        with pytest.raises(ValidationError, match="must be in ascending order"):
            Ring(name="test", r=[10.0, 20.0, 30.0, 40.0], z=[10.0, 0.0])
    
    def test_ring_coolingslit_angle_overflow(self):
        """Test Ring rejects cooling slits that exceed 360 degrees"""
        with pytest.raises(
            ValidationError, 
            match="total angular length.*cannot exceed 360 degrees"
        ):
            Ring(
                name="test",
                r=[10.0, 20.0, 30.0, 40.0],
                z=[0.0, 10.0],
                n=10,      # 10 slits
                angle=40.0  # 10 * 40 = 400 > 360!
            )


class TestHelixValidation:
    """Negative tests for Helix class"""
    
    def test_helix_invalid_r_length(self):
        """Test Helix rejects wrong r length"""
        with pytest.raises(ValidationError, match="must have exactly 2 values"):
            Helix(
                name="H1",
                r=[10.0],  # Need 2 values!
                z=[0.0, 50.0],
                cutwidth=0.2,
                odd=True,
                dble=False
            )
    
    def test_helix_negative_cutwidth(self):
        """Test Helix rejects negative cutwidth"""
        with pytest.raises(ValidationError):
            Helix(
                name="H1",
                r=[10.0, 20.0],
                z=[0.0, 50.0],
                cutwidth=-0.2,  # Negative!
                odd=True,
                dble=False
            )
    
    def test_helix_overlapping_radii(self):
        """Test Helix rejects when inner > outer radius"""
        with pytest.raises(ValidationError, match="ascending order"):
            Helix(
                name="H1",
                r=[20.0, 10.0],  # Inner > outer!
                z=[0.0, 50.0],
                cutwidth=0.2,
                odd=True,
                dble=False
            )


class TestInsertValidation:
    """Negative tests for Insert class"""
    
    def test_insert_mismatched_helix_ring_count(self):
        """Test Insert rejects wrong helix/ring ratio"""
        h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False)
        h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False)
        
        r1 = Ring("R1", [20, 22, 25, 27], [50, 55])
        r2 = Ring("R2", [35, 37, 40, 42], [50, 55])
        
        # 2 helices need 1 ring, not 2
        with pytest.raises(
            ValidationError,
            match="expected 1 connecting rings.*got 2"
        ):
            Insert(
                name="test",
                helices=[h1, h2],
                rings=[r1, r2],
                currentleads=[],
                hangles=[],
                rangles=[]
            )
    
    def test_insert_rings_with_single_helix(self):
        """Test Insert rejects rings when only 1 helix"""
        h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False)
        r1 = Ring("R1", [20, 22, 25, 27], [50, 55])
        
        with pytest.raises(
            ValidationError,
            match="at least 2 helices"
        ):
            Insert(
                name="test",
                helices=[h1],
                rings=[r1],
                currentleads=[],
                hangles=[],
                rangles=[]
            )
    
    def test_insert_mismatched_hangles(self):
        """Test Insert rejects mismatched hangles count"""
        h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False)
        h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False)
        
        with pytest.raises(
            ValidationError,
            match="Number of hangles.*must match number of helices"
        ):
            Insert(
                name="test",
                helices=[h1, h2],
                rings=[],
                currentleads=[],
                hangles=[90.0],  # 2 helices but 1 angle!
                rangles=[]
            )
    
    def test_insert_innerbore_greater_than_outerbore(self):
        """Test Insert rejects innerbore >= outerbore"""
        h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False)
        
        with pytest.raises(
            ValidationError,
            match="innerbore.*must be less than outerbore"
        ):
            Insert(
                name="test",
                helices=[h1],
                rings=[],
                currentleads=[],
                hangles=[],
                rangles=[],
                innerbore=100.0,
                outerbore=50.0  # Inner > outer!
            )


class TestBitterValidation:
    """Negative tests for Bitter class"""
    
    def test_bitter_invalid_r_length(self):
        """Test Bitter rejects wrong r length"""
        with pytest.raises(ValidationError, match="must have exactly 2 values"):
            Bitter(
                name="B1",
                r=[10.0],  # Need 2!
                z=[0.0, 10.0],
                odd=True,
                modelaxi=None
            )
    
    def test_bitter_negative_radius(self):
        """Test Bitter rejects negative radius"""
        with pytest.raises(ValidationError, match="cannot be negative"):
            Bitter(
                name="B1",
                r=[-5.0, 20.0],
                z=[0.0, 10.0],
                odd=True,
                modelaxi=None
            )


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_ring_zero_radii(self):
        """Test Ring with zero radius (boundary case)"""
        # Zero radius should be valid (represents axis)
        ring = Ring(
            name="test",
            r=[0.0, 5.0, 10.0, 15.0],
            z=[0.0, 10.0]
        )
        assert ring.r[0] == 0.0
    
    def test_ring_very_large_values(self):
        """Test Ring with very large values"""
        ring = Ring(
            name="test",
            r=[1000.0, 2000.0, 3000.0, 4000.0],
            z=[0.0, 5000.0]
        )
        assert ring.r[0] == 1000.0
    
    def test_ring_very_small_positive_values(self):
        """Test Ring with very small positive values"""
        ring = Ring(
            name="test",
            r=[0.001, 0.002, 0.003, 0.004],
            z=[0.0, 0.005]
        )
        assert ring.r[0] == 0.001
    
    def test_insert_empty_helices(self):
        """Test Insert with no helices"""
        with pytest.raises(ValidationError):
            Insert(
                name="test",
                helices=[],  # Empty!
                rings=[],
                currentleads=[],
                hangles=[],
                rangles=[]
            )
    
    def test_insert_none_vs_empty_list(self):
        """Test Insert handles None vs [] correctly"""
        h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False)
        
        # Both should work
        insert1 = Insert(
            name="test1",
            helices=[h1],
            rings=None,  # None
            currentleads=None,
            hangles=None,
            rangles=None
        )
        
        insert2 = Insert(
            name="test2",
            helices=[h1],
            rings=[],  # Empty list
            currentleads=[],
            hangles=[],
            rangles=[]
        )
        
        assert len(insert1.rings) == 0
        assert len(insert2.rings) == 0
```

**Step 2: Test Error Message Quality**

Create `tests/test_error_messages.py`:

```python
import pytest
from python_magnetgeo import Ring
from python_magnetgeo.validation import ValidationError

def test_error_message_contains_parameter_name():
    """Test error messages identify the problematic parameter"""
    try:
        Ring(name="test", r=[10.0, 20.0], z=[0.0, 10.0])
    except ValidationError as e:
        assert "r" in str(e).lower()
        assert "4" in str(e)  # Expected length

def test_error_message_contains_actual_vs_expected():
    """Test error messages show what was expected vs what was given"""
    try:
        Ring(name="test", r=[10.0, 20.0, 30.0, 40.0], z=[0.0, 5.0, 10.0])
    except ValidationError as e:
        error_msg = str(e)
        assert "2" in error_msg  # Expected
        assert "3" in error_msg  # Got

def test_error_message_for_descending_order():
    """Test error shows the problematic values"""
    try:
        Ring(name="test", r=[10.0, 20.0, 15.0, 40.0], z=[0.0, 10.0])
    except ValidationError as e:
        error_msg = str(e)
        assert "ascending" in error_msg.lower()
        # Should show the actual values that are wrong
        assert "10.0" in error_msg or "20.0" in error_msg or "15.0" in error_msg
```

**Step 3: Integration Tests for Error Handling**

Create `tests/test_error_propagation.py`:

```python
import pytest
from python_magnetgeo import Insert, Helix
from python_magnetgeo.validation import ValidationError

def test_error_propagates_from_nested_object():
    """Test that validation errors from nested objects propagate correctly"""
    
    # Create invalid helix data
    invalid_helix_dict = {
        'name': 'H1',
        'r': [20.0, 10.0],  # Wrong order!
        'z': [0.0, 50.0],
        'cutwidth': 0.2,
        'odd': True,
        'dble': False
    }
    
    insert_dict = {
        'name': 'test_insert',
        'helices': [invalid_helix_dict],
        'rings': [],
        'currentleads': [],
        'hangles': [],
        'rangles': []
    }
    
    # Should get error from nested helix
    with pytest.raises(ValidationError, match="ascending order"):
        Insert.from_dict(insert_dict)

def test_multiple_validation_errors():
    """Test behavior when multiple things are wrong"""
    # Currently raises first error found
    # Could be enhanced to collect all errors
    
    with pytest.raises(ValidationError):
        Ring(
            name="",  # Invalid: empty
            r=[20.0, 10.0, 30.0, 40.0],  # Invalid: wrong order
            z=[10.0, 0.0],  # Invalid: wrong order
            n=-5  # Invalid: negative count
        )
    # Note: Only first error is raised
```

### Benefits

- **Catches bugs early** during development
- **Documents expected behavior** - shows what's NOT allowed
- **Prevents regressions** - ensures validation keeps working
- **Better error messages** - verified to be helpful
- **Confidence in robustness** - code handles bad input gracefully

### Estimated Time

- Implementation: 4-5 hours
- **Total: 4-5 hours**

---

## Summary: Medium Priority Tasks

| Task | Description | Estimated Time | Benefits |
|------|-------------|----------------|----------|
| **Task 5** | Consolidate nested object loading | 3-5 hours | Eliminate 200+ lines of duplication |
| **Task 6** | Add auto-registration for classes | 3-4 hours | No manual class registry updates |
| **Task 7** | Improve runtime type validation | 5-6 hours | Catch type errors at construction |
| **Task 8** | Add negative test cases | 4-5 hours | Ensure robust error handling |
| **TOTAL** | | **15-20 hours** | Significant code quality improvement |

---

## Recommended Implementation Order

### Phase 1: Foundation (Tasks 5 & 6)
**Week 1:**
1. Implement Task 5 (nested object loading)
2. Implement Task 6 (auto-registration)
3. Test both together

**Why first:** These are infrastructure changes that benefit all other work.

### Phase 2: Validation (Tasks 7 & 8)
**Week 2:**
1. Implement Task 7 (type validation)
2. Implement Task 8 (negative tests)
3. Comprehensive testing

**Why second:** Builds on the foundation and ensures robustness.

---

## Future Discussion Prompts

### For Task 5 Discussion:
```
I want to implement Task 5: Consolidate Nested Object Loading. 

Context:
- Currently Insert, Bitter, and Helix have duplicated _load_nested_* methods
- Want to move this to YAMLObjectBase as generic _load_nested_list() and _load_nested_single()

Please help me:
1. Review the proposed _load_nested_list() implementation in base.py
2. Identify any edge cases I might have missed
3. Create a migration plan for refactoring Insert.py first as a pilot
4. Suggest test cases to ensure backward compatibility
```

### For Task 6 Discussion:
```
I want to implement Task 6: Add Auto-Registration for Class Registry.

Context:
- Currently deserialize.py has a hardcoded `classes = {...}` dictionary
- Want classes to auto-register when defined using __init_subclass__

Please help me:
1. Review the __init_subclass__ approach vs alternatives
2. Ensure this works with YAML deserialization
3. Plan migration to avoid breaking existing code
4. Verify all existing classes will auto-register correctly
```

### For Task 7 Discussion:
```
I want to implement Task 7: Improve Type Validation at Runtime.

Context:
- Type hints exist but aren't enforced at runtime
- Want to add runtime type checking to catch errors early

Please help me:
1. Review the proposed validate_type() implementation
2. Decide between decorator approach vs explicit validation
3. Identify performance implications
4. Plan gradual rollout to existing classes
```

### For Task 8 Discussion:
```
I want to implement Task 8: Add Negative Test Cases.

Context:
- Current test suite focuses on success cases
- Need comprehensive negative testing for all validation

Please help me:
1. Review the proposed test structure
2. Identify missing edge cases
3. Ensure error messages are tested
4. Plan test organization and naming conventions
```

---

## Success Criteria

After completing Medium Priority tasks:

✅ **Code Quality**
- < 50 lines of duplicated code across entire codebase
- All classes auto-register (no manual updates needed)
- Runtime type checking prevents invalid constructions

✅ **Test Coverage**
- Negative tests for all validation rules
- Edge case coverage > 90%
- Error message quality verified

✅ **Maintainability**
- Adding new class requires minimal boilerplate
- Validation logic centralized and reusable
- Clear error messages for debugging

✅ **Developer Experience**
- Type errors caught at construction, not later
- Helpful error messages with context
- Self-documenting code through validation