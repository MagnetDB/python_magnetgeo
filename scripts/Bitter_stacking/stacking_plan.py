#!/usr/bin/env python3
"""Tolerance stacking for a magnet stacking plan, driven by a JSON config.

The stacking schema, component widths, tolerances and tolerance
distributions are all read from a JSON file (``--config``). Example::

    {
      "components": {
        "plate_end":  {"mu": 2.0,   "tolerance": 0.15, "distribution": "normal"},
        "plate_body": {"mu": 2.0,   "sigma": 0.05,     "distribution": "normal"},
        "kapton":     {"mu": 0.125, "tolerance": 0.02, "distribution": "uniform"}
      },
      "segments": [
        {"n_turns": 6,   "plates_per_turn": 8, "plate": "plate_end"},
        {"n_turns": 158, "plates_per_turn": 4, "plate": "plate_body"},
        {"n_turns": 6,   "plates_per_turn": 8, "plate": "plate_end"}
      ],
      "kapton": "kapton",
      "n_kaptons": null
    }

Component fields
----------------
mu : float
    Mean (nominal) width.
sigma : float, optional
    Standard deviation of the random, piece-to-piece part. Either
    ``sigma`` or ``tolerance`` must be given.
tolerance : float, optional
    Half-width of the tolerance band (mu +/- tolerance). Converted to a
    standard deviation according to ``distribution``:

    * ``normal``     : sigma = tolerance / tolerance_k   (default k=3)
    * ``uniform``    : sigma = tolerance / sqrt(3)
    * ``triangular`` : sigma = tolerance / sqrt(6)
sigma_syst : float, optional
    Standard deviation of a systematic offset shared by *all* pieces of
    this component type in one stack (batch bias). Default 0.
distribution : {"normal", "uniform", "triangular"}, optional
    Distribution of the random part. Default ``"normal"``.
tolerance_k : float, optional
    Coverage factor used to convert ``tolerance`` to ``sigma`` for the
    normal distribution (default 3, i.e. tolerance = 3 sigma).

Plan fields
-----------
segments : list
    Ordered groups of turns. Each entry: ``n_turns``,
    ``plates_per_turn`` and ``plate`` (component name). The axial
    height of a turn is the sum of its plate widths.
kapton : str
    Component name used for the inter-turn insulation.
n_kaptons : int or null, optional
    Number of kapton sheets; null means one between each pair of
    consecutive turns (``total_turns - 1``).

Analytic model
--------------
With independent pieces, contributions add in quadrature per component
group g (N_g pieces, sigma_g):

    E[H]   = sum_g N_g * mu_g
    var[H] = sum_g ( N_g * sigma_g^2 + (N_g * sigma_syst_g)^2 )

H is approximately Gaussian (CLT), whatever the per-piece distribution.
The worst-case bound uses the hard tolerance limit of each piece
(``tolerance`` if given, else k*sigma) all in the same direction. A
Monte Carlo simulation cross-checks both, sampling each component from
its declared distribution.

Usage
-----
    python stacking_plan.py --config plan.json [--samples 100000]
                            [--coverage 3] [--plot stack.png] [--seed 42]
    python stacking_plan.py --write-example plan.json   # starter config
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

_TOL_TO_SIGMA = {
    "normal": lambda tol, k: tol / k,
    "uniform": lambda tol, k: tol / np.sqrt(3.0),
    "triangular": lambda tol, k: tol / np.sqrt(6.0),
}

EXAMPLE_CONFIG: dict = {
    "components": {
        "plate": {"mu": 2.0, "tolerance": 0.15, "distribution": "normal"},
        "kapton": {"mu": 0.125, "tolerance": 0.02, "distribution": "uniform"},
    },
    "segments": [
        {"n_turns": 6, "plates_per_turn": 8, "plate": "plate"},
        {"n_turns": 158, "plates_per_turn": 4, "plate": "plate"},
        {"n_turns": 6, "plates_per_turn": 8, "plate": "plate"},
    ],
    "kapton": "kapton",
    "n_kaptons": None,
}


@dataclass(frozen=True)
class Component:
    """A stacked component type (plate or kapton sheet).

    Attributes
    ----------
    name : str
        Component label.
    mu : float
        Mean width.
    sigma : float
        Random (piece-to-piece) standard deviation.
    tolerance : float
        Hard half-width of the tolerance band (used for the worst-case
        bound; equals k*sigma if not given explicitly).
    sigma_syst : float
        Systematic (batch) standard deviation.
    distribution : str
        Random-part distribution: 'normal', 'uniform' or 'triangular'.
    """

    name: str
    mu: float
    sigma: float
    tolerance: float
    sigma_syst: float = 0.0
    distribution: str = "normal"

    @classmethod
    def from_dict(cls, name: str, d: dict, default_k: float = 3.0) -> "Component":
        """Build a Component from a JSON dictionary entry."""
        dist = d.get("distribution", "normal")
        if dist not in _TOL_TO_SIGMA:
            raise ValueError(
                f"component {name!r}: unknown distribution {dist!r} "
                f"(expected one of {sorted(_TOL_TO_SIGMA)})"
            )
        k = float(d.get("tolerance_k", default_k))
        sigma = d.get("sigma")
        tol = d.get("tolerance")
        if sigma is None and tol is None:
            raise ValueError(f"component {name!r}: need 'sigma' or 'tolerance'")
        if sigma is None:
            sigma = float(_TOL_TO_SIGMA[dist](float(tol), k))
        if tol is None:
            tol = k * float(sigma)
        return cls(
            name=name,
            mu=float(d["mu"]),
            sigma=float(sigma),
            tolerance=float(tol),
            sigma_syst=float(d.get("sigma_syst", 0.0)),
            distribution=dist,
        )


@dataclass(frozen=True)
class Group:
    """N identical pieces of one component type in the stack."""

    component: Component
    count: int


@dataclass(frozen=True)
class StackingPlan:
    """Resolved stacking plan: component groups + bookkeeping."""

    groups: list[Group]
    n_turns: int
    n_plates: int
    n_kaptons: int
    label: str

    @classmethod
    def from_config(cls, cfg: dict) -> "StackingPlan":
        """Build the plan from a parsed JSON configuration."""
        components = {
            name: Component.from_dict(name, d)
            for name, d in cfg["components"].items()
        }

        plate_counts: dict[str, int] = {}
        n_turns = 0
        n_plates = 0
        parts = []
        for seg in cfg["segments"]:
            nt, ppt = int(seg["n_turns"]), int(seg["plates_per_turn"])
            pname = seg.get("plate", "plate")
            if pname not in components:
                raise ValueError(f"segment references unknown component {pname!r}")
            plate_counts[pname] = plate_counts.get(pname, 0) + nt * ppt
            n_turns += nt
            n_plates += nt * ppt
            parts.append(f"{nt}x{ppt}({pname})")

        kname = cfg["kapton"]
        if kname not in components:
            raise ValueError(f"'kapton' references unknown component {kname!r}")
        n_kaptons = cfg.get("n_kaptons")
        n_kaptons = int(n_kaptons) if n_kaptons is not None else n_turns - 1

        groups = [Group(components[n], c) for n, c in plate_counts.items()]
        groups.append(Group(components[kname], n_kaptons))
        label = (
            f"[{' + '.join(parts)}] -> {n_turns} turns, "
            f"{n_plates} plates, {n_kaptons} kaptons"
        )
        return cls(groups, n_turns, n_plates, n_kaptons, label)


@dataclass(frozen=True)
class StackResult:
    """Summary statistics of the total stack height."""

    mean: float
    std: float
    lo: float
    hi: float
    coverage_k: float

    def __str__(self) -> str:
        return (
            f"H = {self.mean:.4f} +/- {self.coverage_k:g}*{self.std:.4f}"
            f"  ->  [{self.lo:.4f}, {self.hi:.4f}]"
        )


def analytic_rss(plan: StackingPlan, k: float = 3.0) -> StackResult:
    """Analytic (RSS) estimate: quadrature sum over component groups."""
    mean = sum(g.count * g.component.mu for g in plan.groups)
    var = sum(
        g.count * g.component.sigma**2 + (g.count * g.component.sigma_syst) ** 2
        for g in plan.groups
    )
    std = float(np.sqrt(var))
    return StackResult(mean, std, mean - k * std, mean + k * std, k)


def worst_case(plan: StackingPlan, k: float = 3.0) -> StackResult:
    """Worst-case bound: every piece at its hard tolerance limit."""
    mean = sum(g.count * g.component.mu for g in plan.groups)
    half = sum(
        g.count * (g.component.tolerance + k * g.component.sigma_syst)
        for g in plan.groups
    )
    return StackResult(mean, half / k, mean - half, mean + half, k)


def _sample_group(
    g: Group, n_samples: int, rng: np.random.Generator
) -> np.ndarray:
    """Sample the total width of one component group, shape (n_samples,)."""
    c = g.component
    size = (n_samples, g.count)
    if c.distribution == "normal":
        widths = rng.normal(c.mu, c.sigma, size=size)
    elif c.distribution == "uniform":
        half = np.sqrt(3.0) * c.sigma
        widths = rng.uniform(c.mu - half, c.mu + half, size=size)
    elif c.distribution == "triangular":
        half = np.sqrt(6.0) * c.sigma
        widths = rng.triangular(c.mu - half, c.mu, c.mu + half, size=size)
    else:  # pragma: no cover - validated at load time
        raise ValueError(f"unknown distribution: {c.distribution!r}")
    if c.sigma_syst > 0.0:
        widths += rng.normal(0.0, c.sigma_syst, size=(n_samples, 1))
    return widths.sum(axis=1)


def monte_carlo(
    plan: StackingPlan,
    n_samples: int = 100_000,
    k: float = 3.0,
    rng: np.random.Generator | None = None,
) -> tuple[StackResult, np.ndarray]:
    """Monte Carlo simulation of the total stack height.

    Each component group is sampled from its declared distribution;
    batch biases are drawn once per simulated stack. The reported
    interval uses empirical quantiles with the same coverage
    probability as +/- k sigma.
    """
    if rng is None:
        rng = np.random.default_rng()
    heights = np.zeros(n_samples)
    for g in plan.groups:
        heights += _sample_group(g, n_samples, rng)

    from scipy.stats import norm

    p = norm.cdf(k) - norm.cdf(-k)
    lo, hi = np.quantile(heights, [(1 - p) / 2, (1 + p) / 2])
    return (
        StackResult(
            float(heights.mean()), float(heights.std(ddof=1)),
            float(lo), float(hi), k,
        ),
        heights,
    )


def budget_table(plan: StackingPlan) -> str:
    """Variance budget: contribution of each component group to sigma_H^2."""
    rows: list[tuple[str, float]] = []
    for g in plan.groups:
        rows.append((f"{g.component.name} x{g.count} (random)",
                     g.count * g.component.sigma**2))
        if g.component.sigma_syst > 0.0:
            rows.append((f"{g.component.name} x{g.count} (batch)",
                         (g.count * g.component.sigma_syst) ** 2))
    total = sum(v for _, v in rows)
    lines = ["  variance budget:"]
    for name, v in rows:
        lines.append(
            f"    {name:<28} {v:10.6f}  ({v / total:6.1%})"
            f"   -> sigma contrib {np.sqrt(v):.4f}"
        )
    lines.append(
        f"    {'total':<28} {total:10.6f}   -> sigma_H = {np.sqrt(total):.4f}"
    )
    return "\n".join(lines)


def plot_results(
    plan: StackingPlan, heights: np.ndarray, rss: StackResult, path: str
) -> None:
    """Plot the Monte Carlo histogram against the analytic Gaussian."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.stats import norm

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(heights, bins=120, density=True, alpha=0.55,
            color="steelblue", label="Monte Carlo")
    x = np.linspace(heights.min(), heights.max(), 400)
    ax.plot(x, norm.pdf(x, rss.mean, rss.std), "k-", lw=2,
            label=rf"Analytic ($\sigma_H$={rss.std:.3f})")
    ax.axvline(rss.lo, color="k", ls="--", lw=1)
    ax.axvline(rss.hi, color="k", ls="--", lw=1,
               label=rf"$\pm{rss.coverage_k:g}\sigma$")
    ax.set_xlabel("total stack height")
    ax.set_ylabel("probability density")
    ax.set_title(plan.label, fontsize=10)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    logger.info("plot saved to %s", path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Tolerance stacking for a stacking plan defined in JSON."
    )
    parser.add_argument("--config", metavar="JSON", default=None,
                        help="stacking plan configuration file")
    parser.add_argument("--write-example", metavar="JSON", default=None,
                        help="write an example configuration file and exit")
    parser.add_argument("--samples", type=int, default=100_000,
                        help="number of Monte Carlo samples")
    parser.add_argument("--coverage", type=float, default=3.0,
                        help="coverage factor k for reported intervals")
    parser.add_argument("--plot", metavar="PNG", default=None,
                        help="save a histogram plot to this file")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for reproducibility")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: evaluate the stacking plan tolerance budget."""
    logging.basicConfig(
        stream=sys.stderr, level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    if args.write_example:
        with open(args.write_example, "w", encoding="utf-8") as f:
            json.dump(EXAMPLE_CONFIG, f, indent=2)
            f.write("\n")
        logger.info("example configuration written to %s", args.write_example)
        return 0

    if args.config is None:
        logger.warning("no --config given, using built-in example plan")
        cfg = EXAMPLE_CONFIG
    else:
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)

    plan = StackingPlan.from_config(cfg)
    k = args.coverage
    rng = np.random.default_rng(args.seed)

    rss = analytic_rss(plan, k)
    wc = worst_case(plan, k)
    mc, heights = monte_carlo(plan, args.samples, k, rng)

    print(f"plan: {plan.label}")
    for g in plan.groups:
        c = g.component
        print(f"  {c.name:<12} x{g.count:<4} mu={c.mu}, sigma={c.sigma:.5f}, "
              f"tol=+/-{c.tolerance:.5f}, dist={c.distribution}"
              + (f", sigma_syst={c.sigma_syst}" if c.sigma_syst else ""))
    print(f"  worst case   : {wc}")
    print(f"  analytic RSS : {rss}")
    print(f"  Monte Carlo  : {mc}   ({args.samples} samples)")
    print(f"  relative dispersion: sigma_H/H = {rss.std / rss.mean:.4%}")
    print(budget_table(plan))

    if args.plot:
        plot_results(plan, heights, rss, args.plot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
