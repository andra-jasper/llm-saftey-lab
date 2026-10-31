# Paper notes: StruQ — structured queries against prompt injection

## Paper

Sizhe Chen, Julien Piet, Chawin Sitawarin, David Wagner (all UC
Berkeley).
"StruQ: Defending Against Prompt Injection with Structured Queries."
arXiv:2402.06363 (v1: Feb 2024; v2 read here). USENIX Security
Symposium 2025.
Link: https://arxiv.org/abs/2402.06363 — USENIX page:
https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe
Code: https://github.com/Sizhe-Chen/StruQ — project page:
https://sizhe-chen.github.io/StruQ-Website/

Read 2026-10-31 from the arXiv HTML full text (v2). This is a
study note, not a replication — the lab trained no model — so
every number below is the paper's, cited as such. The lab-side
half of the idea (a front-end in the harness, without the
training) is the next roadmap task, C6.

## One-paragraph summary

Prompt injection is, in the paper's framing, the classic
injection flaw recurring in a new substrate: control (the
developer's prompt) and data (untrusted user / retrieved content)
travel over one channel — a single concatenated string — so data
can spoof control, exactly as with SQL injection, XSS, and the
2600 Hz phone-phreaking tone. The robust historical fix was never
better filtering of the mixed string; it was changing the API so
control and data arrive separately (SQL prepared statements).
StruQ is that fix for LLMs: a **structured query** presents the
prompt and the data as two components. The system has two halves,
and both are load-bearing: (1) a **secure front-end** that encodes
the pair into a fixed format delimited by *reserved special
tokens* and filters those delimiter strings out of the data, so
data cannot forge the boundary; and (2) **structured instruction
tuning**, which fine-tunes a *base* (non-instruction-tuned) model
on clean samples plus samples with extra instructions planted in
the data portion, teaching it to follow instructions only from
the prompt portion. On Llama-7B and Mistral-7B this drives every
tested manual attack below 2% attack success rate (ASR) at
essentially no utility cost — but optimisation-based attacks
survive in part (TAP 97% → 9%, GCG 97% → 58% on Llama), and the
authors are explicit that StruQ is a first step, not a solution.

## Threat model (§3.1) — three parties, not two

- The attacker can **arbitrarily modify the data portion** and
  cannot modify the prompt. The attacker is assumed to *know*
  the prompt and the application's formatting — no security
  through obscurity.
- An attack succeeds iff the response obeys the hidden
  instruction in the data instead of treating it as data (the
  model may or may not also complete the benign instruction).
- Prompt injection is a **three-party** setting — model provider
  (trusted), application developer (trusted), data source
  (untrusted) — unlike jailbreaking's two parties. An injected
  instruction can be superficially benign ("print 10") and still
  be an attack, so safety tuning / harmful-content filtering
  cannot in principle catch it. This is the same distinction the
  lab drew in C2 (Greshake et al.) between injection-for-hierarchy
  and jailbreak-for-harm.

## The mechanism (§4)

### Secure front-end: reserved tokens + filtering

- The format adapts Alpaca's, but every delimiter piece is a
  **reserved special token** instead of text: `[MARK]` replaces
  `###`, `[INST]` / `[INPT]` / `[RESP]` replace the words
  "instruction" / "input" / "response", and `[COLN]` replaces
  the colon. After tokenisation, data text can never produce
  these tokens, because the front-end **filters the delimiter
  strings out of the data, repeatedly**, until none remain.
- The filter also strips `##` from data — empirically necessary,
  because attackers otherwise approximate `[MARK]` with a fake
  `##` delimiter (a Completion attack with a near-miss
  delimiter).
- The new tokens' embeddings are **initialised from the
  embeddings of the text they replace** ("###", "instruction",
  …) and then updated in fine-tuning. This detail matters:
  random initialisation measurably damages utility (the paper
  suspects it is one cause of BIPIA's utility collapse, §5.5).

### Structured instruction tuning: position, not content

Starting from the cleaned Alpaca dataset
`T = {(p, d, r)}`, the training set `T'` is:

- **50% clean** samples, unchanged — to preserve utility.
- **25% Naive-attacked**: the data of one sample gets *another
  training sample's instruction + data concatenated onto it*;
  the target output stays the response to the prompt-portion
  instruction. The injected instruction is drawn from the **same
  distribution as real instructions** — the model cannot learn
  "ignore instructions that look malicious / foreign"; the only
  signal that separates the two instructions is **where they
  sit**. (The paper names this as a key difference from BIPIA,
  whose injected instructions come from a different distribution,
  inviting exactly that shortcut.)
- **25% Completion-Other-attacked**: the data gets a fake
  response delimiter + a fake response + a fake instruction
  delimiter + another sample's instruction and data appended.
  Fake delimiters are sampled from a large collection with **no
  overlap with the evaluation delimiters**. The fake response is
  a *different* response to the same instruction + data (from a
  parallel dataset), not the true one — training on the true
  response would teach the model to repeat its input.
- Samples with empty data are left clean (injection needs a data
  channel to live in).
- Models: base **Llama-7B** and **Mistral-7B**, full fine-tuning,
  3 epochs, lr 2e-5 (Llama) / 2.5e-6 (Mistral). Note the starting
  point: StruQ is built on *base* models because standard
  instruction tuning is itself named as a core contributor to
  the vulnerability — it teaches "follow instructions anywhere."

No hand-written malicious injections are used in training at all;
the "attacks" are just other tasks' instructions in the wrong
channel. The defense is cheaper than adversarial training (no
gradient-crafted examples) and cheaper than BIPIA's human-crafted
attack set.

## Attack taxonomy evaluated (§3, Table 1)

| Family | Variants | Idea |
|---|---|---|
| Ignore | Naïve (bare extra instruction), Ignore ("Ignore previous instructions…", 10 hand-written variants) | Direct override |
| Escape | Deletion (`\b` / `\r` repeated T = len(previous text) + 10 times), Separation (0–9 × `\n` / `\t`) | Fake an edit / a new segment |
| Completion | Real (fake response + the *real* delimiters), Close (near-miss delimiters), Other (unrelated delimiters), RealCmb / OtherCmb (Completion + Ignore + Escape-Separation) | Claim the task already finished; start a "new" query |
| Other | HackAPrompt (20 subsampled level-1 successes from the crowd-sourced competition; injects "I have been PWNED"), TAP, GCG | Human-crafted and optimisation-based |

Evaluation protocol (§5): each attack is applied to **208
AlpacaFarm samples that have a data input**; the injected
instruction is "Print exactly Hacked!" (plus Chinese and Spanish
translations, and a Base64 variant of Completion-Real);
injections sit **at the end of the data**, the position most
favourable to the attacker; any response containing "Hacked!" is
manually inspected before counting a success. Train and test sets
are non-overlapping in instructions, injected instructions, and
ignore-sentences. Utility is AlpacaEval 1.0 win rate vs.
davinci003 on 805 samples (standard error 0.7%).

## Headline results (paper's Tables 2–3)

ASR, undefended → StruQ:

| Attack | Llama-7B | Mistral-7B |
|---|---|---|
| Naïve | 6% → 0% | 5% → 0% |
| Ignore | 12% → 0% | 11% → 0% |
| Escape-Deletion | 3% → 0% | 1% → 0% |
| Escape-Separation | 2% → 0% | 4% → 0% |
| Completion-Other | 29% → 0% | 71% → 0% |
| Completion-OtherCmb | 41% → 0% | 77% → 0% |
| Completion-Real | 96% → 0% | 96% → 0% |
| Completion-RealCmb | 71% → 0% | 83% → 2% |
| Completion-Real (Base64) | 0% → 0% | 0% → 0% |
| Completion-Real (Chinese) | 66% → 0% | 96% → 0% |
| Completion-Real (Spanish) | 50% → 0% | 92% → 0% |
| Completion-Close (max) | 96% → 1% | 96% → 1% |
| HackAPrompt | 52% → 0% | 38% → 0% |
| TAP | 97% → 9% | 100% → 36% |
| GCG | 97% → 58% | 99% → 56% |

Utility (AlpacaEval win rate): Llama 67.2% → 67.6% (no
significant change); Mistral 80.0% → 78.7% (~1 point,
borderline-significant). Three readings:

1. **Completion is the strongest manual family, and it is a
   channel attack, not a content attack.** Faking a completed
   turn beats "ignore previous instructions" by ~8× on the
   undefended models (96% vs. 12%). Nothing in the payload is
   malicious-looking; the payload *is a boundary claim*.
2. **The two halves cover each other's hole.** Real-delimiter
   Completion is stopped by the front-end filter (the data
   literally cannot contain the delimiter); every near-miss
   variant is stopped by the tuning (a near-miss tokenises as
   ordinary text, far in embedding space from the reserved
   token). The authors' adaptive-attack section (§5.2) tried
   nine near-miss delimiter variants (hash count, case, spacing,
   colon, typos, similar-meaning word): undefended ASR 61–96%,
   StruQ ≤ 1%; case variants of `[INST]` itself score 0%.
   Remove the filter and real delimiters work again; remove the
   tuning and near-misses work. Neither half alone is the
   defense.
3. **Optimisation-based attacks are a different regime.** TAP
   and GCG craft *task-specific* injections (68% of TAP's
   injections against StruQ are semantically tied to the benign
   instruction) rather than one fixed string for all tasks, and
   StruQ — trained only on task-agnostic manual injections —
   only partially generalises. GCG's residual 58% is the paper's
   headline open problem, with a cost caveat: GCG needs ~256k
   model queries per sample and TAP ~100; both are >100× the
   GPU-hours of manual attacks.

Two smaller results worth keeping:

- **Base64 Completion-Real is 0% even undefended** — the 7B
  models mostly cannot follow a Base64 instruction at all. Same
  capability-gating the lab noted in B3 (Wei et al.): GPT-3.5
  cannot follow Base64, GPT-4 can and is therefore vulnerable.
  An encoding attack surface exists only where the capability
  exists.
- **Non-English injections are not a soft spot here:**
  Chinese / Spanish Completion-Real go 66–96% undefended → 0%
  defended, despite English-only Alpaca training — position
  training transfers across language better than content
  training would.

## Ablations (§5.3–5.4) — what each ingredient buys

- **Augmentation ablation** (standard Alpaca text delimiters, no
  secure front-end; metric = best ASR over six manual attacks):
  undefended 41%; Naive alone 16%; Ignore alone 6% but utility
  drops to 64.3%; Completion-Other alone 3%; **Fake-Delimiter
  augmentation is actively harmful — 70% best-ASR and utility
  60.3%** (it teaches the model to reject oddly-formatted inputs,
  including clean ones); **Naive + Completion-Other = 0% at
  utility 66.0%** — the recipe StruQ ships. Lesson: training on
  the two *simplest* attack shapes beats training on more
  attack shapes; coverage of shapes is not the mechanism —
  position discrimination is.
- **Delimiter ablation** (Llama-7B, with filter): every
  combination of textual vs. special delimiter pieces lands at
  1% ASR on the strongest Completion attacks, but utility varies
  widely — all-special 67.6%, partial-special as low as 60.2%.
  Reserved tokens buy their keep mostly in **utility and
  headroom against unseen attacks**, not in the headline ASR
  once a strong `##` filter exists. Read carefully: this
  ablation keeps the filter on, so it does not show delimiters
  alone suffice.

## Comparison with other defenses (§5.5)

- **Test-time (prompting) defenses vs. Completion-Real, Llama-7B**
  (undefended 96%): Reminder in Prompt 83%; Delimiter Isolation
  (wrap data in ``` fences) 85%; In-Context Demonstration 48%;
  Reminder after Data 39%; **StruQ 0%**. Prompting defenses move
  the number; they do not close the hole — the paper's verdict
  on the whole B1-style family, measured on a real model.
- **Jatmo** (task-specific fine-tuning) reaches <1% ASR but
  produces a single-task model — one fine-tune per application.
  StruQ's claim is a *general-purpose* defended model.
- **BIPIA** (concurrent work: delimiter + fine-tuning on attack
  samples, Vicuna-7B): utility collapses 53.9% → 26.0%; on its
  own test set it holds Completion-RealCmb to 7%, but on StruQ's
  test set Ignore still succeeds 54% and GCG 100%. StruQ scores
  0% on *both* test sets. The paper's four suspected causes —
  no front-end / no completion-attack design, injected
  instructions from a different distribution than prompts, no
  clean samples in training, randomly initialised delimiter
  embeddings — read as a checklist of StruQ's design decisions
  in negative.
- **Instruction hierarchy** (Wallace et al. 2024, appearing
  months after StruQ's first version): the paper itself frames
  it as a generalisation of StruQ — more than two privilege
  levels (system / user / tool output) instead of prompt / data
  — and notes its deployment in GPT-4o mini. StruQ is the
  two-channel special case with the full recipe published.

## Limitations (§6, as the authors state them)

- **Programmatic applications only.** StruQ needs an API where
  prompt and data are supplied separately. It does not apply to
  open-ended multi-turn chatbots, where end users will not mark
  which parts of their messages are instructions vs. data.
- **Injection only.** Not a defense against jailbreaks, data
  extraction, or other LLM attacks.
- **Not worst-case secure.** GCG retains a non-trivial ASR; the
  paper is, by its own claim, the first to evaluate GCG / TAP
  *as prompt-injection attacks* at all, and flags defense
  against optimisation-based injection as the open problem.
  Suggested future directions: access control / rate-limiting
  against iterative attackers (Glukhov et al.), architectures
  that mask attention between the prompt and data portions in
  early layers, and richer structured queries (system prompt +
  user prompt + data).
- **Scale of evidence:** 7B open models, one utility benchmark
  (AlpacaEval 1.0), injections only at the end of the data.
  Nothing here measures 2025-scale frontier models.

## Follow-on work (for orientation, not part of these notes)

The same group's direct successor is **SecAlign** (Chen et al.,
arXiv:2410.05451, ACM CCS 2025): it replaces StruQ's SFT-only
recipe with preference optimisation over (secure response,
insecure response) pairs on injected inputs, motivated exactly
by StruQ's optimisation-based residual — its abstract reports
GCG-based injection ASR falling 56% → 2% on Mistral-7B under its
own evaluation setup (a different model / setup from StruQ's
Table 2; do not merge the numbers). A later open-weights release,
Meta SecAlign (arXiv:2507.02735), builds on that recipe. C6 / D5
planning should treat StruQ as the channel-separation baseline
and SecAlign as the current state of this line.

## Mapping to this lab

- **B2 / B6 are StruQ's front-end idea at prompting time, without
  either of StruQ's two load-bearing parts.** B2's spotlighting
  variants (S1–S5) and B6's RAG variants (R2–R5) separate prompt
  and data with *textual* delimiters, datamarking, or encoding
  on a model whose channel behaviour is an ideal-follower
  simulation. StruQ predicts both halves of what B2 / B6 found:
  (a) the separation works when the boundary holds — and (b)
  textual boundaries are forgeable: B2's fixed delimiters fell
  to payloads containing their own closing string (esc-01/02;
  6/8 probes blocked) and B6's fell the same way (rag-esc-01/03;
  4/6), which is precisely the paper's Completion-Real failure
  (96% undefended). StruQ's answer is that a boundary the data
  *cannot contain* (reserved tokens + filtering) plus *training*
  is what makes separation real.
- **The lab's random-token delimiters are the closest prompt-time
  analogue of reserved tokens.** B2 S2 / B6 R3 (and the combined
  S4 / R5) blocked 8/8 and 6/6 escape probes under simulation —
  an unguessable per-request delimiter approximates
  unforgeability. But the approximation differs from StruQ in
  kind, not degree: the lab's numbers are **upper bounds** that
  assume the model perfectly honours a boundary it can see;
  StruQ's numbers are **measured** on a model that had to be
  trained to honour a boundary, against an undefended baseline
  that honoured textual boundaries only 4% of the time under
  Completion-Real. C3's sim-vs-measured separation must be kept
  when C6 adds a StruQ row: a front-end-only harness variant
  belongs on the simulation side of the ledger, permanently.
- **What StruQ does not do, that B2 / B6 transforms do:** StruQ
  never transforms the *content* of the data, so it has no
  analogue of datamarking's no-space escape (B2 esc-05/06/07;
  B6 rag-esc-04/05/06) — there is nothing to evade by removing
  spaces. Conversely, StruQ *deletes* delimiter-like strings
  from data (including any `##`), a small clean-data cost the
  lab's exactly-invertible transforms never pay (B2 / B6
  recovery was exact, 10/10 and 15/15). The paper never measures
  data fidelity — AlpacaEval win rate would not show mangled
  markdown in the data — so this cost is real but unquantified
  in the source. Flagged for C6: a front-end prototype should
  report how many benign-suite documents its filter alters.
- **B1 sits in the paper's weakest measured family.**
  System-prompt hardening is a reminder-style test-time defense;
  the paper's real-model numbers for that family against
  Completion-Real are 39–85% ASR remaining. B1's simulated L3
  (18/25 blocked) is not comparable — different measurement kind
  — but the direction agrees: rule text in the prompt is the
  layer real models honour least exactly when the payload
  attacks the channel rather than the content.
- **A2 and B5 have no Completion attacks — the paper's strongest
  manual family is missing from both lab suites.** A2's
  direct_override ≈ the paper's Ignore; A2's encoded_payload
  overlaps Completion-Real (Base64) only in encoding, not in the
  fake-completed-turn structure; B5's indirect cases end with an
  instruction in a document but none *forge a response and a new
  instruction block*. The lab's escape probes are the nearest
  relatives — they spoof the lab's own delimiters — but they
  spoof a closing delimiter, not a whole completed turn. This is
  the single most concrete gap these notes produce, and it is
  C6-shaped: completion-style cases (fake response + fake new
  instruction inside the data channel) belong in the harness
  suites before any front-end is evaluated, or the evaluation
  will not contain the attack the front-end exists to stop.
- **A6 meets StruQ at the GCG residual.** The lab's perplexity
  work (A6, C4) targets the gibberish-suffix family; StruQ shows
  a model *trained* for channel separation still lets GCG
  through 58% of the time on Llama. Read together: suffix
  detection (input-side, A6) and channel training (model-side,
  StruQ) attack the same residual from opposite ends, and
  neither closes it — the honest motivation for D5's
  red-team / blue-team loop.

## What C6 should build (carried forward)

1. A harness front-end: structured format with
   reserved-token-*style* delimiters + a filter that strips
   delimiter strings (and `##`) from the data channel — StruQ
   §4.3 minus the training, labelled as such everywhere.
2. Completion-style test cases first (see the gap above), in
   both direct (A2-style) and RAG (B5-style) shapes, including
   near-miss delimiter variants modelled on §5.2.
3. Report the filter's clean-data cost: how many benign control
   documents it alters, and whether the altered document still
   answers the benign task — the measurement the paper skipped.
4. Keep every result on the simulation side of C3's ledger: with
   no structured instruction tuning, a "blocked" result means
   "blocked if the model honours the channel," which is exactly
   the assumption StruQ's undefended baselines falsify.

## Limitations of these notes

- Study notes from the arXiv v2 HTML text; the USENIX 2025
  camera-ready may differ in details not re-checked here.
- All ASR / utility figures are the paper's, on 7B models with
  AlpacaFarm / AlpacaEval 1.0; none were reproduced locally.
- The SecAlign paragraph summarises that paper's abstract only;
  it has not been read in full by this lab yet.

## Sources

- Chen, Piet, Sitawarin, Wagner. "StruQ: Defending Against
  Prompt Injection with Structured Queries." arXiv:2402.06363.
  https://arxiv.org/abs/2402.06363 (USENIX Security 2025;
  code: https://github.com/Sizhe-Chen/StruQ)
- Chen et al. "SecAlign: Defending Against Prompt Injection
  with Preference Optimization." arXiv:2410.05451.
  https://arxiv.org/abs/2410.05451 (follow-on work, abstract
  only)
- Lab-internal: `results/spotlighting.md` (B2),
  `results/rag_defenses.md` (B6),
  `results/system_prompt_hardening.md` (B1),
  `results/leaderboard.md` (C3), `notes/gcg.md` (A5),
  `results/perplexity_filter.md` (A6).
