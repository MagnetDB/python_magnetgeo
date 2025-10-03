# Python MagnetGeo Version Comparison Guide

Quick reference for understanding differences between versions.

## Version Timeline

```
v0.3.x → v0.4.0 → v0.5.x → v0.6.0 → v0.7.0 → v1.0.0
  ↓        ↓        ↓        ↓        ↓        ↓
 Init   Helix    Legacy   Core    Type    Full
        change   format   API    system  refactor
```

## Feature Comparison Matrix

| Feature | v0.5.x | v0.7.0 | v1.0.0 |
|---------|--------|--------|--------|
| **YAML Format** |
| Type annotations (`!<ClassName>`) | ✗ | ✓ | ✓ |
| Field names | Capitalized | lowercase | lowercase |
| Nested type tags | ✗ | ✓ | ✓ |
| **Python API** |
| Type hints | Partial | Enhanced | Complete |
| Validation | Basic | Enhanced | Strict |
| Error messages | Generic | Better | Detailed |
| Base classes | Individual | Refactored | Unified |
| **Developer Experience** |
| YAML auto-registration | Manual | Semi-auto | Automatic |
| Custom class support | Complex | Moderate | Simple |
| IDE integration | Poor | Good | Excellent |
| Error handling | Manual | Manual | Built-in |
| **Quality** |
| Input validation | ⚠️ | ✓ | ✓✓ |
| Type safety | ⚠️ | ✓ | ✓✓ |
| Code duplication | High | Medium | Low |
| Maintainability | ⚠️ | ✓ | ✓✓ |

## YAML Format Examples

### Insert Definition

#### v0.5.x Format
```yaml
name: "HL-31"
Helices:
  - HL-31_H1
  - HL-31_H2
Rings:
  - Ring-H1H2
CurrentLeads:
  - inner
HAngles: []
RAngles: []
```

#### v0.7.0 Format
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
hangles: []
rangles: []
```

#### v1.0.0 Format
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
hangles: []
rangles: []
innerbore: 18.54      # New optional field
outerbore: 186.25     # New optional field
probes: []            # New optional field
```

### Helix with Nested Objects

#### v0.5.x Format
```yaml
name: "HL-31_H1"
r: [19.3, 24.2]
z: [-226, 108]
axi:
  name: "HL-31.d"
  h: 86.51
shape:
  name: "NewShape"
  profile: "profile.txt"
```

#### v0.7.0 Format
```yaml
!<Helix>
name: "HL-31_H1"
r: [19.3, 24.2]
z: [-226, 108]
axi: !<ModelAxi>
  name: "HL-31.d"
  h: 86.51
shape: !<Shape>
  name: "NewShape"
  profile: "profile.txt"
```

#### v1.0.0 Format
```yaml
!<Helix>
name: "HL-31_H1"
odd: true             # Now explicitly required
dble: true            # Now explicitly required
cutwidth: 0.22        # Now explicitly required
r: [19.3, 24.2]
z: [-226, 108]
axi: !<ModelAxi>
  name: "HL-31.d"
  h: 86.51
  turns: [0.292, 0.287]
  pitch: [29.59, 30.10]
shape: !<Shape>
  name: "NewShape"
  profile: "profile.txt"
  length: 15
  angle: [60, 90, 120, 120]
  position: ALTERNATE  # Enum support
```

## Python API Examples

### Loading Objects

#### v0.5.x
```python
from python_magnetgeo import Insert
import yaml

# Manual loading
with open("HL-31.yaml") as f:
    data = yaml.safe_load(f)
insert = Insert.from_dict(data)
```

#### v0.7.0
```python
from python_magnetgeo import Insert

# Type-specific loading
insert = Insert.from_yaml("HL-31.yaml")

# Or lazy loading (if available)
from python_magnetgeo.utils import loadYaml
insert = loadYaml("Insert", "HL-31.yaml", Insert)
```

#### v1.0.0
```python
from python_magnetgeo import Insert
from python_magnetgeo.utils import getObject
from python_magnetgeo.validation import ValidationError

# Method 1: Type-specific with validation
try:
    insert = Insert.from_yaml("HL-31.yaml")
except ValidationError as e:
    print(f"Invalid config: {e}")

# Method 2: Lazy loading (automatic type detection)
obj = getObject("HL-31.yaml")

# Method 3: With debug output
insert = Insert.from_yaml("HL-31.yaml", debug=True)
```

### Creating Objects

#### v0.5.x
```python
from python_magnetgeo import Ring

# No validation
ring = Ring(
    name="R1",
    r=[20.0, 10.0],  # Wrong order - may work anyway
    z=[0.0, 10.0]
)
```

#### v0.7.0
```python
from python_magnetgeo import Ring

# Some validation
ring = Ring(
    name="R1",
    r=[10.0, 20.0],
    z=[0.0, 10.0],
    n=1,
    angle=0.0
)
```

