# Feature: Dry-Run Dependency Analysis

## Summary

Added a new `get_required_files()` method to all geometry classes that performs a dry-run analysis of object creation to identify which files would need to be loaded, without actually loading any files or creating objects.

## What Was Implemented

### 1. Base Class Methods (base.py)

Added to `YAMLObjectBase`:

- **`get_required_files(values, debug=False)`**: Main entry point - analyzes a configuration dictionary and returns a set of file paths that would be loaded

- **`_analyze_nested_dependencies(values, required_files, debug)`**: Abstract method that subclasses override to specify which fields contain nested objects

- **`_analyze_single_dependency(data, object_class, required_files, debug)`**: Helper for analyzing single nested object fields

- **`_analyze_list_dependency(data, object_class, required_files, debug)`**: Helper for analyzing list fields containing nested objects

### 2. Helix Implementation (Helix.py)

Implemented `_analyze_nested_dependencies()` for the Helix class to handle its specific nested objects:
- modelaxi (ModelAxi)
- model3d (Model3D)
- shape (Shape)
- chamfers (list of Chamfer)
- grooves (Groove)

### 3. Documentation

- **docs/dependency_analysis.md**: Comprehensive documentation including:
  - API reference
  - How it works
  - Use cases with examples
  - Implementation details
  - Best practices
  - Comparison with `from_dict()`

### 4. Examples

- **test_get_required_files.py**: Simple demonstration script showing three scenarios:
  1. All file references
  2. All inline objects
  3. Mixed file/inline

- **example_dependency_analysis.py**: Real-world examples showing practical use cases

### 5. Tests

- **tests/test_get_required_files.py**: Comprehensive unit tests covering:
  - All file references
  - All inline definitions
  - Mixed references
  - Empty configs
  - None values
  - Empty lists
  - Debug mode consistency

## How to Use

### Basic Usage

```python
from python_magnetgeo.Helix import Helix

config = {
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
required_files = Helix.get_required_files(config)
print(required_files)
# Output: {'H1_modelaxi.yaml', 'H1_model3d.yaml', 'H1_shape.yaml'}
```

### Pre-Flight Validation

```python
import os

# Analyze configuration
required_files = Helix.get_required_files(config)

# Check if all files exist
missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"Error: Missing files: {missing}")
else:
    # Safe to create object
    helix = Helix.from_dict(config)
```

## Key Benefits

1. **No File I/O**: Analysis is fast and doesn't touch the filesystem
2. **Early Error Detection**: Find missing files before attempting object creation
3. **Recursive Analysis**: Handles nested inline dictionaries that might have their own dependencies
4. **Mixed Configurations**: Works with both file references and inline object definitions
5. **Extensible**: Easy to add to other geometry classes

## Use Cases

- **Pre-flight validation**: Verify all required files exist before loading
- **Dependency analysis**: Understand configuration structure
- **Performance optimization**: Pre-fetch files in distributed systems
- **Error prevention**: Avoid partial object construction failures
- **Validation pipelines**: Build automated validation systems

## Files Modified/Created

### Modified
- `python_magnetgeo/base.py`: Added 4 new methods to YAMLObjectBase
- `python_magnetgeo/Helix.py`: Added _analyze_nested_dependencies() implementation

### Created
- `docs/dependency_analysis.md`: Complete documentation
- `test_get_required_files.py`: Simple demonstration
- `example_dependency_analysis.py`: Real-world examples
- `tests/test_get_required_files.py`: Unit tests (7 tests, all passing)

## Testing

Run the tests:
```bash
python -m pytest tests/test_get_required_files.py -v
```

Run the examples:
```bash
python test_get_required_files.py
python example_dependency_analysis.py
```

## Next Steps for Other Geometry Classes

To add this functionality to other geometry classes (Ring, Insert, Supra, etc.):

1. Override `_analyze_nested_dependencies()` in the class
2. Use `_analyze_single_dependency()` for single nested objects
3. Use `_analyze_list_dependency()` for lists of nested objects
4. Add tests

Example template:
```python
@classmethod
def _analyze_nested_dependencies(cls, values: dict, required_files: set, debug: bool = False):
    """Analyze nested dependencies specific to this class."""
    # Single nested objects
    cls._analyze_single_dependency(values.get("field1"), Class1, required_files, debug)
    
    # Lists of nested objects
    cls._analyze_list_dependency(values.get("field2"), Class2, required_files, debug)
```

Classes without nested objects (like Ring) don't need to override anything - the base implementation returns an empty set.

## Implementation Quality

✓ Fully tested (7 unit tests, all passing)
✓ Comprehensive documentation
✓ Working examples
✓ Follows existing code patterns
✓ No breaking changes
✓ Extensible design
