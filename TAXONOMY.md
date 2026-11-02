# TAXONOMY.md — attack & defense taxonomy for this lab

Built 2026-11-02 (ROADMAP C7). This is a synthesis of the lab's own
suites, defenses, and paper notes through C6 — **no new measurements**.
Every count below is recomputed from `data/*.yaml` by
`eval/taxonomy.py`, which fails if this file drifts from the data.
Attack totals are kept suite-separate, as in `results/leaderboard.md`
(C3): direct, indirect, completion, probe, and output-stage suites are
never averaged or ranked against each other.

## 0. Inventory (verified by `eval/taxonomy.py`)

117 cases across the taxonomy suites:

| Suite file | Cases | Role |
|---|---|---|
| `data/injection_tests.yaml` | 25 | A2 direct-injection attacks |
| `data/indirect_injection_tests.yaml` | 15 | B5 indirect (RAG) attacks |
| `data/completion_tests.yaml` | 13 | C6 completion-style attacks |
| `data/spotlight_escape_probes.yaml` | 8 | B2 escape probes |
| `data/rag_escape_probes.yaml` | 6 | B6 escape probes |
| `data/output_cases.yaml` | 30 | B4 candidate outputs (15 compromised, 15 benign) |
| `data/benign_controls.yaml` | 10 | A4 benign controls |
| `data/structured_benign.yaml` | 10 | C6 benign documents for filter-cost measurement |

Plus `data/jailbreak_corpus.md` (A3): 20 curated public jailbreak
entries across 7 technique families, with sources — a reference corpus,
not a scored suite.

## 1. Classification axes

An attack in this lab is classified on five axes:

1. **Channel** — where the hostile instruction enters: the user turn
   itself (direct), retrieved/third-party content (indirect), a faked
   completed turn inside data (completion), or the model's own output
   stage (leaked/compliant text scored by B4).
2. **Mechanism** — how it tries to win: override wording, persona/frame,
   forged authority, encoding, delimiter forgery, multi-turn build-up.
3. **Goal** — system-prompt disclosure, task hijack, manipulation of
   the answer, fraud/exfiltration framing (Greshake threat taxonomy,
   C2 notes).
4. **Encoding / surface** — plain text, base64, foreign language,
   separator tricks (newlines, underscores, single tokens) that defeat
   space-based marking.
5. **Position** — payload at document end (13/15 of B5, recorded skew)
   vs hidden mid-document (2/15).

## 2. Attack families

### 2.1 Direct injection — `injection_tests.yaml` (25)
- `direct_override` (5) — "ignore previous instructions" and
  cancel-and-replace wording.
- `roleplay` (5) — persona adoption (e.g. DAN-style) smuggling new rules.
- `encoded_payload` (5) — base64 / transformed payloads; the lab's
  clearest *mismatched-generalization* family (Wei et al., B3 notes).
- `multi_turn` (5) — gradual build-up across turns; weakest fit to the
  single-turn papers (B3, C1 notes) and still the least-defended shape.
- `authority_claim` (5) — forged developer/admin priority claims.
  Mechanism ≈ *competing objectives* (Wei et al.); no counterpart
  category exists in the 2023 formalisation (C1 notes).

### 2.2 Indirect injection (RAG) — `indirect_injection_tests.yaml` (15)
Five categories × 3: `exfiltration`, `task_hijack`, `manipulation`,
`authority_spoof_in_document`, `hidden_encoded_in_document`.
Every user query is benign; the attack lives only in the retrieved
document. In Greshake et al.'s delivery taxonomy (C2) the lab covers
only the **passive** mode — active, user-driven, hidden/multimodal,
and availability attacks are recorded gaps, not covered families.

### 2.3 Completion attacks — `completion_tests.yaml` (13)
The data fakes a *finished* turn — fake response delimiter, plausible
fake response, fake new instruction — instead of arguing with the
instruction. Families: `completion_real_textual` (3),
`completion_real_reserved` (3), `completion_close` (3),
`completion_close_nested` (1), `completion_other` (3).
Added in C6 because C5 found A2/B5 contained none, while StruQ
measured Completion-Real as the strongest manual family
(96% ASR undefended vs 12%/11% for Ignore).

### 2.4 Escape probes — adaptive attacks on a named defense
- `spotlight_escape_probes.yaml` (8): `delimiter_escape` (2),
  `delimiter_spoof_generic` (2), `datamark_separator_trick` (3),
  `delimiter_guess` (1).
- `rag_escape_probes.yaml` (6): `delimiter_escape` (3),
  `datamark_escape` (3).
Probes are the lab's adaptive tier (B3's "any attack in the pool
succeeds" column in C3): a defense is only credited with its pool
result, not its headline-suite result.

