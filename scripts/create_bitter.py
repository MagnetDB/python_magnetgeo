#!/usr/bin/env python3
"""Create a Bitter disk-magnet object from a stacking-plan JSON configuration.

The stacking plan (``components``, ``segments``, ``kapton``) defines the axial
geometry:

* one "turn" = ``plates_per_turn`` plates + one kapton sheet
* ``pitch_i = plates_per_turn[i] × mu_plate + mu_kapton``  (mm per turn)
* ``h = Σ n_turns[i] × pitch_i / 2``                       (ModelAxi half-height)
* ``z = [−h, +h]``                                          (physical axial extent, overridable)

The extended JSON adds the Bitter-specific geometric fields that are not part
of the stacking plan (``name``, ``r``, ``odd``, ``innerbore``, ``outerbore``,
``coolingslits``, ``tierod``).

JSON schema
-----------
Stacking-plan fields (same as stacking_plan.py):
    components    dict    component catalogue (needs "plate" and "kapton" entries)
    segments      list    ordered stack segments, each with n_turns, plates_per_turn
                          and optional plate name (default: "plate")
    kapton        str     name of the kapton component in components
    n_kaptons     int|null  total kapton sheets (null → total_turns − 1)

Additional Bitter geometry fields:
    name          str     unique identifier
    r             [float, float]  [r_inner, r_outer] in mm
    odd           bool    helix handedness (true = left-handed)
    innerbore     float   inner bore radius in mm  (default: 0)
    outerbore     float   outer bore radius in mm  (default: 0)
    z_offset      float   shift the centre of the stack away from z=0  (default: 0)
    coolingslits  list    list of CoolingSlit dicts  (default: [])
    tierod        dict|null  Tierod dict or null      (default: null)

Usage
-----
    python create_bitter.py --write-example bitter_plan.json
    python create_bitter.py bitter_plan.json
    python create_bitter.py bitter_plan.json --yaml --json --output-dir /tmp
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Allow running as a standalone script: add repo root to sys.path so that
# 'python_magnetgeo' is importable without 'pip install -e .'.
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Example configuration
# ---------------------------------------------------------------------------

EXAMPLE_CONFIG: dict = {
    # --- Bitter geometry ---
    "name": "B1",
    "r": [100.0, 150.0],
    "odd": True,
    "innerbore": 80.0,
    "outerbore": 160.0,
    "z_offset": 0.0,
    "coolingslits": [
        {
            "name": "slit1",
            "r": 120.0,
            "angle": 4.5,
            "n": 10,
            "dh": 2.0,
            "sh": 3.0,
            "contour2d": None,
        },
    ],
    "tierod": None,
    # --- Stacking plan ---
    "components": {
        "plate": {"mu": 0.775, "tolerance": 0.005, "distribution": "normal"},
        "kapton": {"mu": 0.125, "tolerance": 0.00001, "distribution": "uniform"},
    },
    "segments": [
        {"n_turns": 10, "plates_per_turn": 8, "plate": "plate"},
        {"n_turns": 140, "plates_per_turn": 4, "plate": "plate"},
        {"n_turns": 10, "plates_per_turn": 8, "plate": "plate"},
    ],
    "kapton": "kapton",
    "n_kaptons": None,
}


# ---------------------------------------------------------------------------
# Stacking-plan → ModelAxi conversion
# ---------------------------------------------------------------------------

def _resolve_stacking(cfg: dict) -> tuple[list[float], list[float], float, float, int]:
    """Derive (turns, pitches, h, H_actual, n_kaptons) from the stacking-plan fields.

    Returns
    -------
    turns      list of n_turns per segment
    pitches    list of mm-per-turn per segment  (plates_per_turn*mu_plate + mu_kapton)
    h          ModelAxi half-height = sum(n*p)/2
    H_actual   physical stack height = 2*h - mu_kapton  (one fewer kapton than pitch formula)
    n_kaptons  number of kapton sheets in the stack
    """
    components = cfg["components"]
    kapton_name = cfg["kapton"]
    mu_kapton = float(components[kapton_name]["mu"])

    turns: list[float] = []
    pitches: list[float] = []
    n_total_turns = 0

    for seg in cfg["segments"]:
        plate_name = seg.get("plate", "plate")
        mu_plate = float(components[plate_name]["mu"])
        ppt = int(seg["plates_per_turn"])
        nt = int(seg["n_turns"])
        turns.append(float(nt))
        pitches.append(ppt * mu_plate + mu_kapton)
        n_total_turns += nt

    n_kaptons_cfg = cfg.get("n_kaptons")
    n_kaptons = int(n_kaptons_cfg) if n_kaptons_cfg is not None else n_total_turns - 1

    h = sum(t * p for t, p in zip(turns, pitches)) / 2.0
    H_actual = 2 * h - mu_kapton

    return turns, pitches, h, H_actual, n_kaptons


def build_bitter_from_config(cfg: dict, debug: bool = False):
    """Instantiate a Bitter object from the extended stacking-plan config."""
    from python_magnetgeo.Bitter import Bitter
    from python_magnetgeo.coolingslit import CoolingSlit
    from python_magnetgeo.ModelAxi import ModelAxi
    from python_magnetgeo.tierod import Tierod

    name = cfg["name"]
    r = cfg["r"]
    odd = cfg["odd"]
    innerbore = cfg.get("innerbore", 0.0)
    outerbore = cfg.get("outerbore", 0.0)
    z_offset = cfg.get("z_offset", 0.0)

    turns, pitches, h, H_actual, _ = _resolve_stacking(cfg)

    z_half = H_actual / 2.0
    z = [z_offset - z_half, z_offset + z_half]

    modelaxi = ModelAxi(name=f"{name}_axi", h=h, turns=turns, pitch=pitches)

    # Cooling slits
    coolingslits = []
    for s in cfg.get("coolingslits", []):
        if isinstance(s, dict):
            coolingslits.append(CoolingSlit.from_dict(s, debug=debug))
        else:
            coolingslits.append(s)

    # Tierod
    tierod_cfg = cfg.get("tierod")
    tierod = None
    if tierod_cfg is not None:
        if isinstance(tierod_cfg, dict):
            tierod = Tierod.from_dict(tierod_cfg, debug=debug)
        else:
            tierod = tierod_cfg

    return Bitter(
        name=name,
        r=r,
        z=z,
        odd=odd,
        modelaxi=modelaxi,
        coolingslits=coolingslits,
        tierod=tierod,
        innerbore=innerbore,
        outerbore=outerbore,
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary(bitter, cfg: dict) -> None:
    """Print a human-readable summary of the Bitter object and its stacking plan."""
    rb, zb = bitter.boundingBox()
    n_turns_total = bitter.get_Nturns()
    lc = bitter.get_lc()
    channels = bitter.get_channels(bitter.name)
    names_3d = bitter.get_names(bitter.name, is2D=False)

    print(f"\nBitter: {bitter.name!r}")
    print(f"  Radial extent : r = [{rb[0]}, {rb[1]}] mm  (dr = {rb[1]-rb[0]:.3f} mm)")
    print(f"  Axial extent  : z = [{zb[0]:.4f}, {zb[1]:.4f}] mm  (dz = {zb[1]-zb[0]:.4f} mm)")
    print(f"  Odd           : {bitter.odd}")
    print(f"  Inner bore    : {bitter.innerbore} mm")
    print(f"  Outer bore    : {bitter.outerbore} mm")

    axi = bitter.modelaxi
    print(f"\n  ModelAxi      : {axi.name!r}")
    print(f"    h           : {axi.h:.4f} mm  (pattern [{-axi.h:.4f}, {axi.h:.4f}])")
    print(f"    Total turns : {n_turns_total:.1f}")

    # Stacking plan breakdown per segment
    components = cfg["components"]
    kapton_name = cfg["kapton"]
    mu_kapton = float(components[kapton_name]["mu"])
    print(f"\n  Stacking plan ({'segments'})")
    print(f"  {'Segment':<6} {'n_turns':>8} {'ppt':>4} {'mu_plate':>10} {'pitch':>10} {'height':>10}")
    print(f"  {'-'*52}")
    for i, (seg, t, p) in enumerate(zip(cfg["segments"], axi.turns, axi.pitch)):
        plate_name = seg.get("plate", "plate")
        mu_plate = float(components[plate_name]["mu"])
        ppt = seg["plates_per_turn"]
        print(f"  {i:<6} {int(t):>8} {ppt:>4} {mu_plate:>10.4f} {p:>10.4f} {t*p:>10.4f}")
    print(f"  {'total':<6} {int(n_turns_total):>8}      {'':>10} {'':>10} {sum(t*p for t,p in zip(axi.turns, axi.pitch)):>10.4f}")
    print(f"  kapton mu={mu_kapton:.4f} mm")

    print(f"\n  Mesh lc       : {lc:.4f} mm")

    n_slits = len(bitter.coolingslits)
    print(f"\n  Cooling slits : {n_slits}")
    for s in bitter.coolingslits:
        print(f"    {s.name}: r={s.r} mm, n={s.n}, angle={s.angle}°, "
              f"dh={s.dh} mm, sh={s.sh} mm²")

    print(f"\n  Channels      : {channels}")
    print(f"  3-D markers   : {names_3d}")

    if bitter.tierod is not None:
        tr = bitter.tierod
        print(f"\n  Tierod        : {tr.name}, r={tr.r} mm, n={tr.n}")
    else:
        print(f"\n  Tierod        : none")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a Bitter object from a stacking-plan JSON config. "
            "Use --write-example to generate a starter file."
        )
    )
    parser.add_argument(
        "config",
        nargs="?",
        metavar="JSON",
        default=None,
        help="extended stacking-plan JSON config file",
    )
    parser.add_argument(
        "--write-example",
        metavar="JSON",
        default=None,
        help="write a starter JSON configuration to FILE and exit",
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="write the Bitter object to a YAML file",
    )
    parser.add_argument(
        "--json",
        dest="write_json",
        action="store_true",
        help="write the Bitter object to a serialised JSON file",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=None,
        help="directory for output files (default: current directory)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG if "--debug" in (argv or sys.argv) else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    args = parse_args(argv)

    if args.write_example:
        path = Path(args.write_example)
        path.write_text(json.dumps(EXAMPLE_CONFIG, indent=2) + "\n", encoding="utf-8")
        print(f"Example configuration written to {path}")
        return 0

    if args.config is None:
        print("error: provide a JSON config file or use --write-example", file=sys.stderr)
        return 1

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    bitter = build_bitter_from_config(cfg, debug=args.debug)
    print_summary(bitter, cfg)

    if args.yaml:
        bitter.write_to_yaml(directory=args.output_dir)
        out = Path(args.output_dir or ".") / f"{bitter.name}.yaml"
        print(f"\nYAML written to {out}")

    if args.write_json:
        bitter.write_to_json(directory=args.output_dir)
        out = Path(args.output_dir or ".") / f"{bitter.name}.json"
        print(f"JSON written to {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
