# Flagship blocked-corpus variant, part 1 — G1 results

**Date:** 2026-11-17. **Task:** G1, the E4 blocked-corpus variant's
first measurement. **Script:** `eval/flagship_variant_g1.py`
(5 helper unit tests pass); rows:
`results/flagship_variant_g1_rows.jsonl` (25 new scorings);
machine-readable analysis: `results/flagship_variant_g1_summary.json`.

## What this is — and is not

The flagship's primary arms (E2/E3 predictions P1–P3) remain
**BLOCKED**: AmpleGCG publishes no static suffix corpus. G1 does
not substitute for them and makes no AmpleGCG claim. It asks the
roadmap's narrower question with the generators this lab actually
has: *does the windowed AUROC on generator-distribution gibberish
match A6's 0.887 hand-written figure?* Two arms:

- **GEN-SAMPLE (new):** 25 suffixes sampled from distilgpt2 itself
  (temperature 1.0, top-k 50, 20 new tokens, seed 20261117), each
  attached to one of A6's 5 rotating base requests, scored with
  the frozen A6/E3 pipeline (distilgpt2; full-text + 10-token
  windowed perplexity). Benign reference: A6's committed rows,
  reused, never rescored.
- **D5-POOL (re-analysis, no rescoring):** D5's committed
  random-suffix pools (30 gibberish + 30 fluent word-salad), which
  carry full-text scores only, so this arm is full-text only.

## Results

| arm | score | n | median | AUROC vs benign [95% CI] |
|---|---|---|---|---|
| A6 hand-written suffixes (reference) | full-text | 15 | 370.5 | 0.780 |
| A6 hand-written suffixes (reference) | windowed | 15 | 7989.5 | 0.887 |
| GEN-SAMPLE (distilgpt2-sampled) | full-text | 25 | 106.3 | 0.496 [0.296, 0.712] |
| GEN-SAMPLE (distilgpt2-sampled) | windowed | 25 | 555.4 | **0.416 [0.248, 0.612]** |
| D5-POOL random gibberish | full-text | 30 | 686.1 | 0.987 [0.950, 1.000] |
| D5-POOL random fluent word-salad | full-text | 30 | 423.0 | 0.970 [0.893, 1.000] |

Benign reference (n = 10): full-text median 73.2, windowed median
609.1. The GEN-SAMPLE windowed median (555.4) sits *below* the
benign windowed median — sampled suffixes look, to this scorer,
slightly more ordinary than ordinary text.

## Honest reading

- **The 0.887 does not transfer to a generator distribution —
  with a confound that must be stated in the same breath.** In
  GEN-SAMPLE the generator *is* the scorer: text sampled from
  distilgpt2 is in-distribution for distilgpt2 by construction,
  so low perplexity is close to guaranteed. This arm therefore
  does **not** estimate what would happen with AmpleGCG suffixes
  (a different, larger generator, scored by distilgpt2 — the
  cross-model case, which is exactly the blocked P1 test). What
  it does establish is the mechanism behind the
  generator-distribution worry, in its purest form: a perplexity
  detector's separation is a property of the *gap* between the
  suffix distribution and the scorer's own distribution, not of
  "gibberish" as a category. Hand a perplexity filter suffixes
  drawn from a model close to itself and the separation can fall
  below chance (0.416 < 0.5: the sampled arm is, if anything,
  anti-separated on the windowed score).
- **Randomness is not the same as generator distribution.**
  D5-POOL's uniformly random token salad separates *better* than
  A6's hand-written suffixes on the full-text score (0.987 vs
  0.780), and even random *fluent-word* salad reaches 0.970 —
  random ordering is itself unnatural text. So "machine-made"
  suffixes split into two opposite cases: uniform-random (trivially
  detected) and model-sampled (invisible to a same-family scorer).
  Any future claim of the form "generator suffixes evade / do not
  evade perplexity filters" is meaningless without naming the
  generator *and* its relation to the scorer. This sharpens, and
  was not obvious before, the E3 discussion point that papers
  should name the suffix distribution the way they name the model:
  they should also name the generator–scorer relationship.
- **Verdict language.** G1 was not pre-registered with bands in
  E2, so no supported/refuted verdict is claimed. Descriptively:
  the windowed AUROC on the generator-sampled arm (0.416) does
  not match the 0.887 hand-written figure, and its CI excludes
  even the E2 P1 *supported* band (≤ 0.79) — but applying those
  bands here would be a category error, because P1 is about the
  AmpleGCG distribution specifically. P1–P3 remain BLOCKED /
  UNANSWERED, unchanged.
- **Limitations.** Generator = scorer confound (above, deliberate
  and disclosed — it is the cheapest way to demonstrate the
  mechanism, not an estimate of the cross-model effect); sampled
  suffixes are not optimised against any target, unlike real
  amortised attacks; benign n = 10 (wide CIs by construction);
  D5-POOL is full-text only because D5 committed no windowed
  scores for its pools. The natural follow-on — a *different*
  small generator scored by distilgpt2 — is what G9's second-model
  work and a future variant part 2 should separate out.

## Sources

- Liao & Sun 2024, "AmpleGCG…", COLM 2024, arXiv:2404.07921 —
  https://arxiv.org/abs/2404.07921 (the blocked corpus; no
  AmpleGCG suffix was used or claimed here)
- Jain et al. 2023, "Baseline Defenses for Adversarial Attacks
  Against Aligned Language Models", arXiv:2309.00614 —
  https://arxiv.org/abs/2309.00614 (filter design, frozen in A6)
- Lab-internal: A6 `results/perplexity_filter.md` +
  `results/perplexity_rows.jsonl`; D5
  `results/redteam_blueteam_rows.jsonl`; E2
  `data/flagship_dataset_spec.md`; E3
  `results/flagship_baselines.md`; E4 `paper/outline.md` §7
  (blocked-corpus variant).
