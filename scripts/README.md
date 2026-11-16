# Helper scripts

Standalone utilities that work alongside `python_magnetgeo`. They are **not**
part of the installed package; run them directly from a checkout of the
repository.

| script | purpose |
|---|---|
| [`create_bitter.py`](create_bitter.py) | build a `Bitter` object from a stacking-plan JSON config |
| [`Bitter_stacking/stacking_plan.py`](Bitter_stacking/stacking_plan.py) | tolerance stacking of plates + kaptons (worst case / RSS / Monte Carlo) |
| [`Bitter_stacking/read_thickness.py`](Bitter_stacking/read_thickness.py) | analyse measured plate thicknesses and patch a stacking plan |
| [`Bitter_stacking/notice_to_plan.py`](Bitter_stacking/notice_to_plan.py) | build a stacking plan from a Bitter identification sheet (YAML notice) |
| [`Bitter_stacking/pdf_to_notice.py`](Bitter_stacking/pdf_to_notice.py) | extract the YAML notice from a digital identification sheet (PDF) |
| [`upgrade-magnetgeo-1.0.0.sh`](upgrade-magnetgeo-1.0.0.sh) | migrate legacy YAML files to the 1.0.0 key names |

## Typical Bitter workflow

```bash
cd scripts/Bitter_stacking

# 0. (as-built magnet) identification sheet -> notice -> stacking plan
python pdf_to_notice.py "BITTER M9M10 INT26-06-2026.pdf" --output notices/M9M10-int-n10.yaml
python notice_to_plan.py notices/M9M10-int-n10.yaml --output M9M10-int-n10.json

# 1. measured thicknesses -> patched stacking plan
python read_thickness.py thickness.xlsx --config plan.json --output plan_measured.json

# 2. check the stack height and its dispersion
python stacking_plan.py --config plan_measured.json --plot stack.png

# 3. build the Bitter object (after adding the Bitter geometry fields, see below)
python ../create_bitter.py bitter_plan.json --yaml --output-dir out/
```

## `create_bitter.py`

Creates a `Bitter` disk-magnet object from an *extended* stacking-plan JSON
file, prints a summary (radial/axial extent, ModelAxi, per-segment stacking
table, cooling slits, tierod, channels) and optionally serialises it.

```bash
python create_bitter.py --write-example bitter_plan.json   # starter config
python create_bitter.py bitter_plan.json                    # summary only
python create_bitter.py bitter_plan.json --yaml --json --output-dir /tmp
```

Options:

```text
JSON                 extended stacking-plan JSON config file
--write-example F    write a starter configuration to F and exit
--yaml               write the Bitter object to <name>.yaml
--json               write the Bitter object to <name>.json
--output-dir DIR     directory for output files (default: current directory)
--debug              enable debug logging
```

The script adds the repository root and `Bitter_stacking/` to `sys.path`, so
it works without `pip install -e .`.

### Configuration

The JSON holds the stacking-plan fields (`components`, `segments`, `kapton`,
`n_kaptons`; see the [Bitter_stacking README](Bitter_stacking/README.md#configuration-file))
plus the Bitter geometry:

| field | type | meaning |
|---|---|---|
| `name` | str | unique identifier |
| `r` | [float, float] | `[r_inner, r_outer]` [mm] |
| `odd` | bool | helix handedness (`true` = left-handed) |
| `innerbore` | float | inner bore radius [mm] (default 0) |
| `outerbore` | float | outer bore radius [mm] (default 0) |
| `coolingslits` | list | list of `CoolingSlit` dicts (default `[]`) |
| `tierod` | dict \| null | `Tierod` dict (default `null`) |

### From stacking plan to ModelAxi

One ModelAxi "turn" is `plates_per_turn` plates plus one kapton sheet:

- `pitch_i = plates_per_turn_i × mu_plate_i + mu_kapton` [mm per turn]
- `h = Σ n_turns_i × pitch_i / 2` (ModelAxi half-height)
- `z = [−h, +h]` (Bitter axial extent)

The Bitter is always centred on z = 0. A `z_offset` field is rejected: to
position the magnet axially, use `Assembly.z_offset`. The physical stack height
(`Σ plates + n_kaptons × mu_kapton`) is only reported in the summary.

## `Bitter_stacking/`

Tolerance analysis of the axial stack height. See
[Bitter_stacking/README.md](Bitter_stacking/README.md) for the theory,
configuration reference and references.

- `stacking_plan.py`: estimates the total stack height with worst-case,
  analytic RSS and Monte Carlo methods, and prints a variance budget.
  Options: `--config`, `--write-example`, `--samples`, `--coverage`, `--plot`,
  `--seed`.
- `read_thickness.py`: reads measured thicknesses from an xlsx workbook,
  computes statistics and, with `--config`, patches `components.plate`
  (`mu`, `sigma`, `sigma_syst = sigma/√n`). Options: `--sheet`, `--config`,
  `--output`, `--column`, `--plot`.

`M9Bitters-18MW-new-*.json` are stacking plans for the M9 Bitters (18 MW), one
per segment layout (e.g. `10-140-10` = 10 end turns of 8 plates, 140 body turns
of 4 plates, 10 end turns of 8 plates). They hold only the stacking-plan fields:
use them with `stacking_plan.py`, or add the Bitter geometry fields before
passing them to `create_bitter.py`.

Requires `numpy`, `scipy`, `pandas` (for xlsx), `matplotlib` (for `--plot`),
`pyyaml` (notices) and `pypdf` (for `pdf_to_notice.py`).

## `upgrade-magnetgeo-1.0.0.sh`

Migrates YAML files written for older versions to the 1.0.0 key names. Run it
from the directory containing the `*.yaml` files:

```bash
cd path/to/yaml/files
/path/to/python_magnetgeo/scripts/upgrade-magnetgeo-1.0.0.sh
```

Renamed top-level keys:

| old | new |
|---|---|
| `Helices:` | `helices:` |
| `Rings:` | `rings:` |
| `HAngles:` | `hangles:` |
| `RAngles:` | `rangles:` |
| `CurrentLeads:` | `currentleads:` |
| `axi:` | `modelaxi:` |
| `m3d:` | `model3d:` |

Lines starting with `material` are deleted.

> **Warning:** the script edits every `*.yaml` in the current directory **in
> place** (`perl -pi`) with no backup. Commit or copy the files first.
