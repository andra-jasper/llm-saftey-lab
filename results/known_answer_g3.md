# Known-answer detection prototype — G3 results

**Date:** 2026-11-18. **Task:** G3 (E1 Candidate 3, the one
Liu et al. taxonomy family this lab had never tried).
**Script:** `eval/known_answer.py` (6 unit tests pass);
rows: `results/known_answer_g3_rows.jsonl` (100 rows);
machine-readable summary: `results/known_answer_g3_summary.json`.

## Method — simulation, labelled

No live model. A deterministic executor stand-in (the lab's
B1/B2/B6 ideal-follower tradition, an **upper bound**) ranks the
instructions it can recognise by *salience* — fixed surface-feature
weights over the injected text (override verbs, task-replacement,
authority claims, urgency, action verbs, roleplay frames, encoded
payloads, forced formats), with a design-constant channel factor
(document ×0.85, direct ×1.0). The planted known-answer instruction
lives in the system channel; an injected instruction **displaces**
it (known answer absent → flagged) iff its effective salience beats
the planted weight + a margin frozen at 0.10 for all configs.
Injections in the band just below the threshold are followed
*alongside* the user task while the canary survives — scored as
**partial misses**, per E1's requirement, never as detections.

The only tuned parameters are the planted-instruction config
(A append-once w0.55/single-token, B bookend w0.85/token-pair,
C verify-first w0.70/token-pair), tuned on one suite, frozen, and
evaluated untouched on the other — in both directions. Suites are
never averaged (C3 rule).

**Circularity caveat (stated, not buried):** the salience features
are hand-built from the same override vocabulary these attacks use,
so this measures the *transfer protocol + this executor*, not a
live model. E1 flagged exactly this validity risk for Candidate 3.

## Results

| direction | frozen config | tuning suite | test suite (untouched) | benign |
|---|---|---|---|---|
| A2 → B5 | C (verify-first) | A2: **3/25** detected, 5 partial, 17 missed | B5: **2/15** detected, 4 partial, 9 missed | 0/10 FP |
| B5 → A2 | B (bookend) | B5: **2/15** detected, 1 partial, 12 missed | A2: **2/25** detected, 3 partial, 20 missed | 0/10 FP |

The two B5 detections in both directions are the same pair —
`ind-aut-01` (authority spoof, salience 0.977) and `ind-hid-01`
(hidden instruction, 1.02) — the B5 cases whose injected text most
resembles a direct override. B5's manipulation family scored 0.0
salience on all 3 cases: those attacks carry no instruction-like
surface at all, so no displacement signal exists for this executor.

## Verdicts on E1's pre-registered predictions

- **P1 (≥8/15 on B5 with A2-frozen config): FAILED.** 2/15.
  Displacement detection does beat detector_v1's 0/15 on B5, but
  by a small margin, not the predicted one. Under this executor,
  the cross-channel transfer failure is **not** mainly about the
  signal type: most B5 injections never out-salience a planted
  instruction because they do not try to replace the task loudly —
  they append a side-action (exfiltration) or nudge content
  (manipulation), which a single-task executor absorbs without
  dropping the canary (the partial-miss band catches 4 more, and
  even counting those, 6/15 < 8/15).
- **P2 (reverse direction worse): supported on rates, equal on
  counts.** Reverse test: 2/25 on A2 (8%) vs forward test 2/15 on
  B5 (13%). A2's quiet families (roleplay, encoded, multi-turn —
  15 of 25 cases score ≤0.45 salience) are exactly as hard for
  displacement as E1 guessed.
- **P3 (benign cost non-zero and reported): measured.** False
  positives 0/10 in both directions; the real cost is overhead —
  the frozen configs in both directions use the token-pair format,
  i.e. 4 canary tokens added to every output, benign or not. No
  benign task was displaced.

## What this means

Known-answer detection, at least in this executor, inherits the
same blind spot as instruction-likeness thresholding: attacks that
do not compete for the task slot do not displace anything. The
partial-compliance band is where the interesting mass sits
(4–5 cases per suite) — a real known-answer deployment would need
the executor to *sometimes* drop the canary under partial
compliance, which this deterministic stand-in cannot express.
That is a design note for any live-model follow-up, and the
transfer protocol itself (tune/freeze/test, both directions,
partial as a scored category) is reusable as-is for F8/G6.

Sources: Liu et al. 2023, "Prompt Injection attack against
LLM-integrated Applications" (arXiv:2306.05499) and Liu et al.
2023/2024 formalisation (arXiv:2310.12815) — taxonomy per C1
notes; suites A2 (`data/injection_tests.yaml`), B5
(`data/indirect_injection_tests.yaml`), benign controls
(`data/benign_controls.yaml`); E1 predictions in
`proposals/flagship_candidates.md` Candidate 3.
