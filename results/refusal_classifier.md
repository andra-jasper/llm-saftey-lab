# D3 — Refusal-phrasing classifier (synthetic data)

Date: 2026-11-06 · Code: `eval/refusal_classifier.py` (stdlib only) ·
Data: `data/refusal_synthetic.yaml` · Rows: `results/refusal_classifier_rows.jsonl` ·
Tests: `eval/test_refusal_classifier.py` (5 pass)

## The data is synthetic — read this first

All 600 examples were **generated** from 10 hand-written template
families (3 templates each) crossed with one pool of 20 request topics:
300 refusal / 300 compliance. **No example is a real model output**, and
no number below is evidence about any real model or real refusal
behaviour. The experiment is about the *classifier and the evaluation
design*, not about refusals in the wild.

Two design choices do the real work:

1. **Same topic pool for both labels.** Refusals and compliances are
   generated over identical topics (benign and sensitive mixed), so topic
   words cannot carry the label — only phrasing can.
2. **Two splits.** A random split leaks templates between train and test;
   a family-held-out split does not. Reporting only the first would be
   the classic synthetic-data self-deception.

The model is a bag-of-words (unigrams + bigrams, TF-IDF, L2) logistic
regression trained by full-batch gradient descent, implemented in the
file — no sklearn. The baseline is a fixed keyword list ("can't",
"sorry", "unable", "policy", …).

## Predictions (registered in the code before the first full run)

- **P1** Random-split LR accuracy ≥ 0.95 (template leakage).
- **P2** Family-held-out LR accuracy materially below the random split.
- **P3** Keyword baseline false-positives on apologetic compliance and
  misses keyword-free terse refusals.

## Results (real run, 2026-11-06)

| Split | Model | Accuracy | Precision (refusal) | Recall (refusal) | F1 |
|---|---|---|---|---|---|
| Random stratified (n=150 test) | Logistic regression | **1.000** | 1.000 | 1.000 | 1.000 |
| Random stratified | Keyword baseline | 0.720 | 0.714 | 0.733 | 0.724 |
| Family-held-out (n=240 test) | Logistic regression | **0.771** | 0.741 | 0.833 | 0.784 |
| Family-held-out | Keyword baseline | **0.250** | 0.286 | 0.333 | 0.308 |
| Hand-written probes (n=12) | Logistic regression | 0.667 | 0.625 | 0.833 | 0.714 |
| Hand-written probes | Keyword baseline | 0.500 | 0.500 | 0.333 | 0.400 |

Family-held-out LR accuracy by family: `refusal_plain` 1.000,
`compliance_refusal_words` 0.750, `compliance_apologetic` 0.667,
`refusal_terse` 0.667.

Strongest LR refusal features (held-out model): *i, i'm, i can't, can't,
help with, not*; strongest compliance features: *let's, happy, happy to,
here*-family n-grams — the model leans on opener phrasing, as designed.

## Verdicts on the predictions

- **P1 — supported, and it is the warning, not the result.** A perfect
  1.000 on the random split means the test set contained the same
  templates as training. On synthetic data a random split measures
  memorisation; anyone reporting only this number would be claiming a
  solved problem that does not exist.
- **P2 — supported.** Held-out accuracy drops 1.000 → 0.771. The model
  does generalise somewhat to unseen phrasing families (it beats the
  keyword rule by 52 points there), mostly via first-person negation
  features, but a quarter of unseen-family examples are still wrong.
- **P3 — supported, dramatically.** On held-out families the keyword
  baseline falls to **0.250 — worse than chance** — because the split is
  adversarial to it by construction: the held-out compliance families
  are loaded with "sorry" / "can't" and the held-out refusal families
  are keyword-free. That is the point: a keyword rule's accuracy is a
  property of the phrasing distribution, not of refusal itself.

## Probes and the ambiguous middle

On 12 hand-written sentences in none of the templates, LR scores 0.667
(errors include "Why not? Here's a complete walkthrough." → refusal,
and "I can't wait to help" → refusal — enthusiasm with "can't" in it)
and the keyword rule scores 0.500. Four safe-completion / partial-
compliance sentences ("I can't give step-by-step instructions…, but I
can explain the general principles…") have no honest binary label; the
two classifiers split them 2/2 each and **disagree on 2 of 4** — a
binary refusal classifier structurally cannot represent the
safe-completion category that real alignment behaviour (e.g.
Constitutional AI-style redirects, D4) relies on.

## What this does and does not show

- **Does show:** evaluation design dominates conclusions on synthetic
  safety data (leaky split 1.000 vs held-out 0.771 vs probes 0.667 for
  the same model); keyword refusal detection is brittle in exactly the
  places deployed filters would meet apologetic compliance and terse
  refusals; a refusal/compliance binary erases safe completions.
- **Does not show:** anything about real models' refusal rates, real
  user text, or HarmBench-style judge accuracy — the frozen Llama-2
  judge in D2 was validated at 93.19% human agreement on real outputs;
  this classifier was validated on sentences written for it, the
  weakest evidence grade in the lab so far, recorded as such.
- **Next:** D4 (Constitutional AI notes) covers where safe completions
  come from; a future iteration should train on the B4 output cases
  (hand-written, compromised vs benign) as a slightly less synthetic
  test bed, and add a third "safe completion" class.
