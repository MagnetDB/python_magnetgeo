# Dependency Analysis - Dry-Run Mode for Object Creation

## Overview

The `get_required_files()` method provides a "dry-run" capability for analyzing object dependencies without actually loading files or creating objects. This is useful for:

- **Pre-flight validation**: Check if all required files exist before attempting to load
- **Dependency analysis**: Understand configuration structure and file dependencies
- **Performance optimization**: Pre-fetch files in distributed/cloud environments
- **Error prevention**: Detect missing files early, before partial object construction
- **Validation pipelines**: Build automated validation and verification systems

## API Reference

### `get_required_files(values, debug=False)`

**Class method** available on all geometry classes (Helix, Ring, Insert, etc.)

**Parameters:**
- `values` (dict): Dictionary containing object parameters (as would be passed to `from_dict`)
- `debug` (bool): Enable debug output showing analysis progress (default: False)

**Returns:**
- `set[str]`: Set of file paths that would be loaded (e.g., `{"modelaxi.yaml", "shape.yaml"}`)

**Example:**
```python
from python_magnetgeo.Helix import Helix

helix_config = {
    "name": "H1",
    "r": [15.0, 25.0],
    "z": [0.0, 100.0],
    "cutwidth": 2.0,
    "odd": True,
    "dble": False,
    "modelaxi": "H1_modelaxi",  # Would load H1_modelaxi.yaml
    "model3d": "H1_model3d",    # Would load H1_model3d.yaml
    "shape": "H1_shape",        # Would load H1_shape.yaml
}

# Analyze dependencies without loading anything
required_files = Helix.get_required_files(helix_config, debug=True)
print(required_files)
# Output: {'H1_modelaxi.yaml', 'H1_model3d.yaml', 'H1_shape.yaml'}
```

## How It Works

### String References → Files

When a nested object is specified as a string, it indicates a file reference:

```python
{
    "modelaxi": "my_modelaxi"  # Will load my_modelaxi.yaml
}
```

### Inline Dictionaries → No Files

When a nested object is specified as a dictionary, it's defined inline (no file needed):

```python
{
    "modelaxi": {  # Inline definition - no file to load
        "num": 10,
        "h": 8.0,
        "turns": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
}
```

However, the inline dictionary might itself have nested dependencies, which are analyzed recursively.

### Mixed Configurations

You can mix file references and inline definitions:

```python
{
    "modelaxi": "H1_modelaxi",  # File reference
    "model3d": {                 # Inline definition
        "with_shapes": True,
        "with_channels": False
    },
    "chamfers": [
        "chamfer1",              # File reference
        {                        # Inline definition
            "name": "chamfer2",
            "dr": 1.0,
            "dz": 1.0
        }
    ]
}
```

Result: `{'H1_modelaxi.yaml', 'chamfer1.yaml'}`

## Use Cases

### 1. Pre-Flight Validation

Check if all required files exist before attempting to create an object:

```python
import os
from python_magnetgeo.Helix import Helix

# Analyze configuration
config = {...}
required_files = Helix.get_required_files(config)

# Validate all files exist
missing_files = [f for f in required_files if not os.path.exists(f)]
if missing_files:
    print(f"Error: Missing files: {missing_files}")
    exit(1)

# All files present - safe to create object
helix = Helix.from_dict(config)
```

### 2. Dependency Tree Analysis

Understand the structure of complex configurations:

```python
from python_magnetgeo.Insert import Insert

insert_config = {...}  # Complex configuration with many nested objects
files = Insert.get_required_files(insert_config, debug=True)

print(f"This Insert requires {len(files)} external files:")
for f in sorted(files):
    print(f"  - {f}")
```

### 3. Parallel File Pre-fetching

In distributed systems, pre-fetch all required files before object construction:

```python
import concurrent.futures
from cloud_storage import download_file

# Analyze dependencies
required_files = Helix.get_required_files(config)

# Download all files in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_file, f) for f in required_files]
    concurrent.futures.wait(futures)

# Now create the object (all files are local)
helix = Helix.from_dict(config)
```

### 4. Configuration Validation Pipeline

Build automated validation systems:

```python
def validate_configuration(config, object_class):
    """Validate a configuration before using it."""
    
    # Step 1: Analyze dependencies
    required_files = object_class.get_required_files(config)
    
    # Step 2: Check file existence
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        return False, f"Missing files: {missing}"
    
    # Step 3: Check file permissions
    unreadable = [f for f in required_files if not os.access(f, os.R_OK)]
    if unreadable:
        return False, f"Unreadable files: {unreadable}"
    
    # Step 4: Could add more checks (file size, format, etc.)
    
    return True, "OK"

# Use in validation pipeline
valid, message = validate_configuration(config, Helix)
if not valid:
    print(f"Validation failed: {message}")
```

## Implementation Details

### Base Class Implementation

