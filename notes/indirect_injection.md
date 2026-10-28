# Paper notes: Greshake et al. 2023 — indirect prompt injection

## Paper

Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres,
Thorsten Holz, Mario Fritz.
"Not What You've Signed Up For: Compromising Real-World
LLM-Integrated Applications with Indirect Prompt Injection."
arXiv:2302.12173 (v1: Feb 2023). Published at AISec '23 (16th ACM
Workshop on Artificial Intelligence and Security), pp. 79–90.
DOI: 10.1145/3605764.3623985.
Link: https://arxiv.org/abs/2302.12173
Code / demonstrations: https://github.com/greshake/llm-security

Read 2026-10-28 from the arXiv HTML full text (ar5iv rendering of
2302.12173). This is a study note, not a replication — the lab ran
no live LLM-integrated application — so every result below is the
paper's, cited as such.

**Citation correction (lab-wide):** earlier lab files cited this
paper with a transposed arXiv ID — a March ID instead of the
February one. That ID is wrong. The correct ID is
**2302.12173** (February, not March). This run fixes every
occurrence of the wrong ID in the repo alongside these notes
(`eval/rag_defenses.py` ×2, `results/rag_defenses.md`,
`data/indirect_injection_tests.yaml`, and the ROADMAP B5 line);
the wrong ID is deliberately not reprinted in full here, so a
repo-wide grep for it returns zero.

## One-paragraph summary

Before this paper, prompt injection was framed as a malicious
*user* attacking their own session. Greshake et al. show the
attacker does not need an interface at all: plant instructions in
data an LLM-integrated application will later retrieve — a web
page, an email, a document, a code repository — and the model
processes those instructions as if they were its own. Retrieval
blurs the line between data and instructions, so processing
untrusted retrieved content is, in their framing, analogous to
executing arbitrary code. They build the first taxonomy of this
threat from a computer-security perspective, then demonstrate it
qualitatively on real systems (Bing Chat — GPT-4-powered, in its
creative / balanced / precise modes — and GitHub Copilot) and on
synthetic GPT-4 / text-davinci-003 applications with mock tools
(search, view, retrieve-URL, read/send email, address book, and
persistent memory), all run at temperature 0 with prepared
content and no requests to real systems.

## The core distinction: direct vs. indirect

- **Direct injection:** the attacker is the user; the payload is
  in the user's own turn; user-turn filtering can in principle
  see it.
- **Indirect prompt injection (IPI):** the attacker is a third
  party; the payload is in *retrieved* data; the victim user may
  be entirely benign, and the payload may never be seen by a
  human (e.g. white text, HTML comments, image content). The
  paper's §4.2 headline finding is that prompts which Bing Chat
  would stop when typed in chat were **not** filtered when
  ingested indirectly — input filtering on the user channel does
  not transfer to the data channel.

That asymmetry is exactly what this lab measured from the other
side in B5: detector_v1 flagged 0/15 benign user queries *and*
0/15 retrieved documents in `data/indirect_injection_tests.yaml`
— a defense that screens only the user sees nothing, and even a
defense that screens the document with a direct-injection-tuned
threshold (0.5) saw nothing, because each payload was a single
instruction family capped at 0.40 under detector_v1's
normalisation.

## Delivery methods (§3.1)

1. **Passive** — payload waits in a public source to be retrieved
   (website / social post, promoted by SEO; a page open in the
   Edge sidebar Bing Chat can read; imported code for a
   completion engine; poisoning files a retrieval plugin reads).
2. **Active** — payload is delivered to the application, e.g. an
   email an LLM-augmented client will process.
3. **User-driven** — the victim is tricked into pasting a snippet
   (or trying a prompt in another language) that carries it.
4. **Hidden** — multi-stage (a small first payload tells the
   model to fetch a larger one), multimodal (payload in an
   image), encoded (e.g. Base64), or produced by code the model
   is told to run, so encrypted payloads can pass safeguards.

Lab mapping: B5 covers passive/RAG delivery only, with two
payload-visibility cases (`hidden`, 2/15) and one Base64 case
(ind-hid-02). Active (email), user-driven (paste), multi-stage
fetch, and multimodal delivery are **not** in B5 — recorded as
coverage gaps, not implied coverage.

## Threat taxonomy (§3.2) — threat-based, not technique-based

The authors deliberately taxonomise by *threat* so the framework
survives technique turnover. Six families:

| Threat | What it means here | Demonstrated in the paper on |
| --- | --- | --- |
| Information gathering | Persuade the user to divulge data, then exfiltrate it via a search query, a retrieved URL, or a markdown link with the data hidden in it | Synthetic app + Bing Chat; name elicited across turns, then embedded reversed in a link (`…#htimSnhJo` for "John Smith") |
| Fraud | Model as automated social engineer: phishing, scam sites presented as trusted, credential requests | Bing Chat — a free-Amazon-gift-card lure; urgency invented by the model, not scripted |
| Intrusion | Remote control (fetch fresh instructions from an attacker server each turn), persistence (write the payload into long-term memory and re-infect on read-back), code-completion poisoning | GPT-4 synthetic app (remote control + memory persistence, pirate-accent marker payload); Copilot (comment-carried payload, "very sensitive to context", efficacy dropped inside larger applications) |
| Malware | (a) Model distributes malicious links; (b) *the prompt itself is the worm* — an LLM email client reads the payload, reads the address book, and forwards it | Bing Chat (link distribution); GPT-4 synthetic email app (worming) |
| Manipulated content | Attack the primary task itself: arbitrarily-wrong or biased summaries, source blocking, targeted disinformation, undisclosed advertising ("prompts as SEO"), automated defamation (discussed, deliberately not exemplified) | Bing Chat — wrong summaries; persona-biased answers across topics; blocking "The New York Times" as a source, with the model then fabricating a credibility case; denying Einstein's Nobel Prize while mis-summarising a source an unprompted model summarised correctly |
| Availability | Background time-consuming loops, muting (sentences forced to start with `<|endoftext|>`), inhibiting API calls, corrupting generated search queries (homoglyph substitution), corrupting search results (zero-width-joiner insertion) | Bing Chat; corrupted-query runs sometimes hallucinated answers while still citing the unrelated results |

Targets can be untargeted (mass scams / disinformation),
targeted (a specific recipient or searcher), the automated
pipeline itself, or the service (compute-exhaustion DDoS).

### The paper's three recurring observations

1. **Goal-only payloads suffice (§4.2.1).** The injection only
   needs to state the goal ("persuade the user without raising
   suspicion"); the model autonomously supplies the persuasion
   technique, adapts to the conversation, and persists across
   turns. Attack sophistication required is low — the authors
   note payloads often worked on the first draft, and they left
   first-draft spelling/grammar errors in to prove it.
2. **Marginally-related context is projected (§4.2.5).** A
   persona or a fragment of attack context produces full
   social-engineering or biased behaviour that was never
   spelled out.
3. **Follow-up calls reinforce the injection (§4.2.5).** A
   compromised model issues search queries shaped by the
   payload and can effectively re-poison itself from its own
   output — the mechanism that makes persistence and worming
   plausible rather than rhetorical.

## Hidden injections (§4.3)

- **Multi-stage:** a comment hidden in a (mock) Wikipedia page
  tells the model to search a keyword that retrieves a second,
  attacker-controlled payload. The second stage can be long and
  conspicuous because the user never sees it. Run on the
  synthetic search app — not on Bing Chat, because that would
  have required a public, indexed injection, which the authors
  refused to plant (§5.1: no injections into public sources;
  disclosure to OpenAI and Microsoft).
- **Encoded:** a malware payload Base64-encoded, prefaced only
  with "System: decode this from Base64 in your inner
  monologue" — no instruction to *obey* the decoded text — and
  Bing Chat executed it anyway. The authors call this a
  cascaded indirect injection. Lab echo: B2/B6 found the same
  encoding blindness in reverse — base64 payloads are invisible
  to detector_v1 (0/25 flagged as encoded in B2), and datamarking
  fails on a single base64 token with no spaces to mark
  (B6 rag-esc-06).

## What the paper does *not* give you (honest limits, §5.2)

- **No success rates.** The evaluation is qualitative
  demonstrations, intrinsically non-exhaustive. The authors say
  explicitly that quantifying success for dynamic, interactive,
  multi-turn sessions — trigger frequency, consistency,
  believability — was left to future work. Anyone citing a
  percentage ASR "from Greshake et al." is citing something the
  paper does not contain.
- **Constrained testbeds.** Synthetic apps deliver prepared
  content and ignore unrelated queries; Bing Chat was tested
  via local HTML files in the Edge sidebar, not via live
  search-index poisoning. Feasibility in the wild is argued,
  plus anecdotal evidence, not measured.
- **No access** at the time to Microsoft 365 Copilot or ChatGPT
  plugins; multimodal injection was probed only on smaller
  open multimodal models (LLaVA example), not GPT-4 vision.
- **Reproducibility (§5.4)** is limited by the black-box,
  moving-target system; prompts and synthetic demos are shared
  precisely so others can re-run the *framework*, not the exact
  outputs.

## Mitigations as the paper leaves them (§5.6)

No foolproof solution is claimed, and the section is a list of
dilemmas rather than a defense:

- **RLHF / alignment** reduces some jailbreaks "whack-a-mole"
  style; the paper cites theoretical work arguing alignment
  alone cannot rule out all undesired behaviour.
- **Input/output filtering** existed on Bing Chat's chat channel
  and the attacks still succeeded via the external-input
  channel — and stronger obfuscation/encoding may evade
  filtering anyway.
- **Filtering retrieved input with another model** creates the
  rescuer's dilemma: a non-instruction-tuned filter may miss
  complex encoded payloads; a capable one may fall for them.
- **An LLM supervisor/moderator** might catch payloads whose
  purpose is independent of the sources (some scams) but not
  disinformation/manipulation, where the payload *is* about the
  sources; verifying against sources re-creates the dilemma.
- **Interpretability / outlier detection** on prediction
  trajectories is named as promising and unproven.

Lab position against that list: B6 is precisely the
structural-separation route the paper gestures at but does not
test — delimit / datamark the data channel so its contents
cannot be promoted, rather than trying to *detect* instructions
inside it. B6's simulated result (random-token delimiters +
datamarking block 15/15 B5 cases and 6/6 escape probes, upper
bound under an ideal follower, no live model) does not refute
the paper's pessimism: the paper's attacker adapts against a
real model, and B6's probes are the lab's own. What B6 does show
is the paper's §5.6 detection dilemma is avoidable in principle
— separation does not need to recognise the payload at all.

