#!/usr/bin/env python3
"""Build a stacking-plan JSON from a Bitter identification sheet (notice).

The notice is a YAML transcription of the raw facts of a "fiche
d'identification aimant Bitter" (filled by hand for now). It is turned into a
stacking plan for ``stacking_plan.py`` with deterministic rules, and a report
lists the reading chosen, the consistency checks and the warnings.

Notice fields
-------------
overlap : str
    Electrical overlap ("recouvrement électrique"), e.g. ``"3/4"``.
active_discs : dict
    ``qty`` (number of active discs) and ``thickness`` (nominal) [mm].
dead_discs : dict, optional
    ``hp`` and ``bp`` dead-disc counts (HP = top, BP = bottom).
insulators : dict
    ``thickness`` [mm], optional ``qty`` and ``material`` (default kapton).
measured_height : float, optional
    Clamped stack height without end plates [mm]; used to back-calculate
    the disc width. Without it the nominal thickness is used.
height_limits : [float, float], optional
    Allowed clamped height [mm].
thickness_range : [float, float], optional
    Range of measured disc thicknesses [mm].
tolerances : dict, optional
    ``plate`` and ``insulator`` tolerance half-widths [mm].
observations : str
    Free text, e.g. "14 spires à 8 disques aux extrémités ... 126 spires à
    4 disques en partie centrale".
notes : str, optional
    Doubts about the sheet, repeated as a warning in the report.
type, number, slit_direction : optional
    Informational.

Rules
-----
1. groups per turn = 1 / (1 - overlap) (3/4 -> 4).
2. Observation items "N spires à AxB|K disques": discs per turn = A*B or K;
   an item mentioning "centrale" is the body, any other the ends.
3. End turns are read either per end or as a total over both ends; the
   reading whose disc count equals ``active_discs.qty`` is kept, otherwise
   it is an error.
4. Insulators in the plan: n_turns - 1; a given ``qty`` must equal
   groups * (n_turns - 1).
5. Disc width mu = (H - (n_turns - 1) * t_ins) / (active + dead discs).

Usage
-----
    python notice_to_plan.py notices/M9M10-int-n10.yaml [--output plan.json]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import yaml

from stacking_plan import StackingPlan

logger = logging.getLogger(__name__)

DEFAULT_PLATE_TOLERANCE = 0.0125
DEFAULT_INSULATOR_TOLERANCE = 0.00001

_ITEM_RE = re.compile(
    r"(\d+)\s*spires?\s+[àa]\s+(?:(\d+)\s*[x×]\s*(\d+)|(\d+))\s+disques?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ObservationItem:
    """One "N spires à K disques" item of the observations.

    Attributes
    ----------
    n_turns : int
        Number of turns.
    discs_per_turn : int
        Discs per turn.
    location : str
        ``"body"`` or ``"ends"``.
    factors : tuple of int or None
        ``(A, B)`` when written as "AxB disques", else None.
    """

    n_turns: int
    discs_per_turn: int
    location: str
    factors: tuple[int, int] | None = None


@dataclass
class Report:
    """Outcome of the notice interpretation.

    Attributes
    ----------
    reading : str
        End-turn reading kept: ``"per end"``, ``"total"`` or ``"body only"``.
    info : list of str
        Checks passed and derived values.
    warnings : list of str
        Failed checks and notes to review.
    """

    reading: str = ""
    info: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"reading of end turns: {self.reading}"]
        lines += [f"  {line}" for line in self.info]
        lines += [f"  WARNING: {w}" for w in self.warnings]
        return "\n".join(lines)


def load_notice(path: str | Path) -> dict:
    """Load a notice YAML file.

    Parameters
    ----------
    path : str or Path
        Notice file.

    Returns
    -------
    dict
        Raw notice fields.
    """
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def groups_per_turn(overlap: str) -> int:
    """Number of disc groups per turn for an electrical overlap.

    Parameters
    ----------
    overlap : str
        Overlap fraction, e.g. ``"3/4"``.

    Returns
    -------
    int
        ``1 / (1 - overlap)``.

    Raises
    ------
    ValueError
        If the result is not an integer >= 2.
    """
    f = Fraction(str(overlap))
    if not 0 < f < 1:
        raise ValueError(f"overlap must be in ]0, 1[, got {overlap}")
    g = 1 / (1 - f)
    if g.denominator != 1:
        raise ValueError(f"overlap {overlap} gives a non-integer {float(g):.3f} groups per turn")
    return int(g)


def parse_observations(text: str) -> list[ObservationItem]:
    """Extract the turn items from the observations text.

    Parameters
    ----------
    text : str
        Free-text observations of the sheet.

    Returns
    -------
    list of ObservationItem
        Items in text order; exactly one is the body.

    Raises
    ------
    ValueError
        If there is not exactly one body item and at most one ends item.
    """
    matches = list(_ITEM_RE.finditer(text))
    items = []
    for k, m in enumerate(matches):
        end = matches[k + 1].start() if k + 1 < len(matches) else len(text)
        context = text[m.end():end].lower()
        location = "body" if "centr" in context else "ends"
        if m.group(2):
            factors = (int(m.group(2)), int(m.group(3)))
            discs = factors[0] * factors[1]
        else:
            factors = None
            discs = int(m.group(4))
        items.append(ObservationItem(int(m.group(1)), discs, location, factors))
    n_body = sum(i.location == "body" for i in items)
    n_ends = sum(i.location == "ends" for i in items)
    if n_body != 1 or n_ends > 1:
        raise ValueError(
            f"expected one body item and at most one ends item in observations, "
            f"found {n_body} body and {n_ends} ends items"
        )
    return items


def resolve_segments(
    items: list[ObservationItem], active_qty: int
) -> tuple[list[dict], str]:
    """Choose the end-turn reading matching the active disc count.

    Parameters
    ----------
    items : list of ObservationItem
        Output of :func:`parse_observations`.
    active_qty : int
        Number of active discs on the sheet.

    Returns
    -------
    segments : list of dict
        Stacking-plan segments (bottom end, body, top end).
    reading : str
        ``"per end"``, ``"total"`` or ``"body only"``.

    Raises
    ------
    ValueError
        If no reading, or more than one, matches ``active_qty``.
    """
    body = next(i for i in items if i.location == "body")
    ends = next((i for i in items if i.location == "ends"), None)
    body_seg = {"n_turns": body.n_turns, "plates_per_turn": body.discs_per_turn, "plate": "plate"}
    if ends is None:
        candidates = {"body only": [body_seg]}
    else:
        candidates = {}
        for reading, n_end in (("per end", ends.n_turns), ("total", ends.n_turns / 2)):
            if n_end != int(n_end):
                continue
            end_seg = {"n_turns": int(n_end), "plates_per_turn": ends.discs_per_turn,
                       "plate": "plate"}
            candidates[reading] = [end_seg, body_seg, dict(end_seg)]
    counts = {r: sum(s["n_turns"] * s["plates_per_turn"] for s in segs)
              for r, segs in candidates.items()}
    matching = [r for r, c in counts.items() if c == active_qty]
    if len(matching) != 1:
        raise ValueError(
            f"no unique reading of the observations matches {active_qty} active discs "
            f"(disc counts per reading: {counts})"
        )
    return candidates[matching[0]], matching[0]


def build_plan(notice: dict) -> tuple[dict, Report]:
    """Build a stacking-plan config from a notice.

    Parameters
    ----------
    notice : dict
        Notice fields (see module docstring).

    Returns
    -------
    config : dict
        Stacking-plan configuration for ``stacking_plan.py``.
    report : Report
        Reading chosen, checks and warnings.

    Raises
    ------
    ValueError
        If the notice cannot be interpreted unambiguously.
    """
    report = Report()
    groups = groups_per_turn(notice["overlap"])
    items = parse_observations(notice["observations"])
    for item in items:
        if item.discs_per_turn % groups:
            report.warnings.append(
                f"{item.location}: {item.discs_per_turn} discs per turn is not a "
                f"multiple of {groups} groups per turn"
            )
        if item.factors and item.factors[0] != groups:
            report.warnings.append(
                f"{item.location}: '{item.factors[0]}x{item.factors[1]}' does not start "
                f"with {groups} groups per turn"
            )

    active = notice["active_discs"]
    segments, report.reading = resolve_segments(items, int(active["qty"]))
    n_turns = sum(s["n_turns"] for s in segments)
    layout = " + ".join(f"{s['n_turns']}x{s['plates_per_turn']}" for s in segments)
    report.info.append(f"segments: {layout} = {active['qty']} active discs, {n_turns} turns")

    dead = notice.get("dead_discs") or {}
    n_hp, n_bp = int(dead.get("hp", 0)), int(dead.get("bp", 0))
    n_discs = int(active["qty"]) + n_hp + n_bp

    ins = notice["insulators"]
    t_ins = float(ins["thickness"])
    material = str(ins.get("material", "kapton")).lower()
    if ins.get("qty") is not None:
        expected = groups * (n_turns - 1)
        if int(ins["qty"]) == expected:
            report.info.append(
                f"insulator count {ins['qty']} = {groups} x ({n_turns} - 1): one per turn"
            )
        else:
            report.warnings.append(
                f"insulator count {ins['qty']} differs from {groups} x ({n_turns} - 1) "
                f"= {expected}"
            )
    else:
        report.info.append("insulator count not given: check skipped")

    nominal = float(active["thickness"])
    height = notice.get("measured_height")
    if height is not None:
        mu = round((float(height) - (n_turns - 1) * t_ins) / n_discs, 4)
        report.info.append(
            f"disc width {mu} mm back-calculated from H = {height} mm "
            f"({(mu - nominal) / nominal:+.2%} vs nominal {nominal} mm)"
        )
        limits = notice.get("height_limits")
        if limits is not None:
            lo, hi = limits
            if lo <= float(height) <= hi:
                report.info.append(f"measured height within limits [{lo}, {hi}] mm")
            else:
                report.warnings.append(
                    f"measured height {height} mm outside height limits [{lo}, {hi}] mm"
                )
    else:
        mu = nominal
        report.info.append(f"no measured height: nominal disc width {mu} mm used")

    trange = notice.get("thickness_range")
    if trange is not None:
        lo, hi = trange
        if not lo <= mu <= hi:
            report.warnings.append(
                f"disc width {mu} mm outside thickness range [{lo}, {hi}] mm"
            )

    if notice.get("notes"):
        report.warnings.append(f"note: {str(notice['notes']).strip()}")

    tol = notice.get("tolerances") or {}
    cfg: dict = {
        "components": {
            "plate": {"mu": mu, "tolerance": tol.get("plate", DEFAULT_PLATE_TOLERANCE),
                      "distribution": "normal"},
            material: {"mu": t_ins,
                       "tolerance": tol.get("insulator", DEFAULT_INSULATOR_TOLERANCE),
                       "distribution": "uniform"},
        },
        "segments": segments,
    }
    if n_hp or n_bp:
        cfg["dead_discs"] = {"top": n_hp, "bottom": n_bp, "plate": "plate"}
    cfg["kapton"] = material
    cfg["n_kaptons"] = None

    plan = StackingPlan.from_config(cfg)
    report.info.append(
        f"plan: {plan.label}; nominal height {plan.nominal_height:.3f} mm, "
        f"magnetic centre offset {plan.magnetic_centre_offset:+.3f} mm"
    )
    return cfg, report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build a stacking-plan JSON from a Bitter notice YAML."
    )
    parser.add_argument("notice", help="notice YAML file")
    parser.add_argument("--output", metavar="JSON", default=None,
                        help="write the stacking plan to this file (default: print it)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: interpret a notice and write the stacking plan."""
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    args = parse_args(argv)
    try:
        cfg, report = build_plan(load_notice(args.notice))
    except (ValueError, KeyError) as err:
        logger.error("%s: %s", args.notice, err)
        return 1
    print(report)
    out = json.dumps(cfg, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        logger.info("stacking plan written to %s", args.output)
    else:
        print()
        print(out, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
