# Evasiveness-aware refusal metric (3-way) — results (ROADMAP task F8)

- run at: 2026-11-21 (America/Chicago); code `eval/refusal_metric_v2.py` (stdlib-only 3-way softmax logistic regression on TF-IDF uni+bigram features, sparse full-batch gradient descent), tests `eval/test_refusal_metric_v2.py` (3 pass)
- data: `data/refusal_synthetic_v2_a.yaml` + `data/refusal_synthetic_v2_b.yaml` (committed in two parts under a connector size limit; the code generates the single-file form) — 900 SYNTHETIC examples, generated from hand-written templates in the code: D3's 10 refusal/compliance families regenerated exactly (600) + 5 new safe-completion families (300); the same 20-topic pool serves all three labels, so topic cannot carry the label. No real model outputs.
- question (from D3 + D4): D3's binary refusal/compliance label "structurally erases safe completions" — a response that refuses the harmful part and offers the safe part is neither. F8 adds the third label and quantifies what the binary metric does to those responses.

## Headline

| model / split | accuracy | per class |
| --- | --- | --- |
| 3-way, random split | 1.000 | refusal 60/60, compliance 60/60, safe 60/60 |
| 3-way, family-held-out | 0.708 | refusal 60/120, compliance 95/120, safe completion 100/120 |
| D3 binary baseline, forced onto safe completions (random test, n=60) | — | labels 48/60 **compliance**, 12/60 refusal |
| D3 keyword baseline, forced onto safe completions (n=60) | — | labels 40/60 compliance, 20/60 refusal |

D3 comparison points: binary LR was 1.000 random / 0.771 family-held-out; the 3-way model is 1.000 random / 0.708 held-out on a strictly harder task (6 held-out families instead of 4, three classes instead of two).

## Predictions (registered in the code before the first run)

- P1 (random ≥ 0.95): **supported** — 1.000, template leakage exactly as in D3; an upper bound, not a result.
- P2 (held-out materially below random): **supported** — 0.708 vs 1.000.
- P3 (binary forces ≥80% of safe completions into "refusal"): **FAILED — the erasure runs the other way.** The binary LR labels 80% of safe completions (48/60) as **compliance**, because safe-completion phrasing is built from offering language ("I can help with…", "here is a safer alternative"). A binary metric therefore does not just erase safe completions, it systematically counts partial refusals as full compliance — which, in an attack-success evaluation, inflates measured compliance and hides exactly the harmless-but-non-evasive behaviour D4 (Constitutional AI) identified as the goal. The keyword baseline erases in the same direction (40/60 compliance).
- P4 (safe completion is the weakest held-out class): **FAILED** — held-out, safe completion is the *strongest* class (100/120); **refusal** is weakest (60/120), because the held-out refusal families (plain/terse) share almost no vocabulary with the trained refusal families, while safe-completion templates retain distinctive markers ("safer alternative", "general principles", "high-level overview") even in held-out families.

## What this means for the lab's metrics

1. Any future lab refusal/ASR number reported on a binary label should be read as an upper bound on compliance: safe completions are swept into it. The 3-way label is now the lab standard for refusal measurement (alongside F4's reporting triple).
2. The metric is only as good as its weakest class under family shift: terse/plain refusals — the ones with the least phrasing — are the hardest to recognise, the same recognition-ceiling pattern as the input-side detectors (C3).

## Limits

- Synthetic template data only; the held-out split tests phrasing generalisation across *my* template families, not across real models.
- Safe-completion families were written by the same author as the classifier's feature design (as in D3) — treat all numbers as a lab baseline.
- Implementation note: the first version used dense vectors and was too slow in pure Python; the shipped code uses sparse feature dicts with identical maths (verified by the same test suite + a 15-second full run).
