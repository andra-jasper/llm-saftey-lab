# Paper notes: Jailbroken — How Does LLM Safety Training Fail?

## Paper
Alexander Wei, Nika Haghtalab, Jacob Steinhardt (all UC Berkeley).
"Jailbroken: How Does LLM Safety Training Fail?"
NeurIPS 2023. arXiv:2307.02483 (v1: 5 Jul 2023).
Link: https://arxiv.org/abs/2307.02483 — publisher page: https://neurips.cc/virtual/2023/poster/70702
Read 2026-10-23 from the arXiv full text.

Content note: the paper discusses jailbreaks for harmful-content generation.
These notes describe its concepts and headline results only; they do not
reproduce the paper's strongest attack prompts, which the authors themselves
withheld under responsible disclosure to OpenAI and Anthropic.

## One-paragraph summary
Instead of cataloguing jailbreaks one by one, Wei et al. ask *why* safety
training fails and hypothesise two failure modes. (1) **Competing
objectives:** a model is trained at once for language modelling /
pretraining, instruction following, and safety; a prompt can force a choice
in which obeying the first two is heavily rewarded and refusing is heavily
penalised, so compliance wins. Their new examples are *prefix injection*
(force an affirmative-looking opening such as an enthusiastic compliance
prefix, after which a refusal is unlikely in the pretraining distribution)
and *refusal suppression* (impose output rules that rule out the wording of
a typical refusal). (2) **Mismatched generalization:** pretraining covers a
far larger, more diverse distribution than safety training, so there are
inputs the model can *understand and follow* but has never been trained to
refuse — Base64-encoded requests are the sharp example, alongside ROT13,
leetspeak, Morse code, payload splitting, synonyms, translation, unusual
output formats, and distractor instructions. Evaluating 30 attacks on GPT-4,
Claude v1.3, and GPT-3.5 Turbo, over a curated set of 32 harmful prompts
taken from OpenAI's and Anthropic's own red-teaming material and a held-out
set of 317 GPT-4-generated harmful prompts (filtered to prompts both models
refused unattacked, and not seen by the authors until after data collection),
they find that simple attacks succeed only on a fraction of prompts but
*combinations* are extremely effective, and an adaptive attack — succeeding
if any one of the tested attacks succeeds on a prompt — reaches 100% on the
curated set for both GPT-4 and Claude v1.3.

## Headline results (paper's Tables 1–2, BAD BOT = on-topic compliance)
- No attack (`none`): GPT-4 0.03, Claude v1.3 0.00 on the curated set —
  confirming the prompts really are ones the models refuse.
- Single new attacks, curated set: prefix injection 0.22 (GPT-4) / 0.00
  (Claude); refusal suppression 0.25 / 0.16; Base64 0.34 / 0.38.
- Ablations support the mechanism, not just the wording: prefix injection
  with a neutral greeting prefix falls to 0.06 on GPT-4, and refusal
  suppression with its rules inverted falls to 0.00 on both models.
- Combination attacks (prefix injection + refusal suppression + Base64,
  then adding style injection, then website-generation / formatting
  constraints): `combination_3` 0.94 (GPT-4) / 0.81 (Claude) and
  `combination_2` 0.69 / 0.84 on the curated set; on the 317-prompt held-out
  set `combination_3` 0.93 ± 0.03 / 0.87 ± 0.04 and `combination_2`
  0.86 ± 0.04 / 0.89 ± 0.03. Adaptive attack: 1.00 / 1.00 curated,
  0.96 / 0.99 held-out.
- Targeted training is not enough: Claude v1.3, apparently trained against
  harmful roleplay, scores 0.00 on every roleplay attack — yet remains
  fully vulnerable to an adaptive attacker using other families.
- Scale can *create* vulnerabilities: GPT-3.5 Turbo mostly cannot follow
  Base64 instructions at all (Base64 rows are 0.91–1.00 UNCLEAR, BAD BOT
  ≤ 0.03), while GPT-4 can follow them and does so with fewer safeguards.
  A capability that only exists at larger scale is an attack surface that
  only exists at larger scale.

## The two failure modes, precisely
- **Competing objectives** is a conflict *inside the training objective*.
  The paper points at the RLHF objective itself (a KL / pretraining term
  alongside the safety preference term): even ideal safety training under
  that objective trades safety off against staying close to the pretrained
  model. Hence their claim that this mode is not fixed by more data or
  scale — resolving it may require moving beyond pretrain-then-finetune,
  e.g. incorporating values from pretraining.
- **Mismatched generalization** is a *coverage* gap: capability
  generalisation outruns safety generalisation. Every new capability
  (a new encoding, language, format, or tool-like behaviour the model
  acquires) is a domain in which refusal behaviour may simply never have
  been installed.
- Their proposed design principle follows from both: **safety-capability
  parity** — safety mechanisms must be as sophisticated as the underlying
  model. A filter that cannot decode Base64 cannot flag a Base64 attack;
  a human labeller who cannot read the obfuscation cannot label it; and
  models can be used to *generate* attacks against themselves (their
  `auto_payload_splitting` and `auto_obfuscation` attacks are partly
  model-built, and in the latter the models themselves rediscovered
  encodings).

