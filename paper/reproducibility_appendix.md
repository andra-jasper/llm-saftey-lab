# Reproducibility appendix (draft for the preprint — G10)

One command reproduces every headline number in the C3 leaderboard
(`results/leaderboard.md`) from the per-case rows committed in this
repository:

```
python3 eval/reproduce.py
```

- **What it does.** 41 checks recompute the published headlines from
  `results/*_rows.jsonl` only — A4 detector totals (17/25, 0/10 FP),
  A6 perplexity AUROCs (0.780 / 0.712 full-text, 0.887 / 0.788
  windowed) and medians, B1 level totals (0/12/17/18), B2 variant and
  probe totals, B5 document-channel 0/15, B6 variant and probe
  totals, B4 combined 13/15 with 0/15 benign blocked — plus the
  post-C3 flagship numbers: E3 REP-DILUTION full-text medians at
  repeat factors 2 and 4 (159.8, 32.5; the factor-1 baseline is the
  A6 suffix median 370.5, checked in the A6 block) and G8's frozen
  benign-only windowed threshold (1099.28) with its REP-DILUTION
  detections (26/30 windowed vs 4/30 full-text). Result on
  2026-11-22: **41/41 match**, exit code 0. The full table is
  regenerated at `results/reproducibility_g10.md` on every run.
- **Environment.** Recomputation is Python 3.12 stdlib only
  (`repro/requirements.txt`, tier 1). The model runs behind the
  committed rows (A6 distilgpt2, G9 gpt2) used the pinned tier-2
  versions in the same file, verified on the lab VM 2026-11-22.
- **What it does not do.** No model is re-run and no number is
  re-measured; perplexity scores are taken from their committed
  rows. Tasks after C3 (F6–F8, G1–G9) carry their own per-task
  recomputation checks and are not folded into this runner.
- **Known gaps.** sklearn is unavailable on the lab VM, so B4's
  TF-IDF layer is reproduced only through its committed rows, not
  re-derived; the AmpleGCG arms of E3 remain BLOCKED (no static
  corpus published), so no reproducibility claim covers them.
