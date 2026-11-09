# Paper notes: Gradient-based adversarial attacks — the follow-ups to GCG

## Scope and sources

This is a survey note, not a replication. The lab ran no gradient
attack, no aligned model, and no model at all for D6 — every
attack success rate (ASR) below is the cited paper's, on that
paper's models and judge, and ASRs are **not comparable across
papers** without matching the model, behaviour set, generation
settings and judge (the HarmBench lesson, D2).

Primary sources, all read from their arXiv abstract / HTML full
text on 2026-11-09:

- Wallace et al. 2019, "Universal Adversarial Triggers for
  Attacking and Analyzing NLP", arXiv:1908.07125 —
  https://arxiv.org/abs/1908.07125
- Guo et al. 2021, "Gradient-based Adversarial Attacks against
  Text Transformers" (GBDA), arXiv:2104.13733 —
  https://arxiv.org/abs/2104.13733
- Zou et al. 2023, "Universal and Transferable Adversarial
  Attacks on Aligned Language Models" (GCG), arXiv:2307.15043 —
  https://arxiv.org/abs/2307.15043 (full notes: `notes/gcg.md`, A5)
- Zhu et al. 2023, "AutoDAN: Interpretable Gradient-Based
  Adversarial Attacks on Large Language Models",
  arXiv:2310.15140 — https://arxiv.org/abs/2310.15140
- Liu et al. 2023, "AutoDAN: Generating Stealthy Jailbreak
  Prompts on Aligned Large Language Models", ICLR 2024,
  arXiv:2310.04451 — https://arxiv.org/abs/2310.04451
- Jia et al. 2024, "Improved Techniques for Optimization-Based
  Jailbreaking on Large Language Models" (I-GCG), ICLR 2025,
  arXiv:2405.21018 — https://arxiv.org/abs/2405.21018
- Geisler et al. 2024, "Attacking Large Language Models with
  Projected Gradient Descent", NextGenAISafety workshop @ ICML
  2024, arXiv:2402.09154 — https://arxiv.org/abs/2402.09154
- Guo et al. 2024, "COLD-Attack: Jailbreaking LLMs with
  Stealthiness and Controllability", ICML 2024,
  arXiv:2402.08679 — https://arxiv.org/abs/2402.08679
- Sadasivan et al. 2024, "Fast Adversarial Attacks on Language
  Models In One GPU Minute" (BEAST), ICML 2024, PMLR
  235:42976–42998, arXiv:2402.15570 —
  https://arxiv.org/abs/2402.15570
- Liao & Sun 2024, "AmpleGCG: Learning a Universal and
  Transferable Generative Model of Adversarial Suffixes for
  Jailbreaking Both Open and Closed LLMs", arXiv:2404.07921 —
  https://arxiv.org/abs/2404.07921
- Paulus et al. 2024, "AdvPrompter: Fast Adaptive Adversarial
  Prompting for LLMs", ICML 2025, arXiv:2404.16873 —
  https://arxiv.org/abs/2404.16873

