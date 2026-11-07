# Paper notes: Constitutional AI — harmlessness from AI feedback

## Paper

Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell,
Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia
Mirhoseini, Cameron McKinnon, Carol Chen, Catherine Olsson,
Christopher Olah, Danny Hernandez, Dawn Drain, Deep Ganguli,
Dustin Li, Eli Tran-Johnson, Ethan Perez, Jamie Kerr, Jared
Mueller, Jeffrey Ladish, Joshua Landau, Kamal Ndousse, Kamile
Lukosuite, Liane Lovitt, Michael Sellitto, Nelson Elhage,
Nicholas Schiefer, Noemi Mercado, Nova DasSarma, Robert Lasenby,
Robin Larson, Sam Ringer, Scott Johnston, Shauna Kravec,
Sheer El Showk, Stanislav Fort, Tamera Lanham, Timothy
Telleen-Lawton, Tom Conerly, Tom Henighan, Tristan Hume,
Samuel R. Bowman, Zac Hatfield-Dodds, Ben Mann, Dario Amodei,
Nicholas Joseph, Sam McCandlish, Tom Brown, Jared Kaplan
(Anthropic; 51 authors in total).
"Constitutional AI: Harmlessness from AI Feedback."
arXiv:2212.08073, submitted 15 Dec 2022.
https://arxiv.org/abs/2212.08073
DOI: https://doi.org/10.48550/arXiv.2212.08073

Read 2026-11-07 from the arXiv abstract page and secondary
method summaries of the full text. This is a study note, not a
replication — the lab ran no training and no model — so every
result below is the paper's, cited as such. Where a number comes
from a secondary summary rather than the paper text itself, that
is flagged in place.

## One-paragraph summary

Constitutional AI (CAI) trains a harmless assistant with **no
human labels identifying harmful outputs at all**. The only human
oversight for harmlessness is a short list of written principles —
the "constitution" (16 principles for the supervised phase and 16
for the RL phase, per the paper's appendix as summarised in
secondary sources). Training has two phases. In the supervised
phase the starting model — a helpful-only assistant with no
harmlessness training — answers red-team prompts, then critiques
its own answer against a randomly drawn principle, then revises
it; a pretrained model is fine-tuned on the revisions (SL-CAI).
In the RL phase, pairs of SL-CAI answers are compared by a
feedback model applying a randomly drawn comparison principle,
those AI preferences train a preference model, and the policy is
optimised against it — RL from AI Feedback (RLAIF), producing
RL-CAI. The headline result is a harmless-but-**non-evasive**
assistant: where the earlier human-feedback (HH RLHF) assistant
had learned to refuse or dodge controversial questions, RL-CAI
engages with harmful queries by explaining its objections, and
crowdworkers preferred it over assistants trained on previously
collected human harmfulness labels.

## Why the paper exists: the evasiveness problem

The direct predecessor is Anthropic's own "Training a Helpful
and Harmless Assistant" (Bai et al. 2022), which used human
preference labels (RLHF) for both helpfulness and harmlessness.
The CAI paper reports that assistant often refused controversial
questions and could get stuck giving evasive answers for the rest
of a conversation, because crowdworkers had rewarded evasiveness
as a response to harmful requests. CAI's design goal is therefore
not "refuse more" but "decline the harmful part while still
engaging and explaining."

The paper lists three further motivations, all worth recording
because they explain the method's shape:

1. **Scalable oversight** — use AI systems to help supervise
   other AI systems as capabilities grow.
2. **Explicit principles** — the behavioural goals live in a
   short, readable text that can be inspected and argued with,
   instead of being implicit in thousands of labeler judgements.
3. **Fast iteration** — changing the objective means editing
   principles and regenerating labels, not commissioning a new
   human labelling project.

## Phase 1 — supervised learning: critique, revise, fine-tune (SL-CAI)

- **Starting point matters.** The loop needs harmful first
  drafts to correct, so it starts from a helpful-only RLHF model
  that has *not* been trained for harmlessness.
- **Prompts.** Red-team prompts written to draw out harmful
  behaviour (the line of work from Ganguli et al.'s red-teaming
  data), plus ordinary helpfulness prompts used later to keep
  the model useful.
- **The loop, per prompt:** sample an initial answer → append a
  critique request drawn from the constitution and sample a
  self-critique → append the matching revision request and
  sample a revision. The loop can repeat, drawing a *different*
  random principle each time. One principle at a time is a
  design choice, not an oversight: the model sees each principle
  many times across training, and ensembling over principles
  made the later preference model more robust than using a
  single principle for every label.
- **Fine-tune.** A pretrained model is fine-tuned on the revised
  answers mixed with ordinary helpful answers, so the revisions
  do not destroy usefulness. The result is SL-CAI.
