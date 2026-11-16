#!/usr/bin/env python3
"""Extract a notice YAML from a digital Bitter identification sheet (PDF).

Reads the text layer of a "fiche d'identification aimant Bitter" (form
FOR 007 A) and writes the notice YAML used by ``notice_to_plan.py``. Page 1
is authoritative: every value comes from page 1, except ``height_limits``
which only appears on page 2. Sentences of the form "N disques morts en HP
et M en BP" are compared with the dead-disc rows of the table; a
disagreement is recorded in ``notes`` (the table is kept).

Scanned sheets have no text layer and must be transcribed by hand.

Usage
-----
    python pdf_to_notice.py sheet.pdf [--output notices/name.yaml]
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_NUM = r"\d+(?:[.,]\d+)?"
_DIMS = rf"Ø\s*{_NUM}\s*x\s*Ø\s*{_NUM}\s*x\s*({_NUM})\s*mm"

_TYPE_RE = re.compile(r"TYPE BOBINAGE\s*:\s*(.+)")
_NUMBER_RE = re.compile(r"^\s*N°\s+(\d+)\s*$", re.MULTILINE)
_DATE_RE = re.compile(r"DATE\s*:\s*(\d{2}/\d{2}/\d{4})")
_OVERLAP_RE = re.compile(r"RECOUVREMENT\s+[EÉ]LECTRIQUE\s*:\s*(\d+\s*/\s*\d+)")
_SLIT_RE = re.compile(r"fente\s+se\s+d[ée]place\s+vers\s+la\s+(gauche|droite)")
_HEIGHT_RE = re.compile(rf"dynamom[ée]trique\s+{_NUM}\s+\d+\s*N\s+({_NUM})")
_ACTIVE_RE = re.compile(rf"Disques\s+actifs\s+\S+\s+(\d+)\s+{_DIMS}")
_DEAD_RE = re.compile(r"Disques\s+«\s*morts\s*»\s+(HP|BP)\s+\S+\s+(\d+)")
_INSULATOR_RE = re.compile(rf"Isolants\s+(\S+)\s+\S+\s+(?:(\d+)\s+)?{_DIMS}")
_LIMIT_RE = {
    "mini": re.compile(rf"C[ôo]te\s+mini[^\n]*?({_NUM})\s*mm"),
    "maxi": re.compile(rf"C[ôo]te\s+maxi[^\n]*?({_NUM})\s*mm"),
}
_OBS_RE = re.compile(r"OBSERVATIONS\s*:\s*\n(.*?)(?:GRENOBLE HIGH|\Z)", re.DOTALL)
_DEAD_SENTENCE_RE = re.compile(
    r"(\d+|aucun)\s+disques?\s+morts?\s+en\s+HP\s+et\s+"
    r"(?:(\d+|aucun)\s+(?:disques?\s+morts?\s+)?)?en\s+BP",
    re.IGNORECASE,
)


def _num(text: str) -> float:
    """Parse a number written with a decimal point or comma."""
    return float(text.replace(",", "."))


def _count(text: str | None, default: int) -> int:
    """Parse a dead-disc count ("aucun" = 0, None = default)."""
    if text is None:
        return default
    return 0 if text.lower() == "aucun" else int(text)


def extract_pages(path: str | Path) -> list[str]:
    """Return the text layer of each page of a PDF.

    Parameters
    ----------
    path : str or Path
        PDF file.

    Returns
    -------
    list of str
        One text per page (empty for a scanned page).
    """
    from pypdf import PdfReader

    return [page.extract_text() or "" for page in PdfReader(str(path)).pages]


def dead_disc_statements(text: str) -> list[tuple[int, int, str]]:
    """Find the sentences giving the HP and BP dead-disc counts.

    Parameters
    ----------
    text : str
        Text to search (whitespace is collapsed first).

    Returns
    -------
    list of tuple
        ``(hp, bp, sentence)`` for each statement.
    """
    flat = " ".join(text.split())
    out = []
    for m in _DEAD_SENTENCE_RE.finditer(flat):
        hp = _count(m.group(1), 0)
        out.append((hp, _count(m.group(2), hp), m.group(0)))
    return out


def parse_sheet(pages: list[str]) -> dict:
    """Build a notice from the page texts of an identification sheet.

    Parameters
    ----------
    pages : list of str
        Text of each page, page 1 first.

    Returns
    -------
    dict
        Notice fields, in the order used by the hand-written notices.

    Raises
    ------
    ValueError
        If the sheet has no text layer or a required field is missing
        (overlap, active discs, insulators, observations).
    """
    pages = [p.replace("\xa0", " ") for p in pages]
    if not any(p.strip() for p in pages):
        raise ValueError("no text layer (scanned sheet?): transcribe by hand")
    page1 = pages[0]
    notice: dict = {}
    missing = []

    if m := _TYPE_RE.search(page1):
        notice["type"] = m.group(1).strip()
    if m := _NUMBER_RE.search(page1):
        notice["number"] = int(m.group(1))
    if m := _DATE_RE.search(page1):
        notice["date"] = m.group(1)
    if m := _OVERLAP_RE.search(page1):
        notice["overlap"] = re.sub(r"\s", "", m.group(1))
    else:
        missing.append("overlap")
    if m := _SLIT_RE.search(page1):
        notice["slit_direction"] = "left" if m.group(1) == "gauche" else "right"
    if m := _ACTIVE_RE.search(page1):
        notice["active_discs"] = {"qty": int(m.group(1)), "thickness": _num(m.group(2))}
    else:
        missing.append("active_discs")
    dead = {side: int(qty) for side, qty in _DEAD_RE.findall(page1)}
    if dead:
        notice["dead_discs"] = {"hp": dead.get("HP", 0), "bp": dead.get("BP", 0)}
    if m := _INSULATOR_RE.search(page1):
        notice["insulators"] = {
            "qty": int(m.group(2)) if m.group(2) else None,
            "thickness": _num(m.group(3)),
            "material": m.group(1),
        }
    else:
        missing.append("insulators")
    if m := _HEIGHT_RE.search(page1):
        notice["measured_height"] = _num(m.group(1))
    text = "\n".join(pages)
    limits = [_LIMIT_RE[k].search(text) for k in ("mini", "maxi")]
    if all(limits):
        notice["height_limits"] = [_num(m.group(1)) for m in limits]
    if m := _OBS_RE.search(page1):
        lines = [line.strip() for line in m.group(1).splitlines()]
        notice["observations"] = "\n".join(line for line in lines if line) + "\n"
    else:
        missing.append("observations")
    if missing:
        raise ValueError(f"fields not found in the sheet: {', '.join(missing)}")

    table = (notice.get("dead_discs", {}).get("hp", 0), notice.get("dead_discs", {}).get("bp", 0))
    notes = []
    for k, page in enumerate(pages, start=1):
        for hp, bp, sentence in dead_disc_statements(page):
            if (hp, bp) != table:
                where = "page 1 text" if k == 1 else f"page {k}"
                notes.append(
                    f'{where} differs from page 1 (page 1 kept): "{sentence}" gives '
                    f"{hp} HP / {bp} BP dead discs, the table {table[0]} HP / {table[1]} BP."
                )
    if notes:
        notice["notes"] = "\n".join(notes) + "\n"
    return notice


class _NoticeDumper(yaml.SafeDumper):
    """YAML dumper writing multi-line strings as literal blocks."""


def _str_representer(dumper: yaml.SafeDumper, data: str) -> yaml.Node:
    """Represent multi-line strings with the ``|`` style."""
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_NoticeDumper.add_representer(str, _str_representer)


def dump_notice(notice: dict, source: str) -> str:
    """Serialise a notice to YAML with a provenance header.

    Parameters
    ----------
    notice : dict
        Notice fields.
    source : str
        Name of the PDF the notice was extracted from.

    Returns
    -------
    str
        YAML text.
    """
    header = f"# extracted from {source} - review before use\n"
    body = yaml.dump(notice, Dumper=_NoticeDumper, sort_keys=False,
                     allow_unicode=True, default_flow_style=None)
    return header + body


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract a notice YAML from a digital Bitter identification sheet."
    )
    parser.add_argument("pdf", help="identification sheet (PDF with a text layer)")
    parser.add_argument("--output", metavar="YAML", default=None,
                        help="write the notice to this file (default: print it)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: extract the notice and write it."""
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    args = parse_args(argv)
    try:
        notice = parse_sheet(extract_pages(args.pdf))
    except ValueError as err:
        logger.error("%s: %s", args.pdf, err)
        return 1
    for note in notice.get("notes", "").splitlines():
        logger.warning("%s", note)
    text = dump_notice(notice, Path(args.pdf).name)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        logger.info("notice written to %s", args.output)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
