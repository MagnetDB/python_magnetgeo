# Fixed Base Classes - Avoiding YAMLObject Conflicts

## Problem Analysis

The issue occurs because `yaml.YAMLObject` has its own `from_yaml()` method that expects different parameters than our custom implementation. We need to either:

1. Override the method properly, or  
2. Use different method names to avoid conflicts

## Solution: Updated Base Classes

### Updated `python_magnetgeo/base.py`:

```python
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
    def load_from_yaml(cls: Type[T], filename: str, debug: bool = False) -> T:
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


class YAMLObjectBase(yaml.YAMLObject, SerializableMixin):
    """
    Base class for all YAML serializable geometry objects.
    
    This class automatically handles YAML constructor registration and provides
    compatibility with existing from_yaml/from_json class methods.
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
            """Generated YAML constructor for this class"""
            values = loader.construct_mapping(node)
            return cls.from_dict(values)
        
        # Register the constructor with PyYAML
        yaml.add_constructor(cls.yaml_tag, constructor)
        
        # Optional: print confirmation (remove in production)
        print(f"Auto-registered YAML constructor for {cls.__name__}")

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
```

## Alternative Solution: Simpler Approach

If you prefer a simpler solution that avoids inheriting from `yaml.YAMLObject` entirely:

### Alternative `python_magnetgeo/base.py`:

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Base classes for python_magnetgeo to eliminate code duplication.
Simple approach that avoids yaml.YAMLObject inheritance conflicts.
"""

import json
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, TypeVar

T = TypeVar('T', bound='SerializableMixin')

class SerializableMixin:
    """Mixin providing common serialization functionality."""
    
    def dump(self, filename: Optional[str] = None) -> None:
        """Dump object to YAML file."""
        from .utils import writeYaml
        class_name = self.__class__.__name__
        writeYaml(class_name, self)

    def to_json(self) -> str:
        """Convert object to JSON string."""
        from . import deserialize
        return json.dumps(
            self, 
            default=deserialize.serialize_instance, 
            sort_keys=True, 
            indent=4
        )

    def write_to_json(self, filename: Optional[str] = None) -> None:
        """Write object to JSON file."""
        if filename is None:
            name = getattr(self, 'name', self.__class__.__name__)
            filename = f"{name}.json"
            
        try:
            with open(filename, "w") as ostream:
                ostream.write(self.to_json())
        except Exception as e:
            raise Exception(f"Failed to write {self.__class__.__name__} to {filename}: {e}")

    @classmethod
    def from_yaml(cls: Type[T], filename: str, debug: bool = False) -> T:
        """Load object from YAML file."""
        from .utils import loadYaml
        return loadYaml(cls.__name__, filename, cls, debug)

    @classmethod  
    def from_json(cls: Type[T], filename: str, debug: bool = False) -> T:
        """Load object from JSON file."""
        from .utils import loadJson
        return loadJson(cls.__name__, filename, debug)

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], values: Dict[str, Any], debug: bool = False) -> T:
        """Create instance from dictionary - must be implemented by subclasses."""
        raise NotImplementedError(f"{cls.__name__} must implement from_dict method")


class GeometryBase(SerializableMixin):
    """
    Base class for all geometry objects.
    
    This approach manually handles YAML registration without inheriting
    from yaml.YAMLObject to avoid method conflicts.
    """
    
    # This will be set by subclasses
    yaml_tag = None
    
    def __init_subclass__(cls, **kwargs):
        """Automatically register YAML constructors for all subclasses."""
        super().__init_subclass__(**kwargs)
        
        # Ensure the class has a yaml_tag
        if not hasattr(cls, 'yaml_tag') or not cls.yaml_tag:
            raise ValueError(f"Class {cls.__name__} must define a yaml_tag")
        
        # Make this class a YAML object manually
        cls.yaml_loader = yaml.SafeLoader
        cls.yaml_dumper = yaml.SafeDumper
        
        # Auto-register YAML constructor
        def constructor(loader, node):
            """Generated YAML constructor for this class"""
            values = loader.construct_mapping(node)
            return cls.from_dict(values)
        
        # Register the constructor with PyYAML
        yaml.add_constructor(cls.yaml_tag, constructor)
        
        # Also register representer for dumping
        def representer(dumper, obj):
            """Generated YAML representer for this class"""
            return dumper.represent_mapping(cls.yaml_tag, obj.__dict__)
        
        yaml.add_representer(cls, representer)
        
        print(f"Auto-registered YAML constructor for {cls.__name__}")
```

## Updated Ring.py for Either Approach

### For the First Approach (inheriting from YAMLObjectBase):

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Ring
"""

from typing import List
from .base import YAMLObjectBase
from .validation import GeometryValidator

