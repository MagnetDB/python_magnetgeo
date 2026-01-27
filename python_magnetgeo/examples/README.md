# Python MagnetGeo Examples

This directory contains example scripts demonstrating various features and usage patterns of the python_magnetgeo library.

## Table of Contents

- [helix-cut.py](#helix-cutpy) - Helix geometry processing and cut generation
- [load_profile_from_dat.py](#load_profile_from_datpy) - Load Profile objects from DAT files
- [probe_example.py](#probe_examplepy) - Basic Probe class usage
- [probe_usage_python.py](#probe_usage_pythonpy) - Advanced probe integration with magnet components

---

## helix-cut.py

**Purpose:** Demonstrates how to process Helix objects from JSON files, compact their model data, and generate cut files for different CAD systems (SALOME and LNCMI).

**Key Features:**
- Loading Helix objects from JSON files
- Accessing and modifying object attributes
- Compacting axisymmetric model data (turns and pitch)
- Converting between JSON and YAML formats
- Generating cut files for CAD systems

**Usage:**
```bash
python helix-cut.py <json_file1> [json_file2 ...]
```

**Example:**
```bash
python helix-cut.py helix_config.json
```

**What it does:**
1. Creates a sample Helix object with specified parameters
2. Loads Helix configuration(s) from JSON file(s)
3. Compacts the axisymmetric model data with 1e-6 tolerance
4. Exports the processed data to YAML
5. Generates cut files in SALOME and LNCMI formats

**Output:**
- `<filename>.yaml` - YAML representation of the Helix
- Cut files for SALOME and LNCMI CAD systems

---

## load_profile_from_dat.py

**Purpose:** Helper script to create Profile objects from DAT files. This is the reverse operation of the `Profile.generate_dat_file()` method.

**Key Features:**
- Loads Profile objects from DAT files
- Handles both formats: with and without region labels
- Export to YAML or JSON
- Command-line interface with multiple output options
- Automatic detection of label presence

**Usage:**
```bash
# Display profile information
python load_profile_from_dat.py Shape_HR-54-116.dat

# Display with verbose details
python load_profile_from_dat.py Shape_HR-54-116.dat -v

# Export to YAML (console)
python load_profile_from_dat.py Shape_HR-54-116.dat --yaml

# Save to YAML file
python load_profile_from_dat.py Shape_HR-54-116.dat --save-yaml my_profile.yaml

# Save to JSON file
python load_profile_from_dat.py Shape_HR-54-116.dat --save-json my_profile.json

# Run without arguments to see examples
python load_profile_from_dat.py
```

**In Python code:**
```python
from load_profile_from_dat import load_profile_from_dat

# Load a profile from DAT file
profile = load_profile_from_dat("Shape_HR-54-116.dat")

# Access profile data
print(f"CAD: {profile.cad}")
print(f"Number of points: {len(profile.points)}")
print(f"Labels: {profile.labels}")

# Save to YAML
import yaml
with open("output.yaml", 'w') as f:
    yaml.dump(profile, stream=f, default_flow_style=False)
```

**DAT File Format:**

With labels:
```
#Shape : HR-54-116
#
# Profile with region labels
#
#N_i
7
#X_i F_i    Id_i
-5.34 0.00    0
-3.34 0.00    0
-2.01 0.90    0
0.00 0.90     1
2.01 0.90     0
3.34 0.00     0
5.34 0.00     0
```

Without labels:
```
#Shape : SIMPLE-AIRFOIL
#
# Profile geometry
#
#N_i
4
#X_i F_i
0.00 0.00
0.50 0.05
1.00 0.03
1.50 0.00
```

**Output:**
- Console display of profile information
- YAML files with Profile data
- JSON files with Profile data

---

## probe_example.py

**Purpose:** Demonstrates basic usage of the Probe class for creating and managing different types of measurement probes in magnet systems.

**Key Features:**
- Creating voltage tap probes
- Creating temperature sensor probes
- Creating magnetic field measurement probes
- Saving probes to YAML and JSON
- Loading probes from YAML
- Adding probes dynamically
- Querying probe information

**Usage:**
```bash
python probe_example.py
```

**What it demonstrates:**

1. **Voltage Taps:**
   ```python
   voltage_probes = Probe(
       name="H1_voltage_taps",
       probe_type="voltage_taps",
       index=["V1", "V2", "V3", "V4"],
       locations=[
           [10.5, 0.0, 15.2],
           [12.3, 0.0, 18.7],
           [14.1, 0.0, 22.1],
           [15.9, 0.0, 25.6]
       ]
   )
   ```

2. **Temperature Sensors:**
   ```python
   temp_probes = Probe(
       name="H1_temperature",
       probe_type="temperature",
       index=[1, 2, 3],
       locations=[
           [11.0, 5.2, 16.5],
           [13.5, -3.1, 20.0],
           [16.2, 2.7, 24.8]
       ]
   )
   ```

3. **Magnetic Field Probes:**
   ```python
   field_probes = Probe(
       name="center_field",
       probe_type="magnetic_field",
       index=["Bz_center", "Br_edge"],
       locations=[
           [0.0, 0.0, 0.0],     # Center of bore
           [5.0, 0.0, 0.0]      # Edge measurement
       ]
   )
   ```

**Output:**
- `H1_voltage_taps.yaml` - Voltage tap probe configuration
- `H1_temperature.yaml` - Temperature probe configuration
- `center_field.yaml` - Magnetic field probe configuration
- Corresponding JSON files

---

## probe_usage_python.py

**Purpose:** Advanced examples showing how to integrate Probe objects with magnet system components (Insert, Bitters, Supras).

**Key Features:**
- Embedding Probe objects in Insert configurations
- Using probe references (strings) that link to external YAML files
- Integrating probes with Bitters (resistive magnets)
- Integrating probes with Supras (superconducting magnets)
- Mixed probe types in single component
- Loading probe configurations from YAML

**Usage:**
```bash
python probe_usage_python.py
```

**What it demonstrates:**

1. **Insert with Embedded Probes:**
   ```python
   voltage_probes = Probe(name="H1_voltage_taps", ...)
   temp_probes = Probe(name="H1_temperature", ...)
   
   insert = Insert(
       name="M9_Insert",
       helices=["H1", "H2"],
       rings=["R1"],
       probes=[voltage_probes, temp_probes]  # Embedded objects
   )
   ```

2. **Insert with Probe References:**
   ```python
   insert = Insert(
       name="M9_Insert_Refs",
       helices=["H1", "H2"],
       probes=["voltage_probes", "temp_probes"]  # String references
   )
   # These will be loaded from voltage_probes.yaml and temp_probes.yaml
   ```

3. **Bitters with Monitoring Probes:**
   ```python
   bitter_probes = Probe(
       name="bitter_monitoring",
       probe_type="voltage_taps",
       index=["BV1", "BV2"],
       locations=[[20.0, 0.0, 5.0], [30.0, 0.0, -5.0]]
   )
   
   bitters = Bitters(
       name="Bitter_Stack",
       magnets=["B1", "B2", "B3"],
       probes=[bitter_probes]
   )
   ```

4. **Supras with Multiple Probe Types:**
   ```python
   quench_probes = Probe(name="quench_detection", probe_type="voltage_taps", ...)
   temp_probes = Probe(name="hts_temperature", probe_type="temperature", ...)
   
   supras = Supras(
       name="HTS_Stack",
       magnets=["S1", "S2"],
       probes=[quench_probes, temp_probes]
   )
   ```

5. **Mixed Probe Configuration in YAML:**
   ```yaml
   name: M9_Mixed_Probes
   helices: ["H1", "H2"]
   probes:
     - "external_voltage_probes"  # String reference to external file
     - name: embedded_temp_probes  # Embedded probe definition
       probe_type: temperature
       index: [1, 2, 3]
       locations:
         - [16.5, 5.2, 11.0]
         - [20.0, -3.1, 13.5]
   ```

**Output:**
- `M9_Insert.yaml` - Insert configuration with embedded probes
- `Bitter_Stack.yaml` - Bitters configuration with probes
- `HTS_Stack.yaml` - Supras configuration with probes
- Console output showing probe counts and types

---

## Common Patterns

### Loading from YAML
```python
from python_magnetgeo.Profile import Profile
from python_magnetgeo.Probe import Probe
from python_magnetgeo.Insert import Insert

# Load Profile
profile = Profile.from_yaml("my_profile.yaml")

# Load Probe
probe = Probe.from_yaml("voltage_probes.yaml")

# Load Insert
insert = Insert.from_yaml("M9_Insert.yaml")
```

### Saving to YAML
```python
import yaml

# Save any object to YAML
with open("output.yaml", 'w') as f:
    yaml.dump(obj, stream=f, default_flow_style=False)

# Or use the dump() method if available
obj.write_to_yaml()  # Creates {obj.name}.yaml
```

### Working with Probes
```python
# Create a probe
probe = Probe(name="test", probe_type="voltage_taps", 
              index=["V1", "V2"], locations=[[0, 0, 0], [1, 0, 0]])

# Get probe count
count = probe.get_probe_count()

# Get specific probe
info = probe.get_probe_by_index("V1")

# Add a new probe location
probe.add_probe("V3", [2.0, 0.0, 0.0])
```

## Requirements

All examples require the `python_magnetgeo` package to be installed or available in the Python path. Some examples may have additional dependencies:

- `pyyaml` - YAML file handling
- `argparse` - Command-line argument parsing (standard library)
- `pathlib` - File path operations (standard library)

## Contributing

When adding new examples:
1. Add clear docstrings explaining the purpose
2. Include usage examples in comments
3. Update this README with a new section
4. Follow the existing code style and patterns
