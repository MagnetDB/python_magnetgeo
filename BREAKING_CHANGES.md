# API Breaking Changes - python_magnetgeo v1.0.0

## Overview

This document details all API breaking changes introduced in version 1.0.0 compared to previous versions (0.3.x - 0.7.x). **No backward compatibility is provided.**

## Version History Summary

### v1.0.0 (Current) - Major Architectural Overhaul
- Complete rewrite with base class architecture
- Enhanced type safety and validation system
- **New Profile class** for bump profile management
- **Enhanced Shape class** with Profile integration and ShapePosition enum
- Breaking changes from all previous versions

### v0.7.0 - YAML Type System Enhancement
- **Introduced YAML type annotations** (`!<ClassName>`)
- **Field names changed to lowercase** (`Helices` → `helices`)
- Enhanced YAML type system
- Updated API methods
- Complete refactor of internal structure

### v0.6.0 - Core API Changes
- Major API changes in core geometry classes
- Breaking changes in YAML format structure
- Updated method signatures

### v0.5.x - Pre-annotation Era
- Used capitalized field names (`Helices`, `Rings`, `CurrentLeads`)
- No YAML type annotations
- Legacy serialization methods

### v0.4.0 - Helix Definition Changes
- Breaking changes in Helix definition
- Rewritten test suite
- Updated serialization methods

### v0.3.x - Initial Versions
- Initial development releases
- Original API design

---

## 1. YAML Format Changes

### Evolution Across Versions

#### v0.5.x and earlier (Legacy Format)
```yaml
name: "HL-31"
Helices:
  - HL-31_H1
  - HL-31_H2
Rings:
  - Ring-H1H2
CurrentLeads:
  - inner
```

#### v0.7.0 (Type Annotation Introduction)
```yaml
!<Insert>
name: "HL-31"
helices:
  - HL-31_H1
  - HL-31_H2
rings:
  - Ring-H1H2
currentleads:
  - inner
```

#### v1.0.0 (Current - Enhanced Validation)
```yaml
!<Insert>
name: "HL-31"
helices:
  - HL-31_H1
  - HL-31_H2
rings:
  - Ring-H1H2
currentleads:
  - inner
innerbore: 18.54
outerbore: 186.25
```

**Key Changes:**
- **v0.5.x → v0.7.0**: Introduced type annotations (`!<ClassName>`), lowercase field names
- **v0.7.0 → v1.0.0**: Enhanced validation, additional optional fields, stricter type checking

### 1.1 Type Annotations Required (Since v0.7.0)

**Old Format (v0.5.x and earlier):**
```yaml
name: "HL-31"
Helices:
  - HL-31_H1
  - HL-31_H2
Rings:
  - Ring-H1H2
CurrentLeads:
  - inner
```

**New Format (v1.0.0):**
```yaml
!<Insert>
name: "HL-31"
helices:
  - HL-31_H1
  - HL-31_H2
rings:
  - Ring-H1H2
currentleads:
  - inner
```

**Breaking Changes:**
- All YAML files MUST include type annotation tags (`!<ClassName>`)
- Field names are now lowercase
- No implicit type inference

### 1.2 Field Name Changes

#### Complete Field Name Migration History

| Field (v0.5.x) | Field (v0.7.0) | Field (v1.0.0) | Status in v1.0.0 |
|----------------|----------------|----------------|------------------|
| `Helices` | `helices` | `helices` | ✓ Required |
| `Rings` | `rings` | `rings` | ✓ Required |
| `CurrentLeads` | `currentleads` | `currentleads` | Optional |
| `HAngles` | `hangles` | `hangles` | Optional |
| `RAngles` | `rangles` | `rangles` | Optional |
| `Supras` | `supras` | `supras` | Optional |
| `Bitters` | `bitters` | `bitters` | Optional |
| - | - | `innerbore` | **New in v1.0.0** |
| - | - | `outerbore` | **New in v1.0.0** |
| - | - | `probes` | **New in v1.0.0** |

**Migration Notes:**
- **v0.5.x → v0.7.0**: All field names changed to lowercase
- **v0.7.0 → v1.0.0**: Field names unchanged, but new optional fields added

### 1.3 Nested Object Structure

**Old Format:**
```yaml
name: "HL-31_H1"
axi:
  name: "HL-31.d"
  h: 86.51
```

