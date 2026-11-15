# Paper notes: Constitutional Classifiers (v1) and Constitutional Classifiers++ (CC++)

## Papers
Mrinank Sharma, Meg Tong, Jesse Mu, Jerry Wei, et al. (Safeguards
Research Team, Anthropic).
"Constitutional Classifiers: Defending against Universal Jailbreaks
across Thousands of Hours of Red Teaming."
arXiv:2501.18837 (31 Jan 2025).
Link: https://arxiv.org/abs/2501.18837 (subjects: cs.CL, cs.AI, cs.CR).

Constitutional Classifiers++ paper (Anthropic; ICLR 2026 proceedings),
summarised in Anthropic's research post "Next-generation
Constitutional Classifiers" (9 Jan 2026).
Link: https://www.anthropic.com/research/next-generation-constitutional-classifiers

Read 2026-11-15 from the arXiv abstract/text of the v1 paper and
Anthropic's v1 and CC++ research posts.
**Study note, not a replication** — no classifier was trained or run
here; every number below is the papers'. CC++ figures are cited from
the ICLR 2026 paper as reported in Anthropic's post; where the two
generations' metrics are not the same quantity, this note says so
instead of tabulating them as one series.

## One-paragraph summary
Constitutional Classifiers defend a model against *universal
jailbreaks* — prompting strategies that reliably extract detailed
harmful content (the papers' target domain is CBRN) across most
queries — by placing trained classifiers on the model's input and
output. The classifiers are not trained on human-labelled attack
corpora: a natural-language *constitution* states which content
categories are permitted and which are restricted, an LLM generates
synthetic training data under that constitution (including
augmentations such as paraphrase, translation and jailbreak-style
rewrites, plus pools of benign data to hold false positives down),
and the classifiers learn the constitution's boundary. The output
classifier is *streaming*: it scores the harmfulness of the output
so far at each token, so generation can be halted mid-response.
Changing the threat model means editing the constitution and
regenerating data — days, not a new labelling programme. That
adaptability is the contribution; the classifiers themselves are
ordinary fine-tuned models (prototypes from Claude 3.5 Sonnet, the
evaluated generation from Claude 3.5 Haiku).

## Results (papers')

**v1 (Sharma et al. 2025), guarded Claude 3.5 Sonnet:**
- Automated evaluation, 10,000 synthetic jailbreak prompts:
  jailbreak success **86% unguarded → 4.4% guarded**.
- Human red teaming: >3,000 estimated hours (183 participants in the
  prototype phase); **no red teamer found a universal jailbreak** —
  defined strictly: extracting detail comparable to the unguarded
  model across *most* target queries. Individual harmful answers
  were obtained; the claim is about universality, and the paper
  states it that way.
- Cost, reported as headline numbers alongside the ASR: refusals on
  production traffic rose by an **absolute 0.38 percentage points**,
  and inference compute overhead was **+23.7%**. The 0.38% was not
  statistically significant on a 5,000-conversation sample — the
  paper reports the point estimate *and* its significance, which is
  itself part of the standard extracted below.

**CC++ (2026), production-grade system:**
- Architecture change, not just tuning: a cheap **linear probe on
  internal activations** screens all traffic; flagged exchanges
  escalate to a probe–classifier ensemble. (A two-stage cascade
  without probes already cut overhead 5.4× at similar robustness;
  adding probes reached the final figures.)
- Refusal rate on harmless production traffic: **0.05%** after one
  month of deployment on Claude Sonnet 4.5 traffic — an 87% drop
  from v1's system. Compute overhead: **~1%** (on Opus 4.0 traffic),
  i.e. >40× cheaper than the CC++ paper's own exchange-classifier
  baseline and ~24× cheaper than v1's +23.7%.
- Red teaming: >1,700 cumulative hours, 198,000 attempts; **one**
  high-risk vulnerability found (0.005 per thousand queries — a
  *rate per attempt*, not comparable to v1's 86%→4.4% automated ASR)
  and **no universal jailbreak**.
- Named residual attack classes in the CC++ work: *reconstruction*
  attacks (harmful content fragmented across individually benign
  segments) and *output obfuscation* (code words, metaphor). These
  are recorded as open, not solved.

## The deliverable this task requires: the cost/refusal reporting
standard, extracted for lab detectors

The reason this paper is on the lab's roadmap is not the classifier
— the lab trains nothing at this scale — it is that Sharma et al.
report a defense the way F1 (Nasr et al.) demands and most defense
papers do not: **robustness, benign cost, and compute cost as three
co-headline numbers, each with its measurement protocol stated.**
Extracted as a checklist, the standard is:

1. **Report the triple, always together.** (a) Attack success with
   vs without the defense on the *same* attack set (86% → 4.4%);
   (b) benign refusal/false-positive rate as an *absolute*
   percentage-point change on traffic-like benign data (v1: +0.38
   pp; CC++: 0.05% absolute); (c) compute overhead as a percentage
   of the undefended system's inference cost (v1: +23.7%; CC++:
   ~1%). No one of the three may appear without the other two.
2. **State the benign sample and its size, and the significance of
   small deltas.** v1's +0.38 pp comes with n = 5,000 and an explicit
   "not statistically significant." A benign set of 10 hand-written
   cases cannot support a refusal-rate claim at this resolution —
   it can only support "0/10 observed," labelled as such.
3. **Define the success criterion before the red-team number.**
   "Universal jailbreak" is defined (detail parity across most
   queries) *before* "none found in 3,000 hours" is claimed; hours
   and attempt counts are both reported (CC++: 1,700 h / 198,000).
   A red-team result without the criterion and the budget is
   marketing, per F1's ladder.
4. **Report the adaptive budget as part of the result.** Both
   generations were tested by defense-aware humans at stated scale,
   and the surviving attack classes are *named* (reconstruction,
   obfuscation) rather than folded into an aggregate ASR.
5. **Version the numbers.** v1's 23.7% / 0.38% and CC++'s ~1% /
   0.05% are different systems on different traffic; the CC++ post
   never silently substitutes the new figures for the old system's.
   (This lab does the same for CaMeL's v1/v2 utility in F2.)

**Applied to this lab's detectors — the honest current state:**

| Lab detector | ASR/detection reported | Benign cost reported | Compute cost reported | Gap vs the standard |
|---|---|---|---|---|
| A4 detector_v1 | 17/25 flagged on A2 (static) | 0/10 FP on 10 hand-written benign cases | Not measured (regex; negligible but unstated) | Benign n=10 supports no rate claim; no adaptive budget |
| A6 perplexity filter | AUROC 0.887 windowed (static) | FP read off ROC at stated thresholds vs 10 benign | distilgpt2 scoring cost never timed/reported | Cost column empty; E3 inherited this |
| B4 output filter | 13/15 compromised blocked | 0/15 FP | Not measured | Same as A4 |
| D3 refusal classifier | 0.771 family-held-out accuracy | Reported as accuracy, not refusal-rate delta | Not measured | Metric shape differs from the standard's |
| E3 flagship pipeline | S1 supported; P1–P3 BLOCKED | Benign reference medians reported | Not measured | Closest to the standard on (a)/(b); (c) still missing |

**Lab rule adopted (proposed here, binding on future lab reports
from F4 onward):** every detector or defense report in this repo
must carry the triple — attack result, benign cost with its sample
size, and a compute-cost statement (a measured timing, or the
explicit sentence "compute cost not measured") — and must name its
attacker model per F1. Existing reports are *not* retro-edited; the
table above is their gap record.

## What the classifiers do not settle (limits)

- **The robustness claim is human-budget-relative.** "No universal
  jailbreak in 3,000 hours" is an L3 result at a stated budget
  (F1's ladder), not a proof; CC++'s one high-risk vulnerability is
  the honest remainder. F1's finding that detector-style defenses
  fall to score-feedback search at >90% ASR applies to *standalone*
  detectors evaluated statically — the CC systems' defence is
  precisely that they were *not* evaluated only statically.
- **Scope is one constitution.** Both generations target CBRN
  detail. Nothing here measures prompt injection, agent tool misuse,
  or the lab's A2/B5 channels; importing the ASR numbers across that
  boundary would be the category error F2 flagged for CaMeL.
- **Synthetic-data boundary risk.** A classifier trained on
  constitution-generated data inherits the generating model's idea
  of the boundary; reconstruction/obfuscation attacks live exactly
  in the gap between that idea and the constitution's text.
- **Production-traffic numbers are not reproducible here.** The
  refusal rates are measured on Anthropic's real traffic mix; the
  lab can adopt the *reporting shape*, never the figures.

## Consequences for the lab

1. **E4's preprint claims ledger gains a cost column.** Every claim
   row that cites a lab detector must now also cite its benign-cost
   and compute-cost status from the table above — including
   "not measured," stated in the paper rather than omitted.
2. **F7/F8 inherit the triple directly.** The output-filter v2 and
   the 3-way refusal metric are the next two detector-building tasks
   on this roadmap; both reports must ship with the triple and a
   benign set large enough to state a rate, or label the rate as
   unresolvable at their n.
3. **For the flagship:** perplexity filtering is a detector in
   Nasr's §5.3 sense and in Sharma's sense; the preprint's defense
   of it must therefore read like a CC report — frozen thresholds,
   benign cost with n, scoring cost timed — or expect the F1
   objection in review.
