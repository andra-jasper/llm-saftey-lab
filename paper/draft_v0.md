# Does Windowed Perplexity Survive Amortised Suffixes? — Draft v0

**A Frozen Pipeline, an Unobtainable Corpus: Pre-Registration and
Reproducibility Notes for Perplexity-Defense Evaluation**

*Draft v0 — 2026-11-17. ROADMAP task G2. This is a working draft,
not a submission. Every empirical claim is checked against the E4
claims ledger (`paper/outline.md` §4); the ledger check is appended
as §9. While the AMP arms stay blocked, this draft makes no
AmpleGCG claim of any kind (ledger C5).*

Author: Jasper Andra (independent researcher; MS Cybersecurity —
AI emphasis, Webster University, 2024–2026). Lab repository:
`andra-jasper/llm-saftey-lab` (public).

---

## Abstract

Perplexity filtering is among the most-cited baseline defenses
against adversarial suffix attacks on large language models, and
its windowed variant carries the strongest separation reported in
small-scale replications — in our lab, a windowed AUROC of 0.887
for hand-written gibberish suffixes against benign text. That
number, however, was produced against suffixes from a different
generator distribution than modern amortised attacks use, and the
most-cited evasion of the whole-prompt score — repetition
dilution — was never evaluated against the windowed score. We
pre-registered three predictions with frozen verdict bands,
froze the detector pipeline, benign reference set and corpus
selection rule, and ran the baseline. The pipeline reproduces its
own reference numbers exactly and reproduces an earlier
optimisation result under rescoring; dilution is shown to be a
full-text phenomenon that a max-window statistic structurally
resists, on lab-generated suffixes; and the primary test arms are
reported BLOCKED, because the amortised-suffix corpus the
question turns on is not published in obtainable form. We argue
the blocked corpus is itself a finding: a defense-relevant
artefact gated behind verified-organisation requests cannot be
independently re-measured by the small labs where replication
capacity lives. This is a study of a detector, not of any model's
jailbreak resistance; no attack success rate is measured or
claimed anywhere in this paper.

## 1. Introduction

A perplexity filter scores an input with a small language model
and flags inputs whose perplexity is abnormally high (Jain et al.
2023). Gibberish adversarial suffixes of the kind produced by
gradient-based search (Zou et al. 2023) are unnatural text, so
they should score far above ordinary prompts. The windowed
variant — the maximum perplexity over short sliding windows —
exists because a short suffix attached to a long fluent prompt is
diluted in the whole-text average.