**New Format:**
```yaml
!<Helix>
name: "HL-31_H1"
axi: !<ModelAxi>
  name: "HL-31.d"
  h: 86.51
```

**Breaking Changes:**
- Nested objects require explicit type annotations
- All nested structures must follow new format

---

## 2. Class API Changes

### Version Comparison Overview

| Aspect | v0.5.x | v0.7.0 | v1.0.0 |
|--------|--------|--------|--------|
| YAML Annotations | ✗ None | ✓ Required | ✓ Required |
| Field Names | Capitalized | lowercase | lowercase |
| Type Hints | Partial | Enhanced | Comprehensive |
| Validation | Basic | Enhanced | Strict + ValidationError |
| Base Classes | Individual | Refactored | YAMLObjectBase |
| Auto Registration | Manual | Semi-auto | Fully automatic |
| Error Messages | Generic | Improved | Detailed |
| Profile Class | ✗ None | ✗ None | ✓ New Class |
| Shape Integration | Limited | Limited | ✓ Profile Support |

### Key Differences: v0.7.0 → v1.0.0

#### What Changed
1. **Base class architecture** - All classes now inherit from `YAMLObjectBase`
2. **Validation system** - New `ValidationError` with descriptive messages
3. **Type safety** - Stricter type checking and enforcement
4. **Method signatures** - Added `debug` parameter to `from_dict()` and loading methods
5. **Automatic YAML registration** - No manual constructor functions needed

#### What Stayed the Same
1. **YAML format** - Type annotations and lowercase fields (from v0.7.0)
2. **Basic API** - Core methods like `from_yaml()`, `dump()`, `to_json()`
3. **Constructor parameters** - Most constructors have same signature

### 2.1 Constructor Signatures

#### Helix
**Old:**
```python
Helix(name, r, z, cutwidth, odd=True, dble=False)
```

**New:**
```python
Helix(
    name: str,
    r: List[float],
    z: List[float],
    cutwidth: float,
    odd: bool,
    dble: bool,
    axi: Optional[ModelAxi] = None,
    model3d: Optional[Model3D] = None,
    shape: Optional[Shape] = None
)
```

**Breaking Changes:**
- Removed default values for `odd` and `dble` (now required)
- Added type hints (strictly enforced)
- New optional parameters: `axi`, `model3d`, `shape`

#### Ring
**Old:**
```python
Ring(name, r, z)
```

**New:**
```python
Ring(
    name: str,
    r: List[float],
    z: List[float],
    n: int = 0,
    angle: float = 0,
    bpside: bool = True,
    fillets: bool = False,
    cad: Optional[str] = None
)
```

**Breaking Changes:**
- All parameters now have explicit types
- New optional parameters with defaults

#### Insert
**Old:**
```python
Insert(name, Helices=[], Rings=[], CurrentLeads=[])
```

**New:**
```python
Insert(
    name: str,
    helices: List[Union[str, Helix]] = None,
    rings: List[Union[str, Ring]] = None,
    currentleads: List[str] = None,
    hangles: List[float] = None,
    rangles: List[float] = None,
    supras: List[Union[str, Supra]] = None,
    bitters: List[Union[str, Bitter]] = None,
    innerbore: float = 0,
    outerbore: float = 0,
    probes: List[Probe] = None
)
```

**Breaking Changes:**
- Parameter names changed to lowercase
- Parameters are now `None` by default (not empty lists)
- Added new parameters: `supras`, `bitters`, `innerbore`, `outerbore`, `probes`

### 2.2 Method Signature Changes

#### from_dict() - All Classes
**Old:**
```python
@classmethod
def from_dict(cls, values):
    return cls(name=values["name"], ...)
```

**New:**
```python
@classmethod
def from_dict(cls, values: Dict[str, Any], debug: bool = False) -> T:
    """Type-safe dictionary loading with validation"""
    return cls(name=values["name"], ...)
```

**Breaking Changes:**
- Added `debug` parameter
- Return type annotation
- Input validation enforced
- Will raise `ValidationError` for invalid data

#### from_yaml() / from_json()
**Old:**
```python
@classmethod
def from_yaml(cls, filename):
    # Manual YAML loading
    with open(filename) as f:
        data = yaml.safe_load(f)
    return cls.from_dict(data)
```

**New:**
```python
@classmethod
def from_yaml(cls: Type[T], filename: str, debug: bool = False) -> T:
    """Automatic YAML constructor registration"""
    return cls.load_from_yaml(filename, debug)
```

