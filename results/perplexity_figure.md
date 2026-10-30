# Reproduced figure: perplexity distribution, benign vs attack — C4

Figure: `figures/perplexity_dist.svg` (vector form, committed here) and
`figures/perplexity_dist.png` (identical render at 200 dpi, produced by the
same script — see the note at the bottom). Script:
`eval/plot_perplexity.py`; tests: `eval/test_plot_perplexity.py` (5 tests,
all passing, run 2026-10-30).

## What the figure is

A two-panel plot of the A6 per-case scores in
`results/perplexity_rows.jsonl` (distilgpt2, CPU, originally run
2026-10-20 by `eval/perplexity_filter.py`). **No model was re-run and no
number was re-measured for C4** — this task only renders the committed
data. Before drawing, the script recomputes every group median and AUROC
from the rows and refuses to plot if they disagree with
`results/perplexity_filter.md`. On 2026-10-30 the recomputation matched
exactly:

| score | benign (n=10) | natural_injection (n=25) | suffix_attack (n=15) |
|---|---|---|---|
| full-text median | 73.2 | 129.8 | 370.5 |
| windowed median | 609.1 | 1271.9 | 7,989.5 |
| AUROC vs benign, full-text | — | 0.712 | 0.780 |
| AUROC vs benign, windowed | — | 0.788 | 0.887 |

- **Panel A** — full-text perplexity: overlapping histograms on
  log-spaced bins (a log axis is necessary: scores span 4.1–3,800.2),
  per-group median lines, and the A6 threshold of 200 marked. At that
  threshold the A6 sweep caught 10/15 suffix cases with 1/10 benign
  false positives.
- **Panel B** — windowed perplexity (max over 10-token windows): one dot
  per case, bar = group median. Scores span 335.0–109,603.3.

## Honest reading (what the figure shows that the A6 table hid)

- The headline separation is a *median* story, not a clean split. In
  Panel A the three histograms overlap heavily in the 40–200 band where
  most cases of every group live; only the suffix group's right tail
  (5 cases above 1,000) is visually distinct.
- The repetition blind spot is the most striking feature: suf-07 (4.09)
  and suf-08 (6.83) form two isolated bars at the far LEFT of Panel A —
  the lowest perplexities in the entire dataset, below every benign
  case (benign min 44.09) — and in Panel B they remain the suffix
  group's two lowest dots (434.7 / 558.9), at or below the benign
  windowed median of 609.1. A perplexity threshold at any value flags
  them last, not first.
- Windowing helps the suffix group as a whole (Panel B: 13/15 suffix
  dots sit above the benign maximum of 1,099.28) but barely separates
  natural injection from benign — the blue dots interleave with the
  green across the whole axis, matching the modest windowed AUROC of
  0.788. The encoded-payload cases are the natural group's high tail,
  as A6 noted.
- Small-n caveat stands: 10/25/15 hand-built cases, synthetic suffixes
  (not GCG-optimized). The figure reproduces A6; it does not strengthen
  its evidence.

## Note on file formats

The roadmap names a PNG. The script writes both files from the same
figure object, so they are the same plot. This repo is updated through a
text-only push channel that cannot carry binary files, so the SVG is
the committed figure and the PNG (2200×840, 163,040 bytes on
2026-10-30) is regenerated locally by running
`python eval/plot_perplexity.py`.

## Sources

- Data: `results/perplexity_rows.jsonl` / `results/perplexity_filter.md`
  (A6, this repo).
- Jain et al. 2023, "Baseline Defenses for Adversarial Attacks Against
  Aligned Language Models", arXiv:2309.00614 —
  https://arxiv.org/abs/2309.00614
- Zou et al. 2023, "Universal and Transferable Adversarial Attacks on
  Aligned Language Models", arXiv:2307.15043 —
  https://arxiv.org/abs/2307.15043 (see `notes/gcg.md`)
