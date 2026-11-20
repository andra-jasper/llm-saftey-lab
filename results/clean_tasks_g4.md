# Clean-task suite v1 — G4 results

**Date:** 2026-11-18. **Task:** G4. **Dataset:**
`data/clean_tasks.yaml` (24 tasks). **Validator/scorer:**
`eval/clean_tasks.py` (5 unit tests pass); rows:
`results/clean_tasks_g4_rows.jsonl`; summary:
`results/clean_tasks_g4_summary.json`.

## What was built

The dataset E1 Candidate 2 and D7 require before any clean-task
cost claim: 24 programmatic-check tasks — 8 **extract** (one field
verbatim: order number, date, amount, email, city, time, title,
phone), 8 **qa** (short fact from a passage), 8 **extractive
summary** (return the one sentence stating a requested fact,
verbatim). Every `expected` is an exact substring of its `input`
— the validator enforces this mechanically, so scoring needs no
judge: normalised exact match (lowercase, strip punctuation,
collapse whitespace). All texts and figures are synthetic.

## Baseline scores (the floor G5 must beat)

| baseline | extract | qa | extractive_summary | total |
|---|---|---|---|---|
| first_sentence | 0/8 | 0/8 | 0/8 | **0/24** |
| keyword_overlap sentence pick | 0/8 | 0/8 | 7/8 | **7/24** |

Read honestly: sentence-picking baselines can only ever solve the
extractive-summary type (7/8 — the one miss is ct-sm-02, where the
storage sentence shares fewer content words with the instruction
than the sowing sentence). Extract and QA require returning a
*span*, not a sentence, so both baselines score 0 there by
construction. That is the point of the floor: a defense's benign
cost in G5 will be measured with a span-capable executor, and any
accuracy it loses against its own no-defense run on this suite is
the cost number — this suite makes that difference computable
with no human or model judge in the loop.

## Validation

Schema, unique ids, known types, and the expected-is-substring
rule all pass for 24/24 tasks; the validator's failure modes are
unit-tested (non-substring and duplicate-id cases both caught).

## Next

G5 runs the B2/B6/C6 front-ends over this suite and reports task
accuracy per defense in the F4 triple format (robustness +
benign cost + compute cost). Until G5, no clean-task cost claim
exists in this lab — which is exactly the gap D7 flagged.
