# Paper notes: Liu et al. 2023 — prompt injection, surveyed and formalised

## Papers (there are two, and they are not the same paper)

The roadmap entry said "Liu et al. 2023 prompt-injection survey". That
description matches **two** different 2023 papers with different first
authors named Liu, and conflating them is a common citation error, so
these notes cover both and keep them separate throughout.

1. **Yi Liu**, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang,
   Xiaofeng Wang, Tianwei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng,
   Leo Yu Zhang, Yang Liu.
   "Prompt Injection attack against LLM-integrated Applications."
   arXiv:2306.05499 (v1: 8 Jun 2023; v2: 2 Mar 2024).
   Link: https://arxiv.org/abs/2306.05499
   — the *empirical / real-world* paper: a pilot study on commercial
   apps plus the **HouYi** black-box attack. This is the one most
   secondary sources mean by "Liu et al. 2023" for prompt injection.

2. **Yupei Liu**, Yuqi Jia, Runpeng Geng, Jinyuan Jia, Neil Zhenqiang Gong.
   "Formalizing and Benchmarking Prompt Injection Attacks and Defenses."
   arXiv:2310.12815 (v1: 19 Oct 2023); USENIX Security 2024.
   Link: https://arxiv.org/abs/2310.12815
   Code: https://github.com/liu00222/Open-Prompt-Injection
   — the *formalisation / benchmark* paper: a definition, an attack
   framework, 5 attacks × 10 defenses × 10 LLMs × 7 tasks. This is the
   one that actually functions as the field's early survey-and-taxonomy
   reference, which is presumably why the roadmap called C1 a "survey".

Read 2026-10-27 from the arXiv HTML full texts (2306.05499v2 and
2310.12815v3). Neither paper is replicated here — this lab has no live
LLM-integrated application under test — so every number below is the
papers', cited as such.

## One-paragraph summary

Yi Liu et al. start from practice: existing heuristic injections only
partially succeeded on 2 of 10 commercial LLM-integrated applications
in their pilot, for three reasons — apps interpret the prompt slot
inconsistently (query vs. data payload), input/output format
requirements act as accidental syntax sanitisation, and multi-step
pipelines time out before a hijacked generation can surface. Their
fix, HouYi, is modelled explicitly on SQL injection / XSS: a successful
injection must make the model read the payload as a *new question*,
not as data. Yupei Liu et al. start from theory instead: they define a
prompt injection as compromising the **data** of a *target task* so the
application performs an attacker-chosen *injected task*, show the
known attacks are special cases of one construction
(compromised data = A(target data, injected instruction, injected
data)), derive a stronger **Combined Attack** from that framework, and
benchmark everything — concluding that **no existing defense is
sufficient**: prevention defenses either leave attacks working or cost
large clean-task utility, and detection defenses miss large fractions
of compromised data and/or flag large fractions of clean data.

## Yi Liu et al. — HouYi, in detail

**Threat model.** Black-box, public endpoints only. The adversary can
arbitrarily manipulate their own inputs but does *not* know the app's
pre-constructed prompt, structure, or backend model, and must infer
context from responses. Indirect injection (poisoning external
resources the app reads) is explicitly *out* of scope for their threat
model — that is Greshake et al.'s setting, our C2/B5 — which matters
when comparing their numbers to B5/B6.

**The three components of an injected prompt** (the paper's central
decomposition):

1. **Framework component** — a pre-constructed prompt that blends
   seamlessly with the target application's own prompt, so the payload
   reads as a continuation of legitimate use.
