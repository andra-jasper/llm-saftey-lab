# Month-1 retrospective — what the lab actually established, and what it did not

**Date:** 2026-11-10 (Day 28 of the daily lab)
**Scope:** Roadmap sections A–D, tasks A1–D6 — 26 tasks checked off between
2026-10-15 (seed + A1) and 2026-11-09 (D6). This is a synthesis of committed
work only: every number below is taken from the task's own committed report
(`results/…` / `notes/…`, summarised on its ROADMAP line). No new experiment
was run for this retro, and no number here is a re-measurement.

---

## 1. What was built

- **Suites (117 cases across 8 suites, counted in C7):** A2 direct injection
  (25), B5 indirect/RAG injection (15), C6 completion attacks (13), B2/B6
  escape probes (8 + 6), B4 output cases (30), and two benign sets (10 + 10),
  plus the A3 20-entry jailbreak corpus. Suites are kept separate throughout —
  direct and indirect results are never averaged into one score (C3 rule).
- **Defenses implemented (prompt-time / detection only):** system-prompt
  hardening B1 (L0–L3), spotlighting B2 (S0–S5), an output filter B4, RAG
  variants B6 (R0–R5), and a StruQ-style structured-query front-end C6
  (Q0–Q3, front-end only — no structured instruction tuning).
- **Detectors implemented:** heuristic detector_v1 A4 (9 regex/keyword
  families), perplexity + windowed-perplexity filter A6 (distilgpt2, CPU),
  and a stdlib TF-IDF logistic-regression refusal classifier D3 (synthetic
  data only, labelled as such).
- **Paper notes (9 sources indexed in C7's `TAXONOMY.md`, plus later
  additions):** GCG (A5), Wei et al. jailbreak failure modes (B3), the two
  distinct "Liu et al. 2023" papers (C1), Greshake et al. indirect injection
  (C2), StruQ (C5), many-shot jailbreaking (C8), HarmBench (D2),
  Constitutional AI (D4), and an 11-source survey of gradient-attack
  follow-ups (D6).

## 2. What worked — methods worth keeping

1. **Pre-registered predictions, reported either way.** D1, D3 and D5 wrote
   predictions down before running. Two headline predictions *failed* and
   were recorded as failed: D1's power-law fit for compliant-continuation
   NLL (R²_log 0.003 — the fall saturates ~4 shots and reverses by 32), and
   D5's P2 (hill-climbing cut suffix perplexity 67–90% on all 3 bases but
   evaded the full-text threshold on only 1 of 3). The retro verdict: this
   is the single most valuable habit in the month — it is what makes the
   negative results believable.
2. **Recompute, don't transcribe.** C3's leaderboard recomputes every cell
   from committed per-case JSONL, and C4's figure script refuses to render
   until recomputed medians/AUROCs match A6 exactly (full-text medians
   73.2 / 129.8 / 370.5; windowed AUROC 0.887). C7 and D2 went further and
   made the synthesis *machine-checked* (`eval/taxonomy.py` fails if the
   taxonomy drifts from the data; `eval/harmbench_map.py` checks the
   HarmBench mapping).
3. **Escape probes to separate defenses that tie.** On the main suites the
   structural defenses saturate: every B2 variant blocks 25/25 A2 attacks
   and every structural B6 variant blocks 15/15 B5 cases. The small probe
   sets are what separate them — fixed delimiters fall to their own closing
   string (B2 probes 6/8 blocked; B6 probes 4/6), datamarking falls to
   payloads with no spaces to mark (5/8; 3/6), while random-token delimiters
   and the combined variants block all probes (8/8; 6/6).
4. **Honest labelling of what a number is.** Ideal-follower simulation
   results (B1, B2, B6, C6) are labelled upper bounds, never live-model ASR;
   measured detector rows are kept in a separate part of the C3 ledger.
   StruQ's measured numbers and the lab's simulated ones are never placed
   on the same scale without that caveat (C5/C6).
