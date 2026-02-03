# Lazy Loading Quick Reference

## What is Lazy Loading?

Lazy loading in `python_magnetgeo` means geometry classes are only imported when you explicitly access them, not when you import the package. This improves startup time and reduces memory usage.

## Basic Pattern

```python
import python_magnetgeo as pmg

# Package imported - only core utilities loaded
# Geometry classes NOT yet imported

# Access a class - triggers import
helix = pmg.Helix(name="H1", r=[10, 20], z=[0, 50])  # Helix imported here
ring = pmg.Ring(name="R1", r=[5, 15], z=[0, 10])     # Ring imported here

# Subsequent access uses cache - no re-import needed
another_helix = pmg.Helix(name="H2", r=[15, 25], z=[0, 60])  # Fast!
```

## YAML Loading

When loading YAML files with type tags (`!<Helix>`, `!<Ring>`, etc.), you **must** register classes first:

```python
import python_magnetgeo as pmg

# Required: Register YAML constructors
pmg.verify_class_registration()

# Now load YAML files
helix = pmg.load("helix.yaml")
ring = pmg.load("ring.yaml")
insert = pmg.load("insert.yaml")
```

### Why?

YAML parsing needs to know how to construct objects for tags like `!<Helix>`. Classes register their constructors when imported. Lazy loading defers imports, so we need to force registration before YAML parsing.

## Common Patterns

### Pattern 1: Batch YAML Processing

```python
import python_magnetgeo as pmg
from pathlib import Path

# Register all classes once
pmg.verify_class_registration()

# Load multiple files
for yaml_file in Path("configs/").glob("*.yaml"):
    obj = pmg.load(yaml_file)
    print(f"Loaded {type(obj).__name__}: {obj.name}")
```

### Pattern 2: Type-Specific Loading (No Registration Needed)

```python
import python_magnetgeo as pmg

# Accessing the class triggers import and registration
helix = pmg.Helix.from_yaml("helix.yaml")
ring = pmg.Ring.from_yaml("ring.yaml")

# No verify_class_registration() needed!
```

### Pattern 3: Selective Import

```python
import python_magnetgeo as pmg

# Only import the classes you need
if working_with_helices:
    helix_class = pmg.Helix  # Only Helix imported
    
if working_with_rings:
    ring_class = pmg.Ring    # Only Ring imported

# Other classes remain unloaded
```

### Pattern 4: Script with Unknown Types

```python
#!/usr/bin/env python3
import sys
import python_magnetgeo as pmg

def load_geometry(filename):
    """Load any geometry file with automatic type detection."""
    # Register all classes for YAML parsing
    pmg.verify_class_registration()
    
    # Load with automatic type detection
    return pmg.load(filename)

if __name__ == "__main__":
    obj = load_geometry(sys.argv[1])
    print(f"Loaded {type(obj).__name__}: {obj.name}")
```

## Available Classes (All Lazy Loaded)

```python
import python_magnetgeo as pmg

# Core geometry types
pmg.Insert       # Magnet insert
pmg.Helix        # Helical coil
pmg.Ring         # Ring coil
pmg.Bitter       # Bitter coil
pmg.Supra        # Superconducting coil
pmg.Screen       # Screening element
pmg.Probe        # Probe element

# Additional components
pmg.Shape        # Shape modification
pmg.Profile      # 2D profile
pmg.ModelAxi     # Axisymmetric model
pmg.Model3D      # 3D model
pmg.InnerCurrentLead    # Inner current lead
pmg.OuterCurrentLead    # Outer current lead
pmg.Contour2D    # 2D contour
pmg.Chamfer      # Chamfer modification
pmg.Groove       # Groove modification
pmg.Tierod       # Tie rod
pmg.CoolingSlit  # Cooling slit

# Collections
pmg.Supras       # Multiple Supra
pmg.Bitters      # Multiple Bitter
```

## Utility Functions

```python
import python_magnetgeo as pmg

# Loading
obj = pmg.load("file.yaml")              # Load YAML/JSON
obj = pmg.loadObject("file.yaml")        # Legacy alias
obj = pmg.load_yaml("file.yaml")         # Explicit YAML

# Class registration
pmg.verify_class_registration()          # Register all YAML constructors
classes = pmg.list_registered_classes()  # Get all registered classes

# Logging
pmg.configure_logging(level=pmg.INFO)    # Configure logging
logger = pmg.get_logger(__name__)        # Get logger
pmg.set_level(pmg.DEBUG)                 # Change level

# Log levels
pmg.DEBUG, pmg.INFO, pmg.WARNING, pmg.ERROR, pmg.CRITICAL
```

## Best Practices

### ✓ DO

```python
# Import package once
import python_magnetgeo as pmg

# Register for YAML loading
pmg.verify_class_registration()

# Load files
obj = pmg.load("config.yaml")

# Access classes as needed
helix = pmg.Helix(name="H1", r=[10, 20], z=[0, 50])
```

### ⚠ AVOID

```python
# Don't import all classes explicitly (defeats lazy loading)
from python_magnetgeo import Helix, Ring, Insert, Bitter, Supra, ...

# Don't use deep imports (use package-level access instead)
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
```

## Troubleshooting

### Error: "could not determine a constructor for the tag '!<Helix>'"

**Problem**: YAML file uses type tag but class isn't registered yet.

**Solution**: Call `pmg.verify_class_registration()` before loading YAML.

```python
import python_magnetgeo as pmg
pmg.verify_class_registration()  # ← Add this
obj = pmg.load("helix.yaml")
```

### Alternative: Use type-specific loading

```python
import python_magnetgeo as pmg
helix = pmg.Helix.from_yaml("helix.yaml")  # No registration needed
```

## Performance

Lazy loading provides:

- **Faster startup**: Only core utilities loaded initially (~50-100ms faster)
- **Lower memory**: Unused classes never loaded into memory
- **Cleaner code**: Single import statement instead of many
- **Better IDE support**: Autocomplete works via `__dir__` implementation

## Examples

See these files for complete examples:

- `python_magnetgeo/examples/lazy_loading_demo.py` - Interactive demonstration
- `python_magnetgeo/examples/check_magnetgeo_yaml.py` - Practical usage
- `README.md` - Full documentation

## Implementation Details

Lazy loading uses Python's `__getattr__` mechanism in `python_magnetgeo/__init__.py`:

1. Only core utilities imported at package level
2. `__getattr__` intercepts attribute access (e.g., `pmg.Helix`)
3. Class imported on first access and cached
4. Subsequent accesses use cached class (no re-import)
5. `__dir__` provides IDE autocomplete support

See `python_magnetgeo/__init__.py` for implementation.
