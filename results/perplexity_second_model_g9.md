# Second-model perplexity check — gpt2 vs distilgpt2 (ROADMAP task G9)

Run 2026-11-22 with `eval/perplexity_second_model.py`: A6's scoring
repeated **exactly** — same 50 texts (10 benign, 25 natural injections,
15 synthetic gibberish-suffix cases, suffix strings copied verbatim
from `eval/perplexity_filter.py`), same full-text and 10-token
windowed perplexity functions — with a second small model, **gpt2**,
in place of distilgpt2. Question: is A6's headline windowed AUROC
0.887 (suffix vs benign) a distilgpt2 artefact?

## Answer: no — the second model separates slightly *better*

| metric | distilgpt2 (A6) | gpt2 (G9) |
| --- | --- | --- |
| AUROC suffix, windowed | 0.887 | **0.927** |
| AUROC suffix, full-text | 0.780 | 0.820 |
| AUROC natural, windowed | 0.788 | 0.824 |
| AUROC natural, full-text | 0.712 | 0.804 |
| Median full-text PPL, benign / suffix | 73.2 / 370.5 | 41.3 / 268.0 |

Per-case rankings are near-identical across models (Spearman
ρ = 0.972 windowed, 0.965 full-text, n = 50): the two models mostly
agree about *which* texts look anomalous; gpt2's absolute scale is
lower on benign text, which widens the separation.

## Frozen-threshold transfer (G8 rule, per model)

Applying G8's benign-only rule (threshold = max benign windowed
score) separately per model gives **identical detection counts**:

| | threshold | suffix detected | natural detected |
| --- | --- | --- | --- |
| distilgpt2 | 1099.28 | 13/15 | 14/25 |
| gpt2 | 690.13 | 13/15 | 14/25 |

Threshold *values* do not transfer across models (690 vs 1099 —
perplexity scales are model-specific), but the benign-only
calibration *procedure* reproduces the same operating point.

## What does not change with the model

- The pure-repetition evaders (suf-07, suf-08) still evade: gpt2
  windowed scores 260.36 / 281.45, below gpt2's own benign maximum
  (690.13) — repetition evasion is a property of the score, not of
  distilgpt2.
- Natural injections still overlap benign text far more than
  suffixes do (best natural AUROC 0.824): perplexity remains a
  gibberish detector, not an injection detector, under both models.
- This does **not** touch G1's confound in reverse: G1's GEN-SAMPLE
  suffixes were *sampled from* distilgpt2, so their invisibility to
  distilgpt2 (windowed AUROC 0.416) is a generator = scorer effect.
  G9's suffixes are hand-written, generator-free text, and both
  models see them. A cross-model rescore of the GEN-SAMPLE pool is
  the clean follow-up (queued as H3).

## Provenance & limits

- Environment: torch 2.15.0+cpu, transformers 5.24.0, Python 3.12
  (pinned in `repro/requirements.txt`, G10). A first run's summary
  step crashed on a dict-comprehension bug *after* all 50 rows were
  written; the fixed script was re-run end-to-end and reproduced
  every per-case score exactly (perplexity scoring is deterministic
  here), so the committed rows and summary come from one clean run.
- Both models are small, old, same-family (GPT-2 architecture,
  same tokenizer family): agreement between them rules out a
  single-checkpoint artefact, not a family-wide one. A differently
  trained scorer (e.g. a modern small LM) remains untested.
- Rows: `results/perplexity_gpt2_rows.jsonl`; summary:
  `results/perplexity_second_model_g9_summary.json`; 3 unit tests in
  `eval/test_perplexity_second_model.py` pin the headline AUROCs and
  the identical frozen-threshold counts.
