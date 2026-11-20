#!/usr/bin/env python3
"""G5 — Clean-task cost measurement for the lab's structural front-ends.

E1 Candidate 2 / D7: before any clean-task cost claim, measure task
accuracy per defense on the G4 suite (`data/clean_tasks.yaml`, 24
programmatic-check tasks). This script runs the B2 (S0–S5), B6 (R0–R5)
and C6 (Q0–Q3) front-ends over every G4 task and reports, per variant,
the F4 triple format:

  1. robustness — the variant's previously reported attack-suite
     numbers (B2/B6/C6 reports, quoted, NOT re-measured here);
  2. benign cost — task accuracy of a deterministic reader on the
     front-end's output, vs the undefended G4 baseline;
  3. compute cost — character overhead ratio of the transformed
     prompt/document vs the original input (mean over tasks).

Reader model (bounded claim, stated in the report): there is no live
model in this lab, so the "reader" is G4's deterministic
keyword-overlap scorer (the stronger G4 baseline, 7/24) applied in
two modes:
  - aware: the pipeline first inverts the front-end transform with
    the front-end's own recovery function (what a correctly built
    pipeline hands the model), then scores;
  - naive: the scorer reads the transformed text directly (what a
    pipeline that forgets to invert would hand the model).
Aware-mode accuracy therefore measures INFORMATION LOSS of the
transform (only a non-invertible step, e.g. C6 Q3's lossy filter,
can cost accuracy); naive-mode accuracy measures how much of the
cost a careless integration would pay. Neither is a live-model
utility number.

Run: python eval/clean_task_cost.py
Outputs: results/clean_task_cost_g5_rows.jsonl,
         results/clean_task_cost_g5_summary.json,
         results/clean_task_cost_g5.md
"""
import base64
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clean_tasks as ct  # G4 validator + baselines, unchanged
import rag_defenses as rg  # B6, unchanged
import spotlighting as sp  # B2, unchanged
import structured_query as sq  # C6, unchanged

ROOT = Path(__file__).resolve().parent.parent
SUITE = ROOT / "data" / "clean_tasks.yaml"

READER = ct.BASELINE_keyword_overlap if hasattr(ct, "BASELINE_keyword_overlap") else None


def reader_answer(input_text, instruction):
    """G4 keyword-overlap baseline applied to an arbitrary input text."""
    task = {"input": input_text, "instruction": instruction}
    return ct.baseline_keyword_overlap(task)


def score_variant(recovered_list, tasks):
    correct = 0
    per_type = {}
    for rec, t in zip(recovered_list, tasks):
        ok = ct.exact_match(reader_answer(rec, t["instruction"]), t["expected"])
        correct += ok
        a, b = per_type.get(t["type"], (0, 0))
        per_type[t["type"]] = (a + ok, b + 1)
    return correct, {k: f"{a}/{b}" for k, (a, b) in per_type.items()}


# --- B2 recovery (mirror of B6's recover_document logic + S5 decode) ---
def recover_s(variant, seg, case_id):
    if variant == "S0":
        return seg
    if variant in ("S1", "S2", "S4"):
        data, _ = sp.split_channels(variant, seg)
        return data
    if variant == "S3":
        return sp.undatamark(seg)
    if variant == "S5":
        return base64.b64decode(seg.strip()).decode("utf-8")
    raise ValueError(variant)


def recover_r(variant, seg, case_id):
    return rg.recover_document(variant, seg, case_id)


def recover_q(variant, prompt, data):
    """Extract the data segment from a C6 assembled query."""
    assembled = sq.assemble(variant, prompt, data)
    if variant == "Q0":
        return data
    if variant == "Q1":
        seg = assembled.split(sq.ALPACA_INPT, 1)[1]
        return seg.split(sq.ALPACA_RESP)[0].strip("\n")
    seg = assembled.split(sq.RES_INPT, 1)[1]
    return seg.split(sq.RES_RESP)[0].strip("\n")


