# Paper notes: Meta SecAlign — the first open model-level prompt-injection defense, and whether this lab can run it

## Paper

Sizhe Chen (UC Berkeley / FAIR at Meta), Arman Zharmagambetov (Meta),
David Wagner (UC Berkeley), Chuan Guo (FAIR at Meta).
"Meta SecAlign: A Secure Foundation LLM Against Prompt Injection
Attacks." arXiv:2507.02735 (v1: 3 Jul 2025; v2 read here, revised
10 Nov 2025).
Link: https://arxiv.org/abs/2507.02735
Code + weights: https://github.com/facebookresearch/Meta_SecAlign —
models `facebook/Meta-SecAlign-8B` and `facebook/Meta-SecAlign-70B`
on Hugging Face (both gated; see Feasibility).

**Version note (recorded 2026-11-16).** arXiv now lists a v4
(28 Sep 2026), retitled "Meta-SecAlign: Training LLMs against
Prompt Injection for Robust Agents." v4 reframes the contribution
around a scaling finding — the original SecAlign recipe suffers
significant utility degradation at scale, especially on agentic
tasks — and extends experiments to Llama-4-Scout and Qwen3-4B /
Qwen3.6-27B across 6 benchmarks. The two techniques v4 names
(randomized injection position; self-generated responses as labels)
are already the SecAlign++ recipe detailed in v2 (§III-C), which is
what these notes document. The released weights are unchanged:
v4's abstract still links only the 8B and 70B models. No 4B
SecAlign weights are released, so the smallest *obtainable* model
is the 8B — that is the model the feasibility section prices.

Read 2026-11-16 from the arXiv HTML full text (v2), the v4
abstract, and the Hugging Face model API records for both released
models. **Study note, not a replication** — no SecAlign model was
run here (that is the point of the feasibility section); every
performance number below is the paper's, cited as such.

## One-paragraph summary

Meta SecAlign is SecAlign (Chen et al., arXiv:2410.05451 — the
lab's C5 notes cover its predecessor StruQ) turned into a released
foundation model. The recipe, **SecAlign++**, fine-tunes an
instruct model with DPO on simulated prompt injections so it
prefers the secure response (follow the user instruction, ignore
the instruction planted in data) over the insecure one. Two
changes over the original SecAlign carry the paper: (1) a new
**`input` chat role** holds untrusted data, separated from the
`user` role by special delimiters that are repeatedly filtered out
of the data itself (the StruQ/C6 front-end move, enforced by
training instead of by a parser); and (2) two utility fixes —
**randomized injection position** during training (injections only
at the end of data teach a shortcut: "ignore the last message,"
which then also ignores legitimate trailing user instructions) and
**self-generated responses** as the preferred labels
(ground-truth Alpaca labels are low-quality and out-of-distribution
labels — even GPT-4o/GPT-5 responses — destroy security by
shifting output style instead of teaching the separation). The
result is the first fully open model with a built-in model-level
defense: the 70B posts near-zero ASRs on most of 7 security
benchmarks at utility comparable to its undefended base, and the
defense — trained only on generic instruction-tuning data —
transfers to unseen agentic tasks (tool calling, web navigation).

## The mechanism (§III)

- **Separation by role, not by string.** A fourth message type,
  `input`, is added to the Llama 3 chat template alongside system /
  user / assistant. Untrusted data goes in the `input` role; the
  security policy is "follow the `user` role, treat `input` as
  data." Because the delimiters are special tokens, data text
  cannot produce them — provided the pipeline **repeatedly filters
  any special delimiter out of the data** until none remain (§III-A;
  the same repeated-filter load-bearing detail the lab hit in C6's
  nested-delimiter case, comp-close-04).
- **Preference data.** Built from Cleaned Alpaca samples that have
  a data part: another sample's instruction is injected into the
  data, the secure response (to the real instruction) is preferred
  over the insecure response (to the injection). 19,157 preference
  samples; DPO, 3 epochs, β = 0.1; LoRA (r = 64 / α = 8 for the 8B,
  r = 32 / α = 8 for the 70B; the paper notes full fine-tuning with
  proper hyperparameters performs similarly). LoRA α doubles as a
  **test-time utility–security dial**: lowering α at inference
  trades security back for utility (paper Fig. 2–3).
- **What is never trained on:** injections with explicit malicious
  intent ("Ignore previous instruction", "IMPORTANT INSTRUCTION").
  The injected instructions are ordinary instructions in the wrong
  channel — position is the only signal, exactly StruQ's training
  principle (C5). The robustness to explicit attacks at test time
  is therefore a generalisation result, not memorisation.

## Results (paper's, v2)

**Meta-SecAlign-70B** (base: Llama-3.3-70B-Instruct; Tables II–III):

| benchmark | undefended | Meta-SecAlign-70B |
|---|---|---|
| AlpacaFarm ASR | 95.7% | 0.5% |
| AlpacaFarm adaptive ASR (fake-delimiter completion) | 98.1% | 0.5% |
| SEP ASR | 99.7% | 6.4% |
| SEP adaptive ASR | 99.7% | 6.4% |
| TaskTracker ASR | 19.6% | 0.2% |
| CyberSecEval2 ASR | 52.7% | 1.8% |
| AgentDojo ASR | 14.7% | 1.9% |
| InjecAgent ASR | 53.8% | 0.5% |
| WASP end-to-end ASR | 2.4% | 0% |

Utility cost at 70B is small on knowledge benchmarks (MMLU
86.3% → 85.9%; IFEval 91.3% → 89.5%, the largest drop ≈ 2 points)
and *negative* on AgentDojo in the paper's runs (utility 59.8% →
84.5%; utility-under-attack 43.4% → 79.5%) — reported as-is; the
authors state they have no strong explanation for the increase.
Agentic evaluations use the benchmark's sandwich (repeat-user-
prompt) defense for all models, the paper's Table IX reports the
no-sandwich variant separately.

