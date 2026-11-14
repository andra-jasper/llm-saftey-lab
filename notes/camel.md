# Paper notes: Defeating Prompt Injections by Design (CaMeL)

## Paper
Edoardo Debenedetti, Ilia Shumailov, Tianqi Fan, Jamie Hayes,
Nicholas Carlini, Daniel Fabian, Christoph Kern, Chongyang Shi,
Andreas Terzis, Florian Tramèr.
"Defeating Prompt Injections by Design."
arXiv:2503.18813 (v1: 24 Mar 2025; v2: 24 Jun 2025).
Link: https://arxiv.org/abs/2503.18813 (subjects: cs.CR, cs.AI).
Code (authors' research release): google-research/camel-prompt-injection,
linked from the arXiv abstract page.
Read 2026-11-14 from the arXiv abstract page (v2) and the paper text.
**Study note, not a replication** — CaMeL was not implemented or run
here; every number below is the paper's. **Version note:** the v1
abstract reported solving 67% of AgentDojo tasks with provable
security; the current v2 abstract reports **77% (vs 84% undefended)**.
This note cites v2 as current and records the v1 figure only to keep
the lab's citations honest if an older copy is quoted.

## One-paragraph summary
CaMeL (CApabilities for MachinE Learning) defends LLM *agents* not by
making the model resist injections, but by wrapping it in a system
layer that stays secure **even when the underlying model is fully
susceptible**. Before any untrusted data is seen, a Privileged LLM
(P-LLM) reads only the trusted user query and extracts an explicit
plan — control flow and data flow — as code in a restricted subset of
Python. A custom interpreter then executes that plan. Untrusted content
(tool outputs, documents, web pages) is handled only by a Quarantined
LLM (Q-LLM) that has **no tool access**, or passed through as values;
crucially, untrusted data can fill a value but can never change the
program's control flow, because the plan was fixed from the trusted
query alone. On top of that separation, every value carries
*capabilities* — provenance metadata recording where the value came
from and who may read it — and the interpreter checks security policies
against those capabilities **at every tool call**, which is what stops
private data being exfiltrated through an otherwise-allowed call. The
design is explicitly borrowed from classical software security:
control-flow integrity, access control, and information-flow control.
No model is modified or retrained.

## How it works, in the order data moves

1. **Plan (trusted only).** P-LLM sees the user query and nothing else;
   it writes the task as restricted-Python code (the tools to call, in
   what order, with what data dependencies). Tool results never go
   back to the P-LLM, so nothing untrusted can re-plan the task.
2. **Execute (interpreter, not model).** The custom interpreter runs
   the plan. This is the enforcement point: it, not any LLM, decides
   what happens next.
3. **Process untrusted data (quarantined).** When the plan needs
   information extracted from untrusted content, the Q-LLM does that
   extraction. The Q-LLM cannot call tools, so even a completely
   successful injection inside the content it reads has no direct
   action channel — it can only corrupt the *value* it returns.
4. **Track every value (capabilities).** Each value in the interpreter
   carries metadata: its sources (user / P-LLM / a named tool / the
   Q-LLM over a named source) and its allowed readers. Provenance
   propagates through operations, so a value derived from private data
   is still labelled private downstream.
5. **Check policy at the tool call.** Before a tool executes, the
   interpreter evaluates the security policy over the capabilities of
   the call's arguments (e.g. data labelled as coming from a private
   source may not flow to an untrusted recipient; if a policy cannot
   be satisfied, the call is blocked or the user is asked). This is
   the step that addresses the hole in the plain Dual-LLM pattern
   (Willison 2023): the plan can be clean while its *arguments* are
   poisoned — e.g. the Q-LLM extracts an attacker's address where the
   intended recipient's address was expected — so control-flow
   separation alone is not enough; the data flow must be policed too.

## Results (paper's, AgentDojo)

- **Utility with provable security: 77% of AgentDojo tasks solved,
  vs 84% for the same setup undefended** (v2 abstract). "Provable"
  here is policy-relative: for those tasks the interpreter's
  enforcement guarantees no security-policy violation can occur,
  whatever the untrusted data says — it is not a claim that the task
  output is correct or that no harm of any kind is possible.
