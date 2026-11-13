# Preprint outline — flagship paper (ROADMAP task E4)

**Date:** 2026-11-13 (Day 31 of the daily lab)
**Task:** E4. **Status:** outline only — the paper's structure, claims
ledger and drafting plan. Every empirical claim in the eventual draft
must trace to a committed lab report listed in §8; nothing in this
outline is itself a result. The flagship question, predictions and
verdict bands are frozen in E1 (`proposals/flagship_candidates.md`)
and E2 (`data/flagship_dataset_spec.md`); E3
(`results/flagship_baselines.md`) is the baseline run this outline is
built around.

---

## 1. Working title

Primary: **"Does Windowed Perplexity Survive Amortised Suffixes?
A Pre-Registered, Frozen-Pipeline Test of a Widely-Cited Detector
Number"**

Alternates (keep until the AMP arms resolve — the honest title depends
on which paper this becomes, §7):

- A (AMP corpus obtained, P1 supported): "Amortised Gibberish Breaks
  the Window: Windowed Perplexity After AmpleGCG"
- B (AMP corpus obtained, P1 refuted): "The Window Holds: Windowed
  Perplexity Is Robust to a Generator-Distribution Shift"
- C (corpus still blocked at draft time): "A Frozen Pipeline, an
  Unobtainable Corpus: Pre-Registration and Reproducibility Notes
  for Perplexity-Defense Evaluation" — a methods/short paper built
  on G1/G2 + S1, with the blocked primary question stated as its
  central limitation, not hidden in a footnote.

## 2. One-paragraph pitch (for the abstract's first draft)

Perplexity filtering is among the most-cited baseline defenses
against adversarial suffix attacks on LLMs (Jain et al. 2023), and
its windowed variant carries the strongest reported separation in
small-scale replications — in this lab, windowed AUROC 0.887 for
hand-written gibberish suffixes vs benign text (A6). That number,
however, was produced against suffixes from a different generator
distribution than modern attacks use, and its most-cited evasion
(AmpleGCG's repetition dilution, 80% ASR under a whole-prompt
detector) was never evaluated against the windowed score. We
pre-registered three predictions with verdict bands before scoring
(E2), froze the detector pipeline, benign reference set and corpus
selection rule, and ran the baseline (E3): the pipeline reproduces
its Month-1 reference numbers exactly and D5's windowed result under
rescoring, dilution is shown to be a full-text phenomenon that a
max-window statistic structurally resists (on lab suffixes), and the
primary AmpleGCG arms are reported BLOCKED because the corpus is not
published in obtainable form — a reproducibility finding about the
field's artefact practices in its own right. [When the AMP arms are
scored, this paragraph gains one sentence: the P1–P3 verdicts, in the
frozen bands' language.]

## 3. Section plan

1. **Introduction.** The detector claim and why its scope matters;
   the two unexamined gaps (generator-distribution shift; dilution
   evaluated only whole-prompt). Contributions list, in order:
   (i) a pre-registered protocol with frozen verdict bands for a
   detector-separability question; (ii) an end-to-end reproduction
   of the pipeline's own reference numbers (G1/G2) before any new
   measurement is trusted; (iii) the dilution dose–response S1;
   (iv) the AMP verdicts when scored, or the blocked-corpus
   reproducibility report until then. Scope sentence, verbatim in
   spirit from E2 §8: *this is a study of a detector, not of any
   model's jailbreak resistance; no ASR is measured or claimed.*
2. **Related work.** Jain et al. 2023 (filter design); Zou et al.
   2023 (GCG, AdvBench); Liao & Sun 2024 (AmpleGCG — amortised
   gibberish, *not* fluency-optimised; the E1→E2 correction is
   reported here as a framing lesson); Kumar et al. 2024
   (AmpleGCG-Plus, supersession risk R5); the D6 follow-up families
   (I-GCG, PGD, BEAST, AutoDAN-Zhu/Liu, COLD-Attack, AdvPrompter)
   as the fluency-objective context that is explicitly out of E3
   scope; Nasr et al. 2025 (adaptive evaluation — why fixed-suite
   numbers, including this paper's, are upper bounds on defense
   strength); CaMeL / MELON / Meta SecAlign / Constitutional
   Classifiers as the design-based and training-based alternatives
   whose cost/robustness reporting this paper's protocol borrows.
3. **Method.** Frozen pipeline (distilgpt2; full-text + 10-token
   windowed perplexity; functions imported unchanged from A6);
   frozen reference arms (BEN/NAT/SYN-FROZEN, n = 10/25/15, reused
   never rescored); the 7-arm manifest (159 planned rows) and its
   per-arm status; the frozen selection rule for AMP-PRIMARY
   (first 25 queries in file order × first 2 successful suffixes);
   construction rules R-REP / R-AID; gates G1–G4; analysis plan
   (per-arm AUROC + 1,000-resample bootstrap 95% CI, full ROC for
   P3, length sensitivity check). A "what was frozen when" timeline
   table: E1 predictions 2026-11-11 → E2 bands + spec 2026-11-12 →
   E3 scoring 2026-11-13.
4. **Results.** In gate order, not headline order: G1 (reference
   recomputation), G2 (D5 rescore vs committed windowed values),
   S1 (dilution dose–response with medians at j = 1/2/4 and the
   case-level count below the 609.1 reference line), then P1–P3 —
   each stated in its frozen band language, including BLOCKED /
   UNANSWERED as a first-class verdict for E3. Tables T1–T3 and
   Figures F1–F2 (§5). No number appears in this section that is
   not in a committed `results/` file.