**Meta-SecAlign-8B** (base: Llama-3.1-8B-Instruct; Table XI) — the
numbers that matter for this lab, because the 8B is the smallest
released model:

| benchmark | undefended 8B | Meta-SecAlign-8B |
|---|---|---|
| MMLU | 72.0% | 71.7% |
| AlpacaEval2 utility | 31.2% | 31.0% |
| AlpacaFarm ASR | 68.3% | 0% |
| AlpacaFarm adaptive ASR | 89.4% | 0.5% |
| SEP ASR | 98.1% | 7.8% |
| SEP adaptive ASR | 97.1% | 11.5% |
| TaskTracker ASR | 12.4% | 0.2% |
| CyberSecEval2 ASR | 21.8% | 7.3% |
| InjecAgent ASR | 15.1% | 0% |

The 8B is somewhat less robust than the 70B (SEP adaptive 11.5%
vs 6.4%; CyberSecEval2 7.3% vs 1.8%) at near-identical utility
preservation. Both models' "adaptive ASR" is a *narrow* adaptive
notion — fake delimiters found by embedding distance, used in
completion attacks (§IV-C). It is not a Nasr-style adaptive
evaluation, and the lab's F1 audit already records the difference
(see Lab mapping).

**Ablations (§V, 70B).** Without randomized injection position,
AgentDojo utility collapses (84.5% → 15.5% in the self-label
ablation row of Table IV) while ASRs barely move — the shortcut
failure is a *utility* failure first. With ground-truth (davinci-
003-era) labels instead of self-generated ones, utility craters
the same way; with GPT-4o labels, SEP adaptive ASR degrades to
21.3%. Both SecAlign++ ingredients are necessary; neither is a
security ingredient in isolation.

## Feasibility: can this lab run the smallest model?

This is the deliverable the roadmap asks for — the lab's first
*honestly-reportable aligned model*: a real instruction-following
model with a published defense, whose ASR numbers the lab could in
principle measure instead of simulating. Every prior lab number is
a detector measurement or an ideal-follower simulation upper bound
(B1–B6, C6) precisely because the lab has never had such a model.
The question is whether Meta-SecAlign-8B fits the lab's envelope
(CPU-only, distilgpt2-scale: 82M parameters, ≈0.33 GB fp32).

**What the 8B release actually is (checked 2026-11-16 via the
Hugging Face API).** `facebook/Meta-SecAlign-8B` is **not a full
model — it is a LoRA adapter** (HF `library_name: peft`,
`base_model: meta-llama/Llama-3.1-8B-Instruct`; files are
`adapter_config.json` + `adapter_model.safetensors`; total repo
storage 281,061,608 bytes ≈ 0.28 GB). Running it requires
downloading and running the full 8B base model with the adapter
merged/applied. Both the adapter repo and the base model are
**gated, manual-approval** downloads (the adapter's gate collects
name, date of birth, country and affiliation under the Llama 3
Community License) — neither can be fetched by an unattended
script, and no download was attempted in this run.

**The arithmetic** (parameter counts are the base models' published
sizes; memory = params × bytes/param, weights only, before KV
cache, activations and runtime):