Two gaps in the evidence for this defense motivate this paper.
First, the *generator-distribution gap*: headline separation
numbers (ours included) are measured on hand-written or
hand-assembled gibberish, while deployed attacks increasingly use
amortised generators that learn a suffix distribution (Liao &
Sun 2024). A detector number is a statement about a suffix
distribution, and the distribution has changed. Second, the
*dilution gap*: the AmpleGCG paper's anti-perplexity construction
(repeating the request so the suffix's contribution to the
whole-prompt average shrinks; reported 80% attack success under a
whole-prompt detector — the paper's figure, ledger C7) was never,
to our knowledge, evaluated against the windowed score it
structurally should not fool.

Our contributions, in order: (i) a pre-registered protocol with
frozen verdict bands for a detector-separability question,
registered before any flagship scoring; (ii) an end-to-end
reproduction gate — the pipeline must recompute its own earlier
reference numbers exactly, and reproduce an earlier result under
rescoring, before any new measurement is trusted; (iii) a
dilution dose–response showing the mechanism's scope; and (iv) a
blocked-corpus reproducibility report, because the primary arms
could not be scored: the corpus is not published, and we report
that as a first-class result rather than substituting a
convenient corpus and answering a different question.

## 2. Related work

Jain et al. (2023) introduce the perplexity and windowed
perplexity filters this paper evaluates. Zou et al. (2023)
introduce GCG and the AdvBench behaviours from which suffix
corpora are built. Liao & Sun (2024) introduce AmpleGCG, which
learns a generative model of GCG-style suffixes; we record a
framing correction our own pre-registration process caught:
AmpleGCG suffixes are amortised *gibberish*, not
fluency-optimised — the paper's actual anti-perplexity mechanism
is repetition dilution, and any evaluation designed around
"fluent suffixes" would have tested the wrong property.
AmpleGCG-Plus (Kumar et al. 2024) post-dates and supersedes parts
of that line; it is a different corpus and not a substitute for
the frozen one. Nasr et al. (2025) show that adaptive,
defense-aware attackers bypass most published prompt-injection
defenses at high rates, which is why every number in this paper
is labelled with its attacker model: all of ours are fixed-suite
(L0) or small-budget search (L2) statements, never "robustness"
claims. Design-based and training-based alternatives — CaMeL
(Debenedetti et al. 2025), MELON (Zhu et al. 2025), Meta SecAlign
(Chen et al. 2025) and Constitutional Classifiers (Sharma et al.
2025) — enforce or learn separation by mechanisms whose cost and
robustness reporting this paper's protocol borrows; none of them
answers the separability question asked here.

## 3. Method

**Frozen pipeline.** The scorer is distilgpt2 on CPU. Each input
receives two scores: full-text perplexity and the maximum
perplexity over 10-token sliding windows. The scoring functions
are imported unchanged from the lab's original filter
implementation; no threshold, window size, model or benign-set
change was permitted after freezing (gate G4).

**Frozen reference arms.** The benign reference (n = 10), natural
injection set (n = 25) and hand-written synthetic suffix set
(n = 15) from the original filter study are reused as committed
scores, never rescored. Their reference values: benign full-text
median 73.2, windowed median 609.1; synthetic suffix full-text
median 370.5, windowed median 7989.5; windowed AUROC of synthetic
suffixes vs benign 0.887 (ledger C1).

**Arms and gates.** The full design has 7 arms and 159 planned
manifest rows, including the two AmpleGCG arms (AMP-PRIMARY,
AMP-REP) under a frozen selection rule (first 25 queries in file
order × first 2 successful suffixes). Two gates precede any new
measurement: G1, exact recomputation of the reference numbers
from the committed rows; G2, exact rescoring of an earlier
hill-climb result. Predictions P1–P3 carry verdict bands fixed
before scoring (P1: supported ≤ 0.79, refuted ≥ 0.85, for the
AMP-PRIMARY windowed AUROC). A secondary prediction, S1, tests
dilution directly on lab suffixes: repeat the base request
j = 1, 2, 4 times and track both scores. All AUROCs carry
1,000-resample bootstrap 95% confidence intervals; with benign
n = 10 the intervals are wide by construction, and no conclusion
rests on a difference smaller than its interval.

**What was frozen when.** Predictions: 2026-11-11. Verdict bands,
arm definitions and selection rule: 2026-11-12. Baseline scoring:
2026-11-13. This draft: 2026-11-17.

## 4. Results

**Gates.** G1 PASS: every reference number recomputes exactly
from the committed rows. G2 PASS: all three earlier hill-climb
final suffixes rescore with windowed perplexity matching their
committed values exactly (7293.31, 1778.52, 1339.49; delta 0.00),
each above the 609.1 benign windowed reference line (ledger C2).
The measurement apparatus is therefore verified end-to-end before
the results below are read.

**S1 — dilution dose–response (lab suffixes only).** Repeating
the base request collapses the full-text score monotonically —
medians 370.5 (j = 1) → 159.8 (j = 2) → 32.5 (j = 4), a 91.2%
fall — while the windowed median does not move at all: 7989.5 at
every repeat factor, with per-case windowed scores identical
across j, because the maximum window sits inside the undiluted
suffix. At j = 4 the full-text AUROC falls to 0.107 while the
windowed AUROC stays 0.887. S1 is SUPPORTED, as a statement about
the dilution *mechanism* in this detector, on lab suffixes
(ledger C3). It is not evidence about AmpleGCG suffixes and is
never reported as such.

**P1–P3 — BLOCKED / UNANSWERED.** The AmpleGCG paper publishes no
static suffix corpus: suffixes are shared with verified
organisations on request, and the released generator checkpoints
are 7B models outside this lab's CPU envelope (ledger C4). Per
the frozen spec, the AMP arms are marked BLOCKED — not
substituted. No suffix was harvested from paper tables or
third-party re-uploads, and no P1–P3 verdict other than BLOCKED
may be stated (ledger C5).

**Adaptive context (fixed suites are upper bounds).** A companion
lab study red-teamed the lab's structural front-end defenses
with a defense-aware random search (budget 24 mutations per
case, simulation-level oracle): fixed-delimiter and datamarking
configurations that blocked 25/25 and 15/15 fixed-suite cases
fell to 0 blocked under adaptive search, while random-token and
combined configurations held at full block rates. We cite this
only to scope the present paper's numbers the way Nasr et al.
(2025) require: a fixed-suite detector AUROC — including 0.887 —
is an upper bound on defense strength under an attacker who does
not adapt to the detector, and a lower bound on nothing.

## 5. Discussion

The windowed statistic buys exactly one thing: a max over windows
cannot be averaged away, so the cheapest known evasion of the
whole-prompt score does not transfer to it. It does not buy a
defense. Pure-repetition suffixes already sit below the benign
windowed median in the original study (ledger C6), because a
repeated token is trivially predictable; the window changes
which suffix families evade, not whether evasion exists. The
general lesson is the optimiser-not-attack-class scoping: every
perplexity number is a statement about a suffix *distribution*,
and papers should name the distribution the way they name the
model. "Perplexity filtering detects adversarial suffixes" is
not a claim; "windowed perplexity separates hand-written
gibberish from benign text at AUROC 0.887 (n = 15/10)" is.

The blocked corpus deserves emphasis rather than a footnote. The
field's standard practice — a defense-relevant artefact released
only to verified organisations on request — places independent
re-measurement out of reach of exactly the small, unfunded labs
whose replication work the field says it wants. Our
pre-registration is public, our pipeline is public, our verdict
bands are frozen; the one missing ingredient is an artefact we
cannot obtain. We regard documenting that asymmetry, with the
protocol ready to run the day access resolves, as a legitimate
scientific output — and a more honest one than quietly
substituting a different corpus and answering a different
question under the original title.

## 6. Limitations

Benign n = 10 makes AUROC granular and intervals wide; we accept
this for comparability with the original study and report
intervals throughout. distilgpt2 is a proxy scorer: a suffix's
perplexity under distilgpt2 is not its perplexity under any
target model. No live aligned model appears anywhere in this
work, so no behavioural or attack-success claim is made. The
primary arms are blocked (§4), which caps what this draft can
conclude: S1 and the gates are mechanism and reproducibility
results, not the headline separability verdict, which remains
open. AmpleGCG-Plus supersession is a live risk to the question's
framing if access takes long enough.

## 7. Reproducibility statement

All code, per-case score rows, the dataset spec, the frozen
manifest and this draft's outline and claims ledger are in the
public repository `andra-jasper/llm-saftey-lab`. The spec checker
in that repository is the executable form of the
pre-registration: it recomputes the reference table from the
committed rows and fails if any frozen value drifts. The exact
unblock condition for the AMP arms: a granted
verified-organisation request for the released suffixes, or a
future static, versioned, citable release of the same corpus —
on receipt, file hash and grant date are recorded in the
manifest, the frozen selection rule is applied, and P1–P3 are
read off the frozen bands.

## 8. References

- Chen, Zharmagambetov, Wagner & Guo 2025, "Meta SecAlign: A
  Secure Foundation LLM Against Prompt Injection Attacks",
  arXiv:2507.02735 — https://arxiv.org/abs/2507.02735
- Debenedetti et al. 2025, "Defeating Prompt Injections by
  Design" (CaMeL), arXiv:2503.18813 —
  https://arxiv.org/abs/2503.18813
- Jain et al. 2023, "Baseline Defenses for Adversarial Attacks
  Against Aligned Language Models", arXiv:2309.00614 —
  https://arxiv.org/abs/2309.00614
- Kumar et al. 2024, "AmpleGCG-Plus", arXiv:2410.22143 —
  https://arxiv.org/abs/2410.22143
- Liao & Sun 2024, "AmpleGCG: Learning a Universal and
  Transferable Generative Model of Adversarial Suffixes for
  Jailbreaking Both Open and Closed LLMs", COLM 2024,
  arXiv:2404.07921 — https://arxiv.org/abs/2404.07921
- Nasr et al. 2025, "The Attacker Moves Second",
  arXiv:2510.09023 — https://arxiv.org/abs/2510.09023
- Sharma et al. 2025, "Constitutional Classifiers",
  arXiv:2501.18837 — https://arxiv.org/abs/2501.18837
- Zhu et al. 2025, "MELON: Provable Indirect Prompt Injection
  Defense via Masked Re-execution and Tool Comparison",
  arXiv:2502.05174 — https://arxiv.org/abs/2502.05174
- Zou et al. 2023, "Universal and Transferable Adversarial
  Attacks on Aligned Language Models", arXiv:2307.15043 —
  https://arxiv.org/abs/2307.15043
- Lab-internal: E1 `proposals/flagship_candidates.md`; E2
  `data/flagship_dataset_spec.md`; E3
  `results/flagship_baselines.md`; F6
  `results/adaptive_redteam.md`; A6
  `results/perplexity_filter.md`; D5
  `results/redteam_blueteam.md`.

## 9. Appendix — claims-ledger check (E4 §4)

| Draft claim | Ledger row | Status |
|---|---|---|
| Windowed AUROC 0.887, SYN vs BEN, A6 pipeline | C1 | ✔ traced to A6 + E3 G1 |
| Hill-climb finals' windowed scores; windowed layer caught all 3 | C2 | ✔ traced to D5 + E3 G2 |
| Dilution lowers full-text monotonically, windowed median unmoved (lab suffixes only) | C3 | ✔ traced to E3 S1; scope stated every time |
| AmpleGCG publishes no static corpus; verified-organisation request only | C4 | ✔ paper §4 via E2 §5 |
| P1–P3 status | C5 | ✔ stated only as BLOCKED / UNANSWERED |
| Repetition suffixes evade both scores | C6 | ✔ A6 suf-07/08 + D5 controls |
| 80% AID ASR under whole-prompt detector | C7 | ✔ labelled as the AmpleGCG paper's figure |
| F6 adaptive block-rate falls (0/25, 0/15) and holds | F6 report (own committed evidence) | ✔ simulation-level scope stated |

Never-claims honoured: no ASR derived from perplexity scores; no
S1-derived statement about AmpleGCG; no pooled or cross-suite
AUROC anywhere in the draft.