The core functionality is implemented in `YAMLObjectBase` (in `base.py`):

- `get_required_files()`: Main entry point for dependency analysis
- `_analyze_nested_dependencies()`: Class-specific dependency analysis (override in subclasses)
- `_analyze_single_dependency()`: Helper for analyzing single nested objects
- `_analyze_list_dependency()`: Helper for analyzing lists of nested objects

### Subclass Requirements

Each geometry class should override `_analyze_nested_dependencies()` to specify which fields contain nested objects:

```python
class Helix(YAMLObjectBase):
    @classmethod
    def _analyze_nested_dependencies(cls, values: dict, required_files: set, debug: bool = False):
        """Analyze nested dependencies specific to Helix."""
        # Analyze single nested objects
        cls._analyze_single_dependency(values.get("modelaxi"), ModelAxi, required_files, debug)
        cls._analyze_single_dependency(values.get("model3d"), Model3D, required_files, debug)
        cls._analyze_single_dependency(values.get("shape"), Shape, required_files, debug)
        cls._analyze_single_dependency(values.get("grooves"), Groove, required_files, debug)
        
        # Analyze lists of nested objects
        cls._analyze_list_dependency(values.get("chamfers"), Chamfer, required_files, debug)
```

### Recursive Analysis

The analysis is recursive - when an inline dictionary is found, it's analyzed for its own nested dependencies:

```
Helix configuration
├── modelaxi: "file1" → file1.yaml
├── shape: {...}
│   └── profile: "file2" → file2.yaml
└── chamfers: [...]
    ├── [0]: "file3" → file3.yaml
    └── [1]: {...}
        └── (no nested files)

Result: {file1.yaml, file2.yaml, file3.yaml}
```

## Comparison with `from_dict()`

| Aspect | `from_dict()` | `get_required_files()` |
|--------|---------------|------------------------|
| **Purpose** | Create object | Analyze dependencies |
| **File I/O** | Loads all files | No file I/O |
| **Object creation** | Creates objects | No objects created |
| **Return value** | Object instance | Set of file paths |
| **Side effects** | Yes (file reads, object construction) | No (pure analysis) |
| **Performance** | Slower (I/O bound) | Fast (no I/O) |
| **Use when** | Ready to create object | Planning, validation, analysis |

## Best Practices

1. **Validate before loading**: Always use `get_required_files()` for validation before calling `from_dict()`

2. **Enable debug mode during development**: Use `debug=True` to understand the analysis process

3. **Cache results**: The result set can be cached if the configuration doesn't change

4. **Check file existence**: Always verify files exist before attempting to load

5. **Handle missing files gracefully**: Provide clear error messages when files are missing

## Example: Complete Workflow

```python
from python_magnetgeo.Helix import Helix
import os

def create_helix_safely(config_dict):
    """Create a Helix with proper validation."""
    
    # Step 1: Analyze dependencies
    print("Analyzing configuration...")
    required_files = Helix.get_required_files(config_dict, debug=False)
    print(f"Found {len(required_files)} required files")
    
    # Step 2: Validate files exist
    print("Validating files...")
    missing = []
    for filepath in required_files:
        if not os.path.exists(filepath):
            missing.append(filepath)
            print(f"  ✗ MISSING: {filepath}")
        else:
            print(f"  ✓ OK: {filepath}")
    
    if missing:
        raise FileNotFoundError(f"Missing required files: {missing}")
    
    # Step 3: Create object (all validations passed)
    print("Creating Helix object...")
    helix = Helix.from_dict(config_dict)
    print(f"✓ Successfully created Helix '{helix.name}'")
    
    return helix

# Usage
try:
    config = {
        "name": "H1",
        "r": [15.0, 25.0],
        "z": [0.0, 100.0],
        "cutwidth": 2.0,
        "odd": True,
        "dble": False,
        "modelaxi": "H1_modelaxi",
        "model3d": "H1_model3d",
        "shape": "H1_shape",
    }
    
    helix = create_helix_safely(config)
    
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Please ensure all required files are present")
```

## Limitations

1. **Cannot analyze actual file contents**: The method only identifies which files would be loaded, not what those files contain or their nested dependencies

2. **Requires correct configuration**: If the configuration dict has the wrong structure, the analysis may be incomplete

3. **Class-specific implementation**: Each geometry class must implement `_analyze_nested_dependencies()` for full functionality

4. **No circular dependency detection**: The method doesn't detect or prevent circular file references

## Future Enhancements

Potential improvements for future versions:

- **Deep analysis**: Optionally load and analyze referenced files to build complete dependency tree
- **Circular dependency detection**: Detect and warn about circular file references
- **Dependency graph visualization**: Generate visual dependency graphs
- **File size estimation**: Estimate total data to be loaded
- **Caching recommendations**: Suggest which files to cache based on usage patterns