**Breaking Changes:**
- Now uses inherited `load_from_yaml()` method
- Automatic type registration
- Added `debug` parameter

---

## 3. Validation and Error Handling

### 3.1 New Validation System

**Old Behavior:**
```python
# Silent failures or generic exceptions
ring = Ring("test", r=[10, 5], z=[0, 10])  # Invalid: r not ascending
# May work or fail unpredictably
```

**New Behavior:**
```python
from python_magnetgeo.validation import ValidationError

ring = Ring("test", r=[10, 5], z=[0, 10])
# Raises: ValidationError: r values must be in ascending order
```

**Breaking Changes:**
- All geometry classes now validate inputs
- Raises `ValidationError` with descriptive messages
- No silent failures

### 3.2 Validation Rules

All classes now enforce:
- **Name validation**: Non-empty strings, no special characters
- **Numeric lists**: Correct length and ordering
- **Range checks**: Physical constraints (e.g., r[0] >= 0)
- **Type checking**: Strict type enforcement

---

## 4. Serialization Changes

### 4.1 JSON Format

**Old Format:**
```json
{
  "name": "test_helix",
  "r": [10.0, 20.0],
  "z": [0.0, 50.0]
}
```

**New Format:**
```json
{
  "__classname__": "Helix",
  "name": "test_helix",
  "r": [10.0, 20.0],
  "z": [0.0, 50.0],
  "odd": true,
  "dble": false,
  "cutwidth": 0.2
}
```

**Breaking Changes:**
- Added `__classname__` field
- All fields explicitly included (no defaults)
- Consistent with YAML type annotations

### 4.2 Method Names

| Old Method | New Method | Notes |
|-----------|-----------|-------|
| `write_json()` | `write_to_json()` | Renamed for clarity |
| `load()` | `load_from_yaml()` | More explicit |
| - | `load_from_json()` | New method |

---

## 5. Base Class Hierarchy

### 5.1 New Base Classes

**v1.0.0 introduces:**
```python
from python_magnetgeo.base import YAMLObjectBase

class MyGeometry(YAMLObjectBase):
    yaml_tag = "MyGeometry"
    
    def __init__(self, ...):
        ...
    
    @classmethod
    def from_dict(cls, values, debug=False):
        ...
```

**Breaking Changes:**
- All geometry classes must inherit from `YAMLObjectBase`
- Must implement `from_dict()` classmethod
- Must define `yaml_tag` class attribute
- Automatic YAML constructor registration

---

## 6. Enum Types

### 6.1 Shape Position

**Old:**
```python
shape = Shape(name="s", profile="p", position="above")
# String-based, case-sensitive
```

**New:**
```python
from python_magnetgeo.Shape import ShapePosition

shape = Shape(name="s", profile="p", position=ShapePosition.ABOVE)
# Or case-insensitive string
shape = Shape(name="s", profile="p", position="above")  # Still works
```

**Breaking Changes:**
- Introduced `ShapePosition` enum
- Accepts enum or case-insensitive string
- Invalid positions raise `ValidationError`

### 6.2 New Profile Class (v1.0.0)

**Introduction:**

Version 1.0.0 introduces the `Profile` class for representing bump profiles as 2D point sequences. This is a new addition (not a breaking change) that provides structured profile data management.

**Profile Class Structure:**
```python
from python_magnetgeo import Profile

profile = Profile(
    cad="HR-54-116",                    # CAD identifier
    points=[[-5.34, 0], [0, 0.9], ...], # List of [X, F] coordinates
    labels=[0, 1, 0, ...]               # Optional integer labels per point
)
```

**YAML Format:**
```yaml
!<Profile>
cad: "HR-54-116"
points:
  - [-5.34, 0]
  - [-3.34, 0]
  - [0, 0.9]
  - [3.34, 0]
  - [5.34, 0]
labels: [0, 0, 1, 0, 0]  # Optional - defaults to all zeros if omitted
```

**Features:**
- **DAT File Generation**: `profile.generate_dat_file("./output")` creates Shape_*.dat files
- **Full Serialization**: YAML and JSON support via `from_yaml()`, `to_json()`, `dump()`
- **Validation**: Automatic label length validation against points
- **Optional Labels**: Labels default to zeros if not provided