- The security evaluation is over AgentDojo's attack suite (949
  attacks in the paper's figure): with policy enforcement, successful
  attacks are driven to (near) zero for the evaluated models, in
  contrast to prompt-time defenses evaluated in the same benchmark
  (spotlighting, prompt sandwiching, tool filtering), which still
  register successful attacks. Exact per-model cells are the paper's
  Tables/Figures and are not transcribed here.
- The 84% → 77% gap is the honest price of the guarantee, and the
  paper reports it as a headline rather than hiding it — a reporting
  standard this lab has repeatedly flagged as missing elsewhere
  (StruQ's unmeasured filter cost in C5/C6; the lab's own unmeasured
  true clean-task accuracy in C3).

## The mapping this task requires: CaMeL's enforcement layer vs the lab's B2 / B6 / C6 front-ends

B2 (spotlighting), B6 (RAG variants) and C6 (structured-query
front-end) are the lab's structural defenses. CaMeL is what that family
becomes when the separation is enforced *outside* the model instead of
*requested from* it. Dimension by dimension:

| Dimension | Lab B2 / B6 / C6 | CaMeL |
|---|---|---|
| Where separation lives | Inside one model's context: delimiters, random tokens, datamarking (B2/B6), or reserved-token channels + delimiter filtering (C6) | Outside the model: P-LLM / Q-LLM split + a non-model interpreter that executes a fixed plan |
| What the attacker must defeat | The model's willingness to honour the marking — in the lab this is *assumed* (ideal-follower simulation, explicitly an upper bound, not a live-model ASR) | The interpreter and the policy — model behaviour is assumed *adversarial*: the guarantee is designed to hold even if the model processing untrusted data is fully compromised |
| Control flow | Emerges turn-by-turn from the model's outputs; an injection that is followed *becomes* the plan | Fixed before untrusted data is seen, extracted from the trusted query only; untrusted data has no channel to it |
| Data flow / provenance | Segment tags only (this span is "data"); no per-value provenance, no propagation through derived values | Every value carries capabilities (sources + allowed readers), propagated by the interpreter through operations |
| Tool calls | None exist in the lab harness — there is no action channel to gate | Every call is policy-checked against its arguments' capabilities before execution; exfiltration is blocked at the sink, not detected in the text |
| Known failure mode in the lab's own data | Delimiter forgery: B2 fixed delimiters fall to their own closing string (esc-01/02, 6/8 probes blocked), B6 fixed delimiters likewise (rag-esc-01/03, 4/6); datamarking falls to payloads with no spaces to mark (5/8 and 3/6); C6's unfiltered variants fall to their own delimiter family (10/13) and only the *repeated filter* (Q3) holds at string level (13/13) | Delimiter forgery is not a category: there is no delimiter in a shared context to forge. The analogous risks move to the interpreter's correctness, the policy's completeness, and values that are *allowed* by policy but wrong (poisoned-but-permitted data) |
| Clean-task cost | Only proxies measured: exact recovery of transformed documents (B2/B6, 10/10 and 15/15), small hand-written benign sets; C6 measured its filter's cost (0/5 plain benign altered, 5/5 format-bearing benign altered, key facts 10/10 survive). **True clean-task accuracy still unmeasured** (C3 gap) | Actually measured end-to-end on a benchmark: 77% vs 84% undefended on AgentDojo. This is the reporting standard F9 (AgentDojo-style mini benchmark) is meant to import into the lab |
| Guarantee type | None — empirical blocked-rates on fixed suites (+ hand-written escape probes), attacker-model level L0 + thin hand-written L3 slice per the F1 audit | Design guarantee relative to a stated policy and a trusted interpreter/P-LLM channel; empirical utility measured on top of it |

**The one-sentence version for the taxonomy (C7) and the preprint:**
the lab's front-ends and CaMeL share a *diagnosis* (instructions and
data must not share one undifferentiated channel — the same framing as
StruQ's prepared-statement analogy in C5) but differ in *where the
boundary is enforced*: in-model and behavioural (lab, StruQ-without-
training, all prompting defenses) vs out-of-model and mechanical
(CaMeL's interpreter; StruQ's reserved tokens are a halfway case —
unforgeable markers, but still interpreted by the model). F1's Nasr
results show the behavioural version failing under adaptive attack in
every family tested; CaMeL is the field's current reference point for
the mechanical version, and it is conspicuously **not** among the 12
defenses Nasr et al. broke — consistent with, though not proof of, the
claim that moving enforcement out of the model changes the attacker's
problem from "persuade the model" to "break the interpreter or the
policy."