Naming warning, recorded because it has already cost this lab a
citation once (C2): there are **two different 2023 papers called
AutoDAN**. Zhu et al. is the gradient-based, left-to-right one;
Liu et al. is the hierarchical-genetic-algorithm one, which is
not gradient-based at all. The literature itself cites them as
AutoDAN-Zhu and AutoDAN-Liu (e.g. COLD-Attack's Table 1). Any
bare "AutoDAN" citation is ambiguous.

## One-paragraph summary

Gradient-based adversarial NLP did not start with jailbreaking.
Wallace et al. (2019) showed a short, input-agnostic *trigger*
found by gradient-guided token search could flip almost any NLP
model, and GBDA (2021) showed the discrete-token problem could
be sidestepped by optimising a *distribution* over tokens with a
Gumbel-softmax relaxation plus fluency/semantic constraints.
GCG (2023) ported the trigger idea to aligned LLMs: greedily
swap suffix tokens using one-hot gradients, target an
affirmative opening, and the resulting gibberish suffix is
universal across behaviours and transfers across models. The
2023–2025 follow-ups then attack GCG's three obvious weaknesses
in turn — it is **slow** (I-GCG, PGD, BEAST), **conspicuous**
(AutoDAN-Zhu, COLD-Attack, and the genetic AutoDAN-Liu all add a
fluency/readability objective so perplexity filters stop being a
defense), and **per-prompt** (AmpleGCG and AdvPrompter amortise
the optimisation into a generator model that emits suffixes in
seconds). The through-line for a defender is bleak and useful:
every property that made GCG detectable in this lab's A6/D5 work
— gibberish, high perplexity, one expensive suffix at a time —
was a property of the *first* optimiser, not of gradient-based
attacks as a class.

## Before GCG: where the machinery came from

### Wallace et al. 2019 — universal adversarial triggers

- **Method.** Initialise a short trigger (e.g. "the"), average
  the loss gradient over a batch of inputs, and replace each
  trigger token with the vocabulary token that minimises a
  first-order Taylor approximation of the loss (a HotFlip-style
  update), with a small beam search. One trigger is optimised
  for *all* inputs — universality is in the objective, not an
  accident.
- **Headline results (paper's).** A one-word trigger drops SNLI
  entailment accuracy from 89.94% to 0.55%; triggers make SQuAD
  models return a chosen target span and make GPT-2 produce
  racist output from non-racial contexts.
- **Why it matters here.** GCG is this paper plus an alignment
  target: swap "make the classifier say entailment" for "make
  the chat model start with 'Sure, here's…'". The lab's A5 note
  already filed GCG under "automated / gradient-based"; D6 adds
  that the branch is five years older than the LLM version and
  was always also an *analysis* tool (triggers exposed dataset
  artifacts in SNLI) — a use the jailbreak literature mostly
  dropped.

### Guo et al. 2021 — GBDA, the continuous-relaxation route

- **Method.** Instead of searching for one adversarial example,
  optimise a continuous matrix parameterising a *distribution*
  over examples (Gumbel-softmax sampling), with BERTScore and
  language-model perplexity added as differentiable soft
  constraints for semantic faithfulness and fluency.
- **Claim.** The first general-purpose gradient-based attack
  against transformer text models, state-of-the-art on its tasks
  at the time.
- **Why it matters here.** GBDA is the ancestor of the *other*
  follow-up branch: PGD-for-LLMs and COLD-Attack both return to
  continuous relaxations after GCG's discrete search proved
  effective but expensive. GBDA also introduced, in 2021, the
  exact move the stealth follow-ups repeat — put perplexity
  *inside the attacker's objective* and the perplexity defense
  is optimised away, not merely evaded.

## The follow-ups, by which GCG weakness they fix

### 1. Speed within discrete search — I-GCG (Jia et al.)

- **Diagnosis.** GCG's single fixed target ("Sure…") limits it,
  and one-token-at-a-time updates converge slowly.
- **Fixes.** (i) Diverse target templates containing harmful
  self-suggestion/guidance, of the form "Sure, + [template],
  here is + [rephrased query]"; (ii) automatic multi-coordinate
  updating — adaptively choose how many tokens to replace per
  step; (iii) easy-to-hard initialisation — seed a hard prompt's
  suffix from an easier prompt's solution.
- **Result (paper's).** Nearly 100% ASR on the evaluated models
  and benchmarks, including the NeurIPS 2023 Red Teaming Track;
  published at ICLR 2025. No new attack class — the lesson is
  that a large part of "GCG's limit" was target-template and
  schedule engineering, not the gradient signal.

### 2. Speed by continuous relaxation — PGD (Geisler et al.)

- **Diagnosis.** Discrete optimisation "typically uses more
  than 100,000 LLM calls" per the abstract — too expensive for
  large-scale evaluation or adversarial training.
- **Method.** Projected Gradient Descent on a continuously
  relaxed prompt, "carefully controlling the error introduced
  by the continuous relaxation" (the step earlier attempts got
  wrong); Adam, restarts to the best intermediate point.
- **Result (paper's).** Same effectiveness as GCG at up to one
  order of magnitude lower time cost; outperforms GBDA, which
  the authors report as much weaker on these aligned models.
  The honest caveat is also theirs, in the follow-up note on
  the arXiv record: under a stricter HarmBench-style judge,
  GCG is "slightly superior in some cases" — the cheaper
  optimiser and the stronger optimiser are not yet the same
  optimiser.

### 3. Speed by abandoning gradients — BEAST (Sadasivan et al.)

- **Method.** Beam search over tokens proposed by the victim
  model's own distribution — gradient-free, with interpretable
  knobs trading speed, ASR and readability. Included in this
  survey deliberately as the control case: it is a *successor*
  to gradient attacks, not one of them.
- **Result (paper's).** Jailbreaks Vicuna-7B-v1.5 in under one
  GPU minute at 89% ASR, vs a gradient-based baseline taking
  over an hour for 70% on a single RTX A6000 48GB; suffixes
  also transfer to unseen prompts/models including GPT-4-Turbo.
- **Lab resonance.** D5's optimiser was exactly this shape —
  gradient-free search against a score — and it was weak
  (hill-climbing cut perplexity 67–90% but evaded on only 1/3
  bases). BEAST shows the weakness is not "gradient-free" as
  such: proposing tokens from the *model's own distribution*
  keeps candidates fluent and on-manifold, where D5 proposed
  from fixed gibberish/fluent word pools. That proposal
  distribution, not the gradient, is the design variable D5
  got wrong.

### 4. Stealth: fluency inside the objective — AutoDAN-Zhu

- **Method.** Generate the suffix left-to-right, one token at a
  time, with a Single Token Optimization step scoring both the
  jailbreak objective and a readability objective. No seed
  jailbreak prompt or prior strategy knowledge required.
- **Result (paper's).** Readable suffixes that bypass perplexity
  filters while keeping high ASR; GCG with perplexity
  regularisation cannot reach the same ASR/readability corner;
  typically peaks within ~50 tokens (~200 steps); transfers to
  black-box GPT-3.5/GPT-4 better than gibberish suffixes under
  limited training data / a single proxy model.
- **Note.** The emerging readable suffixes spontaneously use
  strategies seen in manual jailbreaks — optimisation
  rediscovering the A3 corpus's hand-written families is a
  result worth remembering for C7's taxonomy: "manual" and
  "automated" are not disjoint attack classes.

### 5. Stealth by evolution — AutoDAN-Liu (the other AutoDAN)

- **Method.** Hierarchical genetic algorithm over DAN-style
  prompts: sentence- and word-level crossover/mutation, seeded
  from handcrafted jailbreaks, fitness = attack success with a
  stealthiness pressure. No gradients anywhere.
- **Result (paper's).** Semantically meaningful prompts that
  bypass perplexity-based defenses, ICLR 2024.
- **Why it belongs in a gradient survey.** It is the strongest
  evidence that the *stealth* conclusion does not depend on the
  optimiser: gradient, genetic and beam-search methods all
  converge on "fluent attacks defeat perplexity screening".
  A defense that only works against one optimiser family is
  not a defense against the attack class.

### 6. Stealth with explicit controls — COLD-Attack (Guo et al.)

- **Method.** Reframe attack generation as controllable text
  generation: a compositional energy function (attack success +
  fluency + lexical/sentiment/coherence constraints) sampled by
  Langevin dynamics in continuous logit space, then decoded.
  Each control requirement is a separate energy term — fluency,
  stealthiness, sentiment, left-to-right coherence are knobs,
  not side effects.
- **Result (paper's, continuation setting, Table 2).** Lowest
  perplexity in the comparison at competitive ASR: e.g. on
  Llama-2, COLD-Attack ASR 92% / ASR-G 66% at PPL 24.83, where
  AutoDAN-Zhu sits at PPL 152.32 and perplexity-regularised GCG
  at 1142 — i.e. the fluent-attack perplexity is now *below*
  ordinary prompt perplexity ranges, not merely under a
  threshold. Evaluated across Llama-2, Mistral, Vicuna,
  Guanaco, GPT-3.5 and GPT-4 (ICML 2024).

### 7. Amortisation: learn the suffix distribution — AmpleGCG

- **Key observation.** GCG's intermediate candidates are
  discarded except the single lowest-loss suffix, yet many
  higher-loss intermediates also jailbreak — the autoregressive
  loss is "neither sufficient nor necessary" for success.
  Keeping all candidates (AugmentedGCG) yields a large corpus
  of successful suffixes per query.
- **Method.** Train a generative model on that corpus to map
  harmful query → distribution of adversarial suffixes.
- **Result (paper's).** ~200 suffixes per query in ~4 seconds;
  near-100% ASR on Llama-2-7B-chat and Vicuna-7B by sampling
  ~200; transfers to closed models, 99% ASR on the then-latest
  GPT-3.5 with affirmative prefixes added. The attacker's cost
  model inverts: optimisation is paid once, inference is cheap,
  and a defender must block *the distribution*, not one string.

### 8. Amortisation with readable output — AdvPrompter (Paulus et al.)

- **Method.** Fine-tune a separate LLM (the AdvPrompter) to
  emit human-readable, input-conditioned suffixes, via an
  alternating loop: an inner optimiser (AdvPrompterOpt) finds
  target suffixes using only the target's log-probabilities —
  **gray-box, no backpropagated gradient from the target** —
  and the prompter is fine-tuned on them.
- **Result (paper's).** Competitive ASR on AdvBench and
  HarmBench in 1–2 seconds per prompt, readable suffixes
  (e.g. framing a request "as part of a lecture"), transfer to
  closed black-box models; and the dual-use result this lab
  cares about — adversarial safety fine-tuning on
  AdvPrompter-generated data drops Vicuna-7B validation ASR
  from 43.3% to 0.9% in their Table 2 while MMLU/MT-Bench are
  roughly preserved. Fast fluent attacks are also what make
  attack-generated adversarial training data affordable —
  the same loop HarmBench's R2D2 ran with live GCG (D2), at a
  fraction of the generation cost.

## Synthesis: four design axes, not a leaderboard

| Axis | GCG (2023) | Follow-ups |
|---|---|---|
| Optimisation variable | discrete tokens, one-hot gradients | continuous relaxation (GBDA→PGD, COLD), distribution over tokens (GBDA), learned generator (AmpleGCG, AdvPrompter) |
| Fluency | none — gibberish is the signature | explicit objective/constraint (AutoDAN-Zhu, COLD, AdvPrompter), model-distribution proposals (BEAST), evolution under stealth pressure (AutoDAN-Liu) |
| Cost per new prompt | ~10^5 calls, per prompt | multi-coordinate/schedule speedups (I-GCG), ~10× cheaper relaxation (PGD), <1 GPU-minute beam search (BEAST), seconds after one training run (AmpleGCG, AdvPrompter) |
| Target access | white-box gradients, transfer by hope | gray-box log-probs suffice (AdvPrompter); gradient-free works (BEAST, AutoDAN-Liu); transfer measured to GPT-3.5/GPT-4-class closed models (AmpleGCG, COLD, AutoDAN-Zhu) |

Three conclusions the papers jointly support:

1. **Perplexity is a property of the optimiser, not the
   attack.** Every stealth follow-up puts fluency in the
   objective and lands at or below benign perplexity. This
   lab's A6 filter (windowed AUROC 0.887 on *synthetic
   gibberish* suffixes) and D5 loop (windowed layer caught all
   3 hill-climbed finals) measured a defense against the 2023
   optimiser. Against the 2024 optimisers the honest prior is
   that A6's separation collapses toward its natural-injection
   numbers (full-text AUROC 0.712) or below — unmeasured here,
   because no fluent *optimised* suffix exists in any lab suite.
2. **The affirmative-prefix loss is a proxy that leaks.**
   AmpleGCG's "loss neither sufficient nor necessary" finding
   and I-GCG's target-template gains both say the field's
   standard objective undercounts success. Any future lab ASR
   — and any refusal metric built on D3's classifier — inherits
   that measurement error if it scores prefixes instead of
   judged completions (the D2/HarmBench warning, again).
3. **Amortisation changes the defense problem.** Once suffixes
   are sampled from a learned distribution in seconds, blocklists,
   per-string signatures and "the attack is expensive" arguments
   all expire. What survives in the papers is training-time
   defense on generated attacks (R2D2 in D2; AdvPrompter's
   fine-tuning result above) and channel separation (StruQ,
   C5/C6) — neither of which inspects the suffix's surface at all.

## Lab mapping

- **A5/GCG → this note** closes the ROADMAP's D6 pointer and
  TAXONOMY.md's "gradient attacks D5/D6" gap on the *notes*
  side. The *measurement* side stays open: no lab suite contains
  a single gradient-optimised or fluency-optimised suffix
  against an aligned model, and CPU-only distilgpt2 work cannot
  create one honestly (A5's limitation, unchanged).
- **A6 + D5 (perplexity, windowed perplexity)** are now scoped
  precisely: defenses against high-perplexity discrete-search
  suffixes and repetition-free random search. Their known
  evaders list grows by family, not by example — AutoDAN-Zhu,
  COLD and AdvPrompter suffixes are *designed* to sit in the
  benign perplexity range, joining D5's repetition controls
  (PPL 13–48, evading both scores) as structural, not
  incidental, failures.
- **D3 (refusal classifier)** inherits conclusion 2: scoring an
  attack by whether the completion *starts* compliantly is the
  same proxy error, one stage later.
- **Flagship seed (for D7/E1).** The cheapest original question
  this survey leaves on the table: does *windowed* perplexity —
  the one A6 layer that survived D5 — separate fluency-optimised
  suffixes (COLD/AutoDAN-style, low *global* perplexity) from
  benign text at all, or does local fluency defeat the window
  too? It is answerable offline with published suffix corpora
  (e.g. AmpleGCG's released suffixes) scored on distilgpt2,
  no aligned model and no GPU required, and either answer is a
  result: a surviving window is a defense claim, a collapsed
  window closes the perplexity research line honestly.

## Limitations of this note

- Survey of 11 sources chosen for the GCG lineage; it is not a
  systematic review. Logit-based, fine-tuning-based and
  LLM-as-attacker (PAIR/TAP) families are out of scope except
  where a paper above uses them as baselines.
- Numbers are quoted from abstracts, HTML full texts and the
  specific tables named in place; no PDF table was re-derived,
  and cross-paper ASR comparison is explicitly disclaimed above.
- Two 2025 items (AmpleGCG-Plus; annealing-augmented T-GCG
  appraisals) surfaced during the search but were not read in
  full, so they are recorded here as *seen, not studied* and
  carry no claims in this note.