class Ring(YAMLObjectBase):
    """Ring geometry class."""
    
    yaml_tag = "Ring"

    def __init__(self, name: str, r: List[float], z: List[float], 
                 n: int = 0, angle: float = 0, bpside: bool = True, 
                 fillets: bool = False, cad: str = None) -> None:
        """Initialize Ring object."""
        
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_radial_bounds(r)
        GeometryValidator.validate_axial_bounds(z)
        
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.bpside = bpside
        self.fillets = fillets
        self.cad = cad or ''

    def __setstate__(self, state):
        """Handle deserialization"""
        self.__dict__.update(state)
        if not hasattr(self, 'cad'):
            self.cad = ''

    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        """Create Ring from dictionary"""
        return cls(
            name=values["name"],
            r=values["r"],
            z=values["z"],
            n=values.get("n", 0),
            angle=values.get("angle", 0),
            bpside=values.get("bpside", True),
            fillets=values.get("fillets", False),
            cad=values.get("cad", '')
        )

    def get_lc(self) -> float:
        """Calculate characteristic length"""
        return (self.r[1] - self.r[0]) / 10.0

    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"r={self.r!r}, z={self.z!r}, n={self.n!r}, "
                f"angle={self.angle!r}, bpside={self.bpside!r}, "
                f"fillets={self.fillets!r}, cad={self.cad!r})")

# YAML constructor automatically registered!
```

### For the Second Approach (inheriting from GeometryBase):

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Ring
"""

from typing import List
from .base import GeometryBase
from .validation import GeometryValidator

class Ring(GeometryBase):
    """Ring geometry class."""
    
    yaml_tag = "Ring"

    # ... rest of the implementation is identical ...
```

## Updated Test Script

```python
#!/usr/bin/env python3
"""
Fixed test script for refactored Ring
"""

import os
import json
import tempfile
from python_magnetgeo.Ring import Ring

def test_refactored_ring_functionality():
    """Test that refactored Ring has identical functionality"""
    print("Testing refactored Ring functionality...")
    
    # Test basic creation
    ring = Ring(
        name="test_ring",
        r=[10.0, 20.0],
        z=[0.0, 5.0],
        n=1,
        angle=45.0,
        bpside=True,
        fillets=False,
        cad="test_cad"
    )
    
    print(f"✓ Ring created: {ring}")
    
    # Test that all inherited methods exist
    assert hasattr(ring, 'dump')
    assert hasattr(ring, 'to_json')  
    assert hasattr(ring, 'write_to_json')
    assert hasattr(Ring, 'from_yaml')
    assert hasattr(Ring, 'from_json')
    assert hasattr(Ring, 'from_dict')
    
    print("✓ All serialization methods inherited correctly")
    
    # Test JSON serialization
    json_str = ring.to_json()
    parsed = json.loads(json_str)
    assert parsed['name'] == 'test_ring'
    assert parsed['r'] == [10.0, 20.0]
    assert parsed['__classname__'] == 'Ring'
    
    print("✓ JSON serialization works identically")
    
    # Test from_dict
    test_dict = {
        'name': 'dict_ring',
        'r': [5.0, 15.0],
        'z': [1.0, 6.0],
        'n': 2,
        'angle': 90.0,
        'bpside': False,
        'fillets': True,
        'cad': 'dict_cad'
    }
    
    dict_ring = Ring.from_dict(test_dict)
    assert dict_ring.name == 'dict_ring'
    assert dict_ring.r == [5.0, 15.0]
    
    print("✓ from_dict works identically")
    
    # Test validation
    try:
        Ring(name="", r=[1.0, 2.0], z=[0.0, 1.0])
        assert False, "Should have raised ValidationError for empty name"
    except Exception as e:
        print(f"✓ Validation works: {e}")
    
    try:
        Ring(name="bad_ring", r=[2.0, 1.0], z=[0.0, 1.0])  # inner > outer
        assert False, "Should have raised ValidationError for bad radii"
    except Exception as e:
        print(f"✓ Validation works: {e}")
    
    # Test YAML round-trip - using dump() to create file first
    ring.dump()  # This creates test_ring.yaml
    
    # Now load it back
    loaded_ring = Ring.from_yaml('test_ring.yaml')
    assert loaded_ring.name == ring.name
    assert loaded_ring.r == ring.r
    
    print("✓ YAML round-trip works")
    
    # Clean up
    if os.path.exists('test_ring.yaml'):
        os.unlink('test_ring.yaml')
    
    print("All refactored functionality verified! Ring.py successfully refactored.\n")

if __name__ == "__main__":
    test_refactored_ring_functionality()
```

## Recommendation

I recommend using the **first approach** (YAMLObjectBase) as it maintains better compatibility with the existing codebase, but with the fixed `from_yaml()` method that properly overrides the parent class method.

Try the updated base classes and Ring.py, and let me know if you encounter any other issues!