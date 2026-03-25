# python_magnetgeo examples

This directory contains standalone scripts demonstrating various features of `python_magnetgeo`.

## Requirements

```bash
pip install python_magnetgeo
pip install matplotlib   # for visualization scripts
pip install rich         # for find_cadref_in_yaml.py
```

---

## Scripts

### `check_magnetgeo_yaml.py`

Load and validate one or more `python_magnetgeo` YAML configuration files.

```bash
python check_magnetgeo_yaml.py data/HL-31_H1.yaml
python check_magnetgeo_yaml.py data/*.yaml
```

Prints the loaded object type and its string representation. Exits with a non-zero status if any file fails to load.

---

### `find_cadref_in_yaml.py`

Search a directory of YAML config files for Part definitions whose CAD reference matches a given value.
Results are displayed as a styled table (via `rich`) and saved to a CSV file.

```bash
# List all CAD references found in a directory
python find_cadref_in_yaml.py --yaml_dir /path/to/configs

# Search for a specific CAD reference (substring match)
python find_cadref_in_yaml.py --yaml_dir /path/to/configs --cad_ref "HL-31-xxx.brep"

# Restrict to a specific part type
python find_cadref_in_yaml.py --yaml_dir /path/to/configs --type helix

# Restrict to a specific CAD field
python find_cadref_in_yaml.py --yaml_dir /path/to/configs --field model3d.cad

# Walk subdirectories and save results to a custom CSV file
python find_cadref_in_yaml.py --yaml_dir /path/to/configs --recursive --output results.csv

# Exclude specific directories from the search
python find_cadref_in_yaml.py --yaml_dir /path/to/configs --recursive --exclude-dirs archive deprecated old
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--yaml_dir` | *(required)* | Directory containing YAML config files |
| `--cad_ref` | *(none — list all)* | CAD reference string to search for (substring match) |
| `--type` | `all` | Restrict to part type: `helix`, `ring`, `bitter`, `screen`, `lead`, `supra` |
| `--field` | *(all fields)* | Restrict to a specific attribute path (e.g. `model3d.cad`) |
| `--recursive` | off | Walk subdirectories |
| `--exclude-dirs` | *(none)* | Directory names to skip (e.g. `--exclude-dirs archive deprecated`) |
| `--output` | `cad_refs.csv` | Output CSV file path |

**Output:**

- Terminal: a `rich` table with columns **File**, **Name**, **Part Type**, **CAD Value**
- File: a CSV with the same four columns for later use

---

### `visualization.py`

Demonstrates axisymmetric visualization of `Ring` and `Screen` objects using `matplotlib`.

```bash
python visualization.py
```

Generates:
- `example_ring.png` — single Ring cross-section
- `example_screen.png` — single Screen cross-section
- `example_combined.png` — Ring + Screen overlay

---

### `helix_visualization.py`

Demonstrates axisymmetric visualization of a `Helix` with its `ModelAxi` zone, plus a full magnet assembly.

```bash
python helix_visualization.py
```

Generates:
- `example_helix_with_modelaxi.png` — Helix with modelaxi zone highlighted
- `example_helix_without_modelaxi.png` — Helix body only
- `example_complete_assembly.png` — Helix + Ring + Screens combined

---

### `insert_visualization.py`

Demonstrates axisymmetric visualization of a multi-helix `Insert` assembly.

```bash
python insert_visualization.py
```

Generates:
- `example_insert.png` — three concentric helices with their modelaxi zones
