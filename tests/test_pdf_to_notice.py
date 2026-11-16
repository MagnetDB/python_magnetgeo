"""Tests for scripts/Bitter_stacking/pdf_to_notice.py."""

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[1]
_STACKING_DIR = _ROOT / "scripts" / "Bitter_stacking"
_SHEETS = Path(__file__).resolve().parent / "data" / "bitter_sheets"
sys.path.insert(0, str(_STACKING_DIR))

from notice_to_plan import build_plan, load_notice  # noqa: E402
from pdf_to_notice import dump_notice, parse_sheet  # noqa: E402


def _pages(name: str) -> list[str]:
    """Return the page texts of a fixture (pages separated by form feeds)."""
    return (_SHEETS / name).read_text(encoding="utf-8").split("\f")


def test_parse_n8():
    notice = parse_sheet(_pages("int-n8.txt"))
    assert notice["type"] == "bitter int M9/M10 (18MW)"
    assert notice["number"] == 8
    assert notice["date"] == "06/06/2023"
    assert notice["overlap"] == "3/4"
    assert notice["slit_direction"] == "left"
    assert notice["active_discs"] == {"qty": 728, "thickness": 0.8}
    assert notice["dead_discs"] == {"hp": 3, "bp": 0}
    assert notice["insulators"] == {"qty": 680, "thickness": 0.125, "material": "APTIV"}
    assert notice["measured_height"] == pytest.approx(603.0)
    assert notice["height_limits"] == pytest.approx([596.5, 605.0])
    assert "158 spires à 4 disques en partie centrale" in notice["observations"]
    assert "notes" not in notice


def test_parse_n9():
    notice = parse_sheet(_pages("int-n9.txt"))
    assert notice["number"] == 9
    assert notice["measured_height"] == pytest.approx(602.4)
    assert notice["dead_discs"] == {"hp": 0, "bp": 0}
    assert notice["insulators"]["qty"] == 648
    assert "notes" not in notice


def test_parse_n10_page2_dead_discs_noted():
    notice = parse_sheet(_pages("int-n10.txt"))
    assert notice["number"] == 10
    assert notice["measured_height"] == pytest.approx(599.44)
    assert notice["dead_discs"] == {"hp": 5, "bp": 5}
    assert notice["insulators"]["qty"] == 612
    assert "page 2" in notice["notes"]
    assert "page 1 kept" in notice["notes"]
    assert "aucun disque mort" in notice["notes"]


def test_n10_from_pdf_gives_hand_written_plan():
    cfg, report = build_plan(parse_sheet(_pages("int-n10.txt")))
    hand_cfg, _ = build_plan(load_notice(_STACKING_DIR / "notices" / "M9M10-int-n10.yaml"))
    assert cfg == hand_cfg
    assert any("page 2" in w for w in report.warnings)


def test_n8_plan():
    cfg, report = build_plan(parse_sheet(_pages("int-n8.txt")))
    assert [(s["n_turns"], s["plates_per_turn"]) for s in cfg["segments"]] == [
        (6, 8), (158, 4), (6, 8)
    ]
    assert cfg["dead_discs"] == {"top": 3, "bottom": 0, "plate": "plate"}
    assert cfg["components"]["plate"]["mu"] == pytest.approx(0.796)
    assert report.reading == "per end"


def test_no_text_layer():
    with pytest.raises(ValueError, match="no text layer"):
        parse_sheet(["", "  \n"])


def test_missing_required_field():
    pages = _pages("int-n9.txt")
    pages[0] = pages[0].replace("Disques actifs", "Disques ???")
    with pytest.raises(ValueError, match="active_discs"):
        parse_sheet(pages)


def test_dump_round_trip():
    notice = parse_sheet(_pages("int-n10.txt"))
    text = dump_notice(notice, source="int-n10.pdf")
    assert text.startswith("# extracted from int-n10.pdf")
    assert yaml.safe_load(text) == notice
