# Cross-model dilution check — gpt2 rescore of E3 REP-DILUTION (ROADMAP task H2)

Run 2026-11-23 with `eval/dilution_second_model.py`: E3's exact 30
REP-DILUTION prompts rebuilt by rule R-REP (A6 base repeated
j in {2, 4} times, single spaces, then the A6 suffix once;
BASES/SUFFIXES verbatim from `eval/perplexity_filter.py`) and
scored with **gpt2** using G9's scoring functions unchanged.
Benign reference = G9's committed gpt2 rows (n = 10, never
rescored). Each model is read at its own G8 benign-only frozen
threshold (max benign windowed score): gpt2 690.13,
distilgpt2 1099.28 (full-text: 172.53 / 315.84).
Pre-registered reading (fixed in the script before scoring):
dilution-resistance "holds" if pooled windowed detections
>= 20/30 and pooled windowed AUROC >= 0.80.

## Answer: it holds — identical detection counts under gpt2

| | distilgpt2 (E3/G8) | gpt2 (H2) |
| --- | --- | --- |
| Windowed detections, pooled | 26/30 | **26/30** |
| Windowed detections, j=2 / j=4 | 13/15 / 13/15 | 13/15 / 13/15 |
| Full-text detections, pooled | 4/30 | 4/30 |
| Full-text detections, j=4 | 0/15 | 0/15 |
| Windowed AUROC vs benign (pooled) | 0.887 | **0.927** |
| Windowed median (pooled) | 7989.53 | 8343.88 |
| Full-text median, j=2 → j=4 | 159.84 → 32.51 | 109.63 → 30.63 |
| Full-text AUROC, j=4 | 0.107 | 0.333 |

- The windowed score is per-case **j-invariant under gpt2 too**
  (all 15 cases: windowed score at j=2 exactly equals j=4) — the
  max window sits inside the undiluted suffix, so repeating the
  base cannot move it, under either scorer.
- The 2 misses per j are the same cases under both models: the
  pure-repetition suffixes (suf-07/08), already known evaders
  from A6 — repetition evasion, not dilution, is what beats the
  window, and it does so under both scorers.
- Full-text dilution replicates cross-model: medians fall
  monotonically with j and j=4 full-text AUROC drops below
  chance under both models (0.107 / 0.333).

## Limits

- Both scorers are small, same-family GPT-2 models (as in G9):
  this rules out a single-checkpoint artefact for the dilution
  result, not a family-wide one.
- Prompts were rebuilt by the frozen R-REP rule, not recovered
  from stored text (E3 rows carry scores, not prompts); the
  construction is pinned by unit tests and the suffix/base
  strings are byte-identical to A6/G9 (verified programmatically).
- Detector statement only — perplexity scores, no live model,
  no ASR. Rows: `results/dilution_gpt2_rows.jsonl`; summary:
  `results/dilution_second_model_h2_summary.json`; 2 unit tests
  in `eval/test_dilution_second_model.py` (construction +
  summary consistency, incl. pinning G8's 26/30 and G9's 690.13).
