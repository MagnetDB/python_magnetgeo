# Tolerance stacking for magnet stacking plans

`stacking_plan.py` estimates the total axial height of a stack of plates and
kapton insulation sheets, given a *stacking plan* and the width tolerances of
each component. It compares three estimates — worst case, analytic (RSS) and
Monte Carlo — and reports a variance budget showing which component drives the
uncertainty.

## Theory

### The problem

A stack is built from $N$ pieces (plates and kapton sheets) whose individual
widths $w_i$ are not exactly known: each piece has a nominal width $\mu_i$ and
a manufacturing dispersion described either by a standard deviation
$\sigma_i$ or by a tolerance band $\mu_i \pm \Delta_i$. The total height is
simply

$$H = \sum_{i=1}^{N} w_i$$

and the question is how the individual dispersions combine into a dispersion
on $H$.

### Worst case (linear stacking)

The pessimistic answer assumes every piece sits at its tolerance limit, all in
the same direction:

$$H \in \Big[\sum_i (\mu_i - \Delta_i),\ \sum_i (\mu_i + \Delta_i)\Big]$$

The spread grows *linearly* with the number of pieces. For a stack of several
hundred plates this bound is extremely conservative: the probability that 728
independent plates are all simultaneously at the same tolerance extreme is
essentially zero. Use it only when the stack must fit a hard mechanical
envelope with absolute certainty. The trade-off between worst-case and
statistical stacking is the founding subject of tolerance analysis
[Fortini 1967; Greenwood & Chase 1987].

### Statistical stacking (RSS, root-sum-square)

If the widths are independent random variables, variances — not standard
deviations — add:

$$\mathbb{E}[H] = \sum_i \mu_i, \qquad
  \sigma_H^2 = \sum_i \sigma_i^2$$

For a group of $N$ identical pieces with common $(\mu, \sigma)$ this gives the
familiar square-root law

$$\sigma_H = \sigma\sqrt{N}$$

so the *relative* dispersion of the stack shrinks as
$\sigma_H / (N\mu) = \sigma / (\mu\sqrt{N})$: a stack of 728 plates each known
to 2.5 % is known to about 0.09 %.

By the **central limit theorem**, $H$ is very nearly Gaussian as soon as a few
tens of pieces are stacked, *whatever* the distribution of the individual
widths (normal, uniform, ...). One can therefore quote confidence intervals

$$H = \mathbb{E}[H] \pm k\,\sigma_H$$