5. **Discussion.** What the windowed statistic does and does not
   buy: a max-window score cannot be diluted by construction, but
   A6's repetition evaders (suf-07/08) already sit below the benign
   median, so the window is not a defense — it is a differently
   scoped detector. The optimiser-not-attack-class scoping (D6):
   every perplexity number is a statement about a suffix
   *distribution*, and papers should name the distribution the way
   they name the model. The blocked corpus as a field-level
   reproducibility problem: a defense-relevant artefact gated
   behind verified-organisation requests cannot be independently
   re-measured by small labs, which is precisely where replication
   capacity lives.
6. **Limitations.** Benign n = 10 (coarse AUROC steps, wide CIs —
   accepted for A6 comparability, E2 §2); distilgpt2 as proxy
   scorer (R3); no live aligned model anywhere in the lab, so no
   behavioural claim (the standing Month-1 limit, D7 §4); the AMP
   arms' blocked status; AmpleGCG-Plus supersession (R5).
7. **Reproducibility statement.** Repo, commit SHAs for E1/E2/E3,
   the spec checker (`eval/flagship_spec_check.py`) as the
   executable form of the pre-registration, per-case JSONL rows for
   every scored arm, and the exact unblock condition for the AMP
   arms (E3 report, final section).
8. **References.** §8 of this outline; formatted at draft time.

## 4. Claims ledger (each claim → its only permitted evidence)

| # | Claim the draft may make | Evidence |
|---|---|---|
| C1 | Windowed AUROC 0.887 (SYN vs BEN, A6 pipeline) | A6 report + E3 G1 recomputation |
| C2 | D5's windowed layer caught all 3 hill-climb finals | D5 report + E3 G2 rescore |
| C3 | Dilution lowers full-text PPL monotonically (j = 1→2→4) and barely moves the windowed median | E3 S1 (lab suffixes only — never as an AmpleGCG claim) |
| C4 | AmpleGCG publishes no static suffix corpus; access is verified-organisation request only | Paper §4/ethics text, cited in E2 §5 |
| C5 | P1–P3 verdicts | E3 (currently: BLOCKED/UNANSWERED) — the draft may not state any other status |
| C6 | Repetition suffixes evade both scores entirely | A6 (suf-07/08) + D5 repetition controls + E3 D5-RESCORE |
| C7 | Any field number (80% AID ASR, TAP/GCG ASRs, CC++ overhead…) | The cited paper only, labelled as the paper's |

Claims the draft may **never** make: any ASR or "the defense works /
fails against AmpleGCG" statement from perplexity scores alone;
any S1-derived statement about AmpleGCG suffixes; any pooled or
cross-suite AUROC (the C3 suite-separation rule).

## 5. Tables and figures plan

- **T1.** Arm table: 7 arms × (n planned, n scored, status, source).
  From the E3 manifest, generated not transcribed.
- **T2.** Per-arm medians/ranges + AUROC with bootstrap CI (E3
  report's table, extended with the AMP rows when scored).
- **T3.** Frozen-timeline / pre-registration table (§3 above).
- **F1.** Perplexity distributions: the C4 figure extended with the
  REP-DILUTION j = 2/4 arms (same log-axis style).
- **F2.** Dilution dose–response: full-text vs windowed median by
  repeat factor (E3 S1), with the 609.1 / 814.85 reference lines.
- **F3 (conditional).** AMP-PRIMARY windowed ROC with the P3 gate —
  drawn only when the arm is scored.

## 6. Venue and timeline plan

- Target shape: short empirical paper / workshop submission first
  (per E1: "the D7 §7 plan's natural first preprint"), arXiv
  preprint on posting. Venue shortlist is a later task — this
  outline fixes only the paper's shape and evidence rules.
- Timeline against the goal plan: results complete when the AMP
  arms resolve or are formally abandoned at the Feb 2027 milestone;
  draft v1 in the Apr 2027 slot; feedback round May 2027; post Jun
  2027. The blocked-corpus variant (title C) is the fallback if
  access has not resolved by Feb 2027 — decided then, not now.

## 7. Open decisions (for Jasper / the next lab runs)

1. Whether to send the verified-organisation corpus request in
   Jasper's name / a Webster affiliation — the single action that
   unblocks the flagship's headline. (E3 does not send it: it is an
   outward request under Jasper's identity, for Jasper to approve.)
2. Title variant A/B/C once decision 1 resolves.
3. Whether Candidate 3 (known-answer detection) runs as the
   parallel methods thread feeding §2/§5 of this paper or stands
   as paper #2 (E1 §4 recommends the latter).

## 8. Sources

- Liao & Sun 2024, "AmpleGCG…", COLM 2024, arXiv:2404.07921 —
  https://arxiv.org/abs/2404.07921
- Kumar et al. 2024, "AmpleGCG-Plus…", arXiv:2410.22143 —
  https://arxiv.org/abs/2410.22143
- Jain et al. 2023, "Baseline Defenses…", arXiv:2309.00614 —
  https://arxiv.org/abs/2309.00614
- Zou et al. 2023, "Universal and Transferable Adversarial Attacks…",
  arXiv:2307.15043 — https://arxiv.org/abs/2307.15043
- Nasr et al. 2025, "The Attacker Moves Second", arXiv:2510.09023 —
  https://arxiv.org/abs/2510.09023
- Lab-internal: E1 `proposals/flagship_candidates.md`; E2
  `data/flagship_dataset_spec.md`; E3 `results/flagship_baselines.md`
  + `results/flagship_rows.jsonl` + `data/flagship_manifest.yaml`;
  A6 `results/perplexity_filter.md`; D5
  `results/redteam_blueteam.md`; D6 `notes/adv_nlp_survey.md`; D7
  `notes/month_1_retro.md`.