**Example Usage:**
```python
# Load from YAML
profile = Profile.from_yaml("aerodynamic_profile.yaml")

# Generate DAT file for external tools
output = profile.generate_dat_file("./data")
print(f"Created: {output}")  # data/Shape_aerodynamic_profile.dat

# Serialize
profile.dump()  # Saves to aerodynamic_profile.yaml
json_data = profile.to_json()
```

**Migration Impact:**
- **New Feature Only**: No changes required to existing code
- **Backward Compatible**: Existing YAML files unaffected
- **Optional Usage**: Only needed when working with aerodynamic profiles

### 6.3 Enhanced Shape Class (v1.0.0)

**Major Enhancement:**

The `Shape` class has been significantly enhanced to support `Profile` objects and provide better type safety.

**Old Structure (Conceptual):**
```python
# Previous versions (if existed) used simple string references
shape = Shape(name="s", profile="profile_name", ...)
```

**New Structure (v1.0.0):**
```python
from python_magnetgeo import Shape, Profile
from python_magnetgeo.Shape import ShapePosition

# Method 1: Reference Profile by name (auto-loads from YAML)
shape = Shape(
    name="cooling_slot",
    profile="my_profile",      # Loads from my_profile.yaml
    length=[15.0],             # Angular length in degrees
    angle=[60.0, 90.0],        # Angles between shapes
    onturns=[1, 2, 3],         # Turns to apply shape
    position=ShapePosition.ABOVE  # or "ABOVE", "BELOW", "ALTERNATE"
)

# Method 2: Use Profile object directly
profile = Profile.from_yaml("my_profile.yaml")
shape = Shape(
    name="cooling_slot",
    profile=profile,           # Direct Profile object
    length=[15.0],
    angle=[60.0],
    onturns=[1],
    position="ALTERNATE"       # Case-insensitive string
)
```

**Complete Shape Constructor:**
```python
Shape(
    name: str,                          # Shape identifier (required)
    profile: Profile | str,             # Profile object or filename (required)
    length: list[float] = None,        # Defaults to [0.0]
    angle: list[float] = None,         # Defaults to [0.0]
    onturns: list[int] = None,         # Defaults to [1]
    position: ShapePosition | str = ShapePosition.ABOVE
)
```

**YAML Format:**
```yaml
!<Shape>
name: "cooling_channels"
profile: "02_10_2014_H1"  # References Profile YAML file
length: [15.0]
angle: [60, 90, 120, 120]
onturns: [1, 2, 3, 4, 5]
position: ALTERNATE
```

**Embedded in Helix:**
```yaml
!<Helix>
name: "HL-31_H1"
odd: true
r: [19.3, 24.2]
z: [-226, 108]
dble: true
cutwidth: 0.22
shape: !<Shape>
  name: "cooling_slot"
  profile: "aerodynamic_cut"
  length: [15.0]
  angle: [60, 90, 120]
  onturns: [1, 3, 5]
  position: ALTERNATE
```

**Key Features:**
- **Profile Integration**: Profile can be string (auto-loads) or Profile object
- **Type Safety**: ShapePosition enum with string fallback
- **Flexible Parameters**: All list parameters have sensible defaults
- **Position Options**: ABOVE, BELOW, ALTERNATE (case-insensitive)
- **Validation**: Automatic position validation with clear error messages

**Breaking Changes:**
- **Type Annotations**: `profile` parameter now accepts `Profile | str` (was just `str`)
- **Position Enum**: Position must be valid ShapePosition value or string
- **Required Parameters**: `name` and `profile` are required (no defaults)
- **List Types**: `length`, `angle`, `onturns` are now properly typed as `list[float]` or `list[int]`

**Migration Notes:**
- Existing YAML files with string profile references continue to work
- Position strings are now case-insensitive ("above", "ABOVE", "Above" all work)
- Invalid position values now raise `ValidationError` instead of silent failure
- Profile auto-loading looks for `{profile}.yaml` in current directory or base directory

---

## 7. Import Changes

### 7.1 Validation Module

**New imports required:**
```python
from python_magnetgeo.validation import ValidationError, GeometryValidator
```

### 7.2 Base Classes

**New imports available:**
```python
from python_magnetgeo.base import YAMLObjectBase, SerializableMixin
```

### 7.3 Shape and Profile Classes (v1.0.0)

**New imports for bump profiles and shape definitions:**
```python
# Profile class for bump profiles
from python_magnetgeo import Profile

# Shape class and position enum
from python_magnetgeo import Shape
from python_magnetgeo.Shape import ShapePosition

# Example usage
profile = Profile.from_yaml("my_profile.yaml")
shape = Shape(
    name="slot",
    profile=profile,
    position=ShapePosition.ALTERNATE
)
```