- **Honest caveats from the paper itself:** critiques were often
  inaccurate or overstated — a critique is a draft, not a
  verdict — and the first revision removed most of the harm,
  with later revisions giving smaller gains. Critiqued revisions
  scored more harmless than direct (no-critique) revisions for
  small models and made no noticeable difference for large ones;
  the critique step was kept anyway for transparency, because
  chain-of-thought-style reasoning makes the model's decision
  process inspectable.

## Phase 2 — reinforcement learning from AI feedback (RLAIF)

- SL-CAI writes **two** answers to each harmful/red-team prompt.
- A separate feedback model is shown the conversation, **one**
  randomly drawn comparison principle (of the form "choose the
  response that is more X"), and the two answers as a
  multiple-choice question. Its normalised probabilities for
  option A vs B become a **soft** preference label.
- **Soft labels mattered:** the paper found soft labels "led to
  much better results than hard labels" when no chain-of-thought
  was used. With chain-of-thought labelling the model usually
  commits to one answer, so probabilities were clamped to a
  40–60% range — without clamping, trained models learned to
  give more extreme responses.
- AI harmlessness labels are **mixed with human helpfulness
  labels**; a preference model (PM) is trained on the mix, and
  SL-CAI is fine-tuned with RL against that PM, exactly as in
  RLHF after the labelling step. Result: RL-CAI.
- **Scope honesty:** only the *harmlessness* labels came
  entirely from AI. Human feedback was still used for
  helpfulness. The authors' stated goal was to make human
  supervision "more efficient, transparent, and targeted" — not
  to remove humans from alignment.

## Results (all the paper's; crowdworker Elo comparisons)

- **Harmlessness vs helpfulness.** Figure 2 of the paper plots
  harmlessness against helpfulness Elo (from crowdworker model
  comparisons) for all its 52B RL runs: the Helpful-only and HH
  (human-feedback) models exhibit the expected
  helpfulness–harmlessness tradeoff, and the CAI models push
  past it — RL-CAI is preferred by crowdworkers over assistants
  trained with previously collected human feedback labels for
  harmfulness (abstract/introduction claim), i.e. *less harmful
  at a given level of helpfulness*.
- **Non-evasiveness.** The paper reports RL-CAI was "virtually
  never evasive" on red-team prompts, and evaluators were
  instructed to prefer the less evasive answer when two answers
  were equally harmless — evasiveness is counted as a failure
  mode in its own right, not as a safe default. (Wording via
  secondary summary of the paper's evaluation protocol.)
- **Model-size effects.** Figure 3 repeats the Elo comparison
  across model sizes; the ability of a language model to pick
  the better response on helpful/honest/harmless comparisons —
  the capability the whole feedback loop rests on — improved
  with model size and with chain-of-thought reasoning. CAI is
  therefore a method whose supervision quality scales with the
  supervisor model, for better and worse.
- **Over-training is real and was observed.** Pushing the policy
  too hard against the PM degraded real quality: over-trained
  RL-CAI models became overly harsh or appended boilerplate such
  as "you are valid, valued, and cared for" to most red-team
  answers. Rewriting principles to discourage over-reactive or
  accusatory answers helped. This is the paper's own instance of
  reward-model over-optimisation (cf. Gao, Schulman & Hilton on
  reward-model scaling laws).

## What the constitution was — and was not

- In the paper, each principle exists as instructions: a
  critique request, a revision request, and (for the RL phase) a
  comparison principle. Many were similar, general instructions
  to remove harmful, unethical, racist, sexist, toxic, dangerous
  or illegal content; others targeted specific areas such as
  advice for crime or content unsuitable for children. The
  authors describe the set as chosen "in a fairly ad hoc and
  iterative way for research purposes."
- **Do not conflate three different artefacts:** (1) this
  paper's 16+16 research principles; (2) the principles Anthropic
  published in May 2023 as the ones used to train Claude, drawn
  from sources such as the UN Declaration of Human Rights and
  Apple's terms of service; (3) the January 2026 Claude
  constitution, which explains the *reasons* behind the requested
  behaviour rather than listing standalone principles. Only (1)
  is this paper.
- A later variant worth one line: Collective Constitutional AI
  (Anthropic, Oct 2023) drafted principles with ~1,000 members of
  the American public and reported lower bias than the
  Anthropic-written constitution on nine social dimensions at
  equal helpfulness/harmlessness — evidence the *authorship* of
  the constitution is itself a variable, not a detail.

## Mapping to this lab

1. **CAI is the training-time member of a family this lab has
   only studied at prompt time.** TAXONOMY.md files StruQ /
   SecAlign as "training-based (studied in C5, NOT implemented —
   no fine-tuning run exists in this lab)"; CAI belongs in
   exactly that row, one level further from inference: B1's
   system-prompt hardening is a constitution-like principle list
   applied at *prompt* time, B4's output filter applies
   policy-keyword checks at *output* time, and CAI applies
   principles at *training* time so no runtime layer is needed.
   The lab's numbers for the prompt/output-time versions are
   upper bounds and small fixtures; the paper's are measured
   human-preference Elo at 52B scale. Do not compare them
   directly.
2. **The evasiveness failure is D3's ambiguous middle, at
   training scale.** D3 (2026-11-06) ended on the finding that a
   binary refusal label structurally erases *safe completions* —
   4 ambiguous safe completions split 2/2 under both classifiers.
   CAI is the same observation from the other side: a training
   signal that rewards bare refusal produces an evasive model,
   so the paper explicitly trains and evaluates for
   engage-and-explain instead. Any future lab refusal metric
   should carry an evasiveness / safe-completion axis alongside
   the refusal axis, or it will reward exactly the failure this
   paper was written to fix.
3. **Self-critique is a recognition problem, and this lab has
   measured recognition failing.** The SL loop only helps if the
   model can *recognise* what is wrong with its own answer.
   The lab's recurring cross-cutting finding (C3) is that
   recognition is the input-side ceiling: detector_v1 flags
   17/25 direct injections and 0/15 indirect ones. CAI's answer
   is scale plus principle-conditioned critique — the paper
   found critique quality and comparison accuracy improve with
   model size — which a CPU-scale lab cannot replicate; the
   honest local analogue is D5's red-team/blue-team loop, where
   the "critic" is the perplexity filter and its blind spots are
   already documented (A6: fluent and repetition suffixes evade
   it entirely).
4. **Soft, clamped preference labels are a transferable detail.**
   Independent of scale, two labelling choices in Phase 2 are
   directly reusable in any lab-built judge or classifier:
   use the judge's probabilities as soft targets rather than
   hard picks, and clamp over-confident chain-of-thought labels
   (the paper used 40–60%) before training on them. D3's keyword
   baseline collapsing to 0.250 on held-out families is the
   small-scale warning of what hard, over-confident labels do.
5. **What CAI does not address.** Nothing in the method defends
   the prompt/data channel: a CAI-trained model can still be
   prompt-injected, many-shot jailbroken (C8/D1 — and note Yuntao
   Bai is also an author of the many-shot paper), or attacked
   with gradient suffixes (A5/D6). Anthropic's own later
   Constitutional Classifiers (Feb 2025) — input/output
   classifiers trained on constitution-generated synthetic data —
   are an admission that training-time harmlessness alone does
   not close the inference-time attack surface this lab mostly
   studies. CAI and this lab's defenses are complements, not
   substitutes.

## Limitations and open questions

- **The supervisor is the ceiling.** Every label downstream
  comes from the principles as interpreted by the feedback
  model; where that model lacks expertise (clinical, legal) its
  labels will be confidently wrong. The paper checks comparison
  ability on its own task distribution, not in general.
- **Principles were ad hoc.** By the authors' own description
  the constitution was assembled iteratively for research; the
  paper does not ablate which principles carry the effect, and
  later work (specific-vs-general principles, Oct 2023) suggests
  the largest models can generalise from a single broad
  principle while detailed lists give finer control — the
  dose–response curve of "how much constitution" is still open.
- **Elo is a preference, not a safety guarantee.** All headline
  numbers are crowdworker pairwise preferences. A model can win
  Elo while remaining jailbreakable, and the paper makes no
  robust-refusal / ASR claim of the HarmBench kind (D2).
- **No public replication of the full pipeline at scale** exists
  in this lab's sources; open recipes (e.g. Hugging Face's
  Mistral-7B critique/revision + DPO version) report the
  self-critique step sometimes misses responses that break a
  principle — the recognition ceiling again.

