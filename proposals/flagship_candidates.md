# Flagship candidates — three research questions for the lab's first paper

**Date:** 2026-11-11 (Day 29 of the daily lab)
**Task:** E1. **Status:** candidates with a recommendation — the choice itself
is E2's starting point (dataset spec for the *chosen* question) and, on the
goal's monthly plan, the January 2027 milestone. Nothing here is a result:
no new experiment was run for this document. Every lab number cited is from
its committed Month-1 report, via the D7 retrospective
(`notes/month_1_retro.md`).

---

## 0. How these candidates were chosen

D7 handed E1 exactly three seeds, each rooted in a measured Month-1 gap —
not in a topic that merely sounds current:

| Seed (D7 §6) | Month-1 evidence behind it |
|---|---|
| 1. Windowed perplexity vs fluency-optimised suffixes | A6 windowed AUROC 0.887 on gibberish suffixes; D5's windowed layer caught all 3 hill-climbed finals — but D5's optimiser never targeted the windowed score, and D6 showed fluent/amortised attacks are built to sit at natural-text perplexity |
| 2. Clean-task cost of structural defenses, measured as task accuracy | C3's cost column is proxies only (exact recovery, two 10-case benign sets); C6 measured Q3's lossy filter altering 5/5 format-bearing benign docs; StruQ never reported this cost at all |
| 3. Known-answer detection, tuned on A2, tested untouched on B5 | The one defense family in C1's taxonomy the lab never tried; detector_v1's threshold failed to transfer direct → indirect (17/25 flagged on A2, 0/15 on B5) because a lone instruction family caps at 0.40 under its normalisation |

**Selection criteria** (applied in §4): (a) falsifiable with a pre-registered
prediction; (b) runnable on this lab's actual resources — CPU, distilgpt2,
hand-built suites, no GPU, no live aligned model, nights/weekends scale;
(c) a negative result is publishable information, not a dead end;
(d) it closes a gap the lab itself measured, so the paper's motivation is
the lab's own data; (e) it is not already answered by the 2025–26 field
(see §5).

**The constraint every candidate must live with** (D7 §4, stated once here
rather than repeated per candidate): Month 1 evaluated *no live aligned
model* — every defense number is a detector measurement or an ideal-follower
simulation upper bound. A flagship that secretly depends on live-model ASR
would break the lab's labelling rule. Each candidate below states exactly
how it handles this: Candidates 1 and 3 are detector studies by design
(their claims are about the detector, not about a model); Candidate 2 is
the one that needs a task-performing model, and its design says so openly
and scopes its first phase to what can be measured without one.

---

## Candidate 1 — Does windowed perplexity survive fluency-optimised suffixes?

**Research question.** A6/D5's windowed-perplexity layer separated
2023-style gibberish suffixes from benign text (windowed AUROC 0.887) and
caught suffixes hill-climbed against the *full-text* score. Does it still
separate suffixes that were *optimised for fluency* — the published
AmpleGCG corpus and fluency-objective attacks surveyed in D6 — from benign
text, when scored with the same distilgpt2 pipeline, unchanged?

**Why the lab, why now.** This is the lab's single most load-bearing
unexamined assumption. Two committed results lean on the windowed score
(A6's headline AUROC; D5's "the windowed layer held"), and D6's synthesis
already predicts the scoping problem: *perplexity is a property of the
optimiser, not the attack class.* AmpleGCG (Liao & Sun, 2024) is the ideal
test case precisely because its authors already probed perplexity defenses
from the attack side — they report that repeating the harmful query at
inference time lets their suffixes evade perplexity-based defenses at 80%
ASR — but that is a whole-prompt perplexity claim against their target
models, not a windowed-score measurement on a fixed public corpus with a
frozen benign reference set. That specific measurement does not exist in
the lab or, from D6's survey, in the cited follow-ups.

