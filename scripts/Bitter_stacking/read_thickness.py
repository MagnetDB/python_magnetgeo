#!/usr/bin/env python3
"""Analyse measured plate thicknesses from an Excel file.

Reads one or more sheets from an xlsx workbook (columns: disc index,
thickness), computes summary statistics, and optionally patches the
``components.plate`` entry of a JSON stacking-plan config.

The thickness column is chosen by ``--column`` or, by default, by name
(``épaisseur``, ``epaisseur``, ``thickness``, ``ep``, case/accent-insensitive).
Values stored as text with a decimal comma (``0,78``) are converted.

The patched config sets ``sigma_syst = sigma/sqrt(n)``: the standard error on
the measured mean is shared by every plate in the stack, so it adds
``(N_plates × sigma/sqrt(n))²`` to the stack variance.

Usage
-----
    python read_thickness.py thickness.xlsx
    python read_thickness.py thickness.xlsx --sheet Feuil1 --config plan.json
    python read_thickness.py thickness.xlsx --output new_plan.json --config plan.json
    python read_thickness.py thickness.xlsx --column "Ep. (mm)"
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

THICKNESS_COLUMN_NAMES = ("epaisseur", "thickness", "ep")


def _normalise(label: object) -> str:
    """Lower-case, strip accents and surrounding whitespace from a column label."""
    text = unicodedata.normalize("NFKD", str(label))
    return "".join(c for c in text if not unicodedata.combining(c)).strip().lower()


def _find_thickness_column(df: pd.DataFrame, column: str | None) -> object:
    """Return the label of the thickness column, or raise ValueError."""
    if column is not None:
        for label in df.columns:
            if _normalise(label) == _normalise(column):
                return label
        raise ValueError(f"column {column!r} not found (columns: {list(df.columns)})")
    for label in df.columns:
        if _normalise(label) in THICKNESS_COLUMN_NAMES:
            return label
    raise ValueError(
        f"no thickness column found among {list(df.columns)}; "
        f"expected one of {THICKNESS_COLUMN_NAMES} or pass --column"
    )


def _to_float(series: pd.Series) -> pd.Series:
    """Convert to float, accepting text with a decimal comma; unparsable → NaN."""
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(float)
    text = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(text, errors="coerce")


def _check_values(name: str, values: np.ndarray) -> None:
    """Reject data that cannot be plate thicknesses (e.g. an index column)."""
    if len(values) < 2:
        raise ValueError(f"sheet {name!r}: need at least 2 measurements, got {len(values)}")
    if np.any(values <= 0):
        raise ValueError(f"sheet {name!r}: non-positive thickness values found")
    if np.all(values == np.round(values)) and len(np.unique(values)) == len(values):
        raise ValueError(
            f"sheet {name!r}: values are distinct integers {values.min():g}..{values.max():g}, "
            "this looks like an index column, not thicknesses (use --column)"
        )


def load_thicknesses(
    path: str | Path, sheet: str | None = None, column: str | None = None
) -> dict[str, np.ndarray]:
    """Return {sheet_name: thickness_array} for each sheet (or just the requested one)."""
    xl = pd.ExcelFile(path)
    sheets = [sheet] if sheet else xl.sheet_names
    result: dict[str, np.ndarray] = {}
    for name in sheets:
        df = xl.parse(name)
        try:
            label = _find_thickness_column(df, column)
        except ValueError as err:
            if sheet:
                raise ValueError(f"sheet {name!r}: {err}") from err
            logger.warning("sheet %r: %s, skipping", name, err)
            continue
        raw = df[label]
        converted = _to_float(raw)
        # pandas already maps 'n/a', 'NaN', '' ... to NaN, so report every
        # dropped row (empty or unparsable), with the offending text if any.
        dropped = raw[converted.isna()]
        if len(dropped):
            logger.warning(
                "sheet %r: ignoring %d empty or non-numeric entries in column %r "
                "(rows %s, values %s)",
                name, len(dropped), label,
                [i + 2 for i in dropped.index[:5]],  # Excel row numbers (header = 1)
                dropped.tolist()[:5],
            )
        values = converted.dropna().to_numpy(dtype=float)
        _check_values(name, values)
        result[name] = values
        logger.info("sheet %r: loaded %d measurements from column %r", name, len(values), label)
    return result


def statistics(values: np.ndarray) -> dict:
    """Compute descriptive statistics of a thickness array."""
    mu = float(np.mean(values))
    sigma = float(np.std(values, ddof=1))
    tol = float(max(abs(values.max() - mu), abs(mu - values.min())))
    return {
        "n": len(values),
        "mu": mu,
        "sigma": sigma,
        "sem": sigma / float(np.sqrt(len(values))),  # standard error of the mean
        "tolerance": tol,
        "min": float(values.min()),
        "max": float(values.max()),
    }


def print_summary(all_stats: dict[str, dict]) -> None:
    """Print a table of statistics for all sheets."""
    header = (
        f"{'Sheet':<14} {'n':>5} {'min':>8} {'max':>8} {'mu':>10} {'sigma':>10}"
        f" {'sem':>10} {'tol':>10} {'3sigma':>10}"
    )
    print()
    print(header)
    print("-" * len(header))
    for sheet, stats in all_stats.items():
        mu, sigma, tol = stats["mu"], stats["sigma"], stats["tolerance"]
        print(
            f"{sheet:<14} {stats['n']:>5} {stats['min']:>8.4f} {stats['max']:>8.4f}"
            f" {mu:>10.6f} {sigma:>10.6f} {stats['sem']:>10.6f} {tol:>10.6f} {3*sigma:>10.6f}"
        )
    print("  sem = sigma/sqrt(n): uncertainty on mu, shared by every plate of the stack")
    print()


def patch_config(cfg: dict, stats: dict) -> dict:
    """Return a copy of a stacking-plan config with the 'plate' component
    replaced by the measured statistics.

    ``sigma`` is the measured piece-to-piece scatter. ``sigma_syst`` is set to
    the standard error of the measured mean: every plate in the stack shares
    that error, so it contributes ``(N_plates * sem)**2`` to the stack variance.
    ``tolerance`` is removed so that it is derived from ``sigma``.
    """
    cfg = copy.deepcopy(cfg)
    plate = cfg.setdefault("components", {}).setdefault("plate", {})
    old_syst = plate.get("sigma_syst")
    sem = round(stats["sem"], 6)
    if old_syst not in (None, 0, 0.0, sem):
        logger.warning(
            "plate: replacing sigma_syst=%g by the measured standard error of the mean %g",
            old_syst, sem,
        )
    plate["mu"] = round(stats["mu"], 6)
    plate["sigma"] = round(stats["sigma"], 6)
    plate["sigma_syst"] = sem
    plate.pop("tolerance", None)
    plate.setdefault("distribution", "normal")
    return cfg


def plot_distribution(data: dict[str, np.ndarray], all_stats: dict[str, dict], path: str) -> None:
    """Save a histogram + KDE + Gaussian fit for each sheet."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.stats import norm

    n_sheets = len(data)
    fig, axes = plt.subplots(1, n_sheets, figsize=(6 * n_sheets, 5), squeeze=False)

    for ax, (name, values) in zip(axes[0], data.items(), strict=True):
        stats = all_stats[name]
        mu, sigma = stats["mu"], stats["sigma"]
        tol = stats["tolerance"]

        ax.hist(values, bins="auto", density=True, alpha=0.55,
                color="steelblue", label="measured")

        x = np.linspace(values.min() - 3 * sigma, values.max() + 3 * sigma, 300)
        ax.plot(x, norm.pdf(x, mu, sigma), "k-", lw=2,
                label=rf"$\mathcal{{N}}(\mu={mu:.4f},\,\sigma={sigma:.5f})$")

        for sign, ls in ((1, "--"), (-1, "--")):
            ax.axvline(mu + sign * tol, color="red", ls=ls, lw=1)
        ax.axvline(mu, color="gray", ls=":", lw=1, label=rf"$\mu={mu:.4f}$")

        ax.set_xlabel("épaisseur (mm)")
        ax.set_ylabel("probability density")
        ax.set_title(f"Sheet: {name!r}  (n={stats['n']})", fontsize=10)
        ax.legend(fontsize=8)

    from matplotlib.patches import Patch
    for ax, (_name, stats) in zip(axes[0], all_stats.items(), strict=True):
        tol = stats["tolerance"]
        legend = ax.get_legend()
        existing = getattr(legend, "legend_handles", None) or getattr(legend, "legendHandles", [])
        ax.legend(
            handles=existing + [
                Patch(facecolor="none", edgecolor="red", ls="--",
                      label=rf"tol $\pm${tol:.5f}")
            ],
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    logger.info("distribution plot saved to %s", path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyse plate thicknesses from an Excel file."
    )
    parser.add_argument("xlsx", help="Excel workbook with thickness measurements")
    parser.add_argument("--sheet", default=None,
                        help="sheet name to process (default: all sheets)")
    parser.add_argument("--config", metavar="JSON", default=None,
                        help="stacking-plan JSON to patch with measured statistics")
    parser.add_argument("--output", metavar="JSON", default=None,
                        help="write patched config to this file (default: print to stdout)")
    parser.add_argument("--column", default=None,
                        help="name of the thickness column (default: auto-detect "
                             f"from {', '.join(THICKNESS_COLUMN_NAMES)})")
    parser.add_argument("--plot", metavar="PNG", default=None,
                        help="save a distribution histogram to this file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        stream=sys.stderr, level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    try:
        data = load_thicknesses(args.xlsx, args.sheet, args.column)
    except ValueError as err:
        logger.error("%s", err)
        return 1
    if not data:
        logger.error("no thickness data found in %s", args.xlsx)
        return 1

    all_stats = {name: statistics(vals) for name, vals in data.items()}

    print_summary(all_stats)

    if args.plot:
        plot_distribution(data, all_stats, args.plot)

    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)

        # Use the first (or only) sheet's stats to patch the config
        first_stats = next(iter(all_stats.values()))
        patched = patch_config(cfg, first_stats)

        out = json.dumps(patched, indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            logger.info("patched config written to %s", args.output)
        else:
            print("\nPatched config:")
            print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
