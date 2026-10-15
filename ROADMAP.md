# Research roadmap — one task per day

Checked off as completed. When fewer than 5 unchecked tasks remain, append 10 more: survey the current state of the art, then propose the next experiments. Keep every task concrete and verifiable — code, data, or notes that can be reviewed.

## A. Harness & data
- [ ] A1. Scaffold eval harness: `eval/run.py` loads YAML suites, runs defenses, writes JSONL results + a Markdown summary
- [ ] A2. `data/injection_tests.yaml`: 25 hand-written prompt-injection cases across 5 categories (direct override, roleplay, encoded payload, multi-turn, authority claim), each with expected behavior
- [ ] A3. `data/jailbreak_corpus.md`: curated public jailbreak prompts with sources cited (JailbreakBench etc.) + a stats script
- [ ] A4. Heuristic detector v1 (regex + keyword features); evaluate on A2; `results/detector_v1.md`
- [ ] A5. Paper notes: Zou et al. 2023, "Universal and Transferable Adversarial Attacks on Aligned Language Models" → `notes/gcg.md`
- [ ] A6. Perplexity filter with distilgpt2 (CPU): benign vs adversarial-suffix perplexity; `results/perplexity_filter.md`

## B. Defenses
- [ ] B1. System-prompt hardening, 3 levels; A/B on injection suite; record deltas
- [ ] B2. Delimiting + spotlighting (datamarking) defenses; compare against B1
- [ ] B3. Paper notes: Wei et al. 2023, "Jailbroken: How Does LLM Safety Training Fail?" → `notes/jailbreak_failure_modes.md`
- [ ] B4. Output filter: policy keywords + TF-IDF similarity check (offline, sklearn)
- [ ] B5. `data/indirect_injection_tests.yaml`: 15 indirect prompt-injection cases via retrieved documents (RAG setting)
- [ ] B6. RAG defenses: datamark retrieved content + instruction hierarchy; evaluate on B5

## C. Analysis & survey
- [ ] C1. Paper notes: Liu et al. 2023 prompt-injection survey → `notes/prompt_injection_survey.md`
- [ ] C2. Paper notes: Greshake et al., "Not what you've signed up for" (indirect injection) → `notes/indirect_injection.md`
- [ ] C3. `results/leaderboard.md`: defense × attack matrix from all runs so far
- [ ] C4. Reproduced figure: perplexity distribution (benign vs attack), matplotlib → `figures/perplexity_dist.png`
- [ ] C5. Paper notes: "StruQ: Defending Against Prompt Injection with Structured Queries" → `notes/struq.md`
- [ ] C6. Structured-query defense prototype: separate prompt/data channels in the harness
- [ ] C7. `TAXONOMY.md`: full attack/defense taxonomy with paper links
- [ ] C8. Paper notes: Anthropic, "Many-shot jailbreaking" → `notes/many_shot.md`

## D. Deepening
- [ ] D1. Many-shot simulation offline: context-length effects on distilgpt2 behavior; record honestly what transfers and what doesn't
- [ ] D2. Paper notes: "HarmBench" framework → `notes/harmbench.md`; map harness categories to HarmBench
- [ ] D3. Refusal-phrasing classifier: tiny logistic regression on synthetic refusal/compliance data (documented as synthetic)
- [ ] D4. Paper notes: Bai et al., "Constitutional AI" → `notes/constitutional_ai.md`
- [ ] D5. Red-team/blue-team loop offline: random-search suffix generator vs perplexity filter; `results/redteam_blueteam.md`
- [ ] D6. Paper notes: gradient-based adversarial attacks follow-ups → `notes/adv_nlp_survey.md`
- [ ] D7. Month-1 retro: `notes/month_1_retro.md` — what worked, open questions, flagship seeds

## E. Toward the flagship
- [ ] E1. `proposals/flagship_candidates.md`: 3 candidate flagship research questions
- [ ] E2. `data/flagship_dataset_spec.md`: dataset design for the chosen question
- [ ] E3. Baseline results on the flagship dataset
- [ ] E4. First preprint outline: `paper/outline.md`
