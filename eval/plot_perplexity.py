#!/usr/bin/env python3
"""Reproduced figure: perplexity distribution, benign vs attack (ROADMAP C4).

Plots the committed A6 per-case scores (`results/perplexity_rows.jsonl`,
distilgpt2, run 2026-10-20 by `eval/perplexity_filter.py`) -- no model is
re-run and no number is re-measured. Before plotting, the script recomputes
the group medians and AUROCs from the rows and checks them against the
values published in `results/perplexity_filter.md`; it refuses to draw the
figure if the recomputation disagrees, so the figure can never silently
drift from the A6 report.

Figure (two panels, log x-axis throughout -- perplexity spans 4.1 to
109,603.3 in these rows, so a linear axis would hide the benign cluster):
  A. Full-text perplexity: overlapping histograms (log-spaced bins) for
     benign (n=10), natural_injection (n=25) and suffix_attack (n=15),
     with per-group median lines and the A6 threshold of 200 marked.
     The two pure-repetition suffixes suf-07 (4.09) and suf-08 (6.83) are
     annotated: they sit BELOW every benign case, the filter's known
     blind spot.
  B. Windowed perplexity (max over 10-token windows): one jittered dot
     per case, grouped, with median ticks. Windowing lifts suffix scores
     far above benign (median 7,989.5 vs 609.1) except for the same two
     repetition cases (434.7 / 558.9, at or below the benign median).

Outputs: figures/perplexity_dist.png and figures/perplexity_dist.svg
(the SVG is the same figure in vector form).
Run:  python eval/plot_perplexity.py
Requires: matplotlib (plus the stdlib).
"""
import json
import math
import random
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ROWS = ROOT / "results" / "perplexity_rows.jsonl"
FIGDIR = ROOT / "figures"

GROUPS = ["benign", "natural_injection", "suffix_attack"]
LABELS = {
    "benign": "Benign (n=10)",
    "natural_injection": "Natural injection (n=25)",
    "suffix_attack": "Synthetic suffix attack (n=15)",
}
COLORS = {
    "benign": "#2e7d32",
    "natural_injection": "#1565c0",
    "suffix_attack": "#c62828",
}

# Values published in results/perplexity_filter.md (A6, 2026-10-20).
PUBLISHED = {
    "median_full": {"benign": 73.2, "natural_injection": 129.8, "suffix_attack": 370.5},
    "median_windowed": {"benign": 609.1, "natural_injection": 1271.9, "suffix_attack": 7989.5},
    "auroc_full": {"natural_injection": 0.712, "suffix_attack": 0.780},
    "auroc_windowed": {"natural_injection": 0.788, "suffix_attack": 0.887},
}


def load_rows(path=ROWS):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def auroc(pos, neg):
    """AUROC via Mann-Whitney U (ties count 0.5) -- same code as A6."""
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def group_values(rows, group, key):
    return [r[key] for r in rows if r["group"] == group]


def check_against_published(rows):
    """Return a list of mismatch strings; empty means the rows reproduce A6."""
    problems = []
    for key, pub_key in (("perplexity", "median_full"), ("windowed_perplexity", "median_windowed")):
        for g in GROUPS:
            got = median(group_values(rows, g, key))
            want = PUBLISHED[pub_key][g]
            if abs(got - want) > 0.15:
                problems.append(f"{pub_key}[{g}]: recomputed {got:.1f} != published {want}")
    for key, pub_key in (("perplexity", "auroc_full"), ("windowed_perplexity", "auroc_windowed")):
        benign = group_values(rows, "benign", key)
        for g in ("natural_injection", "suffix_attack"):
            got = auroc(group_values(rows, g, key), benign)
            want = PUBLISHED[pub_key][g]
            if abs(got - want) > 0.0015:
                problems.append(f"{pub_key}[{g}]: recomputed {got:.3f} != published {want:.3f}")
    return problems


def build_figure(rows):
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(11, 4.2))

    # --- Panel A: full-text perplexity histograms -------------------------
    bins = [3 * (1.45 ** i) for i in range(20)]  # log-spaced, covers 4.1..3800+
    for g in GROUPS:
        vals = group_values(rows, g, "perplexity")
        ax_a.hist(vals, bins=bins, alpha=0.55, color=COLORS[g], label=LABELS[g],
                  edgecolor="white", linewidth=0.4)
        ax_a.axvline(median(vals), color=COLORS[g], linewidth=1.6)
    ax_a.axvline(200, color="black", linestyle="--", linewidth=1.0)
    ax_a.set_ylim(0, 7.2)
    ax_a.text(212, 6.7, "A6 threshold = 200", fontsize=8)
    ax_a.annotate("suf-07 / suf-08 (repetition,\nPPL 4.1 / 6.8) — below all benign",
                  xy=(6.5, 1.05), xytext=(4.0, 2.7), fontsize=8,
                  arrowprops=dict(arrowstyle="->", lw=0.8))
    ax_a.set_xscale("log")
    ax_a.set_xlabel("Full-text perplexity (distilgpt2, log scale)")
    ax_a.set_ylabel("Cases")
    ax_a.set_title("A. Full-text perplexity by group")
    ax_a.legend(fontsize=8, loc="upper left")

    # --- Panel B: windowed perplexity strip plot --------------------------
    rng = random.Random(42)  # fixed jitter: figure is byte-stable in layout
    for i, g in enumerate(GROUPS):
        vals = group_values(rows, g, "windowed_perplexity")
        ys = [i + rng.uniform(-0.16, 0.16) for _ in vals]
        ax_b.scatter(vals, ys, s=28, color=COLORS[g], alpha=0.75,
                     edgecolor="white", linewidth=0.4, label=LABELS[g])
        ax_b.plot([median(vals)] * 2, [i - 0.28, i + 0.28], color=COLORS[g], linewidth=2.4)
    ax_b.set_xscale("log")
    ax_b.set_yticks(range(len(GROUPS)))
    ax_b.set_yticklabels(["Benign", "Natural\ninjection", "Suffix\nattack"], fontsize=9)
    ax_b.set_xlabel("Windowed perplexity (max over 10-token windows, log scale)")
    ax_b.set_title("B. Windowed perplexity per case (bar = median)")
    ax_b.annotate("suf-07 / suf-08 stay at/below\nthe benign median even windowed",
                  xy=(490, 2.05), xytext=(900, 1.35), fontsize=8,
                  arrowprops=dict(arrowstyle="->", lw=0.8))

    fig.suptitle("Perplexity filter (A6 data, distilgpt2): benign vs attack — "
                 "separation is real but partial", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def main():
    rows = load_rows()
    problems = check_against_published(rows)
    if problems:
        for p in problems:
            print(f"MISMATCH: {p}", file=sys.stderr)
        return 1
    print("Validation: recomputed medians + AUROCs match results/perplexity_filter.md")
    for key in ("perplexity", "windowed_perplexity"):
        for g in GROUPS:
            vals = group_values(rows, g, key)
            print(f"  {key:20s} {g:18s} n={len(vals):2d} median={median(vals):9.1f} "
                  f"min={min(vals):9.2f} max={max(vals):10.2f}")
    fig = build_figure(rows)
    FIGDIR.mkdir(exist_ok=True)
    for name, kwargs in (("perplexity_dist.png", {"dpi": 200}),
                         ("perplexity_dist.svg", {})):
        out = FIGDIR / name
        fig.savefig(out, **kwargs)
        print(f"Wrote {out.relative_to(ROOT)} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