### 2.5 Output-stage compromise — `output_cases.yaml` (30)
Candidate outputs, not prompts: `leak_verbatim` (5), `compliance` (5),
`evasive_leak` (5) compromised; `normal` (7) and `hard_negative` (8)
benign. This is response-based detection moved to the output side
(C1's filing of B4).

### 2.6 Benign / cost sets
- `benign_controls.yaml` (10): `benign_qa`, `benign_coding`,
  `benign_writing`, `benign_translation`, `benign_summarization`,
  `benign_instruction_ref`, `benign_creative`, `benign_math`,
  `benign_roleplay`, `benign_encoding` — one each.
- `structured_benign.yaml` (10): `benign_plain` (5),
  `benign_markdown_headings` (2), `benign_format_tutorial` (2),
  `benign_hash_content` (1) — documents that legitimately contain the
  very strings the C6 filter deletes, so clean-data cost is measurable.

## 3. Defense taxonomy

### 3.1 Prevention — instructional (prompt text only)
- **B1 system-prompt hardening L0–L3.** Blocked 0→12→17→18 of 25
  (ideal-follower simulation, upper bound). Its ceiling tracks the
  recognition layer, not the rule text (C3).

### 3.2 Prevention — structural (channel separation at prompt time)
- **B2 spotlighting S0–S5** (Hines et al.): fixed delimiters,
  per-request random-token delimiters, datamarking, combined, base64
  encoding. All variants block 25/25 on A2 under simulation; probes
  separate them (fixed delimiters 6/8, datamarking 5/8, random-token
  and combined 8/8).
- **B6 RAG variants R0–R5:** the same transforms applied to retrieved
  documents. Hierarchy-only text blocks 0/15 structurally; every
  structural variant blocks 15/15 on B5; probes: fixed 4/6,
  datamarking 3/6, random-token and combined 6/6.
- **C6 structured-query front-end Q0–Q3** (StruQ's front-end only, no
  training): Q3's repeated filter blocks 13/13 at string level; both
  unfiltered delimiter variants fall to their own delimiter family
  (10/13 each).

### 3.3 Detection — input side
- **A4 heuristic detector_v1** (regex/keyword families): 17/25 on A2,
  0/10 benign false positives — but 0/15 on B5 documents: thresholds
  tuned on direct injection do not transfer to indirect.
- **A6 perplexity filter** (distilgpt2): windowed AUROC 0.887 on
  adversarial-suffix cases; pure-repetition suffixes evade entirely,
  and fluent natural injections overlap benign text.

### 3.4 Detection — output side
- **B4 output filter** (policy keywords + TF-IDF similarity):
  13/15 compromised blocked, 0/15 benign false positives; the two
  layers are complementary (only 4 blocked by both).

### 3.5 Training-based defenses — referenced, NOT implemented here
StruQ's structured instruction tuning and its successor SecAlign are
studied (C5 notes) but not replicated: this lab has no fine-tuning
run, and no taxonomy row should be read as one. Known-answer
detection (benchmarked in the 2023 formalisation, C1) is the one
published defense family the lab has never tried — an open slot,
not a result.

## 4. Cross-cutting failure modes (the lab's recurring findings)

1. **Recognition is the input-side ceiling.** Instructional defenses
   cannot block what the recognition layer cannot see (B1 vs A4, C3).
2. **Encoding blindness at every stage.** Datamarked data: 1/25
   flagged; base64 data: 0/25; base64 output leak: similarity 0.000.
3. **Delimiter forgery beats fixed delimiters.** Every fixed-string
   scheme falls to its own closing string (B2 esc-01/02, B6
   rag-esc-01/03, C6 unfiltered variants); unforgeability
   (random tokens, reserved tokens + filtering) is what survives.
4. **Threshold non-transfer.** A detector calibrated on direct
   attacks scores a floor effect on indirect documents (A4/B5).
5. **Lossy-vs-lossless cost trade-off.** B2/B6 transforms are exactly
   invertible (zero clean-data cost); C6/StruQ-style filtering is
   lossy — 5/5 format-bearing benign documents altered, facts intact.

## 5. Known gaps (queued, not covered)

- Many-shot jailbreaking — paper notes C8, simulation D1.
- HarmBench behaviour categories — D2 mapping not yet done.
- Gradient/optimisation attacks (GCG, TAP) — notes D6, loop D5;
  StruQ's own residual (GCG 58% on Llama) says this tier survives
  front-end defenses.
- Active / user-driven / multimodal indirect delivery (C2 gaps).
- True clean-task accuracy — C3 recorded that all cost figures so
  far are proxies (exact recovery, small hand-written benign sets).

## 6. Paper index

- Zou et al. 2023, "Universal and Transferable Adversarial Attacks
  on Aligned Language Models" — https://arxiv.org/abs/2307.15043
  (`notes/gcg.md`, A5)
- Wei et al. 2023, "Jailbroken: How Does LLM Safety Training Fail?" —
  https://arxiv.org/abs/2307.02483 (`notes/jailbreak_failure_modes.md`, B3)
- Yi Liu et al. 2023, HouYi — https://arxiv.org/abs/2306.05499 (C1)
- Yupei Liu et al. 2023, prompt-injection formalisation & benchmark —
  https://arxiv.org/abs/2310.12815 (C1; USENIX Security 2024)
- Greshake et al. 2023, "Not what you've signed up for" —
  https://arxiv.org/abs/2302.12173 (C2; AISec '23)
- Hines et al. 2024, spotlighting —
  https://arxiv.org/abs/2403.14720 (B2/B6)
- Jain et al. 2023, baseline defenses —
  https://arxiv.org/abs/2309.00614 (A6)
- Chen, Piet, Sitawarin & Wagner, StruQ —
  https://arxiv.org/abs/2402.06363 (`notes/struq.md`, C5/C6;
  USENIX Security 2025)
- Chen et al., SecAlign — https://arxiv.org/abs/2410.05451
  (successor noted in C5, not yet studied in depth)