---

## 8. Removed Features

### 8.1 Deprecated Methods

The following methods were removed:

| Removed Method | Replacement |
|---------------|-------------|
| `loadYamlOld()` | `load_from_yaml()` |
| `from_yaml_old()` | `from_yaml()` |
| `simple_load()` | `from_dict()` |

### 8.2 Deprecated Parameters

| Class | Removed Parameter | Reason |
|-------|------------------|--------|
| All | `legacy_mode` | No backward compatibility |
| Insert | `strict=False` | Always strict now |

---

## 9. Migration Scripts

### 9.1 YAML Migration: v0.7.0 → v1.0.0

**Important**: If you're already on v0.7.0, the YAML format is largely compatible with v1.0.0. The main changes are in the Python API, not the YAML structure.

```python
#!/usr/bin/env python3
"""Migrate from v0.7.0 to v1.0.0 - mainly validates format compatibility"""

import yaml
import sys
from pathlib import Path

def migrate_yaml_v7_to_v10(old_file: str, new_file: str):
    """
    Migrate YAML from v0.7.0 to v1.0.0 format.
    
    v0.7.0 already uses type annotations and lowercase fields,
    so this mainly validates compatibility and updates any
    remaining legacy patterns.
    """
    
    with open(old_file, 'r') as f:
        content = f.read()
    
    # v0.7.0 should already have type annotations
    if not content.strip().startswith('!<'):
        print(f"⚠ Warning: {old_file} missing type annotation")
        print("  Adding type annotation based on content analysis...")
        
        data = yaml.safe_load(content)
        
        # Detect type
        if 'helices' in data:
            content = f"!<Insert>\n{content}"
        elif 'r' in data and 'z' in data and 'cutwidth' in data:
            content = f"!<Helix>\n{content}"
        elif 'r' in data and 'z' in data:
            content = f"!<Ring>\n{content}"
    
    # Write validated content
    with open(new_file, 'w') as f:
        f.write(content)
    
    # Validate it loads correctly
    try:
        with open(new_file, 'r') as f:
            yaml.safe_load(f)
        print(f"✓ Validated: {old_file} → {new_file}")
        return True
    except Exception as e:
        print(f"✗ Validation failed for {new_file}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_v7_to_v10.py <old_yaml> <new_yaml>")
        sys.exit(1)
    
    success = migrate_yaml_v7_to_v10(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
```

### 9.2 YAML Migration: v0.5.x → v1.0.0

```python
#!/usr/bin/env python3
"""Migrate YAML files from v0.5.x to v1.0.0 format"""

import yaml
import sys
from pathlib import Path

def migrate_yaml_v5_to_v10(old_file: str, new_file: str):
    """Migrate YAML from v0.5.x to v1.0.0 format"""
    
    with open(old_file, 'r') as f:
        data = yaml.safe_load(f)
    
    if not data:
        return
    
    # Field name migrations
    field_mapping = {
        'Helices': 'helices',
        'Rings': 'rings',
        'CurrentLeads': 'currentleads',
        'HAngles': 'hangles',
        'RAngles': 'rangles',
        'Supras': 'supras',
        'Bitters': 'bitters'
    }
    
    # Apply field name changes
    for old_key, new_key in field_mapping.items():
        if old_key in data:
            data[new_key] = data.pop(old_key)
    
    # Detect and add type annotation
    type_annotation = None
    if 'helices' in data or 'Helices' in data:
        type_annotation = '!<Insert>'
    elif 'r' in data and 'z' in data and 'cutwidth' in data:
        type_annotation = '!<Helix>'
    elif 'r' in data and 'z' in data:
        type_annotation = '!<Ring>'
    
    # Write with type annotation
    with open(new_file, 'w') as f:
        if type_annotation:
            f.write(f"{type_annotation}\n")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Migrated: {old_file} → {new_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_v5_to_v10.py <old_yaml> <new_yaml>")
        sys.exit(1)
    
    migrate_yaml_v5_to_v10(sys.argv[1], sys.argv[2])
```

### 9.2 Bulk Migration Script

