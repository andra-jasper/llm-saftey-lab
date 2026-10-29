# Leaderboard — defense x attack matrix (ROADMAP task C3)

Generated 2026-10-29 by `eval/leaderboard.py` from the per-case JSONL rows
committed by A4, A6, B1, B2, B4, B5 and B6 (`results/*_rows.jsonl`).
No model was run for this task and no number was re-measured: every cell
below is recomputed from those rows, and the script's unit tests
(`eval/test_leaderboard.py`) pin the headline cells to the values the
original result files reported.

## Read this first — what is and is not comparable

- **Suites are separate.** A2 = 25 direct injections (user turn is the attack).
  B5 = 15 indirect injections (attack only inside a retrieved document; the
  user query is benign). B4 = 30 candidate model *outputs*, a different stage
  of the pipeline entirely. Rates are never averaged or ranked across suites.
- **Two kinds of number.** `(measured)` rows score the raw text with a real
  detector/filter. `(sim)` rows are the B1/B2/B6 ideal-follower simulations —
  an *upper bound* under the variant's own segment parser, as those result
  files state; a real model does not parse delimiters reliably.
- **Adaptive column** (asked for in B3's notes): the attacker may try every
  attack in the pool (suite + that task's escape probes where they exist) and
  succeeds if *any one* is not blocked. It is the worst case the mean hides.
- **Clean-task cost column** (asked for in C1's notes, PNA-style): benign
  false positives / blocked benign / exact recovery, as each original run
  measured it. No run measured real task accuracy on clean input, so this
  column is a proxy everywhere — stated per row, not hidden.

## Table 1 — A2 direct-injection suite (25 attacks, 5 per category)

| defense | direct_override | roleplay | encoded_payload | multi_turn | authority_claim | total blocked | clean-task cost | adaptive (any of pool succeeds?) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A4 detector_v1 (measured) | 5/5 | 1/5 | 1/5 | 5/5 | 5/5 | 17/25 | 0/10 benign flagged | SUCCEEDS |
| A6 perplexity >= 100 (measured, distilgpt2) | 3/5 | 3/5 | 4/5 | 3/5 | 3/5 | 16/25 | 3/10 benign flagged | SUCCEEDS |
| A6 perplexity >= 200 (measured, distilgpt2) | 1/5 | 0/5 | 4/5 | 0/5 | 1/5 | 6/25 | 1/10 benign flagged | SUCCEEDS |
| B1 hardening L0 (sim) | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/25 | 0/10 benign blocked | SUCCEEDS |
| B1 hardening L1 (sim) | 3/5 | 1/5 | 1/5 | 3/5 | 4/5 | 12/25 | 0/10 benign blocked | SUCCEEDS |
| B1 hardening L2 (sim) | 5/5 | 1/5 | 1/5 | 5/5 | 5/5 | 17/25 | 0/10 benign blocked | SUCCEEDS |
| B1 hardening L3 (sim) | 5/5 | 1/5 | 2/5 | 5/5 | 5/5 | 18/25 | 0/10 benign blocked | SUCCEEDS |
| B2 spotlighting S0 (sim) | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/25 | no transform (control) | SUCCEEDS |
| B2 spotlighting S1 (sim) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 25/25 | 10/10 benign recovered exactly | SUCCEEDS |
| B2 spotlighting S2 (sim) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 25/25 | 10/10 benign recovered exactly | fails (pool fully blocked) |
| B2 spotlighting S3 (sim) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 25/25 | 10/10 benign recovered exactly | SUCCEEDS |
| B2 spotlighting S4 (sim) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 25/25 | 10/10 benign recovered exactly | fails (pool fully blocked) |
| B2 spotlighting S5 (sim) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 25/25 | 10/10 benign recovered exactly | fails (pool fully blocked) |

Per-category reading: detector_v1 is perfect on direct_override, multi_turn
and authority_claim (5/5 each) and near-blind on roleplay and encoded_payload
(1/5 each) — B1 inherits exactly that ceiling because its rules can only block
families the detector recognises (L3's executed decode-and-inspect adds one
encoded case, 2/5). Perplexity is the mirror image: at >=200 it catches 4/5
encoded_payload (Base64-like text is unnatural) and 0/5 multi_turn / roleplay.
Every B2 variant contains all 25 A2 attacks *structurally* — the A2 cells do
not separate them at all; only the probe column of the adaptive pool does
(S1 fixed delimiters and S3 datamarking fall to crafted escapes; see Table 3).

Perplexity separation recomputed from rows: full-text AUROC suffix-vs-benign 0.780, natural-vs-benign 0.712; windowed AUROC suffix 0.887, natural 0.788. Medians: benign 73.2, natural 129.8, suffix 370.5. The two pure-repetition suffixes score below benign text and evade at every threshold (A6) — no threshold row above catches them.

## Table 2 — B5 indirect-injection suite (15 attacks, 3 per category)

| defense | exfiltration | task_hijack | manipulation | authority_spoof_in_document | hidden_encoded_in_document | total blocked | escape probes | clean-task cost | adaptive (any of pool succeeds?) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A4 detector_v1 on document channel (measured) | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/15 | n/a (no probes in B5) | 0/15 benign user queries flagged | SUCCEEDS |
| B6 RAG defense R0 (sim) | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/15 | 0/6 probes blocked | 15/15 documents recovered exactly | SUCCEEDS |
| B6 RAG defense R1 (sim) | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/15 | 0/6 probes blocked | 15/15 documents recovered exactly | SUCCEEDS |
| B6 RAG defense R2 (sim) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 4/6 probes blocked | 15/15 documents recovered exactly | SUCCEEDS |
| B6 RAG defense R3 (sim) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 6/6 probes blocked | 15/15 documents recovered exactly | fails (pool fully blocked) |
| B6 RAG defense R4 (sim) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 3/6 probes blocked | 15/15 documents recovered exactly | SUCCEEDS |
| B6 RAG defense R5 (sim) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 6/6 probes blocked | 15/15 documents recovered exactly | fails (pool fully blocked) |

The starkest row in the lab: the A4 detector flags 0/15 documents — not
because no family fires (one fires on 6/15) but because a lone family caps at
0.40 under its normalisation, below the 0.5 threshold tuned on A2's stacked
direct attacks (B5's own finding). Instruction hierarchy alone (R1) is
structurally identical to naive RAG (0/15, 0/6 probes): its effect, if any,
is behavioural and this simulation cannot see it. Every structural variant
blocks 15/15 on the suite; again only the probes separate them (Table 3).

## Table 3 — Escape probes: where the structural variants actually differ

| variant | probes blocked |
| --- | --- |
| B2 S1 (direct setting, 8 probes) | 6/8 blocked |
| B2 S2 (direct setting, 8 probes) | 8/8 blocked |
| B2 S3 (direct setting, 8 probes) | 5/8 blocked |
| B2 S4 (direct setting, 8 probes) | 8/8 blocked |
| B2 S5 (direct setting, 8 probes) | 8/8 blocked |
| B6 R2 (RAG setting, 6 probes) | 4/6 blocked |
| B6 R3 (RAG setting, 6 probes) | 6/6 blocked |
| B6 R4 (RAG setting, 6 probes) | 3/6 blocked |
| B6 R5 (RAG setting, 6 probes) | 6/6 blocked |

Pattern, same in both settings: fixed delimiters fall to a payload containing
their own closing string; datamarking falls to payloads with no spaces to
mark (newlines, underscores, a single base64 token); per-request random-token
delimiters and the combined variant block every probe crafted so far. The
probe sets are small and written by the same author as the defenses, so
'blocks all probes' means 'blocks all *these* probes', nothing stronger.

## Table 4 — B4 output filter (own suite: 30 candidate outputs, different stage)

| layer set | leak_verbatim | evasive_leak | compliance | compromised blocked | clean-task cost |
| --- | --- | --- | --- | --- | --- |
| combined (keywords OR TF-IDF >= 0.25) | 5/5 | 3/5 | 5/5 | 13/15 | 0/15 benign blocked |

Layers are complementary, not redundant: keywords alone 9/15, TF-IDF alone 8/15, both together only 4/15 of the compromised set. The two misses are the French leak (TF-IDF 0.221, under threshold) and the base64 leak (0.000 — the same encoding blindness the input-side rows show). This table guards the *output* of an already-compromised model; it is not comparable to Tables 1–2 and is not ranked against them.

## Cross-cutting findings (only claims every underlying run supports)

1. **Recognition, not rule text, is the input-side ceiling.** B1 goes 0 → 12 →
   17 → 18 blocked exactly as rule coverage grows into detector_v1's 17/25
   recognition set (+1 from L3's executed decoding). No prompt-text defense
   in this lab blocks an attack its recogniser cannot see.
2. **Structural separation beats screening — under its own parser.** B2/B6
   structural variants block 25/25 and 15/15 where screening blocks 17/25 and
   0/15, but that gap is partly definitional (the sim parses with the
   variant's own delimiters). The probe tables are the honest discriminator.
3. **Encoding blindness recurs at every stage.** Detector on datamarked data:
   1/25 flagged (17/25 after de-marking); on base64-encoded data: 0/25 (B2).
   Output filter on the base64 leak: 0.000 similarity, allowed (B4). A
   decode-then-rescan step is the single most repeated unbuilt fix in the lab.
4. **Thresholds tuned on direct injection do not transfer to indirect.**
   A lone instruction family scores at most 0.40 in detector_v1, so the 0.5
   threshold that was clean on A2 (0/10 FP) silently passes all of B5.
5. **Adaptive reading removes most of the good news.** Averaged blocked rates
   look graded; the adaptive column shows every non-structural defense — and
   S1/S3/R2/R4 with their probes included — is fully bypassable by at least
   one attack already in the lab's own pools. Only S2, S4, S5 (A2+probes) and
   R3, R5 (B5+probes) block their entire pools, all under simulation.
6. **Clean-task cost is ~zero everywhere it was measured — and it was barely
   measured.** 0 benign flagged/blocked for A4, B1 and B4; exact recovery
   10/10 (B2) and 15/15 (B6); perplexity is the exception (1/10 FP at >=200,
   3/10 at >=100 — a real cost for a weak detector). But benign sets are
   10–15 hand-written cases and recovery is not task accuracy: a true PNA
   (performance under no attack on real tasks) remains unmeasured — a gap
   for C7 / the flagship dataset, recorded here rather than smoothed over.

## Sources (for the underlying runs; this file adds no new external claims)

- Hines et al. 2024, "Defending Against Indirect Prompt Injection Attacks
  With Spotlighting", arXiv:2403.14720 — B2/B6 transforms.
- Greshake et al. 2023, "Not what you've signed up for", arXiv:2302.12173 —
  B5 suite design (see `notes/indirect_injection.md`).
- Wei et al. 2023, "Jailbroken: How Does LLM Safety Training Fail?",
  arXiv:2307.02483 — adaptive-attack framing (see `notes/jailbreak_failure_modes.md`).
- Liu et al. 2023 (Yupei Liu et al.), arXiv:2310.12815 — PNA-style clean-task
  cost framing (see `notes/prompt_injection_survey.md`).
- Jain et al. 2023, arXiv:2309.00614; Zou et al. 2023, arXiv:2307.15043 — A6.

Underlying result files: `results/detector_v1.md`, `results/perplexity_filter.md`,
`results/system_prompt_hardening.md`, `results/spotlighting.md`,
`results/output_filter.md`, `results/indirect_injection_tests.md`,
`results/rag_defenses.md`.