ROBUSTNESS = {
    # Quoted from the committed B2/B6/C6 reports (see ROADMAP B2/B6/C6
    # lines); NOT re-measured in G5.
    "S0": "A2 0/25 blocked (control, B2 report)",
    "S1": "A2 25/25, probes 6/8 (B2); adaptive 0/25 (F6)",
    "S2": "A2 25/25, probes 8/8 (B2); adaptive 25/25 (F6)",
    "S3": "A2 25/25, probes 5/8 (B2); adaptive 0/25 (F6)",
    "S4": "A2 25/25, probes 8/8 (B2); adaptive 25/25 (F6)",
    "S5": "A2 25/25, probes 8/8 (B2)",
    "R0": "B5 0/15 blocked (control, B6 report)",
    "R1": "B5 0/15, probes 0/6 (B6)",
    "R2": "B5 15/15, probes 4/6 (B6); adaptive 0/15 (F6)",
    "R3": "B5 15/15, probes 6/6 (B6); adaptive 15/15 (F6)",
    "R4": "B5 15/15, probes 3/6 (B6); adaptive 0/15 (F6)",
    "R5": "B5 15/15, probes 6/6 (B6); adaptive 15/15 (F6)",
    "Q0": "completion suite 0/13 blocked (control, C6 report)",
    "Q1": "completion suite 10/13 (C6)",
    "Q2": "completion suite 10/13 (C6)",
    "Q3": "completion suite 13/13 (C6)",
}


def main():
    doc = yaml.safe_load(SUITE.read_text())
    tasks = doc["tasks"]
    errors = ct.validate(tasks)
    if errors:
        raise SystemExit("G4 suite validation failed:\n" + "\n".join(errors))

    base_correct, base_per_type = score_variant([t["input"] for t in tasks], tasks)
    rows, summary = [], {"n_tasks": len(tasks),
                         "baseline_keyword_overlap": f"{base_correct}/{len(tasks)}",
                         "baseline_per_type": base_per_type, "variants": {}}

    def record(group, variant, aware_texts, naive_texts, overheads):
        ac, apt = score_variant(aware_texts, tasks)
        nc, _ = score_variant(naive_texts, tasks)
        fidelity = sum(a == t["input"] for a, t in zip(aware_texts, tasks))
        summary["variants"][variant] = {
            "group": group, "aware_accuracy": f"{ac}/{len(tasks)}",
            "aware_per_type": apt, "naive_accuracy": f"{nc}/{len(tasks)}",
            "recovery_exact": f"{fidelity}/{len(tasks)}",
            "mean_overhead_ratio": round(sum(overheads) / len(overheads), 3),
            "robustness_prior": ROBUSTNESS[variant]}
        for t, aw, nv, oh in zip(tasks, aware_texts, naive_texts, overheads):
            rows.append({"variant": variant, "group": group, "id": t["id"],
                         "type": t["type"],
                         "aware_correct": ct.exact_match(
                             reader_answer(aw, t["instruction"]), t["expected"]),
                         "naive_correct": ct.exact_match(
                             reader_answer(nv, t["instruction"]), t["expected"]),
                         "recovery_exact": aw == t["input"],
                         "overhead_ratio": round(oh, 3)})

    for v in ("S0", "S1", "S2", "S3", "S4", "S5"):
        segs = [sp.transform_body(v, t["input"], t["id"]) for t in tasks]
        record("B2", v, [recover_s(v, s, t["id"]) for s, t in zip(segs, tasks)],
               segs, [len(s) / len(t["input"]) for s, t in zip(segs, tasks)])
    for v in ("R0", "R1", "R2", "R3", "R4", "R5"):
        segs = [rg.transform_document(v, t["input"], t["id"]) for t in tasks]
        record("B6", v, [recover_r(v, s, t["id"]) for s, t in zip(segs, tasks)],
               segs, [len(s) / len(t["input"]) for s, t in zip(segs, tasks)])
    for v in ("Q0", "Q1", "Q2", "Q3"):
        asm = [sq.assemble(v, t["instruction"], t["input"]) for t in tasks]
        record("C6", v, [recover_q(v, t["instruction"], t["input"]) for t in tasks],
               asm, [len(a) / len(t["input"]) for a, t in zip(asm, tasks)])

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with open(out / "clean_task_cost_g5_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(out / "clean_task_cost_g5_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
