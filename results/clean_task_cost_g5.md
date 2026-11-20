# G5 — Clean-task cost of the B2/B6/C6 front-ends (2026-11-19)

Suite: G4 `data/clean_tasks.yaml` (24 tasks; validator re-run, 24/24 pass).
Code: `eval/clean_task_cost.py` (5 unit tests pass) — B2/B6/C6 modules
imported unchanged. Rows: `results/clean_task_cost_g5_rows.jsonl`
(384 = 16 variants × 24 tasks); summary JSON alongside.

## Reader model (bounded claim)

No live model exists in this lab. The reader is G4's deterministic
keyword-overlap scorer (baseline **7/24**: extract 0/8, QA 0/8,
extractive-summary 7/8), applied two ways per variant:

- **Aware** — the pipeline inverts the transform with the front-end's
  own recovery function before reading. Measures *information loss*.
- **Naive** — the scorer reads the transformed text directly.
  Measures the cost a pipeline that forgets to invert would pay.

Neither number is a live-model utility number.

## Results (F4 triple format)

| Variant | Robustness (prior reports, not re-measured) | Benign cost: aware acc. | Naive acc. | Recovery exact | Compute: mean char overhead |
|---|---|---|---|---|---|
| S0 none | A2 0/25 blocked | 7/24 | 7/24 | 24/24 | 1.000× |
| S1 fixed delim. | A2 25/25, probes 6/8; adaptive 0/25 (F6) | 7/24 | 7/24 | 24/24 | 1.488× |
| S2 random delim. | A2 25/25, probes 8/8; adaptive 25/25 | 7/24 | 7/24 | 24/24 | 1.507× |
| S3 datamarking | A2 25/25, probes 5/8; adaptive 0/25 | 7/24 | **0/24** | 24/24 | 1.000× |
| S4 combined | A2 25/25, probes 8/8; adaptive 25/25 | 7/24 | **0/24** | 24/24 | 1.507× |
| S5 base64 | A2 25/25, probes 8/8 | 7/24 | **0/24** | 24/24 | 1.344× |
| R0 naive RAG | B5 0/15 | 7/24 | 7/24 | 24/24 | 1.000× |
| R1 hierarchy only | B5 0/15, probes 0/6 | 7/24 | 7/24 | 24/24 | 1.000× |
| R2 hier.+fixed | B5 15/15, probes 4/6; adaptive 0/15 | 7/24 | 7/24 | 24/24 | 1.488× |
| R3 hier.+random | B5 15/15, probes 6/6; adaptive 15/15 | 7/24 | 7/24 | 24/24 | 1.507× |
| R4 hier.+datamark | B5 15/15, probes 3/6; adaptive 0/15 | 7/24 | **0/24** | 24/24 | 1.000× |
| R5 hier.+combined | B5 15/15, probes 6/6; adaptive 15/15 | 7/24 | **0/24** | 24/24 | 1.507× |
| Q0 naive concat. | completion 0/13 | 7/24 | **0/24** | 24/24 | 1.363× |
| Q1 Alpaca delim. | completion 10/13 | 7/24 | **0/24** | 24/24 | 1.776× |
| Q2 reserved delim. | completion 10/13 | 7/24 | **0/24** | 24/24 | 1.917× |
| Q3 reserved+filter | completion 13/13 | 7/24 | **0/24** | 24/24 | 1.917× |

## Findings

1. **Information loss is zero for every front-end on this suite.**
   Aware accuracy equals the undefended baseline (7/24) for all 16
   variants and recovery is exact on 24/24 tasks each — every B2/B6
   transform is exactly invertible and, on this suite, so is Q3.
2. **The cost is an integration cost, not a transform cost.** A
   reader handed the raw transformed text scores 0/24 under
   datamarking (S3/S4/R4/R5), base64 (S5) and every structured-query
   assembly (Q0–Q3 — the prepended instruction itself wins the
   keyword-overlap vote), while plain delimiters (S1/S2/R2/R3) cost
   nothing even naively. The benign-cost question is therefore
   "does the pipeline invert?" before it is "which defense?".
3. **E1's Q3 prediction is UNTESTED here, recorded as a gap.** E1
   predicted Q3's lossy filter cost concentrates on format-bearing
   documents. The G4 suite contains zero inputs with `##` or
   reserved-token strings (verified by grep), so the filter never
   fires and Q3's recovery is exact 24/24. A format-bearing
   clean-task extension is required before that prediction can be
   scored — not claimed either way.
4. Compute cost is modest and known in advance: delimiters add
   ~49–51% characters on these short inputs, structured assembly
   up to 1.917× (Q2/Q3), datamarking 1.000× (same length, marked).

## Limits

Deterministic reader only (information loss, not model confusion —
the E1 Candidate 2 Phase-1 bound). The reader itself is weak
(7/24, 0 on span tasks), so accuracy deltas are coarse; recovery
exactness (24/24) is the sharper instrument and it agrees.
Robustness column quotes prior committed reports, per-suite kept
separate as in C3; nothing was re-measured on attack suites.
