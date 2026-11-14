# Paper notes: The Attacker Moves Second — adaptive attacks bypass LLM defenses

## Paper
Milad Nasr, Nicholas Carlini, Chawin Sitawarin, Sander V. Schulhoff,
Jamie Hayes, Michael Ilie, Juliette Pluto, Shuang Song, Harsh Chaudhari,
Ilia Shumailov, Abhradeep Thakurta, Kai Yuanqing Xiao, Andreas Terzis,
Florian Tramèr.
"The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses
Against LLM Jailbreaks and Prompt Injections."
arXiv:2510.09023 (submitted 10 Oct 2025; dated June 2025 in the PDF).
Link: https://arxiv.org/abs/2510.09023 (subjects: cs.LG, cs.CR).
Read 2026-11-14 from the arXiv abstract page and the full HTML text.
**Study note, not a replication** — no defense was re-run here and no
live aligned model was evaluated; every ASR below is the paper's.

## One-paragraph summary
The paper argues that current evaluations of jailbreak and
prompt-injection defenses are flawed in a specific, fixable way: defenses
are usually tested against a *static* set of attack strings written
before the defense existed, or against generic optimisation attacks
(e.g. off-the-shelf GCG) that were never adapted to the defense and run
at low budget. Following the older adversarial-ML lesson (Kerckhoffs's
principle; Athalye et al. 2018 on obfuscated gradients), the authors
instead evaluate each defense against an attacker who *knows the
defense*, chooses an attack family to fit it, and spends substantial
compute. Their general attack loop is instantiated four ways —
gradient-based, reinforcement-learning (an LLM proposer updated with
GRPO, fed score feedback), search-based (genetic / LLM-guided mutation),
and human red-teaming (an online competition with 500+ participants).
Applied to 12 recent defenses across four families, adaptive attacks
reach **ASR above 90% for most defenses**, even though the majority of
those defenses originally reported near-zero ASR. The conclusion is
methodological, not nihilistic: an empirical evaluation can never prove
a defense robust — it can only *fail to break it* after trying hard —
and future defense papers must be evaluated that way.

## What they actually did, by defense family (paper's numbers)

Benchmarks follow each original paper's protocol, so ASRs are **not
comparable across defenses** (the authors say this themselves):
HarmBench for jailbreaks; AgentDojo, OpenPromptInjection and
adversarial-Davinci-style setups for prompt injection. All reported
attacks were manually verified not to be exploiting the scorer.

1. **Prompting defenses** — Spotlighting (Hines et al. 2024), Prompt
   Sandwiching, RPO. On AgentDojo's static attacks, Spotlighting and
   Sandwiching show ASR as low as ~1%; under the authors' search-based
   adaptive attack both exceed **95% ASR**. Human red-teamers produced
   265 successful attacks against Spotlighting and 178 against Prompt
   Sandwiching (one winning pattern: pose the malicious task as a
   *prerequisite* for the user's task, which sandwiching's re-emphasis
   of the user task does not counter). Against RPO on HarmBench, the
   RL attack reaches 98% ASR and the gradient attack 96%.
2. **Training against existing attacks** — Circuit Breakers, StruQ,
   Meta SecAlign. RL attacker vs StruQ (target-phrase setup, prefix in
   the data channel, often by impersonating system-level prompts):
   succeeds in every case tested. Meta SecAlign: 2% ASR reported on
   static AgentDojo → **96% ASR** under the search-based adaptive
   attack. Circuit Breakers: **100% ASR** for the RL attack on
   HarmBench. The authors' reading mirrors vision adversarial training:
   training on a fixed set of pre-computed attacks does not generalise;
   only robust optimisation *inside* the training loop has historically
   helped, and only for the attack space optimised against.
3. **Filtering-model (detector) defenses** — Protect AI Detector,
   PromptGuard, PIGuard, Model Armor. A search-based attacker fed the
   detector's own confidence score and flag as feedback reaches
   **>90% ASR** against Protect AI, PromptGuard and Model Armor
   (Gemini-2.5 Pro base); PIGuard is the most resistant and still
   reaches **71% ASR**. Human red-teamers collected hundreds of
   successful injections, including 123 against PIGuard under its
   strictest setting. Stacking detectors did not fix this: the adaptive
   attack fools the target model and the detector jointly. The paper
   still grants detectors practical value against unsophisticated,
   opportunistic attacks — a limited component, not a solution.
4. **Secret-knowledge defenses** — Data Sentinel (known-answer /
   canary detection, minimax fine-tuned) and MELON (masked
   re-execution). Against Data Sentinel, an RL attack that simply
   *redefines the task terms* redirects the model to the adversary's
   task at **>80% accuracy on both tested tasks** (sentiment / spam),
   comparable to an undefended model. Against MELON, search reaches
   76% ASR *without* knowledge of the defense, and **95% ASR** with
   perfect knowledge (the mutator discovers a conditional strategy:
   fire only in the real-user run, not the masked run); humans found
   69 successful injections.

