# Jailbreak corpus statistics

Run date: 2026-10-17 | Corpus: `data/jailbreak_corpus.md` | Tool: `eval/corpus_stats.py`

Total entries: **20**

## By technique family

| Technique | Count |
| --- | --- |
| roleplay | 4 |
| encoding | 4 |
| multi-turn | 4 |
| fictional-framing | 3 |
| authority-claim | 2 |
| refusal-suppression | 2 |
| adversarial-suffix | 1 |

## By source citation

| Source | Count |
| --- | --- |
| JailbreakBench (Chao et al., 2024) | 5 |
| Wei et al., "Jailbroken" (2023) | 3 |
| HarmBench (Mazeika et al., 2024) | 2 |
| This lab's A2 suite | 2 |
| Andriushchenko et al. (2024) | 2 |
| Crescendo (Russinovich et al., 2024) | 1 |
| Low-resource languages (Yong et al., 2024) | 1 |
| FlowGPT / JailbreakChat (community) | 1 |
| ArtPrompt (Jiang et al., 2024) | 1 |
| PAIR (Chao et al., 2023) | 1 |
| Many-shot jailbreaking (Anthropic, 2024) | 1 |

## By target harm category

| Target | Count |
| --- | --- |
| general | 6 |
| malware | 3 |
| disinformation | 3 |
| fraud | 3 |
| privacy | 2 |
| physical-harm | 1 |
| harassment | 1 |
| economic-harm | 1 |

## Prompt length (the representative excerpts, not full originals)

- Characters: min 137, mean 233, max 348 (JB-003)
- Words: min 11, mean 38, max 66 (JB-003)
- Shortest entry: JB-017 (GCG-style adversarial suffix (gradient attack artifact)), 137 chars

## Top content tokens (length > 3, stopwords removed)

| Token | Count |
| --- | --- |
| mode | 7 |
| write | 6 |
| developer | 5 |
| turn | 5 |
| user | 5 |
| character | 4 |
| story | 4 |
| answer | 4 |
| about | 4 |
| opposite | 4 |
| instructions | 3 |
| following | 3 |
| word | 3 |
| request | 3 |
| exact | 3 |

## Notes

- Entries are hand-curated, representative excerpts for defensive-evaluation purposes; lengths reflect the excerpts, not the original full prompts.
- `adversarial-suffix` (JB-017) is the only automated-optimization entry; the rest are human-written templates from public compilations.
- Source bucketing is first-match on citation text: JB-017 (GCG suffix) is counted under JailbreakBench because its citation notes the suffixes ship in the JailbreakBench artifact set; the GCG paper itself is cited in its entry.