**Pre-registered predictions** (to be frozen in E2 before any scoring):
- **P1.** Windowed AUROC on fluency-optimised suffixes vs the A6 benign set
  will be materially below A6's 0.887 gibberish figure — predicted range
  0.55–0.75. If it lands ≥ 0.85, the windowed layer is stronger than D6's
  synthesis implies and that is the headline instead.
- **P2.** The repetition trick will again be the cheapest evader: repeated-
  query suffix variants will score *below* the benign median windowed PPL,
  replicating A6's suf-07/08 pattern (PPL 4.1 / 6.8) on a published corpus.
- **P3.** No single windowed threshold will simultaneously keep benign
  false positives ≤ 1/10 and catch ≥ half the fluency-optimised suffixes —
  i.e. the failure, if it comes, is distributional overlap, not a badly
  chosen threshold (check by reporting the full ROC, not one operating
  point).

**Method sketch.** Reuse `eval/perplexity_filter.py`'s scoring exactly
(same model, same window, same benign set — comparability with A6/D5 is
the point). Score: (i) a documented sample of published AmpleGCG suffixes,
(ii) D5's committed suffix rows as an internal control (must reproduce
D5's windowed values before any new number is trusted — the C4
recompute-don't-transcribe rule), (iii) the A6 benign + natural-injection
sets as the reference distributions. Report full-text and windowed AUROC
per family, per-case rows as JSONL, and the threshold analysis for P3.
Family-held-out discipline is automatic here: no threshold is tuned on
the fluency corpus and then reported on it.

**Data needed (E2 spec).** The AmpleGCG authors' public suffix artefacts
(code/data at the project's GitHub, linked from the paper), with the exact
sample, version and selection rule written into the spec *before*
downloading; A6/D5 committed rows (already in-repo). No new hand-written
attack data — using a published corpus is what makes the result checkable
by others.

**Feasibility.** Highest of the three. All scoring is distilgpt2 on CPU —
the A6/D5 pipeline already runs at this scale (126 + 72 rows in prior
tasks). No model behaviour is claimed: the claim is about a *detector's*
separability, which is exactly what the lab can measure honestly today.

**Risks / what a negative result means.** The main risk is artefact
access: if the published corpus cannot be obtained in a documented,
versioned form, the candidate degrades to locally generated fluent
suffixes — which D5 already showed are word salad (median PPL 423.0),
not fluency-optimised, so that fallback must be labelled a different,
weaker experiment, not silently substituted. A negative result (P1–P3
supported) is the expected-value outcome and is still a clean paper:
"the windowed layer that held against a full-text optimiser does not
separate fluency-optimised suffixes" scopes every perplexity claim in
the lab and, by extension, any defense citing A6-style numbers.

**Paper shape.** Short empirical paper / workshop submission: one
detector, one published attack corpus, one frozen benign reference,
three pre-registered predictions. This is the D7 §7 plan's natural first
preprint.

---

## Candidate 2 — The clean-task cost of structural defenses, measured as task accuracy

**Research question.** B2/B6/C6's structural front-ends (spotlighting,
RAG delimiting/datamarking, the StruQ-style filter) tie or saturate on
attack suites and are separated only by escape probes. What do they cost
on the *clean* task — measured as whether the underlying task is still
done correctly — and does the ranking change once that cost is on the
table, in particular for C6's Q3, whose repeated filter is the only
variant that blocked 13/13 completion attacks but is *lossy* on benign
documents that legitimately contain `##` headings, Alpaca format, or
reserved-token vocabulary (5/5 altered, 48 chars removed in C6)?

**Why the lab, why now.** C1 flagged that published defense evaluations
report blocked rates without a PNA-style clean-task cost; C3 could only
fill that column with proxies; C5 noted StruQ itself never measures what
its filter deletes from clean data; C6 measured the deletion but not its
*task consequence* (key facts survived 10/10 — but "facts survive" is a
human judgement on 5 documents, not a task score). Nobody in the lab's
nine-paper index reports task accuracy under these front-ends on a
shared task set. That is a genuine, citable gap — and it is the
question a practitioner actually asks before deploying any of them.

