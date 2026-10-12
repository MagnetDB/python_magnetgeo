#!/usr/bin/env python3
"""Analyse measured plate thicknesses from an Excel file.

Reads one or more sheets from an xlsx workbook (columns: disc index,
thickness), computes summary statistics, and optionally patches the
``components.plate`` entry of a JSON stacking-plan config.

Usage
-----
    python read_thickness.py thickness.xlsx
    python read_thickness.py thickness.xlsx --sheet Feuil1 --config plan.json
    python read_thickness.py thickness.xlsx --output new_plan.json --config plan.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def load_thicknesses(path: str | Path, sheet: str | None = None) -> dict[str, np.ndarray]:
    """Return {sheet_name: thickness_array} for each sheet (or just the requested one)."""
    xl = pd.ExcelFile(path)
    sheets = [sheet] if sheet else xl.sheet_names
    result: dict[str, np.ndarray] = {}
    for name in sheets:
        df = xl.parse(name)
        # thickness column: second numeric column, or column named 'épaisseur' / 'thickness'
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) < 1:
            logger.warning("sheet %r: no numeric columns found, skipping", name)
            continue
        # Skip first column if it looks like a row index (1, 2, 3, …)
        thickness_col = numeric_cols[1] if len(numeric_cols) >= 2 else numeric_cols[0]
        values = df[thickness_col].dropna().to_numpy(dtype=float)
        result[name] = values
        logger.info("sheet %r: loaded %d measurements from column %r", name, len(values), thickness_col)
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
        "tolerance": tol,
        "min": float(values.min()),
        "max": float(values.max()),
    }


def print_summary(all_stats: dict[str, dict]) -> None:
    """Print a table of statistics for all sheets."""
    header = f"{'Sheet':<14} {'n':>5} {'min':>8} {'max':>8} {'mu':>10} {'sigma':>10} {'tol':>10} {'3sigma':>10}"
    print()
    print(header)
    print("-" * len(header))
    for sheet, stats in all_stats.items():
        mu, sigma, tol = stats["mu"], stats["sigma"], stats["tolerance"]
        print(
            f"{sheet:<14} {stats['n']:>5} {stats['min']:>8.4f} {stats['max']:>8.4f}"
            f" {mu:>10.6f} {sigma:>10.6f} {tol:>10.6f} {3*sigma:>10.6f}"
        )
    print()


def patch_config(cfg: dict, stats: dict) -> dict:
    """Update the 'plate' component in a stacking-plan config dict in-place."""
    import copy
    cfg = copy.deepcopy(cfg)
    plate = cfg.setdefault("components", {}).setdefault("plate", {})
    plate["mu"] = round(stats["mu"], 6)
    plate["sigma"] = round(stats["sigma"], 6)
    # keep tolerance as the empirical max deviation; remove stale 'tolerance' if sigma is set
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

    for ax, (name, values) in zip(axes[0], data.items()):
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
    for ax, (name, stats) in zip(axes[0], all_stats.items()):
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
    parser.add_argument("--plot", metavar="PNG", default=None,
                        help="save a distribution histogram to this file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        stream=sys.stderr, level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    data = load_thicknesses(args.xlsx, args.sheet)
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