## What CaMeL does not do (limits, stated carefully)

- **Policy-relative, not absolute.** If the policy permits a flow, a
  poisoned value can travel it: CaMeL stops *unauthorised* flows and
  control-flow hijacks, not bad data arriving through an authorised
  channel (the extracted-address problem is mitigated by policy, e.g.
  restricting recipients, not by making extraction trustworthy).
- **The trusted side must stay trusted.** The guarantee assumes the
  user query is trusted and the P-LLM's plan from it is the user's
  intent; a compromised or malicious *user* is out of scope, as are
  tasks whose legitimate control flow must itself be dictated by
  untrusted content (follow the instructions in this document) — those
  fit the architecture poorly by construction.
- **Utility and expressiveness cost.** 7 points of AgentDojo utility
  (v2), and the plan must be expressible upfront as a restricted-Python
  program; open-ended, exploratory agent behaviour is constrained.
  The authors' release is a research artefact, not a maintained
  product — secondary summaries of the paper note the README says as
  much; treat deployment claims accordingly.
- **No bearing on non-agentic injection.** CaMeL addresses agents with
  tools. It says nothing about the lab's A2 direct-injection suite, the
  perplexity flagship (E3), or jailbreaks for harmful content — its
  threat is integrity/confidentiality of agent actions, and mapping it
  onto those settings would be a category error of the kind C2/C7
  record elsewhere.

## Consequences for the lab

1. **Taxonomy (C7) gains its missing enforcement axis.** Defenses are
   now filed on two axes: stage (prevention/detection, input/output)
   *and* enforcement locus (in-model behavioural vs out-of-model
   mechanical). B2/B6/C6 = behavioural; CaMeL = mechanical; StruQ =
   mixed (mechanical markers + trained behaviour).
2. **F9 is the lab's CaMeL-shaped task.** The AgentDojo-style mini
   benchmark (stateful mock tools, formal state checks, benign utility
   + utility-under-attack + targeted ASR) is where a CaMeL-*style*
   claim could ever be made here: an executor that checks a policy
   over mock-tool calls is buildable offline, and its simulation must
   be labelled an upper bound exactly as B2/B6 were. F9 should copy
   CaMeL's reporting shape: utility undefended vs defended as a
   headline pair, not a footnote.
3. **For the flagship preprint (E4 §2):** CaMeL belongs in related
   work as the design-based alternative whose existence disciplines
   the paper's claims — perplexity filtering is a *detector* (Nasr
   §5.3's weakest family under adaptation), CaMeL is an *architecture*;
   the preprint compares numbers only within the detector family and
   cites CaMeL to show the field's robustness frontier is elsewhere.
4. **A cheap, honest lab experiment suggested (not run):** re-score the
   B6 escape probes under a "mechanical" reading — i.e. an executor
   that *refuses* any document-derived instruction by construction
   rather than simulating a follower that honours delimiters — to show
   in the lab's own data how much of B6's probe failure set is a
   forgery problem vs a policy problem. Queued as an F9 design input,
   not claimed here.

## Sources
- Debenedetti et al. 2025, "Defeating Prompt Injections by Design",
  arXiv:2503.18813 — https://arxiv.org/abs/2503.18813 (v2 abstract:
  77% vs 84% undefended on AgentDojo; v1 abstract: 67% — version
  difference recorded above)
- Debenedetti et al. 2024, AgentDojo (NeurIPS 2024) — the benchmark
  CaMeL is evaluated on; also the template for lab task F9.
- Willison 2023, the Dual LLM pattern — CaMeL's direct ancestor, as
  described in the paper's related work (privileged / quarantined
  split without data-flow enforcement; CaMeL's contribution is
  closing the data-flow hole).
- Lab-internal: B2 `results/spotlighting.md`; B6
  `results/rag_defenses.md`; C6 `results/structured_query.md`; C5
  `notes/struq.md` (front-end vs training, filter cost); C3
  `results/leaderboard.md` (clean-task cost gap); C7 `TAXONOMY.md`;
  F1 `notes/attacker_moves_second.md` (attacker-model audit used in
  the mapping table); E4 `paper/outline.md` §2.