**Pre-registered predictions:**
- **P1.** Exactly-invertible transforms (B2 datamarking/delimiting, B6
  variants) will cost ~0 task accuracy on extraction-style tasks *when
  the reader is the lab's deterministic extractor* — i.e. their C3 proxy
  cost of ~0 will survive a real task measure at this scale.
- **P2.** Q3-style lossy filtering will cost measurable accuracy
  specifically on the format-bearing subset (documents whose answers
  live inside `##` sections or delimiter-shaped text), and ~0 elsewhere —
  the cost is concentrated, not uniform.
- **P3.** The defense ranking by (blocked, task-cost) will differ from
  the ranking by blocked alone: at least one variant that ties on
  attacks will separate on cost.

**Method sketch.** Build a small clean-task set where success is
checkable without a judge model: extractive QA / field extraction over
documents (answer = exact string or field value in the document),
summarisation-key-fact checklists scored by exact key-fact presence
(the C6 method, scaled and pre-registered), and instruction-following
tasks with programmatic checks. Run each document through each
front-end transform (B2 S1–S5, B6 R2–R5, C6 Q1–Q3 — code already
committed) and score task success on the transformed input with a
deterministic reader; report cost per defense × document-type, with the
format-bearing subset pre-declared. Phase 2 (only if a suitable small
open instruction model becomes runnable within the lab's CPU budget)
repeats the measure with a real reader model and is labelled as such;
Phase 1 makes no live-model claim.

**Data needed (E2 spec).** A new clean-task dataset — this is the
heaviest E2 of the three: ~40–60 documents across plain / formatted /
delimiter-bearing types, each with a programmatic success check, plus
the format-bearing subset designed *before* results are seen. The
dataset itself is a deliverable (the lab's first clean-task suite).

**Feasibility.** Medium. Transforms and scoring patterns exist; the
dataset design is real work (this is what E2 is for) and Phase 1's
deterministic reader bounds the claim: it measures information loss
through the transform, not a deployed model's confusion. That bound
must be in the paper's abstract, not its footnotes.

**Risks / what a negative result means.** If P1–P3 all fail — every
front-end costs ~0 even on format-bearing documents — the result is
still useful (it retires the lab's own C5/C6 worry with data), but it
is a weaker paper than Candidate 1's expected result, because "the
cost is negligible at this scale" invites the correct objection that
the scale is the lab's, not production's.

**Paper shape.** Empirical paper with a released dataset + harness:
defense × cost matrix on a shared clean-task suite. The dataset is the
durable contribution even if the headline is null.

---

## Candidate 3 — A detector that transfers: known-answer detection across the direct/indirect channel boundary

**Research question.** Every input-side detector the lab has built
thresholds *instruction-likeness*, and that threshold failed to transfer
from direct to indirect injection (detector_v1: 17/25 on A2 → 0/15 on
B5). Known-answer detection — identified in C1 as the one benchmarked
defense family in Liu et al.'s taxonomy that this lab has never tried —
works differently: the defender plants a secret instruction with a
known answer in the trusted channel and checks whether the output
contains it; an injected instruction that hijacks the task displaces
the known answer. Does a known-answer scheme, tuned *only* on the A2
direct suite, detect B5's indirect attacks *untouched* — and vice
versa?

**Why the lab, why now.** The transfer failure is the lab's cleanest
cross-cutting negative result (C7 failure mode 4), and this is the only
candidate whose success criterion is cross-channel *by construction*:
the evaluation protocol (tune on one suite, freeze, test on the other,
both directions) is the contribution as much as the detector. It also
directly tests a mechanism claim: if detection-by-displacement escapes
the threshold-transfer failure, the failure was about the *signal*
(instruction-likeness), not about cross-channel detection in principle.

**Pre-registered predictions:**
- **P1.** Known-answer detection will flag materially more than
  detector_v1's 0/15 on B5 when its parameters are frozen from A2 —
  predicted ≥ 8/15 — because B5's attacks must displace the task (and
  hence the planted answer) to succeed at all.
- **P2.** The reverse direction (tune on B5, test on A2) will be worse:
  A2's roleplay/encoded families can comply with the injected
  instruction *and* retain surface task behaviour more often than B5's
  document-channel attacks can. Predicted A2 detection ≤ B5 detection
  under the frozen cross-channel protocol.
- **P3.** Benign cost will be non-zero and measurable on the lab's
  benign sets (the planted instruction consumes output space) — report
  it alongside detection, per the C3 cost-column rule; a candidate that
  hides its benign cost is rejected by the lab's own standard.

**Method sketch.** Implement known-answer detection in the harness in
the lab's established simulation-honest way: a deterministic
task-executor stand-in follows the highest-priority instruction it can
recognise in the assembled prompt (the same ideal-follower machinery as
B1/B2/B6/C6, labelled an upper bound), with the planted known-answer
instruction in the system channel. Detection = the known answer is
absent/displaced in the executor's output. Tune the scheme's few
parameters (planted-instruction phrasing family, answer format) on one
suite, freeze them in a committed config, then evaluate untouched on
the other suite; repeat in the reverse direction. Per-case JSONL rows,
suites never averaged (C3 rule).

**Data needed (E2 spec).** No new attack data: A2 (25) + B5 (15) +
benign sets (10 + 10) already exist and are validated. E2 specifies the
planted-instruction families, the freeze protocol, and the executor's
recognition rules — the protocol document *is* the spec.

**Feasibility.** High on effort (reuses suites and simulation
machinery), but the validity risk is the highest of the three: the
result lives or dies on whether the ideal-follower executor's
"displacement" behaviour is a fair stand-in, and a sceptical reader
can reasonably say the simulation assumed the conclusion (an executor
that follows only one instruction guarantees displacement). The design
must therefore include the partial-compliance cases (executor follows
the injected instruction *and* emits the known answer) as a scored
category, not an afterthought — C6's Completion-Other "parser blind
spot, not safety" episode is the lab's own warning about exactly this.

**Risks / what a negative result means.** If P1 fails, the transfer
failure generalises beyond threshold detectors — a strong negative
result, but one whose simulation caveat will draw the most scrutiny of
the three candidates. If the simulation caveat cannot be made
airtight, this candidate's paper is the hardest to defend in review.

**Paper shape.** Methods/protocol paper: a cross-channel transfer
protocol for injection detectors + the first known-answer instance
run under it. The protocol outlives the detector either way.

---

## 4. Comparison and recommendation

| | C1: Windowed PPL vs fluent suffixes | C2: Clean-task cost | C3: Known-answer transfer |
|---|---|---|---|
| Falsifiable, pre-registered | Yes (P1–P3, numeric ranges) | Yes (P1–P3) | Yes (P1–P3, numeric) |
| New data needed | Published corpus (external) | New clean-task suite (heaviest E2) | None (protocol only) |
| Live model needed | No — detector study | Phase 1 no; Phase 2 optional | No — simulation, labelled |
| Reuses committed code | A6/D5 pipeline directly | B2/B6/C6 transforms | B1/B2/B6 simulation machinery |
| Negative result value | High — scopes a whole defense class | Medium — null invites scale objection | High, but caveat-exposed |
| Main risk | Corpus access/versioning | Dataset design effort | Simulation-validity objection |
| Field position (§5) | Perplexity layers still widely cited as a first defense; no windowed measurement on a fluency corpus | Cost-reporting gap acknowledged field-wide post-Nasr et al. | Known-answer is a 2023-era family; transfer protocol is the novel part |

**Recommendation: Candidate 1 as the flagship, Candidate 3 as the
parallel methods thread, Candidate 2's dataset as the E2 deliverable
if Candidate 1's corpus access fails.**

Reasoning, in the lab's own terms: Candidate 1 is the only one where
(a) the motivating gap is a number *this lab published* (windowed
AUROC 0.887) whose scope D6 already questioned, (b) the measurement
needs nothing the lab does not already run, (c) the external artefact
(a published attack corpus) makes the result independently checkable,
and (d) both outcomes are informative — the pre-registration habit
that made D1/D5's failures believable is worth the most exactly here.
Candidate 3 is the best *second* paper because its protocol is cheap
to run once Candidate 1's infrastructure habits are in place, and its
risk (simulation validity) can be retired by design work in E2 rather
than by compute. Candidate 2 asks the most practically important
question and builds the most durable asset (a clean-task suite), but
its E2 is the heaviest and its Phase-1 claim is the most bounded —
it is the right *second-cycle* flagship, and its dataset spec should
be written regardless, because every future defense task in this lab
needs a clean-task measure (D7 §7 already requires one before E3
baselines for whichever question is chosen).

**Decision requested (for E2):** confirm Candidate 1, or override with
2 or 3 — E2 then writes the dataset/protocol spec for the chosen one
only, including its pre-registered predictions frozen verbatim.

---

## 5. Where the field has moved (2025–26) — and why none of it answers these questions

Surveyed 2026-11-11 for this proposal and for the roadmap extension
appended in the same commit (Section F). The field's centre of gravity
has shifted from prompt-time filters to *architecture and adaptation*:

- **Adaptive evaluation is now the standard a defense must survive.**
  Nasr et al., "The Attacker Moves Second" (2025), bypassed 12 recent
  jailbreak/prompt-injection defenses with attack success above 90%
  for most — the majority had originally reported near-zero ASR —
  using attackers who knew the defense and adapted (gradient descent,
  RL, random search, human-guided exploration, on AgentDojo among
  other benchmarks). Lesson for this lab: any flagship claim must state
  its attacker model; all three candidates above are detector/cost
  studies whose claims do not require beating an adaptive attacker,
  and say so.
- **Architectural defenses** separate control from data flow rather
  than asking the model to behave: CaMeL (Debenedetti et al., 2025,
  arXiv:2503.18813) extracts control/data flow from the trusted query
  and enforces capability policies around the model, solving 77% of
  AgentDojo tasks with provable security vs 84% undefended. The lab's
  B2/B6/C6 front-ends are prompt-time cousins of this idea without the
  enforcement layer — Candidate 2's cost question applies to CaMeL-
  style systems too, and CaMeL's own 77-vs-84 gap is a utility-cost
  number of exactly the kind Candidate 2 would measure systematically.
- **Re-execution defenses**: MELON (Zhu et al., ICML 2025,
  arXiv:2502.05174) detects indirect injection by re-running the agent
  with the user request masked and comparing tool calls — detection by
  *behavioural divergence*, a relative of Candidate 3's detection by
  *answer displacement*, and (per the adaptive-attack results above)
  itself bypassed once the attacker knows the design. That strengthens
  Candidate 3's framing: the open question is not whether one scheme
  wins, but whether *any* displacement/divergence signal transfers
  across channels under a frozen protocol.
- **Model-level defenses have gone open-weight**: Meta SecAlign
  (2025, arXiv:2507.02735) releases an open model trained with the
  SecAlign recipe (the StruQ successor line this lab studied in C5),
  reporting commercial-grade robustness with comparable utility. For
  this lab it changes feasibility, not the questions: a small
  SecAlign-family model is the first realistic "real reader" for
  Candidate 2's Phase 2 and the first aligned model the lab could
  honestly report ASR against (roadmap F5/F9 pick this up).
- **Classifier defenses at production scale**: Anthropic's
  Constitutional Classifiers (Sharma et al., 2025) cut jailbreak
  success from 86% to 4.4% on 10,000 synthetic attacks at 23.7%
  compute overhead; the ++ generation (2026) reports ~1% overhead and
  a 0.05% refusal rate on production traffic, with exchange classifiers
  and reconstruction/obfuscation attacks as its named residual
  failures. The lab's D3/D4 line (refusal classification, evasiveness)
  is the small-scale study version of this — and its cost/refusal
  reporting is the standard Candidate 3's P3 adopts.

None of these answer Candidate 1 (no windowed-perplexity measurement
on a published fluency-optimised corpus), Candidate 2 (no shared
clean-task cost matrix for structural front-ends), or Candidate 3
(no frozen cross-channel transfer protocol for detectors). The
candidates survive the survey unchanged; the survey instead adds
Section F's reading and replication tasks so the lab's *next* cycle
works with the field's current instruments (AgentDojo-style stateful
tasks, adaptive attackers, an open aligned model) instead of only its
own hand-built suites.

---

## Sources

Lab-internal evidence is cited by task ID throughout and lives in this
repo (`results/`, `notes/`, `TAXONOMY.md`, ROADMAP lines A1–D7).
External sources for §5 and the candidates:

- Liao, Z. & Sun, H. (2024). "AmpleGCG: Learning a Universal and
  Transferable Generative Model of Adversarial Suffixes for
  Jailbreaking Both Open and Closed LLMs." arXiv:2404.07921.
  https://arxiv.org/html/2404.07921v1 — near-100% ASR sampling ~200
  suffixes; perplexity-defense evasion via query repetition at 80% ASR
  (paper's numbers, §1).
- Nasr, M. et al. (2025). "The Attacker Moves Second: Stronger Adaptive
  Attacks Bypass Defenses Against LLM Jailbreaks and Prompt
  Injections." arXiv:2510.09023. https://arxiv.org/html/2510.09023v1 —
  12 defenses bypassed, ASR > 90% for most, vs near-zero originally
  reported (paper's abstract).
- Debenedetti, E. et al. (2025). "Defeating Prompt Injections by
  Design" (CaMeL). arXiv:2503.18813 — 77% of AgentDojo tasks solved
  with provable security vs 84% undefended (paper's abstract, via the
  authors' PDF).
- Zhu, K. et al. (2025). "MELON: Provable Indirect Prompt Injection
  Defense via Masked Re-execution and Tool Comparison." ICML 2025,
  arXiv:2502.05174. https://borowiecki.dev/pdf/2502.05174v3
- Chen, S. et al. (2025). "Meta SecAlign: A Secure Foundation LLM
  Against Prompt Injection Attacks." arXiv:2507.02735.
  https://ar5iv.labs.arxiv.org/html/2507.02735
- Sharma, M. et al. (2025/2026). "Constitutional Classifiers" and
  "Constitutional Classifiers++: Efficient Production-Grade Defenses
  against Universal Jailbreaks." arXiv:2601.04603.
  https://arxiv.org/html/2601.04603v1 — 86% → 4.4% (v1, 10,000
  synthetic attacks, 23.7% overhead); ++ at ~1% overhead, 0.05%
  refusal rate, 1,700+ red-team hours with no universal jailbreak
  (papers' abstracts/reporting).
- Background already in the lab's index (`TAXONOMY.md`): Zou et al.
  2023 (GCG, arXiv:2307.15043); Liu et al. 2023 benchmark
  (arXiv:2310.12815 — known-answer detection's source taxonomy);
  Hines et al. 2024 (spotlighting, arXiv:2403.14720); Chen et al.
  2024/2025 StruQ/SecAlign (arXiv:2402.06363 / arXiv:2410.05451).

*Honesty note: §5's numbers are the cited papers' own reported figures,
reproduced as claims about what those papers report — the lab has
replicated none of them. Cross-paper ASR comparisons are not made
anywhere in this document, per the D6 rule.*