2. **Separator component** — induces *context partition*: syntax-based
   (special characters / closing structure), language-switching, or
   semantic separators that close the original context and open a new
   one. (§7.2 is honest that these three strategies "likely only
   scratch the surface".)
3. **Disruptor component** — the malicious question/payload that
   achieves the adversary's objective once the partition succeeds.

**The three phases of the attack:** Context Inference (probe the app
to learn its context and input–output behaviour) → Payload Generation
(build framework + separator + disruptor from what was learned) →
Feedback (score the response, iterate the payload). HouYi uses an LLM
itself to infer the target's semantics — an early instance of
LLM-assisted red-teaming.

**Headline results (paper's):**
- Pilot: prior heuristic attacks partially successful on only **2/10**
  commercial applications.
- Full run: HouYi deployed against **36** real LLM-integrated
  applications; **31 susceptible** — reported as an **86.1%** success
  rate at launching attacks (prompt theft and/or free use of the
  service's LLM).
- **10 vendors validated** the findings, including Notion.
- Two demonstrated exploit outcomes, both worth naming precisely
  because they are *application-level*, not model-level, harms:
  **prompt abuse** (unrestricted arbitrary use of the paid LLM behind
  the app — effectively stealing compute) and **prompt leak / theft**
  (extracting the app's proprietary system prompt, enabling zero-cost
  imitation of the service).

**Defenses they evaluate (§7.1).** Six empirically proposed strategies:
(1) Instruction Defense, (2) Post-Prompting (user input placed *before*
the app prompt), (3) Random Sequence Enclosure, (4) Sandwich Defense,
(5) XML Tagging (called particularly robust with XML+escape),
(6) Separate LLM Evaluation. Their verdict, from manual inspection
after implementing each against HouYi: each mitigates traditional
injections, **HouYi circumvents all of them**; no systematic
prevention technique existed at the time of writing.

**Reproducibility caveat (their §7.3, and it has aged as predicted):**
live commercial apps patch and swap backend models, so specific
vulnerabilities are transient and may no longer reproduce. The durable
contribution is the decomposition, not the 31/36 count.

## Yupei Liu et al. — the formalisation, in detail

**Definitions.** A task = instruction + data. The application queries
the backend LLM with target instruction ⊕ target data. An injection
modifies the *data* so the application performs the injected task
instead. The attacker controls the data only — not the instruction
prompt — and is assumed not to know the app's internals; the backend
LLM's integrity is assumed. (Note the difference from Yi Liu et al.:
there the adversary is the app's own *user* attacking through the
input slot; here the adversary is a *third party* whose content the
app ingests — a résumé screened by an LLM is their running example —
which is exactly the B5 indirect setting.)

**The five benchmarked attacks** (their Table 1; each is a strategy
for crafting the compromised data):

| Attack | Mechanism |
|---|---|
| Naive | Concatenate target data ⊕ injected instruction ⊕ injected data |
| Escape Characters | Prepend special characters (`\n`, `\t`) to fake a context switch |
| Context Ignoring | Add task-ignoring text ("Ignore previous instructions…") |
| Fake Completion | Add a fake target-task response ("Answer: task complete") so the model treats the target task as done |
| **Combined** (new, framework-derived) | Escape + Context Ignoring + Fake Completion together |

**The ten benchmarked defenses** (their Table 2) split into the
taxonomy this lab now adopts:

- *Prevention-based* (redesign the prompt or pre-process the data so
  the injected task is not performed): **Paraphrasing**,
  **Retokenization** (BPE-dropout), **Delimiters**, **Sandwich
  prevention** (re-append the target instruction after the data),
  **Instructional prevention** (redesign the instruction to tell the
  model to ignore instructions in the data).
- *Detection-based* (decide whether the data is compromised):
  **Perplexity (PPL) detection**, **Windowed PPL detection**,
  **Naive LLM-based detection**, **Response-based detection**,
  **Known-answer detection** (embed an instruction with a secret known
  answer; if the model doesn't return it, the instruction channel was
  hijacked).

**Metrics.** Performance under No Attack (PNA — clean-task utility),
Attack Success Value (ASV — how well the *injected* task is performed
under attack), and Matching Rate (MR), plus FPR/FNR for detectors.
PNA is the important discipline: a defense is scored on what it costs
when there is *no* attack, not only on what it blocks.

**Headline conclusions (paper's):** the Combined Attack is
consistently effective across target/injected task pairs and
outperforms each single-strategy attack; prevention defenses have
limited effectiveness and/or large PNA losses; one detection defense
(known-answer) works in some settings but misses a large fraction of
compromised data in many others; all other detectors miss a large
fraction and/or false-flag clean data. Their stated minimum bar,
which C3 should adopt verbatim in spirit: *future defenses should at
least be evaluated against the attacks in this benchmark.*

## Mapping to this lab — where our suites and defenses sit in their taxonomies

- **A2 (`data/injection_tests.yaml`) in Yupei Liu et al.'s attack
  framework.** A2 is a *direct* suite (attacker = the user), so the
  mapping is by mechanism, not by threat model:
  - `direct_override` ≈ **Context Ignoring** + Naive — explicit
    task-ignoring text followed by the injected instruction.
  - `authority_claim` has **no counterpart** in the five attacks: it
    works by claiming a higher privilege level rather than by
    partitioning context. A genuine taxonomy gap in the 2023 framework
    (worth a row in C7).
  - `encoded_payload` likewise has **no counterpart**: none of the five
    attacks obfuscates; all are plain-text. Encoding enters Yupei Liu
    et al. only as a *defense-side* transform (retokenization). This
    matches B3's reading of encoded payloads as mismatched
    generalisation — a dimension the formalisation doesn't model.
  - `multi_turn` is **out of scope** for both papers (both are
    single-shot constructions), the same caveat B3 recorded for Wei
    et al.
  - `roleplay` partially ≈ **Fake Completion / framework blending**:
    a roleplay frame is a Framework component in HouYi's sense — it
    makes the payload read as a legitimate continuation.
  - **What A2 lacks that the framework predicts:** a true *Combined*
    case per category (escape + ignoring + fake completion stacked)
    and pure Fake Completion cases. The framework's central empirical
    claim is that stacking beats singles; A2 never tests stacking
    systematically. Concrete follow-up for C3/C7: add a combined-stack
    variant of one case per A2 category before claiming coverage.
- **B5 is Yupei Liu et al.'s threat model, Yi Liu et al.'s blind
  spot.** B5's attacker controls only the retrieved document — exactly
  the data-only capability in the formalisation — while HouYi's
  threat model explicitly excludes poisoning external resources. So
  B5's 15 cases are benchmarkable in the 2310.12815 sense and not
  covered by 2306.05499's 31/36 result. C2 (Greshake) is the paper
  that actually owns B5's setting.
- **Our defenses in the prevention/detection taxonomy:**
  - B1 system-prompt hardening = **Instructional prevention**, graded
    (L0–L3). B1's finding — residual misses were recognition failures,
    not missing rule text — is the lab-scale version of their
    "instructional prevention has limited effectiveness" result.
  - B2/B6 delimiters, random-token delimiters, datamarking, and
    base64 encoding = **Delimiters** prevention, with datamarking and
    encoding as post-2023 refinements of the same idea. B2's escape
    probes are, in HouYi's vocabulary, **Separator components aimed at
    the defense's own partition**: the fixed-delimiter variant falls
    to a payload containing its own closing string — a separator
    beating a separator. That framing (defense = partition, attack =
    counter-partition) is HouYi's decomposition applied to our own
    results, and it predicts B6's outcome before the fact: only
    partitions the attacker cannot reproduce (random per-request
    tokens) or layered partitions (combined) survived all probes.
  - A4 detector_v1 and A6 perplexity filter = **Detection-based**;
    A6 is literally their PPL / Windowed PPL detection, and A6's
    result (windowed AUROC 0.887 on gibberish suffixes, fluent
    injections overlapping benign) is consistent with their verdict
    that perplexity detection misses a large fraction — fluent
    injections are not high-perplexity, as B5 reconfirmed (detector
    scores 0.32–0.40, all sub-threshold, on document-channel attacks).
  - B4 output filter ≈ **Response-based detection** moved to the
    output side: check whether what came back is a valid, on-task,
    non-leaking response rather than whether the input was clean.
    Their taxonomy files response-based detection as the weakest
    family in *input* screening; B4's 13/15 blocked at 0/15 FP
    suggests the same idea does better as an *output* gate on a
    narrow policy (leak/compliance) than as a general input detector —
    a distinction the 2023 taxonomy doesn't draw.
  - **Known-answer detection is the one benchmarked defense this lab
    has never tried.** It is also the paper's best-performing
    detector. Concrete candidate for a future B/C task: plant a
    canary instruction in the R1 hierarchy prompt ("before answering,
    emit token X") and measure, on B5, how often hijack suppresses the
    canary — cheap, offline-simulable, and directly comparable to
    their FNR framing.
- **Metrics discipline for C3.** Our results so far report blocked
  rates (an ASV analogue, inverted) but only B1/B2/B6 report the
  benign-side cost (benign friction 0/10; document recovery 15/15),
  which is PNA by another name. C3's leaderboard should carry both
  columns for every defense — blocked rate *and* clean-task cost —
  or it will repeat exactly the one-sided reporting Yupei Liu et al.
  criticise in the case-study literature. Combined with B3's lesson
  (an "any attack succeeds" adaptive row), C3 now has two imported
  methodological requirements, both from the 2023 papers this lab is
  built on.

## Limitations / open questions

- **Two papers, one roadmap line.** If a future citation in this repo
  says "Liu et al. 2023", it must say *which* Liu: Yi Liu et al.
  (HouYi, arXiv:2306.05499) or Yupei Liu et al. (formalisation,
  arXiv:2310.12815, USENIX Security 2024). These notes use the full
  arXiv IDs wherever the distinction matters.
- **Neither is a survey in the strict sense.** 2306.05499 is an
  attack paper with a pilot study and a defense discussion (§7.1);
  2310.12815 is a formalisation + benchmark. Calling C1 "the survey
  task" is retained only because the roadmap named it that; C7's
  taxonomy should cite these as primary sources, not as a review.
- **2023 snapshots, both.** Yi Liu et al.'s 31/36 is against 2023-era
  commercial apps (their own §7.3 predicts non-reproducibility), and
  Yupei Liu et al.'s defense verdicts predate structured queries
  (StruQ, C5/C6), instruction-hierarchy training, and spotlighting's
  publication (Hines et al. 2024, our B2). "No defense is sufficient"
  was true of the ten they tested; it is a baseline claim to re-test
  per defense, not a permanent theorem — our B2/B6 structural results
  (15/15 B5 blocked, probes aside) are already a partial, simulation-
  bounded counterpoint.
- **Evaluation-style mismatch with this lab.** Both papers measure
  *live models*; every B-series number in this repo is an
  ideal-follower simulation (an upper bound). Their ASV/PNA numbers
  and our blocked rates are not comparable quantities, and these notes
  do not place them in the same table for that reason.
- **Open question for the flagship:** HouYi's separator framing and
  Yupei Liu et al.'s combined-attack result together predict that
  *defense partitions fail exactly when the attacker can generate a
  valid separator for them*. B2/B6 confirmed it for delimiters and
  datamarking. Is there a partition family whose separator cannot be
  generated from inside the data channel at all (structured queries /
  C6 are the obvious candidate)? That is a crisp, testable flagship
  seed for E1.

## Sources

- Yi Liu et al., "Prompt Injection attack against LLM-integrated
  Applications", arXiv:2306.05499 — https://arxiv.org/abs/2306.05499
- Yupei Liu, Yuqi Jia, Runpeng Geng, Jinyuan Jia, Neil Zhenqiang Gong,
  "Formalizing and Benchmarking Prompt Injection Attacks and
  Defenses", arXiv:2310.12815 (USENIX Security 2024) —
  https://arxiv.org/abs/2310.12815 ;
  code: https://github.com/liu00222/Open-Prompt-Injection
- Lab files referenced: `data/injection_tests.yaml` (A2),
  `eval/detector_v1.py` (A4), `results/perplexity_filter.md` (A6),
  `results/system_prompt_hardening.md` (B1),
  `results/spotlighting.md` (B2), `notes/jailbreak_failure_modes.md`
  (B3), `results/output_filter.md` (B4),
  `data/indirect_injection_tests.yaml` (B5),
  `results/rag_defenses.md` (B6).