| model | params | bf16 | int8 | int4 (weights) |
|---|---|---|---|
| distilgpt2 (lab's current model) | 0.082B | — | — | 0.33 GB fp32 |
| Meta-SecAlign-8B (Llama-3.1-8B + adapter) | 8.03B | 16.1 GB | 8.0 GB | ≈4.0 GB |
| Meta-SecAlign-70B (Llama-3.3-70B + adapter) | 70.6B | 141 GB | 70.6 GB | ≈35 GB |

Against this run's machine — 7.7 GiB total RAM, 4 vCPUs, no GPU,
representative of the lab's CPU-only envelope:

- **bf16 and int8 do not fit in RAM at all** (16.1 GB / 8.0 GB of
  weights alone vs 7.7 GiB total). The 70B is out by an order of
  magnitude at every precision.
- **int4 fits on paper** (≈4.0 GB weights + ≈0.3–0.5 GB of scales,
  KV cache and runtime overhead), leaving the OS and Python in the
  remaining ~3 GiB. But the paper's own inference setup is GPU
  throughout (70B: 4× 80 GB GPUs, tensor-parallel; 8B: "tested on
  a single A100 (or even a GPU with smaller memory)" — §IV-A); no
  CPU figure exists in the paper. At the single-digit tokens/second
  an 8B int4 model sustains on 4 shared vCPUs (order-of-magnitude
  estimate from memory bandwidth, **not a measurement**), one
  500-token response takes minutes: the paper's smallest security
  benchmark (CyberSecEval2, 55 samples) is an hours-long run, and
  an AgentDojo-scale evaluation (949 pairs) is days. A handful-of-
  prompts smoke test is the only honestly-scoped CPU experiment.
- **Access is a second, independent blocker:** gated manual
  approval for both repos stands in front of any of the above.

**Verdict, recorded plainly: NOT feasible as an evaluation model
in the lab's current envelope.** Meta-SecAlign-8B is identified as
the lab's first honestly-reportable aligned model — the first
candidate whose live ASR the lab could report without the
simulation caveat — but reporting it requires (a) gated-access
approval for the base model + adapter, and (b) either a GPU or an
int4 CPU smoke-test scope of a few prompts, not a benchmark.
Until one of those changes, every lab defense number keeps the
F1 attacker-model label it already carries, and the flagship's
"no live aligned model evaluated yet" limitation (D7/E1) stands.
If a GPU or access appears, the first experiment is already
scoped by the paper's own tables: Meta-SecAlign-8B on the lab's
B5 indirect suite + B6 probes, reported against the paper's
CyberSecEval2 7.3% / SEP 7.8% reference points, with the F4
triple (ASR + benign cost + compute cost) stated.

## Lab mapping

- **Lineage.** StruQ (C5, front-end + tuning) → SecAlign (C5 note,
  preference optimisation) → Meta SecAlign (this note, SecAlign++
  at foundation scale + released weights). C6 implemented StruQ's
  front-end *without* the tuning and labelled the gap; Meta
  SecAlign is what the tuned half buys at scale — and its `input`-
  role filter is C6's Q3 filter, moved into a chat template.
- **The adaptive gap (F1 applies with full force).** The paper's
  adaptive ASR tests one attack family (fake-delimiter completion).
  The lab's F1 audit of Nasr et al. 2025 (arXiv:2510.09023) records
  Meta SecAlign at ~2% static ASR → **96% ASR under an RL-based
  adaptive attack** (Nasr et al.'s numbers, as noted in F1). Both
  can be true: the defense is strong against the attacks it was
  evaluated on, including its own adaptive variant, and falls to a
  stronger adaptive attacker with a larger budget. Quoting the
  paper's 0–7.8% ASRs without the attacker-model label would
  repeat exactly the reporting failure F1 was written to stop.
- **Shortcut learning is the lab's repetition lesson, at model
  scale.** "Injections only at the end" teaching "ignore the last
  message" is the training-time twin of the lab's measurement
  findings that position skews results (B5: 13/15 payloads at
  document end, recorded as a limitation). Randomized position is
  the fix in both worlds: vary position in training *and* in
  evaluation suites.
- **For F9 (AgentDojo-style mini benchmark).** The paper's agentic
  numbers are the reference points a lab-built mini benchmark
  should sanity-check against (AgentDojo ASR 1.9% / utility 84.5%
  at 70B, sandwich defense on) — and its utility-*increase* under
  defense is a standing warning that utility deltas on small
  suites can move in either direction for reasons nobody has
  explained yet.

## Sources

- Chen, Zharmagambetov, Wagner & Guo, "Meta SecAlign: A Secure
  Foundation LLM Against Prompt Injection Attacks,"
  arXiv:2507.02735v2 — https://arxiv.org/abs/2507.02735 (v4
  abstract checked 2026-11-16 for the version note).
- Hugging Face model records, checked 2026-11-16:
  `facebook/Meta-SecAlign-8B` (adapter; base
  `meta-llama/Llama-3.1-8B-Instruct`; 281,061,608 bytes;
  gated/manual) and the v2/v4 abstract links to
  `facebook/Meta-SecAlign-70B`.
- Chen et al., "SecAlign: Defending Against Prompt Injection with
  Preference Optimization," arXiv:2410.05451 (the recipe Meta
  SecAlign scales); lab notes `notes/struq.md` (C5),
  `notes/attacker_moves_second.md` (F1, for the Nasr et al.
  adaptive figures cited above).