```python
#!/usr/bin/env python3
"""Bulk migrate all YAML files in a directory"""

import yaml
import sys
from pathlib import Path

def migrate_directory(input_dir: str, output_dir: str):
    """Migrate all YAML files in directory"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    yaml_files = list(input_path.glob("*.yaml")) + list(input_path.glob("*.yml"))
    
    print(f"Found {len(yaml_files)} YAML files to migrate")
    
    for yaml_file in yaml_files:
        try:
            old_file = str(yaml_file)
            new_file = str(output_path / yaml_file.name)
            migrate_yaml_v5_to_v10(old_file, new_file)
        except Exception as e:
            print(f"✗ Failed to migrate {yaml_file.name}: {e}")
    
    print(f"\n✓ Migration complete. Files saved to: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bulk_migrate.py <input_dir> <output_dir>")
        sys.exit(1)
    
    migrate_directory(sys.argv[1], sys.argv[2])
```

### 9.3 Code Migration: v0.7.0 → v1.0.0

#### Step 1: Update Imports

```python
# Add new imports for validation
from python_magnetgeo.validation import ValidationError

# Optional: Import base classes if creating custom geometries
from python_magnetgeo.base import YAMLObjectBase
```

#### Step 2: Add Error Handling

**v0.7.0 code:**
```python
from python_magnetgeo import Insert

insert = Insert.from_yaml("HL-31.yaml")
# May fail silently or with generic errors
```

**v1.0.0 code:**
```python
from python_magnetgeo import Insert
from python_magnetgeo.validation import ValidationError

try:
    insert = Insert.from_yaml("HL-31.yaml")
except ValidationError as e:
    print(f"Configuration error: {e}")
    # Handle validation failure
except Exception as e:
    print(f"Loading error: {e}")
    # Handle other errors
```

#### Step 3: Update from_dict Calls

**v0.7.0:**
```python
helix = Helix.from_dict(helix_data)
```

**v1.0.0:**
```python
# Optional debug parameter now available
helix = Helix.from_dict(helix_data, debug=True)
```

#### Step 4: Handle Validation Errors

```python
from python_magnetgeo import Ring
from python_magnetgeo.validation import ValidationError

# v1.0.0 validates inputs strictly
try:
    ring = Ring(
        name="my_ring",
        r=[10.0, 20.0],  # Must be ascending
        z=[0.0, 10.0]    # Must be ascending
    )
except ValidationError as e:
    # New in v1.0.0: descriptive validation errors
    print(f"Invalid geometry: {e}")
```

#### Step 5: Review Custom Classes

If you created custom geometry classes:

**v0.7.0 pattern:**
```python
class CustomGeometry:
    yaml_tag = "CustomGeometry"
    
    def __init__(self, name, r, z):
        self.name = name
        self.r = r
        self.z = z
    
    @classmethod
    def from_dict(cls, values):
        return cls(
            name=values["name"],
            r=values["r"],
            z=values["z"]
        )
    
    # Manual YAML constructor
    def custom_constructor(loader, node):
        values = loader.construct_mapping(node)
        return CustomGeometry.from_dict(values)
    
    yaml.add_constructor("CustomGeometry", custom_constructor)
```

**v1.0.0 pattern:**
```python
from python_magnetgeo.base import YAMLObjectBase
from python_magnetgeo.validation import GeometryValidator

class CustomGeometry(YAMLObjectBase):
    yaml_tag = "CustomGeometry"
    
    def __init__(self, name: str, r: list, z: list):
        # Add validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
        GeometryValidator.validate_numeric_list(z, 'z', expected_length=2)
        
        self.name = name
        self.r = r
        self.z = z
    
    @classmethod
    def from_dict(cls, values: dict, debug: bool = False):
        return cls(
            name=values["name"],
            r=values["r"],
            z=values["z"]
        )
    
    # No manual registration needed - automatic via __init_subclass__!
```

### 9.4 Migration Checklist by Version

#### From v0.5.x → v1.0.0 (Major Migration)
- [ ] Update all YAML files with type annotations (`!<ClassName>`)
- [ ] Change all field names to lowercase (`Helices` → `helices`)
- [ ] Update Python code with new imports
- [ ] Add `try/except` blocks for `ValidationError`
- [ ] Update custom classes to inherit from `YAMLObjectBase`
- [ ] Test all configurations thoroughly
- [ ] Update documentation