5. **Held-out splits by family, not by row.** D3 is the cautionary tale that
   justifies the rule: a random stratified split gave logistic regression
   1.000 accuracy, the family-held-out split gave 0.771, and the keyword
   baseline collapsed to 0.250 — worse than chance — on held-out families.

## 3. Cross-cutting findings (the month's actual results)

These five are distilled in C7 and re-checked against the later D-tasks:

1. **Recognition is the input-side ceiling.** B1's hardening ladder tracks
   detector_v1 almost exactly (L0 0/25 → L1 12/25 → L2 17/25 → L3 18/25
   blocked, against detector_v1's 17/25 flagged on A2). Adding rule text
   past the recognition layer buys little; B1's residual misses were
   recognition/threshold failures, not missing rules.
2. **Encoding blindness recurs at every stage.** Datamarked data: 1/25
   flagged vs 17/25 after de-marking (B2). Base64 data channel: 0/25 (B2).
   Base64 output leak: TF-IDF similarity 0.000 (B4). No defense in the lab
   decodes-then-rescans; that is recorded as B4 v2 work, still open.
3. **Delimiter forgery vs unforgeability.** A defense falls to its own
   delimiter string wherever the attacker can print it (B2 esc-01/02,
   B6 rag-esc-01/03, C6 Q1/Q2 at 10/13). Random per-request tokens are the
   closest prompt-time analogue of StruQ's unforgeable reserved tokens —
   but C6 also shows token-shaped delimiters *without* filtering buy
   nothing in a text harness (Q2 = Q1 = 10/13); only Q3's repeated filter
   reached 13/13, at a clean-data cost (see finding 5).
4. **Thresholds tuned on direct injection do not transfer to indirect.**
   Detector_v1 flags 17/25 direct attacks but 0/15 B5 documents: a lone
   instruction family caps at 0.40 under its normalisation, below the 0.5
   threshold, while direct attacks stack families to clear it (B5).
5. **Lossy filtering vs lossless transforms is a real cost axis.** B2/B6
   transforms are exactly invertible (documents recovered 15/15 and 10/10
   benign exact). C6's StruQ-style filter is not: 0/5 plain documents
   altered, but 5/5 documents legitimately containing `##` headings,
   Alpaca format or reserved-token vocabulary were altered (48 characters
   removed; key facts survived 10/10, but deletion is lossy). StruQ itself
   never measures this cost — C6 measured the lab-scale version of it.

Two further findings from the D-tasks:

6. **Perplexity is a property of the optimiser, not the attack class**
   (D6 synthesis, scoped by A6/D5). A6's filter separates 2023-style
   gibberish suffixes (median PPL 370.5 vs benign 73.2; windowed AUROC
   0.887), and D5's windowed layer caught all 3 hill-climbed finals
   (windowed 7293 / 1779 / 1339 vs the 609.1 benign reference). But fluent,
   fluency-optimised and amortised attacks (AutoDAN, COLD-Attack,
   AmpleGCG, AdvPrompter) are built to sit at natural-text perplexity, and
   plain repetition already evades both scores completely (A6: PPL
   4.1 / 6.8; D5 controls: `the`×12 at 33.9–48.0, `!`×12 at 13.3–18.5).
7. **Format learning is not content learning** (D1). On distilgpt2, many
   compliant demonstrations cut compliant-continuation NLL (2.046 → 0.290
   at 8 shots) while correct-capital *content* NLL worsened to 7.176 at
   32 shots, where all 3 greedy generations answered "Reykjavik" — the
   last demonstration's capital — in perfect format. Any future many-shot
   or ICL claim in this lab must score content separately.

## 4. What did not work / hard limits of Month 1

- **No live aligned model was ever evaluated.** Every "blocked" number is
  either a detector measurement on hand-written cases or an ideal-follower
  simulation (an upper bound). There is no measured attack success rate
  against a real safety-trained model anywhere in this lab yet.
- **No training was run.** StruQ/SecAlign (C5) and Constitutional AI (D4)
  are studied, not implemented; they sit in the taxonomy as
  training-based defenses with no lab instance.
- **True clean-task accuracy is still unmeasured.** C3's PNA-style cost
  column is proxies only — exact recovery of transformed documents and
  two 10-case benign sets. No defense has been scored on whether a model
  still does the underlying task correctly.
- **Coverage is narrow by HarmBench's yardstick.** D2's machine-checked
  mapping: of the lab's 24 attack categories (82 cases), 0 map directly
  onto HarmBench, 7 partially, 17 not at all — the lab classifies
  hierarchy-violation *mechanisms*, HarmBench classifies *behaviours
  requested*, and 6 of its 7 semantic categories are entirely uncovered
  here. That is a scope statement, not a defect — but it bounds every
  claim the lab can make.
- **Known gaps carried forward:** active / user-driven / hidden-multimodal
  indirect injection (C2 — B5 is passive/RAG only); many-shot as a real
  attack (C8/D1 measured only a directional NLL question on a 1,024-token
  unaligned model); gradient attacks (surveyed in D6, never run);
  known-answer detection — the one published defense family in C1's
  taxonomy never tried in this lab.

## 5. Open questions

1. Does *windowed* perplexity separate fluency-optimised suffixes from
   benign text at all, or does the D5 windowed result survive only because
   D5's optimiser never targeted the windowed score? (Seed 1 below.)
2. Can any input-side detector transfer direct → indirect without being
   re-tuned per channel — e.g. known-answer detection (C1), which does
   not threshold instruction-likeness at all?
3. What does the structural-defense ranking (B2/B6/C6) look like once
   clean-task cost is measured as task accuracy instead of exact-recovery
   proxies — does Q3's lossy filter still win?
4. Where does a refusal metric put safe completions? D3's binary label
   erased them (classifiers split 2/2 and disagreed on 2 of 4 ambiguous
   cases); D4 shows the same erasure at training scale as CAI's
   evasiveness failure. A usable lab metric needs an evasiveness axis.
5. Which of these questions survives contact with a real aligned model,
   given every Month-1 defense number is a simulation upper bound?

## 6. Flagship seeds (input to E1 — candidates, not a choice)

- **Seed 1 — Windowed perplexity vs fluency-optimised suffixes.**
  From D6: score a published fluency-optimised suffix corpus (AmpleGCG's)
  against benign text on distilgpt2, offline, and test whether the
  windowed score — the layer that held in D5 — separates them. Directly
  falsifiable, reuses A6/D5 code and scoring, and its negative result
  would be as informative as a positive one.
- **Seed 2 — The clean-task cost of structural defenses, measured
  properly.** From C5/C6/C3: put B2/B6/C6-style front-ends in front of a
  real task set and measure task accuracy lost (PNA-style), including
  Q3-style lossy filtering on documents that legitimately contain the
  filtered strings. The cost StruQ never reported, on the lab's own
  transforms.
- **Seed 3 — A detector that transfers: known-answer detection on A2 + B5.**
  From C1/B5: the one benchmarked defense family never tried here, and
  the only Month-1 candidate whose mechanism does not depend on the
  instruction-likeness threshold that failed to transfer (0/15 on B5).
  Success criterion is cross-channel by construction: tune on A2, test
  untouched on B5 (and vice versa).

  *Secondary seed (noted, not developed):* an evasiveness-aware refusal
  metric, from D3 + D4 (§5, question 4).

## 7. Method rules carried into Month 2

- Keep the one-task / one-commit daily cadence and the pre-registration
  habit (§2.1); failed predictions stay in the record.
- Family-held-out splits wherever templates generate data (D3 rule).
- Suite separation and upper-bound labelling stay non-negotiable (C3).
- Before E3 baselines: pick the flagship in E1, write the dataset spec in
  E2, and include a clean-task accuracy measure in that spec — closing
  the longest-standing unmeasured gap (§4) by design rather than by
  another retro note.

---

*Sources for the underlying work are cited in each task's own note/report
and indexed in `TAXONOMY.md` (C7). This retro adds no new citations because
it reports no new external claims.*
