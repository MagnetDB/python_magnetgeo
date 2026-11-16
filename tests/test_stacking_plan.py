"""Tests for scripts/Bitter_stacking/stacking_plan.py (dead-disc support)."""

import copy
import sys
from pathlib import Path

import pytest

_STACKING_DIR = Path(__file__).resolve().parents[1] / "scripts" / "Bitter_stacking"
sys.path.insert(0, str(_STACKING_DIR))

from stacking_plan import StackingPlan, analytic_rss  # noqa: E402

N5_CONFIG = {
    "components": {
        "plate": {"mu": 0.796, "tolerance": 0.0125, "distribution": "normal"},
        "aptiv": {"mu": 0.125, "tolerance": 0.00001, "distribution": "uniform"},
    },
    "segments": [
        {"n_turns": 7, "plates_per_turn": 16, "plate": "plate"},
        {"n_turns": 62, "plates_per_turn": 8, "plate": "plate"},
        {"n_turns": 7, "plates_per_turn": 16, "plate": "plate"},
    ],
    "dead_discs": {"top": 7, "bottom": 12, "plate": "plate"},
    "kapton": "aptiv",
    "n_kaptons": None,
}


def _without_dead(cfg: dict) -> dict:
    """Return a copy of cfg without the dead_discs field."""
    cfg = copy.deepcopy(cfg)
    cfg.pop("dead_discs")
    return cfg


def test_no_dead_discs_unchanged():
    plan = StackingPlan.from_config(_without_dead(N5_CONFIG))
    assert plan.n_dead_top == 0
    assert plan.n_dead_bottom == 0
    assert plan.n_plates == 720
    assert plan.nominal_height == pytest.approx(720 * 0.796 + 75 * 0.125)
    assert plan.magnetic_centre_offset == pytest.approx(0.0)
    assert "dead" not in plan.label


def test_n5_counts_and_height():
    plan = StackingPlan.from_config(N5_CONFIG)
    assert plan.n_turns == 76
    assert plan.n_plates == 720
    assert plan.n_dead_top == 7
    assert plan.n_dead_bottom == 12
    assert plan.n_kaptons == 75
    assert plan.nominal_height == pytest.approx(597.619)
    assert analytic_rss(plan).mean == pytest.approx(597.619)
    plate_group = next(g for g in plan.groups if g.component.name == "plate")
    assert plate_group.count == 739


def test_n5_magnetic_centre_offset():
    plan = StackingPlan.from_config(N5_CONFIG)
    assert plan.magnetic_centre_offset == pytest.approx((12 - 7) * 0.796 / 2)


def test_dead_discs_default_plate_component():
    cfg = copy.deepcopy(N5_CONFIG)
    del cfg["dead_discs"]["plate"]
    plan = StackingPlan.from_config(cfg)
    assert plan.nominal_height == pytest.approx(597.619)


@pytest.mark.parametrize("key", ["top", "bottom"])
def test_dead_discs_negative_rejected(key):
    cfg = copy.deepcopy(N5_CONFIG)
    cfg["dead_discs"][key] = -1
    with pytest.raises(ValueError):
        StackingPlan.from_config(cfg)


def test_dead_discs_unknown_component_rejected():
    cfg = copy.deepcopy(N5_CONFIG)
    cfg["dead_discs"]["plate"] = "nope"
    with pytest.raises(ValueError):
        StackingPlan.from_config(cfg)