## Sources

- Bai, Yuntao, et al. "Constitutional AI: Harmlessness from AI
  Feedback." arXiv:2212.08073, 15 Dec 2022.
  https://arxiv.org/abs/2212.08073
- Bai, Yuntao, et al. "Training a Helpful and Harmless Assistant
  with Reinforcement Learning from Human Feedback."
  arXiv:2204.05862, 2022. (The HH RLHF predecessor whose
  evasiveness motivated CAI.)
- Ganguli, Deep, et al. "Red Teaming the Mind of the GPT
  Language Models" / Anthropic red-teaming data, 2022 —
  source of the red-team prompt line used in Phase 1.
- Gao, Leo, John Schulman & Jacob Hilton. "Scaling Laws for
  Reward Model Overoptimization." arXiv:2210.10760, 2022 —
  the over-optimisation pattern the paper observes in
  over-trained RL-CAI.
- Anthropic. "Claude's Constitution." May 2023 —
  https://www.anthropic.com/news/claudes-constitution
  (the later production principles; NOT the paper's set).
- Anthropic. "Collective Constitutional AI." Oct 2023 —
  public-input variant cited above.
- Anthropic. "Constitutional Classifiers: Defending against
  universal jailbreaks." Feb 2025 — the inference-time
  successor cited in the lab mapping.
