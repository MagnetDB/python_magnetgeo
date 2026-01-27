# Python Magnet Geometry

<!-- [![PyPI version](https://img.shields.io/pypi/v/python_magnetgeo.svg)](https://pypi.python.org/pypi/python_magnetgeo)
[![Build Status](https://img.shields.io/travis/Trophime/python_magnetgeo.svg)](https://travis-ci.com/Trophime/python_magnetgeo)
[![Documentation Status](https://readthedocs.org/projects/python-magnetgeo/badge/?version=latest)](https://python-magnetgeo.readthedocs.io/en/latest/?version=latest)
[![Updates](https://pyup.io/repos/github/Trophime/python_magnetgeo/shield.svg)](https://pyup.io/repos/github/Trophime/python_magnetgeo/)
 -->
Python Magnet Geometry contains magnet geometrical models for high-field magnet design and simulation.

## Version 1.0.0 Release

**This is a major release with breaking changes.** See [API Breaking Changes](BREAKING_CHANGES.md) for complete migration guide.

## Features

- **Type-safe YAML configuration** - Define magnet geometry with validated YAML files
- **CAD integration** - Load/Create CAD and mesh with Salome (see hifimagnet.salome)
- **Mesh generation** - Create Gmsh meshes from Salome XAO format
- **Comprehensive geometry support** - Helix, Insert, Ring, Bitter, Supra, and more
- **Bump profiles** - New Profile class for 2D profile definitions with DAT file export
- **Advanced shape features** - Enhanced Shape class with Profile integration and position control
- **JSON/YAML serialization** - Full serialization/deserialization support
- **Input validation** - Automatic validation with descriptive error messages
- **Type annotations** - Full type hint support for better IDE integration
- **Extensive test suite** - Comprehensive testing for reliability

## Installation

### Using pip (recommended)

```bash
pip install python_magnetgeo==1.0.0
```

### Using Poetry

```bash
poetry add python_magnetgeo@^1.0.0
```

### Development installation

```bash
git clone https://github.com/Trophime/python_magnetgeo.git
cd python_magnetgeo
git checkout v1.0.0
python -m venv --system-site-packages magnetgeo-env
source ./magnetgeo-env/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Command-line Scripts

The package installs the following command-line scripts for use in MagnetDB context:

- `load-profile-from-dat` - Load and convert DAT profile files
- `split-helix-yaml` - Split helix YAML configuration files

These commands are available globally after installation and can be run from any directory:

```bash
load-profile-from-dat <profile.dat>
split-helix-yaml <helix.yaml>
```

## Quick Start

### Loading Methods Quick Reference

```python
# Method 1: Type-specific loading (when you know the type)
from python_magnetgeo import Insert, Helix, Ring
insert = Insert.from_yaml("HL-31.yaml")
helix = Helix.from_yaml("H1.yaml")
ring = Ring.from_yaml("Ring-01.yaml")

# Method 2: Lazy loading (automatic type detection)
from python_magnetgeo.utils import getObject
obj = getObject("config.yaml")  # Returns Insert, Helix, Ring, etc.

# Method 3: From dictionary
from python_magnetgeo import Helix
helix = Helix.from_dict({
    'name': 'H1',
    'r': [10.0, 20.0],
    'z': [0.0, 50.0],
    'cutwidth': 0.2,
    'odd': True,
    'dble': False
})

# Method 4: JSON loading
helix = Helix.from_json("H1.json")

# Method 5: Direct instantiation
from python_magnetgeo import Ring
ring = Ring(
    name="Ring-01",
    r=[10.0, 20.0],
    z=[0.0, 10.0]
)
```

### YAML Configuration Format

Version 1.0.0 uses structured YAML with type annotations:

#### Profile Configuration (New in v1.0.0)

```yaml
!<Profile>
cad: "HR-54-116"
points:
  - [-5.34, 0]
  - [-3.34, 0]
  - [0, 0.9]
  - [3.34, 0]
  - [5.34, 0]
labels: [0, 0, 1, 0, 0]
```

#### Shape Configuration (Enhanced in v1.0.0)

```yaml
!<Shape>
profile: "HR-54-116"  # References Profile by name
length: [15.0]        # Angular length in degrees
angle: [60, 90, 120]  # Angles between consecutive shapes
onturns: [1, 3, 5]    # Turns where shapes are applied
position: ALTERNATE   # ABOVE, BELOW, or ALTERNATE
```

#### Insert Configuration

```yaml
!<Insert>
name: "HL-31"
helices:
  - HL-31_H1
  - HL-31_H2
  - HL-31_H3
rings:
  - Ring-H1H2
  - Ring-H2H3
currentleads:
  - inner
  - outer-H14
hangles: []
rangles: []
innerbore: 18.54
outerbore: 186.25
```

#### Helix Configuration

```yaml
!<Helix>
name: HL-31_H1
odd: true
r: [19.3, 24.2]
z: [-226, 108]
dble: true
cutwidth: 0.22
axi: !<ModelAxi>
  name: "HL-31.d"
  h: 86.51
  turns: [0.292, 0.287, 0.283]
  pitch: [29.59, 30.10, 30.61]
shape: !<Shape>
  name: "NewShape"
  profile: "02_10_2014_H1"
  length: 15
  angle: [60, 90, 120, 120]
  onturns: 0
  position: ALTERNATE
```

#### Ring Configuration

```yaml
!<Ring>
name: Ring-H1H2
r: [24.5, 28.0]
z: [108, 115]
n: 1
angle: 0.0
bpside: true
fillets: false
```

### Loading Configuration

#### Method 1: Type-Specific Loading

```python
from python_magnetgeo import Insert, Helix, Ring

# Load an Insert configuration
insert = Insert.from_yaml("HL-31.yaml")
print(f"Loaded insert: {insert.name}")
print(f"Number of helices: {len(insert.helices)}")

# Load a Helix
helix = Helix.from_yaml("HL-31_H1.yaml")
print(f"Helix bounds: r={helix.r}, z={helix.z}")

# Load a Ring
ring = Ring.from_yaml("Ring-H1H2.yaml")
print(f"Ring: {ring.name}")
```

#### Method 2: Lazy Loading (Automatic Type Detection)

```python
from python_magnetgeo.utils import getObject

# Load any geometry object without knowing its type
# The type is automatically detected from the YAML type annotation
obj = getObject("HL-31.yaml")
print(f"Loaded {type(obj).__name__}: {obj.name}")

# Works with any geometry type
helix = getObject("HL-31_H1.yaml")  # Returns Helix instance
ring = getObject("Ring-H1H2.yaml")  # Returns Ring instance
bitter = getObject("Bitter-01.yaml")  # Returns Bitter instance

# Useful for command-line tools
import sys
if len(sys.argv) > 1:
    geometry = getObject(sys.argv[1])
    print(f"Loaded: {geometry.name}")
    rb, zb = geometry.boundingBox() if hasattr(geometry, 'boundingBox') else (None, None)
    if rb:
        print(f"Bounds: r=[{rb[0]:.2f}, {rb[1]:.2f}], z=[{zb[0]:.2f}, {zb[1]:.2f}]")
```

#### Method 3: Batch Loading with Type Detection

```python
from python_magnetgeo.utils import getObject
from pathlib import Path

def load_all_geometries(directory: str):
    """Load all YAML files with automatic type detection"""
    geometries = []

    for yaml_file in Path(directory).glob("*.yaml"):
        try:
            obj = getObject(str(yaml_file))
            geometries.append(obj)
            print(f"✓ Loaded {type(obj).__name__}: {obj.name}")
        except Exception as e:
            print(f"✗ Failed to load {yaml_file.name}: {e}")

    return geometries

# Usage
all_objects = load_all_geometries("./configs/")
print(f"\nTotal objects loaded: {len(all_objects)}")

# Group by type
from collections import defaultdict
by_type = defaultdict(list)
for obj in all_objects:
    by_type[type(obj).__name__].append(obj)

for obj_type, objects in by_type.items():
    print(f"{obj_type}: {len(objects)} objects")
```

### Creating Geometry Programmatically

```python
from python_magnetgeo import Helix, Ring, Shape, ModelAxi, Insert
from python_magnetgeo.Shape import ShapePosition

# Create a ModelAxi
axi = ModelAxi(
    name="HL-31.d",
    h=86.51,
    turns=[0.292, 0.287, 0.283],
    pitch=[29.59, 30.10, 30.61]
)

# Create a Shape
shape = Shape(
    profile="02_10_2014_H1",
    length=15,
    angle=[60, 90, 120, 120],
    onturns=0,
    position=ShapePosition.ALTERNATE  # Or just "ALTERNATE"
)

# Create a Helix
helix = Helix(
    name="H1",
    r=[19.3, 24.2],
    z=[-226, 108],
    cutwidth=0.22,
    odd=True,
    dble=True,
    axi=axi,
    shape=shape
)

# Create a Ring
ring = Ring(
    name="Ring-H1H2",
    r=[24.5, 28.0],
    z=[108, 115],
    n=1,
    angle=0.0,
    bpside=True,
    fillets=False
)

# Create an Insert
insert = Insert(
    name="HL-31",
    helices=[helix],
    rings=[ring],
    currentleads=["inner", "outer"],
    innerbore=18.54,
    outerbore=186.25
)

# Save to YAML
insert.dump()  # Creates HL-31.yaml
helix.dump()   # Creates H1.yaml
ring.dump()    # Creates Ring-H1H2.yaml

# Save to JSON
json_str = insert.to_json()
with open("HL-31.json", "w") as f:
    f.write(json_str)
```

### Error Handling with Validation

```python
from python_magnetgeo import Ring
from python_magnetgeo.validation import ValidationError

try:
    # This will raise ValidationError - inner radius > outer radius
    invalid_ring = Ring(
        name="bad_ring",
        r=[30.0, 20.0],  # Wrong order!
        z=[0.0, 10.0]
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Output: Validation error: r values must be in ascending order

try:
    # This will raise ValidationError - negative radius
    invalid_ring = Ring(
        name="bad_ring",
        r=[-5.0, 20.0],
        z=[0.0, 10.0]
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Output: Validation error: Inner radius cannot be negative
```

### Working with Salome

In Salome container:

```bash
export HIFIMAGNET=/opt/SALOME-9.7.0-UB20.04/INSTALL/HIFIMAGNET/bin/salome
salome -w1 -t $HIFIMAGNET/HIFIMAGNET_Cmd.py args:HL-31.yaml,--axi,--air,2,2
```

Create mesh from XAO:

```bash
python -m python_magnetgeo.xao HL-31-Axi.xao mesh --group CoolingChannels --geo HL-31.yaml
```

## Requirements

- Python >= 3.11
- PyYAML >= 6.0
- pytest >= 8.2.0 (for development)

## API Breaking Changes

⚠️ **IMPORTANT**: Version 1.0.0 contains breaking changes. **No backward compatibility is provided.**

### Migration Path

**If you're on v0.7.0:**
- ✓ Your YAML files are compatible!
- ⚠ Update Python code to add error handling
- Estimated migration time: 1-2 hours

**If you're on v0.5.x or earlier:**
- ✗ YAML files need migration (field names + type annotations)
- ✗ Python code needs updates
- Estimated migration time: 1-2 days

### Key Changes from v0.7.0 → v1.0.0

1. **New Base Classes**
   - All geometry classes now inherit from `YAMLObjectBase`
   - Automatic YAML constructor registration

2. **Validation System**
   - New `ValidationError` exceptions for invalid data
   - Descriptive error messages

3. **Enhanced Type Safety**
   - Stricter type checking
   - Comprehensive type hints

4. **Method Updates**
   - Added `debug` parameter to `from_dict()` and loading methods
   - Better error handling

**Good news for v0.7.0 users**: Your YAML files work as-is! Just add error handling in Python code.

### Key Changes from v0.5.x → v1.0.0

1. **YAML Format Changes**
   - Type annotations now required: `!<Insert>`, `!<Helix>`, etc.
   - Field names lowercase: `helices` (not `Helices`)

2. **Constructor Changes**
   - All parameters now type-annotated
   - Required vs optional parameters clarified
   - New validation on all inputs

3. **Method Signature Changes**
   - `from_dict(values: Dict[str, Any], debug: bool = False)`
   - `from_yaml(filename: str, debug: bool = False)`
   - `write_json()` → `write_to_json()`

4. **New Features**
   - `ValidationError` exceptions for invalid data
   - Enum types (e.g., `ShapePosition`)
   - Automatic YAML constructor registration

**See [BREAKING_CHANGES.md](BREAKING_CHANGES.md) for complete migration guide and migration scripts.**

### Version History

#### Version 1.0.0 (Current)
- **Major refactor** - Complete rewrite of internal architecture
- **Type safety** - Full type annotations and validation
- **YAML 2.0** - Enhanced structured format (builds on v0.7.0)
- **Profile class** - New class for bump profile management with DAT file export
- **Enhanced Shape** - Profile integration, ShapePosition enum, flexible positioning
- **Breaking changes** - See BREAKING_CHANGES.md
- **New features**: `ValidationError`, `YAMLObjectBase`, automatic YAML registration

#### Version 0.7.0 (Previous Stable)
- **YAML type annotations** - Introduced `!<ClassName>` tags (major change)
- **Lowercase fields** - Changed `Helices` → `helices` (breaking)
- **Internal refactor** - Complete refactor of internal structure
- **Enhanced type system** - Improved YAML type handling
- **Updated API** - Method signature improvements

#### Version 0.6.0
- Major API changes in core geometry classes
- Breaking changes in YAML format structure
- Updated method signatures

#### Version 0.5.x and Earlier
- Legacy format with capitalized fields (`Helices`, `Rings`, etc.)
- No YAML type annotations
- Original API design

#### Version 0.4.0
- Breaking changes in Helix definition
- Rewritten test suite
- Updated serialization methods

#### Version 0.3.x
- Initial development versions
- Original implementations

## Migration Guide

### Quick Assessment: Which Version Are You Using?

```python
# Check your YAML files
# If they look like this, you're on v0.5.x or earlier:
name: "HL-31"
Helices:              # ← Capitalized
  - HL-31_H1

# If they look like this, you're on v0.7.0:
!<Insert>             # ← Has type annotation
name: "HL-31"
helices:              # ← Lowercase
  - HL-31_H1
```

### Migration Path 1: From v0.7.0 to v1.0.0 (Easy!)

Your YAML files are **already compatible**! Focus on Python code:

```bash
# Step 1: Update your code
pip install python_magnetgeo==1.0.0

# Step 2: Add error handling
# See code examples below
```

**Required Python Code Changes:**

```python
# Add this import
from python_magnetgeo.validation import ValidationError

# Wrap your loading code
try:
    insert = Insert.from_yaml("HL-31.yaml")
except ValidationError as e:
    print(f"Configuration error: {e}")
```

**That's it!** Your YAML files work without modification.

**Optional improvements:**
- Update custom classes to inherit from `YAMLObjectBase`
- Add type hints to your code
- Use the `debug` parameter for troubleshooting

### Migration Path 2: From v0.5.x (or earlier) to v1.0.0

Use the provided migration scripts in [BREAKING_CHANGES.md](BREAKING_CHANGES.md):

```bash
# Migrate a single YAML file
python migrate_v5_to_v10.py old_config.yaml new_config.yaml

# Migrate entire directory
python bulk_migrate.py ./old_configs/ ./new_configs/

# Verify migration
python verify_migration.py ./new_configs/
```

### Quick Migration Checklist

- [ ] Update YAML files with type annotations
- [ ] Change `Helices` → `helices` (and similar)
- [ ] Update Python code using the API
- [ ] Add `try/except` blocks for `ValidationError`
- [ ] Update imports for new modules
- [ ] Test all configurations load correctly

## Architecture

### Base Classes

```python
from python_magnetgeo.base import YAMLObjectBase, SerializableMixin

class MyGeometry(YAMLObjectBase):
    """All geometry classes inherit from YAMLObjectBase"""
    yaml_tag = "MyGeometry"

    @classmethod
    def from_dict(cls, values, debug=False):
        """Required implementation"""
        return cls(**values)
```

### Validation System

```python
from python_magnetgeo.validation import GeometryValidator, ValidationError

# Automatic validation in all geometry classes
GeometryValidator.validate_name(name)
GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
GeometryValidator.validate_ascending_order(r, 'r')
```

### Supported Geometry Classes

| Class | Description | YAML Tag |
|-------|-------------|----------|
| `Insert` | Complete magnet insert assembly | `!<Insert>` |
| `Helix` | Helical coil geometry | `!<Helix>` |
| `Ring` | Ring/cylinder geometry | `!<Ring>` |
| `Bitter` | Bitter plate geometry | `!<Bitter>` |
| `Supra` | Superconducting coil | `!<Supra>` |
| `Supras` | Multiple superconducting coils | `!<Supras>` |
| `Bitters` | Multiple bitter plates | `!<Bitters>` |
| `Screen` | Screening geometry | `!<Screen>` |
| `MSite` | Measurement site | `!<MSite>` |
| `Probe` | Probe/sensor definition | `!<Probe>` |
| `Shape` | 2D profile shape | `!<Shape>` |
| `ModelAxi` | Axisymmetric model | `!<ModelAxi>` |
| `Model3D` | 3D CAD model | `!<Model3D>` |
| `Tierod` | Tie rod geometry | `!<Tierod>` |
| `CoolingSlit` | Cooling channel | `!<CoolingSlit>` |

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Trophime/python_magnetgeo.git
cd python_magnetgeo

# Create virtual environment
python -m venv --system-site-packages venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest pytest-cov flake8 black mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=python_magnetgeo --cov-report=html

# Run specific test file
pytest tests/test_helix.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_yaml"
```

### Code Quality

```bash
# Format code with black
black python_magnetgeo/

# Lint with flake8
flake8 python_magnetgeo/ --max-line-length=100

# Type checking with mypy
mypy python_magnetgeo/
```

### Building Documentation

```bash
cd docs
make html
# Open docs/_build/html/index.html
```

## Testing Your Configuration

### Validation Test Script

```python
#!/usr/bin/env python3
"""Test your YAML configuration"""

from python_magnetgeo import Insert
from python_magnetgeo.validation import ValidationError

def test_configuration(yaml_file):
    """Test loading and validating a configuration"""
    try:
        insert = Insert.from_yaml(yaml_file)
        print(f"✓ Successfully loaded: {insert.name}")

        # Test bounding box
        rb, zb = insert.boundingBox()
        print(f"  Radial bounds: {rb[0]:.2f} - {rb[1]:.2f} mm")
        print(f"  Axial bounds: {zb[0]:.2f} - {zb[1]:.2f} mm")

        # Test serialization
        json_str = insert.to_json()
        print(f"  JSON serialization: OK ({len(json_str)} bytes)")

        return True

    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_config.py <yaml_file>")
        sys.exit(1)

    success = test_configuration(sys.argv[1])
    sys.exit(0 if success else 1)
```

## Advanced Usage

### Working with Shape and Profile

#### Profile Class - Aerodynamic Profiles

The `Profile` class represents bump shape profiles as 2D point sequences with optional labels:

```python
from python_magnetgeo import Profile

# Create a profile programmatically
profile = Profile(
    cad="HR-54-116",
    points=[[-5.34, 0], [-3.34, 0], [0, 0.9], [3.34, 0], [5.34, 0]],
    labels=[0, 0, 1, 0, 0]  # Optional region labels
)

# Load from YAML
profile = Profile.from_yaml("my_profile.yaml")

# Generate DAT file for external tools
output_path = profile.generate_dat_file("./output")
print(f"Generated: {output_path}")
# Creates: output/Shape_HR-54-116.dat

# Serialize to YAML
profile.dump()  # Saves to HR-54-116.yaml
```

**Profile YAML Format:**
```yaml
!<Profile>
cad: "NACA-0012"
points:
  - [0, 0]
  - [0.5, 0.05]
  - [1, 0]
labels: [0, 1, 0]  # Optional - defaults to all zeros
```

**DAT File Output:**
```
#Shape : NACA-0012
#
# Profile with region labels
#
#N_i
3
#X_i F_i	Id_i
0.00 0.00	0
0.50 0.05	1
1.00 0.00	0
```

#### Shape Class - Helical Cut Modifications

The `Shape` class defines additional geometric features (cut profiles) applied to helical cuts:

```python
from python_magnetgeo import Shape, Profile
from python_magnetgeo.Shape import ShapePosition

# Method 1: Load Profile separately
profile = Profile.from_yaml("cooling_profile.yaml")
shape = Shape(
    name="cooling_slot",
    profile=profile,
    length=[15.0],       # 15 degrees wide
    angle=[60.0],        # Spaced 60 degrees apart
    onturns=[1, 2, 3],   # First three turns
    position=ShapePosition.ABOVE
)

# Method 2: Reference Profile by filename (automatic loading)
shape = Shape(
    name="vent_holes",
    profile="circular_hole",  # Loads from circular_hole.yaml
    length=[5.0, 10.0],       # Variable lengths
    angle=[45.0],             # Fixed spacing
    onturns=[1, 3, 5, 7],     # Odd turns only
    position="ALTERNATE"      # String or enum accepted
)

# Method 3: Use in Helix configuration
from python_magnetgeo import Helix
helix = Helix(
    name="H1",
    r=[19.3, 24.2],
    z=[-226, 108],
    cutwidth=0.22,
    odd=True,
    dble=True,
    shape=shape  # Attach shape to helix
)
```

**Shape Position Options:**
```python
from python_magnetgeo.Shape import ShapePosition

# Three placement strategies:
shape1 = Shape(..., position=ShapePosition.ABOVE)     # All above
shape2 = Shape(..., position=ShapePosition.BELOW)     # All below
shape3 = Shape(..., position=ShapePosition.ALTERNATE) # Alternating

# Case-insensitive string also works:
shape4 = Shape(..., position="above")      # Converted to enum
shape5 = Shape(..., position="BELOW")      # Converted to enum
shape6 = Shape(..., position="alternate")  # Converted to enum
```

**Complete Helix with Shape YAML:**
```yaml
!<Helix>
name: "HL-31_H1"
odd: true
r: [19.3, 24.2]
z: [-226, 108]
dble: true
cutwidth: 0.22
shape: !<Shape>
  name: "cooling_channels"
  profile: "02_10_2014_H1"  # References Profile YAML file
  length: [15.0]
  angle: [60, 90, 120, 120]
  onturns: [1, 2, 3, 4, 5]
  position: ALTERNATE
```

**Key Features:**
- **Profile References**: Shape can reference Profile by name (string) or object
- **Automatic Loading**: String profile names automatically load from `{profile}.yaml`
- **Flexible Positioning**: Enum or case-insensitive string for position
- **Multi-Turn Support**: Apply shapes to specific turns or patterns
- **Variable Parameters**: Different lengths/angles for different positions

### Lazy Loading with getObject()

The `getObject()` utility provides automatic type detection and loading for YAML files:

```python
from python_magnetgeo.utils import getObject

# Automatically detects type from YAML annotation and loads
geometry = getObject("config.yaml")

# Returns the appropriate instance:
# - Insert if YAML starts with !<Insert>
# - Helix if YAML starts with !<Helix>
# - Ring if YAML starts with !<Ring>
# etc.

print(f"Type: {type(geometry).__name__}")
print(f"Name: {geometry.name}")
```

#### CLI Tool Example with Lazy Loading

```python
#!/usr/bin/env python3
"""Generic geometry viewer using lazy loading"""

import sys
from python_magnetgeo.utils import getObject
from python_magnetgeo.validation import ValidationError

def display_geometry_info(filename: str):
    """Display information about any geometry file"""
    try:
        # Load without knowing the type
        obj = getObject(filename)

        print(f"File: {filename}")
        print(f"Type: {type(obj).__name__}")
        print(f"Name: {obj.name}")

        # Check for common attributes
        if hasattr(obj, 'r'):
            print(f"Radial range: {obj.r}")
        if hasattr(obj, 'z'):
            print(f"Axial range: {obj.z}")
        if hasattr(obj, 'boundingBox'):
            rb, zb = obj.boundingBox()
            print(f"Bounding box: r=[{rb[0]:.2f}, {rb[1]:.2f}], z=[{zb[0]:.2f}, {zb[1]:.2f}]")
        if hasattr(obj, 'helices'):
            print(f"Number of helices: {len(obj.helices)}")
        if hasattr(obj, 'rings'):
            print(f"Number of rings: {len(obj.rings)}")

        return obj

    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading {filename}: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view_geometry.py <yaml_file>")
        sys.exit(1)

    obj = display_geometry_info(sys.argv[1])
    sys.exit(0 if obj else 1)
```

#### Dynamic Type Handling

```python
from python_magnetgeo.utils import getObject
from python_magnetgeo import Insert, Helix, Ring, Bitter

def process_geometry(filename: str):
    """Process geometry with type-specific logic"""
    obj = getObject(filename)

    # Type-specific processing
    if isinstance(obj, Insert):
        print(f"Processing insert with {len(obj.helices)} helices")
        for helix_name in obj.helices:
            print(f"  - {helix_name}")

    elif isinstance(obj, Helix):
        print(f"Processing helix: {obj.name}")
        print(f"  Radial: {obj.r[0]:.2f} - {obj.r[1]:.2f} mm")
        print(f"  Axial: {obj.z[0]:.2f} - {obj.z[1]:.2f} mm")
        print(f"  Double: {obj.dble}, Odd: {obj.odd}")

    elif isinstance(obj, Ring):
        print(f"Processing ring: {obj.name}")
        print(f"  Inner/Outer radius: {obj.r}")
        print(f"  Height: {obj.z[1] - obj.z[0]:.2f} mm")

    elif isinstance(obj, Bitter):
        print(f"Processing Bitter: {obj.name}")
        if obj.coolingslits:
            print(f"  Cooling slits: {len(obj.coolingslits)}")
        if obj.tierod:
            print(f"  Tie rods: present")

    else:
        print(f"Processing {type(obj).__name__}: {obj.name}")

    return obj

# Usage
for config_file in ["HL-31.yaml", "H1.yaml", "Ring-01.yaml", "Bitter-01.yaml"]:
    print(f"\n{'='*60}")
    process_geometry(config_file)
```

#### Configuration Validator with Lazy Loading

```python
#!/usr/bin/env python3
"""Validate all YAML configurations in a directory"""

from pathlib import Path
from python_magnetgeo.utils import getObject
from python_magnetgeo.validation import ValidationError

def validate_configs(directory: str, verbose: bool = False):
    """Validate all YAML files using lazy loading"""

    yaml_files = list(Path(directory).glob("*.yaml"))
    results = {
        'valid': [],
        'invalid': [],
        'errors': []
    }

    print(f"Validating {len(yaml_files)} YAML files in {directory}...")

    for yaml_file in yaml_files:
        try:
            obj = getObject(str(yaml_file))
            results['valid'].append({
                'file': yaml_file.name,
                'type': type(obj).__name__,
                'name': obj.name
            })
            if verbose:
                print(f"✓ {yaml_file.name}: {type(obj).__name__} '{obj.name}'")

        except ValidationError as e:
            results['invalid'].append({
                'file': yaml_file.name,
                'error': str(e)
            })
            print(f"✗ {yaml_file.name}: Validation error - {e}")

        except Exception as e:
            results['errors'].append({
                'file': yaml_file.name,
                'error': str(e)
            })
            print(f"✗ {yaml_file.name}: Error - {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Validation Summary:")
    print(f"  Valid:   {len(results['valid'])} files")
    print(f"  Invalid: {len(results['invalid'])} files")
    print(f"  Errors:  {len(results['errors'])} files")

    if results['valid']:
        print(f"\nValid configurations by type:")
        from collections import Counter
        type_counts = Counter(item['type'] for item in results['valid'])
        for obj_type, count in type_counts.items():
            print(f"  {obj_type}: {count}")

    return results

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    results = validate_configs(directory, verbose)

    # Exit with error if any invalid or errors
    sys.exit(0 if not (results['invalid'] or results['errors']) else 1)
```

### Custom Geometry Classes

```python
from python_magnetgeo.base import YAMLObjectBase
from python_magnetgeo.validation import GeometryValidator, ValidationError
from typing import List, Optional

class CustomCoil(YAMLObjectBase):
    """Custom coil geometry"""
    yaml_tag = "CustomCoil"

    def __init__(self, name: str, r: List[float], z: List[float],
                 turns: int, current: float):
        # Validate inputs
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
        GeometryValidator.validate_ascending_order(r, 'r')

        self.name = name
        self.r = r
        self.z = z
        self.turns = turns
        self.current = current

    @classmethod
    def from_dict(cls, values, debug=False):
        """Create from dictionary"""
        return cls(
            name=values['name'],
            r=values['r'],
            z=values['z'],
            turns=values.get('turns', 1),
            current=values.get('current', 0.0)
        )

    def compute_inductance(self) -> float:
        """Custom method"""
        # Your computation here
        pass

# Use it
coil = CustomCoil(
    name="my_coil",
    r=[10.0, 20.0],
    z=[0.0, 50.0],
    turns=100,
    current=1000.0
)
coil.dump()  # Saves to my_coil.yaml
```

### Batch Processing

```python
from pathlib import Path
from python_magnetgeo import Insert, Helix

def process_yaml_directory(directory: str):
    """Process all YAML files in directory"""
    results = []

    for yaml_file in Path(directory).glob("*.yaml"):
        try:
            # Try loading as Insert
            obj = Insert.from_yaml(str(yaml_file))
            print(f"✓ Loaded Insert: {obj.name}")
            results.append((yaml_file.name, "Insert", obj))
        except:
            try:
                # Try loading as Helix
                obj = Helix.from_yaml(str(yaml_file))
                print(f"✓ Loaded Helix: {obj.name}")
                results.append((yaml_file.name, "Helix", obj))
            except Exception as e:
                print(f"✗ Failed to load {yaml_file.name}: {e}")

    return results

# Usage
results = process_yaml_directory("./configs/")
print(f"\nProcessed {len(results)} configurations")
```

### Programmatic Mesh Generation

```python
from python_magnetgeo import Insert
from python_magnetgeo.xao import create_mesh

# Load configuration
insert = Insert.from_yaml("HL-31.yaml")

# Generate CAD (requires Salome)
# ... (use Salome API)

# Create mesh from XAO
mesh = create_mesh(
    xao_file="HL-31-Axi.xao",
    groups=["CoolingChannels", "Conductors"],
    geometry_file="HL-31.yaml"
)
```

## Troubleshooting

### Common Issues

#### ValidationError: "r values must be in ascending order"

```python
# Wrong
ring = Ring(name="r1", r=[20.0, 10.0], z=[0, 10])

# Correct
ring = Ring(name="r1", r=[10.0, 20.0], z=[0, 10])
```

#### YAML Loading Error: "could not determine a constructor"

Make sure your YAML has type annotations:

```yaml
# Wrong
name: "HL-31"
helices: [...]

# Correct
!<Insert>
name: "HL-31"
helices: [...]
```

#### Import Error: "cannot import name 'ValidationError'"

```python
# Correct import
from python_magnetgeo.validation import ValidationError
```

#### getObject() Returns None or Fails

The `getObject()` function requires YAML files with type annotations:

```python
from python_magnetgeo.utils import getObject

# This will fail if YAML doesn't have !<TypeName> annotation
try:
    obj = getObject("config.yaml")
    if obj is None:
        print("Failed to load - check YAML format")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure YAML starts with type annotation like !<Insert>")
```

**Fix**: Ensure your YAML file has proper type annotation:
```yaml
!<Insert>
name: "my_insert"
# ... rest of config
```

#### Type Confusion with Lazy Loading

```python
from python_magnetgeo.utils import getObject
from python_magnetgeo import Insert, Helix

# getObject returns the actual type
obj = getObject("unknown_type.yaml")

# Always check type before using type-specific attributes
if isinstance(obj, Insert):
    print(f"Insert with {len(obj.helices)} helices")
elif isinstance(obj, Helix):
    print(f"Helix: r={obj.r}, z={obj.z}")
else:
    print(f"Unknown type: {type(obj).__name__}")
```

### Debug Mode

Enable debug output when loading:

```python
insert = Insert.from_yaml("HL-31.yaml", debug=True)
# Prints detailed loading information
```

## Performance Considerations

- **YAML loading**: ~10-50ms for typical configurations
- **Validation overhead**: <1ms per object
- **JSON serialization**: ~1-5ms for typical objects
- **Memory usage**: ~1-10MB per complex Insert configuration

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes**
4. **Add tests**: Ensure new code is tested
5. **Run test suite**: `pytest`
6. **Check code quality**: `black .` and `flake8`
7. **Update documentation**: Add docstrings and update README if needed
8. **Submit pull request**: With clear description of changes

### Contribution Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public methods
- Maintain test coverage above 80%
- Update CHANGELOG.md for user-facing changes

### Reporting Issues

When reporting issues, please include:

- Python version
- python_magnetgeo version
- Minimal reproducible example
- Full error traceback
- YAML configuration (if applicable)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Documentation

Full documentation is available at: https://python-magnetgeo.readthedocs.io

### Documentation Contents

- **User Guide**: Getting started, tutorials, examples
- **API Reference**: Complete class and method documentation
- **Migration Guide**: Detailed migration instructions
- **Developer Guide**: Contributing, architecture, testing

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

### Authors

- **Christophe Trophime** - Lead Developer - <christophe.trophime@lncmi.cnrs.fr>
- **Romain Vallet** - Contributor - <romain.vallet@lncmi.cnrs.fr>
- **Jeremie Muzet** - Contributor - <jeremie.muzet@lncmi.cnrs.fr>

### Acknowledgments

- LNCMI (Laboratoire National des Champs Magnétiques Intenses)
- CNRS (Centre National de la Recherche Scientifique)

## Support

### Getting Help

- **Documentation**: https://python-magnetgeo.readthedocs.io
- **GitHub Issues**: https://github.com/Trophime/python_magnetgeo/issues
- **Email**: christophe.trophime@lncmi.cnrs.fr

### Professional Support

For professional support, custom development, or consulting services, please contact LNCMI.

## Citation

If you use python_magnetgeo in your research, please cite:

```bibtex
@software{python_magnetgeo,
  author = {Trophime, Christophe and Vallet, Romain and Muzet, Jeremie},
  title = {Python Magnet Geometry},
  version = {1.0.0},
  year = {2025},
  url = {https://github.com/Trophime/python_magnetgeo}
}
```

## TODOs

- [ ] Replace str profile by Profile object in Shape.py
- [ ] Add method to convert dat file for profile into yaml profile file
- [ ] Change gtype to type into Groove (breaking change)
- [ ] Make type an enum in Groove
- [ ] Make side and rside enum objects in Chamfer
- [ ] All field that can be either Object/str make str=filename to be loaded (breaking change)

## Related Projects

- **hifimagnet.salome**: Salome integration for CAD/mesh generation
- **feelpp**: Finite element library for electromagnetics simulation

## Roadmap

### Version 1.1.0 (Planned)
- Additional geometry types (solenoids, gradient coils)
- Enhanced mesh generation options
- Performance optimizations

### Version 1.2.0 (Planned)
- GUI configuration editor
- Visualization tools
- Enhanced CAD export formats

### Version 2.0.0 (Future)
- Python 3.13+ support
- Async I/O for large files
- Cloud integration

---

**Version 1.0.0** | Released: 2025 | [Changelog](CHANGELOG.md) | [Breaking Changes](BREAKING_CHANGES.md)
