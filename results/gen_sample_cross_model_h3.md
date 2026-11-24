# G1 confound control — H3 results

**Date:** 2026-11-24. **Task:** H3. **Script:**
`eval/gen_sample_cross_model.py` (3 unit tests pass); rows:
`results/gen_sample_gpt2_rows.jsonl` (25 rescorings);
summary: `results/gen_sample_cross_model_h3_summary.json`.

## Question

G1's GEN-SAMPLE arm scored windowed AUROC **0.416** — but its
suffixes were sampled from distilgpt2 and scored by distilgpt2, so
generator = scorer. Is 0.416 that confound, or a property of
model-sampled text? H3 rescores G1's exact 25 committed prompts
with **gpt2** (generator ≠ scorer). Benign reference: G9's
committed gpt2 rows (n=10). G1's distilgpt2 AUROCs were recomputed
from its committed rows first and match exactly (0.496 / 0.416) —
the check gate passed before any new scoring.

Reading fixed before scoring: gpt2 windowed AUROC ≥ 0.75 →
mainly generator=scorer artefact; ≤ 0.60 → property of
model-sampled text; between → partial.

## Results

| scorer | full AUROC [95% CI] | windowed AUROC [95% CI] | windowed median | windowed detections at own frozen threshold |
|---|---|---|---|---|
| distilgpt2 (G1) | 0.496 [0.296, 0.712] | 0.416 [0.248, 0.612] | 555.35 | 6/25 (thr 1099.28) |
| gpt2 (H3) | 0.620 [0.376, 0.836] | **0.624 [0.428, 0.800]** | 546.11 | 3/25 (thr 690.13) |

Per-case rank agreement between scorers: Spearman 0.801 windowed,
0.517 full-text. Benign medians under gpt2: full 41.33, windowed
299.62 (G9 rows).

## Honest reading

- **Verdict: PARTIAL, per the pre-registered bands.** Cross-model
  scoring recovers real separation (windowed 0.416 → 0.624) — so
  part of G1's collapse *was* the generator=scorer identity. But
  0.624 is far below A6's 0.887 hand-written figure and below the
  0.75 artefact band: model-sampled suffixes remain hard to
  separate from benign text even for a scorer that did not
  generate them. Both halves of the explanation are true.
- **AUROC and threshold detections move in opposite directions**
  (0.416→0.624 up; 6/25→3/25 down). gpt2 ranks the sampled
  suffixes higher relative to its benign pool, but its own
  benign-only frozen threshold (max benign windowed, 690.13) sits
  lower relative to the suffix distribution than distilgpt2's
  (1099.28). Another instance of the G8/G9 lesson: the calibration
  *procedure* transfers, the threshold *value* and the detection
  count do not follow AUROC.
- **Limits.** gpt2 and distilgpt2 are same-family (distilled
  sibling), so this is a *near* cross-model test, not an
  independent-family one; sampled suffixes are still not optimised
  attacks; benign n=10 keeps CIs wide (gpt2 windowed CI spans
  0.428–0.800, so the partial band is where the evidence sits,
  not a precise point). P1–P3 (AmpleGCG) remain BLOCKED.

Sources: G1 `results/flagship_variant_g1.md` + rows; G9
`results/perplexity_gpt2_rows.jsonl`; Liao & Sun 2024,
arXiv:2404.07921 (blocked corpus, still unused); Jain et al. 2023,
arXiv:2309.00614.