#### v1.0.0
```python
from python_magnetgeo import Ring
from python_magnetgeo.validation import ValidationError

# Strict validation
try:
    ring = Ring(
        name="R1",
        r=[10.0, 20.0],    # Must be ascending
        z=[0.0, 10.0],     # Must be ascending
        n=1,
        angle=0.0,
        bpside=True,
        fillets=False
    )
except ValidationError as e:
    print(f"Invalid geometry: {e}")
    # Output: "r values must be in ascending order"
```

### Custom Classes

#### v0.5.x
```python
class CustomCoil:
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
    
    def dump(self):
        # Manual implementation
        import yaml
        with open(f"{self.name}.yaml", "w") as f:
            yaml.dump(self.__dict__, f)
```

#### v0.7.0
```python
import yaml

class CustomCoil:
    yaml_tag = "CustomCoil"
    
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
    @staticmethod
    def constructor(loader, node):
        values = loader.construct_mapping(node)
        return CustomCoil.from_dict(values)

yaml.add_constructor("CustomCoil", CustomCoil.constructor)
```

#### v1.0.0
```python
from python_magnetgeo.base import YAMLObjectBase
from python_magnetgeo.validation import GeometryValidator

class CustomCoil(YAMLObjectBase):
    yaml_tag = "CustomCoil"
    
    def __init__(self, name: str, r: list, z: list):
        # Automatic validation
        GeometryValidator.validate_name(name)
        GeometryValidator.validate_numeric_list(r, 'r', expected_length=2)
        GeometryValidator.validate_ascending_order(r, 'r')
        
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
    
    # No manual registration needed!
    # Automatic via __init_subclass__
```

## Migration Difficulty

### Easy Migration (v0.7.0 → v1.0.0)

**Time: 1-2 hours**

**Changes needed:**
1. Add `ValidationError` import
2. Add try/except blocks
3. Optionally update custom classes

**YAML files:** ✓ Compatible as-is

### Medium Migration (v0.6.0 → v1.0.0)

**Time: 4-8 hours**

**Changes needed:**
1. Update YAML format
2. Update Python imports
3. Add validation handling
4. Update custom classes

**YAML files:** Need type annotations and field name changes

### Hard Migration (v0.5.x → v1.0.0)

**Time: 1-2 days**

**Changes needed:**
1. Complete YAML migration
2. Extensive Python code updates
3. Custom class rewrites
4. Comprehensive testing

**YAML files:** Need complete restructuring

### Very Hard Migration (v0.3.x-v0.4.x → v1.0.0)

**Time: 2-5 days**

**Changes needed:**
1. Everything from v0.5.x migration
2. Additional API changes
3. Helix definition updates
4. Serialization updates

**YAML files:** Need complete restructuring + additional changes

## Compatibility Quick Reference

### Can I use v1.0.0 with my v0.7.0 YAML files?

**Yes!** ✓ YAML files are fully compatible.

Just add error handling in Python:
```python
from python_magnetgeo.validation import ValidationError

try:
    obj = MyClass.from_yaml("config.yaml")
except ValidationError as e:
    print(f"Error: {e}")
```

### Can I use v1.0.0 with my v0.5.x YAML files?

**No.** ✗ You need to migrate YAML files:
1. Add type annotations (`!<ClassName>`)
2. Change field names to lowercase
3. Update nested objects

Use migration script:
```bash
python migrate_v5_to_v10.py old.yaml new.yaml
```

### Can I mix versions?

**No.** ✗ Use consistent versions:
- Don't load v0.5.x YAML with v1.0.0 code
- Don't save with v1.0.0 and load with v0.5.x

### Do I need to regenerate my YAML files?

- **v0.7.0 → v1.0.0**: No, use existing files
- **v0.5.x → v1.0.0**: Yes, migrate required
- **v0.3.x-v0.4.x → v1.0.0**: Yes, migrate + updates required

## Recommended Upgrade Strategy

### Strategy 1: Gradual (if on v0.5.x or earlier)

```
Phase 1: v0.5.x → v0.7.0 (1-2 days)
  ↓
Test thoroughly
  ↓
Phase 2: v0.7.0 → v1.0.0 (1-2 hours)
  ↓
Production deployment
```

**Pros:** Lower risk, easier to debug
**Cons:** Takes longer

### Strategy 2: Direct (if on v0.7.0)

```
v0.7.0 → v1.0.0 (1-2 hours)
  ↓
Production deployment
```

**Pros:** Quick, YAML compatible
**Cons:** None (recommended!)

### Strategy 3: Direct Jump (if on v0.5.x, small project)

```
v0.5.x → v1.0.0 (1-2 days)
  ↓
Production deployment
```

**Pros:** Get latest features immediately
**Cons:** More changes at once, higher debugging effort

## Support

**For migration help:**
- GitHub Issues: https://github.com/Trophime/python_magnetgeo/issues
- Documentation: https://python-magnetgeo.readthedocs.io
- Migration Guide: See BREAKING_CHANGES.md

**Need professional help?**
Contact: christophe.trophime@lncmi.cnrs.fr