#### From v0.7.0 → v1.0.0 (Moderate Migration)
- [ ] Add `ValidationError` import where needed
- [ ] Wrap geometry creation in `try/except` blocks
- [ ] Update custom classes to use `YAMLObjectBase` (optional but recommended)
- [ ] Review and update any deprecated method calls
- [ ] Test validation with invalid inputs
- [ ] Update code documentation

#### From v0.6.0 → v1.0.0 (Major Migration)
Same as v0.5.x → v1.0.0 migration

### 9.5 Compatibility Matrix

| Your Version | YAML Compatible | Python API Compatible | Migration Effort |
|--------------|-----------------|----------------------|------------------|
| v0.7.0 | ✓ Yes | ⚠ Mostly (add error handling) | Low |
| v0.6.0 | ✗ No | ✗ No | High |
| v0.5.x | ✗ No | ✗ No | High |
| v0.4.0 | ✗ No | ✗ No | Very High |
| v0.3.x | ✗ No | ✗ No | Very High |

**Legend:**
- ✓ = Fully compatible
- ⚠ = Mostly compatible (minor updates needed)
- ✗ = Not compatible (migration required)

```python
#!/usr/bin/env python3
"""Helper to identify code that needs updating"""

import re
import sys
from pathlib import Path

def scan_python_file(filepath: Path):
    """Scan Python file for old API usage"""
    
    issues = []
    
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for old field names
    old_fields = ['Helices', 'Rings', 'CurrentLeads', 'HAngles', 'RAngles']
    for i, line in enumerate(lines, 1):
        for field in old_fields:
            if field in line:
                issues.append(f"Line {i}: Old field name '{field}' found")
    
    # Check for removed methods
    removed_methods = ['loadYamlOld', 'from_yaml_old', 'simple_load']
    for i, line in enumerate(lines, 1):
        for method in removed_methods:
            if method in line:
                issues.append(f"Line {i}: Removed method '{method}' found")
    
    # Check for missing type hints in from_dict
    if 'def from_dict(cls, values)' in content:
        issues.append("from_dict() missing type hints (should be: values: Dict[str, Any])")
    
    return issues

def scan_directory(directory: str):
    """Scan all Python files in directory"""
    
    path = Path(directory)
    python_files = list(path.rglob("*.py"))
    
    print(f"Scanning {len(python_files)} Python files...\n")
    
    total_issues = 0
    for py_file in python_files:
        issues = scan_python_file(py_file)
        if issues:
            print(f"\n{py_file.name}:")
            for issue in issues:
                print(f"  ⚠ {issue}")
            total_issues += len(issues)
    
    if total_issues == 0:
        print("✓ No API compatibility issues found!")
    else:
        print(f"\n⚠ Found {total_issues} potential issues")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scan_api_usage.py <directory>")
        sys.exit(1)
    
    scan_directory(sys.argv[1])
```

---

## 10. Testing Recommendations

### 10.1 Verify Migration

After migrating, run these checks:

```python
#!/usr/bin/env python3
"""Verify migrated files load correctly"""

import sys
from pathlib import Path
from python_magnetgeo import Insert, Helix, Ring

def verify_yaml_file(filepath: str):
    """Test that migrated YAML loads correctly"""
    try:
        # Try to load based on filename
        if 'insert' in filepath.lower():
            obj = Insert.from_yaml(filepath)
        elif 'helix' in filepath.lower():
            obj = Helix.from_yaml(filepath)
        elif 'ring' in filepath.lower():
            obj = Ring.from_yaml(filepath)
        else:
            print(f"⚠ Unknown type: {filepath}")
            return False
        
        print(f"✓ {filepath} loads successfully")
        return True
    except Exception as e:
        print(f"✗ {filepath} failed: {e}")
        return False

def verify_directory(directory: str):
    """Verify all YAML files in directory"""
    path = Path(directory)
    yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))
    
    success = sum(1 for f in yaml_files if verify_yaml_file(str(f)))
    total = len(yaml_files)
    
    print(f"\n{success}/{total} files loaded successfully")
    return success == total

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_migration.py <directory>")
        sys.exit(1)
    
    success = verify_directory(sys.argv[1])
    sys.exit(0 if success else 1)
```

---

## 11. Summary of Breaking Changes

### By Version

#### v0.5.x → v0.7.0 (Historical)
1. ✗ YAML type annotations introduced and required
2. ✗ All field names changed to lowercase
3. ⚠ Internal structure refactored
4. ⚠ Enhanced YAML type system

