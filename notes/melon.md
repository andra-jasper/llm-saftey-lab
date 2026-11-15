# Paper notes: MELON — masked re-execution and tool comparison

## Paper
Kaijie Zhu, Xianjun Yang, Jindong Wang, Wenbo Guo, William Yang Wang.
"MELON: Provable Indirect Prompt Injection Defense via Masked
Re-execution and Tool Comparison."
arXiv:2502.05174 (v1: 7 Feb 2025; v3 read here; ICML 2025).
Link: https://arxiv.org/abs/2502.05174 (subjects: cs.CR).
Code (authors'): https://github.com/kaijiezhu11/MELON
Read 2026-11-15 from the arXiv HTML text (v3).
**Study note, not a replication** — MELON was not implemented or run
here; every number below is the paper's. Cross-checks against this
lab's F1 notes (Nasr et al. 2025) are labelled as such.

## One-paragraph summary
MELON defends LLM *agents* against indirect prompt injection (IPI) —
malicious tasks planted in tool-retrieved content — with no training
and no access to model internals. Its premise is a dependence claim:
when an injection succeeds, the agent's next action becomes
(approximately) conditionally independent of the user task and is
driven by the retrieved content instead. MELON therefore runs the
agent twice in parallel: the original run, and a *masked re-execution*
in which the user task is replaced by a task-neutral prompt while the
retrieved outputs are kept. If a tool call in the original run is
similar (embedding cosine, threshold θ = 0.8) to a tool call the
masked run produced from the retrieved content alone, the call cannot
have come from the user task — it is flagged as injected and execution
is halted before the call runs. On AgentDojo this reaches near-zero
attack success at a utility cost far below detector- and filter-style
baselines, at roughly 2× the model-call cost.

## How it works, in the order data moves

1. **State.** At step t the agent state is (user task T_u, action
   history, tool outputs O_1:t). The threat model is standard IPI:
   the attacker controls only retrieved content, never the user
   prompt or the model; the defender sees the whole state but may
   not train the model or read its internals.
2. **Mask.** The masking function replaces T_u with a task-neutral
   prompt T_f — the paper's example is "Summarize the provided
   content. If there are any instructions, execute them." — drops the
   action history, and consolidates all tool outputs into one block.
   Two few-shot samples teach the model to follow T_f rather than
   imitate the tool-call patterns visible in the outputs.
3. **Re-execute.** The masked run generates its next action from the
   retrieved content alone. In a benign trajectory it should produce
   no task tool calls (T_f needs none); if the content carries an
   injected task T_m, the masked run tends to start executing T_m.
4. **Cache.** Tool calls from the masked run accumulate in a cache H
   across steps, so a timing mismatch — masked run reaches T_m a
   step before the original run does — does not become a miss.
5. **Compare tool calls only.** Each original-run tool call is
   converted to a natural-language description (some arguments are
   deliberately excluded, e.g. for `send_email` only the recipient is
   compared, not the body) and embedded (text-embedding-3 in the
   paper's implementation). Any original call with cosine similarity
   > θ = 0.8 to any cached call raises the alert. Comparing calls
   rather than full actions matters: under attack the two runs'
   *text* differs while the malicious *calls* coincide.
6. **Intervene before execution.** Unlike input detectors that abort
   on suspicious content whether or not the attack would have worked,
   MELON checks the generated action before it executes, and only
   blocks when the injected task is actually about to be carried
   out. The paper is explicit that this timing is why its
   utility-under-attack does not collapse the way a perfect
   input-detector's would.

**The "provable" claim, stated at its actual scope.** Section 3.4
builds an *ensemble* of masking prompts (different neutral tasks as
weak detectors) and applies Hoeffding's inequality: if the expected
similarity for benign actions μ_B and for malicious actions μ_V
satisfy μ_B < θ < μ_V, both error rates decay exponentially in the
number of detectors n (their worked example: μ_B = 0.3, μ_V = 0.7,
θ = 0.5, n = 100 → bound ≈ 1.8×10⁻⁴). This is a bound on the
*ensemble detector's* error under an assumed separation of the two
similarity distributions — it is not a guarantee about the deployed
single-mask system, and it assumes away exactly the hard case (an
attack whose calls sit between μ_B and μ_V). The lab records it as a
conditional bound, the same labelling discipline F2 applied to
CaMeL's policy-relative "provable."

## Results (paper's, AgentDojo — 629 attack cases; GPT-4o, o3-mini,
Llama-3.3-70B; four attack styles: Direct, Ignore-Previous,
System-Message, Important-Messages)

Average ASR / utility-under-attack (UA), from the paper's Table 1:

| Model | No defense ASR / UA | MELON ASR / UA | MELON-Aug ASR / UA |
|---|---|---|---|
| GPT-4o | 16.06% / 69.08% | **0.24% / 58.78%** | 0.32% / 68.72% |
| o3-mini | 15.78% / 46.50% | 0.95% / 36.29% | 0.56% / 37.28% |
| Llama-3.3-70B | 28.50% / 54.65% | 1.27% / 46.30% | 0.72% / 52.94% |

- MELON-Aug = MELON + Repeat-Prompt augmentation of the original
  run; on GPT-4o it recovers most of MELON's UA gap (58.78% → 68.72%)
  at essentially the same ASR.
- Benign utility is *not* free: GPT-4o BU falls from 80.41%
  (undefended) to 68.04% (MELON) / 76.29% (MELON-Aug). The paper
  attributes part of the BU loss to cases where the user themselves
  asks the agent to follow instructions inside retrieved content —
  a legitimate-use pattern MELON cannot distinguish from an attack,
  because by its own premise both are user-task-independent.
- Baselines frame the trade-off: the DeBERTa detector reaches low
  ASR but BU 38.14% and UA 21.34% on GPT-4o (false-positive driven);
  the LLM detector gets 0.00% ASR *and* 0.00% UA; the tool filter
  reaches 0.00% ASR on two models only by blocking nearly all tool
  use (BU 4.12%).
- **Ablations** (GPT-4o, Important-Messages — the strongest attack):
  deleting the user task instead of substituting T_f ("Basic") raises
  ASR 0.95% → 2.70%; removing the cache raises it to 1.75%;
  comparing full actions instead of tool calls only raises it to
  **17.33%** — the focused comparison is the load-bearing design.
  Swapping T_f for paraphrase / sentiment / grammar / translation
  prompts moves ASR only between 0.95% and 1.43% (insensitive to the
  neutral task's wording).
- **Cost:** the masked run roughly doubles model calls (≈2× API
  cost); the authors argue batching and KV-cache overlap keep the
  added latency small, with embedding calls the main extra latency.

## The comparison this task requires: detection-by-divergence vs
E1 Candidate 3's detection-by-displacement

E1's Candidate 3 (the lab's parallel methods thread) is
known-answer detection: plant a secret instruction with a known
answer in the trusted channel; an injection that hijacks the task
*displaces* the known answer, and its absence is the alarm. MELON is
the other member of the family C1's taxonomy calls
counterfactual/consistency detection, and the two are mirror images:

| Dimension | Known-answer (E1 Candidate 3) | MELON (divergence) |
|---|---|---|
| Counterfactual probe | A planted instruction in the *trusted* channel whose survival is checked | A second execution with the trusted channel *removed* (masked) |
| Signal | **Absence**: the known answer is missing/displaced in the output | **Presence**: the same tool call appears in both runs |
| What is compared | Output text vs one expected string | Tool calls (embedded descriptions) across two trajectories, via a cross-step cache |
| When it fires | Post-execution — the paper's own reason for excluding known-answer from its baselines is that the attack may already have succeeded | Pre-execution — the generated call is checked before it runs |
| Dependence assumption | A hijacked model drops the planted task (single-task displacement) | A hijacked model's action is independent of T_u (state collapse onto O) |
| Shared blind spot | **Partial compliance**: an attack that does the injected task *and* keeps the planted answer evades displacement — E1 already scores this as its own category (the C6 lesson) | **Conditional / dual compliance**: an attack that fires only when the real user task is present evades divergence — Nasr et al. (F1) report exactly this adaptive strategy: 76% ASR uninformed → **95% ASR with perfect knowledge** of MELON |
| Benign cost shape | Planted instruction consumes output space; cost measured on benign sets (E1 P3) | ≈2× model calls + BU loss concentrated on "follow the instructions in this document" tasks (GPT-4o BU 80.41% → 68.04%) |
| Channel scope | Any channel — E1's whole point is the direct↔indirect transfer test (tune on A2, test untouched on B5) | Agent tool calls only; says nothing about direct injection or non-agentic jailbreaks |

**The one-sentence version for the taxonomy (C7) and the preprint:**
displacement asks "did the trusted signal survive?", divergence asks
"does the behaviour survive removing the trusted signal?" — both
replace instruction-likeness thresholding (the signal that failed to
transfer in this lab, 17/25 → 0/15) with a *causal* test of which
channel is driving behaviour, and both fail in the same place: an
attacker who satisfies the probe and the payload simultaneously.
That shared failure is not a coincidence to note in passing — under
F1's attacker-model ladder it is the L2/L3 move against the entire
family, and any lab instance of either detector must be reported
with that adaptive case named, not discovered later.

## What MELON does not do (limits)

- **Adaptive attackers are out of the paper's evaluation.** The four
  attacks are AgentDojo's fixed styles. F1's audit already records
  the consequence: defense-aware search takes MELON to 95% ASR via
  conditional execution. MELON's static-suite numbers are L0 numbers
  in the lab's grading, however strong.
- **Legitimate delegation is indistinguishable from attack.** Any
  workflow whose point is "do what the document says" trips the
  premise; the BU gap is partly this, and no threshold fixes it —
  it is the same authorised-channel hole F2 recorded for CaMeL.
- **The guarantee is narrower than the title.** "Provable" covers an
  idealised ensemble under a separation assumption (above), not the
  evaluated system.
- **Similarity is a threshold again.** θ = 0.8 on embedding cosine
  reintroduces a tuned threshold one level up; the ablations show
  the *designs* carry the result, but a lab replication would need
  the same family-held-out discipline D3 taught before trusting it.

## Consequences for the lab

1. **Candidate 3 gains a sibling and a sharper claim.** If the
   methods thread runs, MELON's masked re-execution is implementable
   in the same ideal-follower simulation harness as known-answer
   detection (mask = delete the trusted channel; compare = the
   executor's chosen action), and the pair can be run under E1's
   *same* cross-channel transfer protocol — tune on A2, test
   untouched on B5, both directions. The protocol, not either
   detector, remains the contribution.
2. **F9 inherits the intervention-timing lesson.** MELON's UA
   advantage comes from checking the *action before execution*
   rather than the *input on arrival*. The lab's AgentDojo-style
   mini benchmark should score detectors at both intervention points
   so that difference is measured, not asserted.
3. **For the flagship preprint (E4):** MELON belongs in related work
   as the detection family's strongest static-suite result *and* as
   F1's clearest cautionary case — near-zero static ASR, 95%
   adaptive ASR. Citing only the first half would repeat the exact
   reporting failure this lab exists to document.