with $k = 1, 2, 3$ covering approximately 68 %, 95 % and 99.7 % of stacks.
Engineering practice usually quotes $k = 3$ (RSS or "statistical
tolerancing") [Evans 1974; Greenwood & Chase 1987]. The quadrature law is
the linear case of the general propagation of uncertainty used throughout
experimental physics [Taylor 1997, ch. 3; JCGM 2008, §5.1], and the Gaussian
limit is the central limit theorem [Feller 1968, ch. X].

### Converting a tolerance band into a standard deviation

Drawings usually specify a tolerance half-width $\Delta$ ($\mu \pm \Delta$)
rather than a $\sigma$. The conversion depends on the assumed distribution of
pieces inside the band:

| distribution | assumption | conversion |
|---|---|---|
| `normal` | $\Delta$ is a $k\sigma$ limit (default $k=3$) | $\sigma = \Delta / k$ |
| `uniform` | any value in the band equally likely | $\sigma = \Delta / \sqrt{3}$ |
| `triangular` | values pile up at nominal, vanish at limits | $\sigma = \Delta / \sqrt{6}$ |

The uniform assumption is the conservative choice when nothing is known about
the process; the normal assumption suits a controlled machining process whose
capability is matched to the tolerance. The $\Delta/\sqrt{3}$ (rectangular)
and $\Delta/\sqrt{6}$ (triangular) conversions are the standard "type B"
evaluations of measurement uncertainty [JCGM 2008, §4.3.7 and §4.3.9].

### Correlated errors: batch bias

The $\sqrt{N}$ law requires *independent* widths. If all plates come from the
same rolling batch or machining setup, they may share a common systematic
offset $b \sim \mathcal{N}(0, \sigma_{\text{syst}}^2)$. The mixed model

$$w_i = \mu + b + e_i, \qquad e_i \sim \mathcal{N}(0, \sigma^2)$$

gives

$$\sigma_H^2 = N\sigma^2 + (N\sigma_{\text{syst}})^2$$

The systematic term scales as $N^2$, so even a small batch bias dominates a
long stack: with $N = 728$, a batch bias of only
$\sigma_{\text{syst}} = 0.01$ mm contributes
$728 \times 0.01 = 7.3$ mm to $\sigma_H$, versus
$0.05\sqrt{728} \approx 1.35$ mm from a per-plate scatter five times larger.
For long stacks, batch-to-batch reproducibility matters far more than
individual plate scatter. This is what the `sigma_syst` field models. Such
mean shifts and drifts of the process distribution are the classic failure
mode of naive RSS tolerancing [Evans 1975b; Greenwood & Chase 1987].

### Monte Carlo

The script also simulates the stack directly: each component group is sampled
from its declared distribution (plus one batch offset per simulated stack),
and the reported interval comes from empirical quantiles. This is an
independent cross-check of the analytic formulas and remains valid for
non-Gaussian inputs, small counts, or correlated cases. Monte Carlo is one
of the four canonical methods of statistical tolerancing, alongside linear
(stack) propagation, non-linear propagation and quadrature [Evans 1975a;
Chase & Parkinson 1991].

## The stacking plan

The plan is an ordered list of segments, each made of `n_turns` turns of
`plates_per_turn` plates. The axial height of a turn is the **sum** of its
plate widths, and one kapton sheet is inserted between each pair of
consecutive turns (`n_kaptons = total_turns - 1`, overridable).

The default plan is

| segment | turns | plates/turn | plates |
|---|---|---|---|
| end (bottom) | 6 | 8 | 48 |
| body | 158 | 4 | 632 |
| end (top) | 6 | 8 | 48 |
| **total** | **170** | | **728** (+ 169 kaptons) |

## Installation

Requires Python ≥ 3.10 with `numpy`, `scipy` and (for `--plot`)
`matplotlib`:

```bash
pip install numpy scipy matplotlib
```

## Usage

Generate a starter configuration, edit it, then run:

```bash
python stacking_plan.py --write-example plan.json
python stacking_plan.py --config plan.json --plot stack.png
```

Options:

```text
--config JSON       stacking plan configuration file
--write-example F   write an example configuration to F and exit
--samples N         Monte Carlo sample count (default 100000)
--coverage K        coverage factor k for reported intervals (default 3)
--plot PNG          save a histogram of simulated heights
--seed N            random seed for reproducibility
```

Diagnostics go to stderr (`logging`), results to stdout.

## Configuration file

```json
{
  "components": {
    "plate":  {"mu": 2.0,   "tolerance": 0.15, "distribution": "normal"},
    "kapton": {"mu": 0.125, "tolerance": 0.02, "distribution": "uniform"}
  },
  "segments": [
    {"n_turns": 6,   "plates_per_turn": 8},
    {"n_turns": 158, "plates_per_turn": 4},
    {"n_turns": 6,   "plates_per_turn": 8}
  ],
  "kapton": "kapton",
  "n_kaptons": null
}
```

### `components`

A catalogue of component types. Each entry accepts:

| field | type | meaning |
|---|---|---|
| `mu` | float, required | nominal (mean) width |
| `sigma` | float | standard deviation of the random part |
| `tolerance` | float | tolerance half-width $\Delta$ (alternative to `sigma`) |
| `distribution` | string | `normal` (default), `uniform` or `triangular` |
| `tolerance_k` | float | $k$ in $\sigma = \Delta/k$ for `normal` (default 3) |
| `sigma_syst` | float | systematic (batch) standard deviation, default 0 |

Exactly one of `sigma` / `tolerance` is needed; the other is derived using the
table in the theory section. The `tolerance` value is also used as the hard
limit in the worst-case bound.

### `segments`, `kapton`, `n_kaptons`

Each segment needs `n_turns` and `plates_per_turn`; an optional `"plate"`
field names the component to use (default: the component called `plate`, so
with a single plate type the field can be omitted). `kapton` names the
insulation component, and `n_kaptons` overrides the default count of
`total_turns - 1` (e.g. if the ends are also insulated).

## Example output

```text
plan: [6x8(plate) + 158x4(plate) + 6x8(plate)] -> 170 turns, 728 plates, 169 kaptons
  plate        x728  mu=2.0, sigma=0.05000, tol=+/-0.15000, dist=normal
  kapton       x169  mu=0.125, sigma=0.01155, tol=+/-0.02000, dist=uniform
  worst case   : H = 1477.1250 +/- 3*37.5267  ->  [1364.5450, 1589.7050]
  analytic RSS : H = 1477.1250 +/- 3*1.3574  ->  [1473.0528, 1481.1972]
  Monte Carlo  : H = 1477.1300 +/- 3*1.3570  ->  [1473.1172, 1481.1315]   (100000 samples)
  relative dispersion: sigma_H/H = 0.0919%
  variance budget:
    plate x728 (random)            1.820000  ( 98.8%)   -> sigma contrib 1.3491
    kapton x169 (random)           0.022533  (  1.2%)   -> sigma contrib 0.1501
    total                          1.842533   -> sigma_H = 1.3574
```

Reading the result: the nominal height is 1477.1 mm; at 99.7 % confidence the
real stack lies within ±4.1 mm of nominal, while the worst-case envelope is
±112.6 mm — a factor 27 more pessimistic. The variance budget shows the plates
account for 98.8 % of the uncertainty, so tightening the kapton tolerance
would gain essentially nothing.

## Limitations and possible extensions

The model assumes widths are independent within a component group except for
the optional common batch offset; intermediate correlation structures (e.g.
per-sub-batch biases) would need an extra grouping level. It also ignores any
compression of the kapton under axial preload — if the stack is clamped, the
effective kapton width under load is the quantity to put in the config. If
measured width distributions are available, the Gaussian/uniform sampling in
`monte_carlo` can be replaced by a bootstrap (`rng.choice` over the measured
values) to drop the distributional assumption entirely.

## References

Textbooks:

- Fortini, E. T. (1967). *Dimensioning for Interchangeable Manufacture*.
  Industrial Press, New York. — The classic textbook on dimensional
  tolerancing of assemblies, including statistical (equal-likelihood)
  treatment of dimension chains.
- Feller, W. (1968). *An Introduction to Probability Theory and Its
  Applications*, Vol. 1, 3rd ed. Wiley, New York. — Chapter X for the
  central limit theorem underlying the Gaussian approximation of the stack
  height.
- Taylor, J. R. (1997). *An Introduction to Error Analysis: The Study of
  Uncertainties in Physical Measurements*, 2nd ed. University Science
  Books, Sausalito. — Quadrature addition of independent uncertainties
  (chapter 3); the physicist's view of the same mathematics.

Peer-reviewed articles:

- Evans, D. H. (1974). Statistical tolerancing: The state of the art.
  Part I: Background. *Journal of Quality Technology*, 6(4), 188–195.
  doi:10.1080/00224065.1974.11980646
- Evans, D. H. (1975a). Statistical tolerancing: The state of the art.
  Part II: Methods for estimating moments. *Journal of Quality
  Technology*, 7(1), 1–12. doi:10.1080/00224065.1975.11980657 —
  Reviews the four canonical methods: linear (stack) propagation,
  non-linear propagation, quadrature, and Monte Carlo.
- Evans, D. H. (1975b). Statistical tolerancing: The state of the art.
  Part III: Shifts and drifts. *Journal of Quality Technology*, 7(2),
  72–76. doi:10.1080/00224065.1975.11980672 — Treats exactly the
  systematic-offset problem modelled here by `sigma_syst`.
- Greenwood, W. H., & Chase, K. W. (1987). A new tolerance analysis
  method for designers and manufacturers. *ASME Journal of Engineering
  for Industry*, 109(2), 112–116. doi:10.1115/1.3187099 — Compares
  worst-case and RSS stacking and proposes a correction for biased
  (mean-shifted) component distributions.
- Chase, K. W., & Parkinson, A. R. (1991). A survey of research in the
  application of tolerance analysis to the design of mechanical
  assemblies. *Research in Engineering Design*, 3(1), 23–37.
  doi:10.1007/BF01580066 — Survey of the field, entry point to the
  wider literature.

Standard (supplementary, freely available):

- JCGM (2008). *Evaluation of measurement data — Guide to the expression
  of uncertainty in measurement* (GUM), JCGM 100:2008. BIPM.
  Available at <https://www.bipm.org/en/committees/jc/jcgm/publications>.
  — Not a textbook or journal article, but the authoritative metrology
  reference for quadrature propagation (§5.1) and the rectangular /
  triangular type-B conversions (§4.3.7, §4.3.9).