Four lessons the authors draw: (1) small static evals mislead and
near-zero static ASR correlates with being easy to break adaptively;
(2) automated adaptive evaluation works but is not yet reliable —
robustness to it is necessary, not sufficient; (3) human red-teaming
still beats automation (on a selected subset, search 69% vs humans
collectively 100%) and defense authors should red-team their own
defense and make it easy for others to; (4) model-based auto-raters are
themselves attackable, so scorer exploitation must be checked.

Threat models used: white-box (weights + gradients), black-box with
logits, and black-box generation-only — with a deliberately large
attacker compute budget in all three, because the question is whether
the defense works at all, not how expensive breaking it is.

## The lab audit this task requires: what attacker model does each lab claim survive?

The roadmap wording for F1 is explicit: *state what attacker model each
lab defense claim survives.* Using the paper's ladder — **L0 static**
(attacks written without knowledge of the defense), **L1 generic
optimisation** (an existing attack run unadapted, low budget),
**L2 adaptive automated** (attack chosen/tuned against this defense,
with its score or flag as feedback, substantial budget), **L3 adaptive
human** (defense-aware people iterating) — the honest audit of every
committed lab number is:

| Lab claim (source) | Attacker actually used in the lab | Strongest level the claim survives | Why it stops there |
|---|---|---|---|
| A4 detector_v1 flags 17/25 A2, 0/10 benign FP | Fixed hand-written A2 suite | L0 only | No attacker ever saw the detector's score; Nasr §5.3 shows score-feedback search takes comparable BERT-style detectors past 90% ASR. The lab number is a *static-suite detection rate*, nothing more. |
| A6 perplexity: windowed AUROC 0.887, suffix median 370.5 vs benign 73.2 | Hand-written GCG-*style* suffixes, no optimisation against the filter | L0 only, with an L0 evasion already inside the set | Pure-repetition suffixes (PPL 4.1 / 6.8) evade both scores *without any adaptation* — the weakest possible attacker already finds the hole. |
| B1 hardening L0→L3 blocks 0/12/17/18 of 25 | Fixed A2 suite through an ideal-follower simulation (detector_v1 as recognition layer) | L0, and only as a simulation upper bound | Two discounts stack: no live model, and no adaptive attacker. Nasr's prompting-defense results (static ~1% → adaptive >95%) are exactly this shape of claim failing at L2/L3. |
| B2 spotlighting: defended variants 25/25 on A2; S2/S4/S5 block 8/8 escape probes, S1 6/8, S3 5/8 | Fixed A2 suite **plus hand-written, defense-aware escape probes** (each probe built to attack that variant's own mechanism) | L0 on A2; a *low-budget, hand-written slice of L3* on the probes | The probes are the lab's first genuinely defense-aware attacks, and they already separate the variants (fixed delimiters fall to their own closing string). But 8 hand-written probes are not Nasr-scale human red-teaming (265 successes vs Spotlighting) and no automated search was run. Claim must read: "survives these 8 probes under simulation," never "robust." |
| B4 output filter: combined 13/15 compromised blocked, 0/15 FP | Fixed hand-written candidate outputs | L0 only | The two misses (French leak, base64 leak) are *unadapted* evasions; an L2 attacker with the similarity score as feedback is precisely Nasr's detector setting. F7 (decode-then-rescan) fixes one named hole, not the level. |
| B5/B6 RAG: structural variants 15/15 on B5; R3/R5 6/6 probes, R2 4/6, R4 3/6 | Fixed B5 suite + 6 hand-written defense-aware RAG escape probes, ideal-follower simulation | Same as B2: L0 + low-budget hand-written L3 slice, simulation-discounted | Detector channel is a floor effect (0/15 flagged at every variant), so the structural claim is the whole claim — and structural prompt-time separation is what CaMeL (F2) shows is *not* enforcement without an external interpreter. |
| C6 structured-query front-end: Q3 13/13 at string level; Q1/Q2 10/13 | New completion suite incl. near-miss and nested-delimiter cases written against the front-end's own strings | Low-budget hand-written L3 slice, string level only | Strongest lab design result (the *repeated filter* is load-bearing — the nested case proves it), but Nasr §5.2 is the warning: StruQ *with training* fell to an adaptive RL attacker in every tested case; the lab's front-end-only, untrained variant cannot claim more than its probe set. |
| D5 red-team/blue-team loop: hill-climb cuts PPL 67–90%, evades full-text on 1/3 bases; windowed layer catches all 3 finals; repetition controls evade completely | **Random-search attacker optimised against A6's own scores** (seed 20261108, 72 rows) | **L2 — the lab's only L2 evaluation** — at a small budget, against one detector, on distilgpt2 | This is the one lab experiment already shaped the way Nasr demands: defense-aware, score-feedback, iterated. Its honest limits are budget and scope (3 bases, one filter, evasion of a *detector* only — no model behaviour measured). It also already found the L2-surviving / L0-evading split the flagship rests on: the windowed statistic held at this budget; the full-text statistic did not. |
| D1 many-shot NLL simulation; D3 refusal classifier (1.000 leaky split / 0.771 family-held-out) | Fixed synthetic / simulation setups | L0 measurement claims only | Neither is a defense claim. D3's leaky-vs-held-out gap is the lab's own small instance of Lesson 1: a static, template-sharing split reports 1.000 for a classifier that scores 0.771 on unseen families. |
| E3 flagship: G1/G2 gates pass exactly; S1 dilution dose–response (full-text medians 370.5 → 159.8 → 32.5 at repeat 1→2→4; windowed median 7989.5 unmoved; j=4 full-text AUROC 0.107 vs windowed 0.887); P1–P3 BLOCKED | Frozen pipeline; REP-DILUTION arms are a *defense-aware construction* (AmpleGCG's published dilution trick, rebuilt on lab suffixes) | S1 is an L2-*designed* test executed statically: the attacker strategy was chosen from the defense's known weakness, then frozen — no per-case optimisation loop | That is stronger than L0 (the attack targets the statistic, not a generic suite) and weaker than full L2 (no search against the windowed score itself on these arms; D5 supplies that piece for its own finals). The preprint (E4) must state it exactly this way, and P1–P3 stay BLOCKED — no attacker-model language may be used to imply an AmpleGCG verdict that was never measured. |

**Net finding for the lab.** Every defense number in this repo except
D5's is an L0 number, in several cases already labelled an upper bound
(ideal-follower simulation) in its own report. The escape-probe suites
(B2/B6/C6) add a thin, hand-written, defense-aware layer — real, but
orders of magnitude below Nasr's human and automated budgets. Nothing
in the lab has faced L3 at scale, and only the perplexity filter has
faced L2 at all. This does not invalidate the lab's numbers; it fixes
their *scope sentence*, which the flagship preprint must carry
verbatim in spirit: **fixed-suite and simulation numbers are upper
bounds on defense strength; the only adaptive evidence in the lab is
D5's small-budget search against one detector and E3's
defense-aware-but-frozen dilution construction.**

## What changes in lab practice (adopted from this paper)

1. **Attacker-model label on every future defense claim.** Each new
   `results/` report states its ladder level (L0/L1/L2/L3), budget,
   and what feedback the attacker received — the F1 table above is the
   template, and F6 exists precisely to give B2/B6 a real L2 row.
2. **No "robust" / "blocks prompt injection" language** for any claim
   below L2, and L2 claims name the budget they survived (D5's phrasing
   — "catches all 3 finals at this budget" — is the model).
3. **Scorer check.** Following Lesson 4, any future run that uses a
   model- or heuristic-based judge must manually verify a sample of
   "successes" are not scorer exploits, as Nasr et al. did.
4. **For the flagship (E4 §2/§5):** Nasr is the citation that justifies
   the preprint's scope discipline — and also its sharpest reviewer
   objection. Pre-empt it in the draft: the windowed-PPL question is a
   *detector-separability* question (AUROC on frozen arms), not a
   robustness claim about a deployed defense; the one place the paper
   can speak adaptively is D5 + S1, with budgets stated.

## Limitations of this note
- All ASRs are the paper's, measured on live aligned models under each
  original defense's own protocol; none is transferable as a number to
  this lab's offline, simulation-based results — the transfer is of
  the *evaluation standard*, not the rates.
- The paper's own caveat applies to its headline: numbers across
  defenses are not comparable (different benchmarks/protocols per
  defense), and "above 90% for most" is a statement about these 12
  defenses under these attacks, not a theorem about all defenses —
  design-based systems with enforcement outside the model (CaMeL, F2)
  are notably *not* among the 12 broken, which is part of why F2
  follows F1 in the roadmap.
- Human red-teaming results count collective successes across 500+
  participants; they show existence of breaks, not a per-attacker rate.

## Sources
- Nasr et al. 2025, "The Attacker Moves Second", arXiv:2510.09023 —
  https://arxiv.org/abs/2510.09023 (full HTML read for §§1–6, Tables
  and per-defense results as summarised above)
- Lab-internal: A4 `results/detector_v1.md`; A6
  `results/perplexity_filter.md`; B1 `results/system_prompt_hardening.md`;
  B2 `results/spotlighting.md`; B4 `results/output_filter.md`; B6
  `results/rag_defenses.md`; C6 `results/structured_query.md`; D5
  `results/redteam_blueteam.md`; D3 `results/refusal_classifier.md`;
  E3 `results/flagship_baselines.md`; E4 `paper/outline.md`; C3
  `results/leaderboard.md` (suite-separation and upper-bound labelling
  conventions used in the audit table).