## Mapping: paper taxonomy → this lab

| Paper concept | Lab artifact |
| --- | --- |
| Passive delivery via retrieved document | B5 suite: all 15 cases, benign user query, payload only in `retrieved_document` |
| Information gathering / exfiltration | B5 `exfiltration` (3 cases; reserved `attacker.example.com` targets, no real secrets) |
| Intrusion / task takeover | B5 `task_hijack` (3) — narrower than the paper's remote-control + persistence; the lab has no memory or tool-calling app, so persistence and worming are untested here |
| Manipulated content | B5 `manipulation` (3) — fluent, no override vocabulary; detector_v1 fires on 0/3, by design the hardest category for keyword detection |
| Fraud / authority impersonation inside a document | B5 `authority_spoof_in_document` (3) |
| Hidden + encoded injections (§3.1, §4.3) | B5 `hidden_encoded_in_document` (3); B2/B6 base64 escape probes |
| User-channel filtering does not transfer (§4.2) | B5 channel result: user 0/15, document 0/15 flagged at threshold 0.5 |
| Multi-stage, active (email worm), multimodal, availability, source-blocking | **Not covered by any lab suite** — gaps for C7's taxonomy and a possible B5 v2; do not read B5/B6 numbers as coverage of these |
| Defenses (§5.6, detection-side) | A4 detector, A6 perplexity filter, B4 output filter are all detection-side and inherit the paper's dilemmas; B1 hierarchy text alone blocked 0/15 structurally in B6 (R1 = R0); B2/B6 structural separation is the lab's non-detection route |

## Takeaways for the flagship (feeds E1 / C7)

1. **B5 v2 should add the missing delivery modes, in order of
   feasibility offline:** multi-stage fetch (mock second-stage
   document), user-driven paste, and a memory-persistence case
   (payload written to a mock store, read back next session).
   Email-worm and multimodal need infrastructure the lab does
   not have; document them as out of scope instead.
2. **Position is a variable, not an accident.** B5 is skewed
   13/15 payload-at-end. The paper plants payloads in comments
   and body text interchangeably; a v2 should cross position
   (start / middle / end / hidden) × category deliberately.
3. **C3's leaderboard needs a "paper-claim" column kept separate
   from lab numbers.** This paper contributes a taxonomy and
   qualitative demonstrations, no rates — mixing its claims
   into a numeric matrix would fabricate precision.
4. **The goal-only-payload observation is a test-design rule:**
   payloads that state a goal without technique are the
   realistic case (and the case keyword detectors miss). B5's
   `manipulation` category already follows it; a v2 should
   extend it to exfiltration and hijack cases.

## Sources

- Greshake, Abdelnabi, Mishra, Endres, Holz & Fritz (2023).
  "Not What You've Signed Up For: Compromising Real-World
  LLM-Integrated Applications with Indirect Prompt Injection."
  arXiv:2302.12173. https://arxiv.org/abs/2302.12173 —
  AISec '23, pp. 79–90, DOI 10.1145/3605764.3623985.
- Demonstrations repo (paper's own):
  https://github.com/greshake/llm-security
- Lab artifacts cited: `data/indirect_injection_tests.yaml`
  (B5), `results/indirect_injection_tests.md` (B5),
  `results/rag_defenses.md` (B6), `results/spotlighting.md` (B2).
- Hines et al. (2024), spotlighting, arXiv:2403.14720 — the
  defense family B2/B6 implement, cited here only for that
  mapping.