## Mapping to this lab — where our own results fit, and where they don't
Threat-model caveat first: Wei et al. study *jailbreaking for restricted
(harmful) content* from a black-box chat user who cannot change the system
prompt or history. Most of this lab studies *prompt injection / instruction-
hierarchy violation* (system-prompt disclosure, task override). The failure
modes transfer as an analogy about training and coverage, not as the same
experiment. Keeping that distinction is what makes the mapping honest.

- **A2 categories under the two modes** (`data/injection_tests.yaml`,
  25 cases, 5 per category, verified 2026-10-23):
  - `encoded_payload` (5) → mismatched generalization, almost literally the
    paper's §3.2 list: Base64, ROT13, and leetspeak are named there, and
    our reversed-string and pattern-completion cases are the same idea in
    miniature — the model can decode what its safety / filter layer was
    never trained on.
  - `direct_override` (5) and `authority_claim` (5) → competing objectives:
    instruction-following (including deference to a claimed higher
    authority) is set against the safety / hierarchy objective. One A2
    direct-override case also borrows prefix injection directly, by
    dictating the opening words of the reply.
  - `roleplay` (5) → competing objectives: the paper reads DAN-style
    roleplay exactly this way (dense character instructions plus a forced
    output prefix). Our A3 corpus families overlap here.
  - `multi_turn` (5) → weakest fit, and worth saying so: Wei et al.'s
    threat model is essentially single-turn. Rapport-building and
    quoted-back "commitments" plausibly exploit instruction-following /
    helpfulness against safety, but the paper provides no multi-turn
    evidence; do not cite it as covering this category.
- **A6 perplexity filter is a mismatched-generalization detector — and
  inherits its limit.** Encoded payloads were the highest-perplexity
  natural injections in A6 (unnatural text is exactly what an out-of-
  distribution attack looks like), while fluent competing-objective
  attacks overlapped benign text. A perplexity filter catches attacks
  that *look* off-distribution; it has nothing to say about attacks that
  stay fluent and merely re-rank the model's objectives.
- **B1 hardening vs "targeted training is insufficient".** B1's levels
  blocked 12/25 → 17/25 → 18/25 in ideal-follower simulation, and its
  residual misses were recognition failures, not missing rule text. That
  is the lab-scale version of the paper's Claude-roleplay finding: patch
  one family thoroughly and the adaptive attacker moves to another family.
  Any future B-series result should therefore be reported per-family, not
  only as an aggregate blocked rate.
- **B2 spotlighting gives a concrete parity failure for filters.**
  Safety-capability parity is usually stated about the *model*; B2 showed
  it applies to the *pipeline*: datamarked data was flagged by
  detector_v1 in only 1/25 cases (vs 17/25 after de-marking) and
  Base64-encoded data in 0/25. A defense transform made the content more
  capable-channel (structured, encoded) than the filter scanning it —
  parity lost inside our own stack, fixed only by scanning the restored
  text.
- **Combination / adaptive reporting (for C3).** The paper's most useful
  methodological lesson for our leaderboard: single-attack rates
  understate risk by a lot (best single new attack 0.34 vs adaptive 1.00
  on GPT-4, curated). C3's defense × attack matrix should include an
  "any attack succeeds" row per defense, or it will flatter every defense
  we build.

## Limitations / open questions
- **Indirect evidence only.** GPT-4 and Claude are proprietary; the authors
  cannot inspect training data or objectives, so both failure modes are
  inferred from behaviour and ablations, not confirmed mechanistically.
  The paper itself calls for open replications of safety-trained models.
- **2023 snapshot.** Models, system prompts, and filters have changed
  substantially since GPT-4 / Claude v1.3 in early 2023; the specific
  rates above are historical, not a claim about current systems. The
  failure-mode framing, not the percentages, is the durable contribution.
- **Manual labelling, small curated n.** Outcomes (GOOD BOT / BAD BOT /
  UNCLEAR) were hand-labelled — 2,970 curated-set and 2,536 synthetic-set
  samples — and the curated set is only 32 prompts, so single-attack
  differences of a few points are a handful of cases. The held-out 317 set
  mitigates this for the top attacks only.
- **Not replicated here.** We have no live safety-trained model in this
  lab and ran no jailbreak evaluation for this note; every number above is
  the paper's, cited as such. Our B1/B2 numbers are ideal-follower
  simulations (upper bounds) and are not comparable to the paper's live
  BAD BOT rates.
- **Open question for the flagship:** is "any attack succeeds" (the
  adaptive row) the right headline metric for *injection* defenses too?
  B2's escape probes already behave that way — one escaping probe family
  compromises a variant regardless of its 25/25 A2 score. Formalising an
  adaptive-attack row for C3/B6 would import Wei et al.'s best idea into
  the RAG setting, where the attacker controls retrieved documents rather
  than the user turn.

## Sources
- Wei, Haghtalab & Steinhardt, "Jailbroken: How Does LLM Safety Training
  Fail?", NeurIPS 2023, arXiv:2307.02483 — https://arxiv.org/abs/2307.02483
- Lab files referenced: `data/injection_tests.yaml` (A2),
  `data/jailbreak_corpus.md` (A3), `results/perplexity_filter.md` (A6),
  `results/system_prompt_hardening.md` (B1), `results/spotlighting.md` (B2),
  `notes/gcg.md` (A5 — GCG's affirmative-start trick is the gradient-based
  cousin of this paper's prefix injection).
