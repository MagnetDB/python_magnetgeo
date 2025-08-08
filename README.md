# Python Magnet Geometry

[![PyPI version](https://img.shields.io/pypi/v/python_magnetgeo.svg)](https://pypi.python.org/pypi/python_magnetgeo)
[![Build Status](https://img.shields.io/travis/Trophime/python_magnetgeo.svg)](https://travis-ci.com/Trophime/python_magnetgeo)
[![Documentation Status](https://readthedocs.org/projects/python-magnetgeo/badge/?version=latest)](https://python-magnetgeo.readthedocs.io/en/latest/?version=latest)
[![Updates](https://pyup.io/repos/github/Trophime/python_magnetgeo/shield.svg)](https://pyup.io/repos/github/Trophime/python_magnetgeo/)

Python Magnet Geometry contains magnet geometrical models for high-field magnet design and simulation.

## Features

- Define magnet geometry using YAML configuration files
- Load/Create CAD and mesh with Salome (see hifimagnet.salome)
- Create Gmsh meshes from Salome XAO format
- Support for Helix, Insert, Ring, and other magnet components
- JSON serialization/deserialization support
- Comprehensive testing suite

## Installation

### Using pip (recommended)

```bash
pip install python_magnetgeo
```

### Using Poetry

```bash
poetry add python_magnetgeo
```

### Development installation

```bash
git clone https://github.com/Trophime/python_magnetgeo.git
cd python_magnetgeo
python -m venv --system-site-packages magnetgeo-env
source ./magnetgeo-env/bin/activate
pip install -r requirements.txt
```

## YAML Configuration Format

The package uses YAML files to define magnet geometries. The current format (v0.7.0+) uses structured YAML with type annotations:

### Insert Configuration Example

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

### Helix Configuration Example

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
  turns: [0.292, 0.287, ...]
  pitch: [29.59, 30.10, ...]
shape: !<Shape>
  name: "NewShape"
  profile: "02_10_2014_H1"
  length: 15
  angle: [60, 90, 120, 120]
  onturns: 0
  position: ALTERNATE
```

## API Breaking Changes

⚠️ **Important**: This package contains breaking changes between versions. No backward compatibility is provided.

### Version 0.7.0 (Current)
- Complete refactor of internal structure
- Enhanced YAML type system
- Updated API methods

### Version 0.6.0
- Major API changes in core geometry classes
- Breaking changes in YAML format structure
- Updated method signatures

### Version 0.4.0
- Breaking changes in Helix definition
- Rewritten test suite
- Updated serialization methods

## Migration from Old Versions

### From v0.5.x to v0.7.0

**Key Changes:**
- `Helices` → `helices` (lowercase field names)
- `Rings` → `rings`
- `CurrentLeads` → `currentleads`
- `HAngles` → `hangles`
- `RAngles` → `rangles`
- Enhanced type annotations with `!<ClassName>`
- Restructured nested object definitions

**Migration Script:**

```python
#!/usr/bin/env python3
"""
Migration script from v0.5.x to v0.7.0 YAML format
"""

import yaml
import sys
import os

def migrate_yaml_v5_to_v7(old_file, new_file):
    """Migrate YAML from v0.5.x to v0.7.0 format"""
    
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
        'RAngles': 'rangles'
    }
    
    # Apply field name changes
    for old_key, new_key in field_mapping.items():
        if old_key in data:
            data[new_key] = data.pop(old_key)
    
    # Add type annotations if missing
    if 'name' in data and not str(data).startswith('!<'):
        # Detect type based on structure
        if 'helices' in data or 'Helices' in data:
            data = {'!<Insert>': data}
        elif 'r' in data and 'z' in data:
            data = {'!<Helix>': data}
    
    # Write migrated data
    with open(new_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print(f"Migrated {old_file} → {new_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate.py <old_yaml> <new_yaml>")
        sys.exit(1)
    
    migrate_yaml_v5_to_v7(sys.argv[1], sys.argv[2])
```

### From v0.3.x to v0.7.0

**Major Breaking Changes:**
- Complete rewrite of class constructors
- New YAML schema with type annotations
- Updated method signatures for all geometry classes
- Changed channel handling system

**Required Manual Updates:**
1. Update all YAML files to new format
2. Review and update custom code using the API
3. Update import statements if needed
4. Regenerate any cached/serialized data

## Usage Examples

### Loading Configuration

```python
from python_magnetgeo.utils import loadYaml
from python_magnetgeo import Insert

# Load an Insert configuration
insert = loadYaml("HL-31", "HL-31.yaml", Insert)
print(f"Loaded insert: {insert.name}")
```

### Creating Geometry Programmatically

```python
from python_magnetgeo import Helix, Shape, ModelAxi

# Create a helix
helix = Helix(
    name="H1",
    odd=True,
    r=[19.3, 24.2],
    z=[-226, 108],
    dble=True,
    cutwidth=0.22
)

# Save to YAML
helix.dump()
```

### Working with Salome

In Salome container:

```bash
export HIFIMAGNET=/opt/SALOME-9.7.0-UB20.04/INSTALL/HIFIMAGNET/bin/salome
salome -w1 -t $HIFIMAGNET/HIFIMAGNET_Cmd.py args:HL-31.yaml,--axi,--air,2,2
```

Then create mesh:

```bash
python -m python_magnetgeo.xao HL-31-Axi.xao mesh --group CoolingChannels --geo HL-31.yaml
```

## Requirements

- Python >= 3.11
- PyYAML >= 6.0
- chevron >= 0.13.1
- pytest >= 8.2.0 (for development)

## Development

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests as needed
5. Ensure all tests pass
6. Submit a pull request

## Documentation

Full documentation is available at: https://python-magnetgeo.readthedocs.io

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

**Authors:**
- Christophe Trophime <christophe.trophime@lncmi.cnrs.fr>
- Romain Vallet <romain.vallet@lncmi.cnrs.fr>  
- Jeremie Muzet <jeremie.muzet@lncmi.cnrs.fr>

## Support

For issues and questions:
- GitHub Issues: https://github.com/Trophime/python_magnetgeo/issues
- Documentation: https://python-magnetgeo.readthedocs.io