#### v0.7.0 → v1.0.0 (Current Release)
1. ⊕ New base class architecture (`YAMLObjectBase`)
2. ⊕ Validation system with `ValidationError`
3. ⊕ Enhanced type safety and checking
4. ⚠ Method signatures updated (added `debug` parameter)
5. ⊕ Automatic YAML constructor registration

#### v0.5.x → v1.0.0 (Complete Migration)

### Critical Changes (Will Break Existing Code)
1. ✗ YAML type annotations now required (since v0.7.0)
2. ✗ Field names changed to lowercase (since v0.7.0)
3. ✗ Constructor signatures changed (since v1.0.0)
4. ✗ Validation errors now raised for invalid data (since v1.0.0)
5. ✗ Removed deprecated methods (since v1.0.0)

### Important Changes (May Break Code)
6. ⚠ `from_dict()` signature changed (v1.0.0)
7. ⚠ JSON format includes `__classname__` (v1.0.0)
8. ⚠ Method names changed (`write_json` → `write_to_json`) (v1.0.0)
9. ⚠ Base class requirements (v1.0.0)

### New Features (Backward Incompatible)
10. ⊕ Enum types (ShapePosition) (v1.0.0)
11. ⊕ Validation system (v1.0.0)
12. ⊕ Type hints enforced (v1.0.0)
13. ⊕ Enhanced error messages (v1.0.0)

---

## 12. Upgrade Checklist

### For v0.7.0 Users (Recommended Path)

Your YAML files should already be compatible! Focus on Python code:

- [ ] ✓ YAML files already use type annotations (no changes needed)
- [ ] ✓ Field names already lowercase (no changes needed)
- [ ] Add error handling:
  - [ ] Import `ValidationError`: `from python_magnetgeo.validation import ValidationError`
  - [ ] Wrap geometry creation in `try/except` blocks
- [ ] Update code (optional but recommended):
  - [ ] Update custom classes to inherit from `YAMLObjectBase`
  - [ ] Add type hints to your code
- [ ] Testing:
  - [ ] Run existing test suite
  - [ ] Test with invalid inputs to verify validation
  - [ ] Check that all YAML files still load

**Estimated time: 1-2 hours for typical project**

### For v0.5.x and Earlier Users (Full Migration)

- [ ] Step 1: Backup everything
  - [ ] Backup all YAML configuration files
  - [ ] Backup Python code
  - [ ] Tag current version in git
- [ ] Step 2: Migrate YAML files
  - [ ] Run YAML migration script on all configs
  - [ ] Manually review complex configurations
  - [ ] Verify all YAML files have type annotations
- [ ] Step 3: Update Python code
  - [ ] Change `Helices` → `helices` (and similar)
  - [ ] Update `from_dict()` signatures
  - [ ] Add type hints
  - [ ] Replace removed methods
- [ ] Step 4: Update imports
  - [ ] Add `from python_magnetgeo.validation import ValidationError`
  - [ ] Add `from python_magnetgeo.base import YAMLObjectBase` (for custom classes)
- [ ] Step 5: Add error handling
  - [ ] Wrap validation-sensitive code in try/except
  - [ ] Handle `ValidationError` exceptions
  - [ ] Add descriptive error messages
- [ ] Step 6: Update custom classes (if any)
  - [ ] Inherit from `YAMLObjectBase`
  - [ ] Implement `from_dict()` with new signature
  - [ ] Add validation
  - [ ] Remove manual YAML constructor registration
- [ ] Step 7: Testing
  - [ ] Test all YAML files load correctly
  - [ ] Run full test suite
  - [ ] Test error cases
  - [ ] Verify serialization round-trips
- [ ] Step 8: Documentation
  - [ ] Update code comments
  - [ ] Update user documentation
  - [ ] Update examples

**Estimated time: 1-2 days for typical project**

### Quick Migration Priority

**High Priority (Must Do):**
1. Backup all files
2. Migrate YAML files (if not on v0.7.0)
3. Add `ValidationError` import and error handling
4. Test all configurations load

**Medium Priority (Should Do):**
5. Update method signatures
6. Add type hints
7. Update custom classes
8. Comprehensive testing

**Low Priority (Nice to Have):**
9. Refactor to use new features
10. Optimize validation
11. Update documentation

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/Trophime/python_magnetgeo/issues
- Documentation: https://python-magnetgeo.readthedocs.io

**Version 1.0.0 represents a major overhaul. Plan adequate time for migration and testing.**