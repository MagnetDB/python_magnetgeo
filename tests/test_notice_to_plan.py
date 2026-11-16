"""Tests for scripts/Bitter_stacking/notice_to_plan.py."""

import copy
import json
import sys
from pathlib import Path

import pytest

_STACKING_DIR = Path(__file__).resolve().parents[1] / "scripts" / "Bitter_stacking"
sys.path.insert(0, str(_STACKING_DIR))

from notice_to_plan import (  # noqa: E402
    build_plan,
    groups_per_turn,
    load_notice,
    parse_observations,
    resolve_segments,
)

N5_OBS = (
    "-Aimant constitué de 14 spires à 4x4 disques\n"
    "et de 62 spires à 4x2 disques en partie centrale.\n"
)
N10_OBS = (
    "-Aimant constitué de 14 spires à 8 disques aux extrémités. (HPet BP)\n"
    "-126 spires à 4 disques en partie centrale. (Aimant pour 18MW).\n"
)


def _seg(cfg: dict) -> list[tuple[int, int]]:
    """Return the (n_turns, plates_per_turn) pairs of a plan config."""
    return [(s["n_turns"], s["plates_per_turn"]) for s in cfg["segments"]]


def test_groups_per_turn():
    assert groups_per_turn("3/4") == 4
    assert groups_per_turn("2/3") == 3
    with pytest.raises(ValueError):
        groups_per_turn("3/5")


def test_parse_observations_n5():
    items = parse_observations(N5_OBS)
    assert [(i.n_turns, i.discs_per_turn, i.location) for i in items] == [
        (14, 16, "ends"),
        (62, 8, "body"),
    ]
    assert items[0].factors == (4, 4)


def test_parse_observations_n10():
    items = parse_observations(N10_OBS)
    assert [(i.n_turns, i.discs_per_turn, i.location) for i in items] == [
        (14, 8, "ends"),
        (126, 4, "body"),
    ]
    assert items[0].factors is None


def test_resolve_segments_total_reading():
    segments, reading = resolve_segments(parse_observations(N5_OBS), 720)
    assert reading == "total"
    assert [(s["n_turns"], s["plates_per_turn"]) for s in segments] == [
        (7, 16), (62, 8), (7, 16)
    ]


def test_resolve_segments_per_end_reading():
    segments, reading = resolve_segments(parse_observations(N10_OBS), 728)
    assert reading == "per end"
    assert [(s["n_turns"], s["plates_per_turn"]) for s in segments] == [
        (14, 8), (126, 4), (14, 8)
    ]


def test_resolve_segments_no_match():
    with pytest.raises(ValueError):
        resolve_segments(parse_observations(N10_OBS), 700)


def test_parse_observations_needs_body():
    with pytest.raises(ValueError):
        parse_observations("14 spires à 8 disques aux extrémités")


@pytest.mark.parametrize(
    "notice_name, plan_name",
    [("M9M10-ext-n5.yaml", "M9M10-ext-n5.json"),
     ("M9M10-int-n10.yaml", "M9M10-int-n10.json")],
)
def test_notice_reproduces_hand_written_plan(notice_name, plan_name):
    cfg, _report = build_plan(load_notice(_STACKING_DIR / "notices" / notice_name))
    expected = json.loads((_STACKING_DIR / plan_name).read_text(encoding="utf-8"))
    assert _seg(cfg) == _seg(expected)
    assert cfg["dead_discs"]["top"] == expected["dead_discs"]["top"]
    assert cfg["dead_discs"]["bottom"] == expected["dead_discs"]["bottom"]
    assert cfg["kapton"] == expected["kapton"]
    assert cfg["n_kaptons"] is None
    assert cfg["components"]["plate"]["mu"] == pytest.approx(
        expected["components"]["plate"]["mu"], abs=5e-4
    )


def test_n10_report_has_no_check_warnings():
    _cfg, report = build_plan(load_notice(_STACKING_DIR / "notices" / "M9M10-int-n10.yaml"))
    assert report.reading == "per end"
    assert not any("insulator count" in w for w in report.warnings)
    assert not any("outside" in w for w in report.warnings)


def _n10() -> dict:
    return copy.deepcopy(load_notice(_STACKING_DIR / "notices" / "M9M10-int-n10.yaml"))


def test_warning_insulator_count():
    notice = _n10()
    notice["insulators"]["qty"] = 600
    _cfg, report = build_plan(notice)
    assert any("insulator count" in w for w in report.warnings)


def test_warning_height_limits():
    notice = _n10()
    notice["height_limits"] = [600.0, 605.0]
    _cfg, report = build_plan(notice)
    assert any("outside height limits" in w for w in report.warnings)


def test_warning_thickness_range():
    notice = _n10()
    notice["thickness_range"] = [0.790, 0.800]
    _cfg, report = build_plan(notice)
    assert any("outside thickness range" in w for w in report.warnings)


def test_nominal_thickness_without_measured_height():
    notice = _n10()
    del notice["measured_height"]
    cfg, _report = build_plan(notice)
    assert cfg["components"]["plate"]["mu"] == pytest.approx(0.8)
