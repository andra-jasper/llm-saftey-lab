#!/usr/bin/env python3
"""G4 — Clean-task suite v1: validator + baseline scorers.

The suite exists so defense evaluations can report BENIGN COST
(task accuracy under a defense) instead of only attack detection —
the dataset E1 Candidate 2 and D7 require before any clean-task
cost claim. Every task is programmatic-check: the expected answer
is an exact substring of the input, scored by normalised exact
match (lowercase, strip punctuation, collapse whitespace).

This script:
  1. validates the suite (schema, unique ids, expected is a
     substring of input, per-type counts);
  2. scores two deterministic baselines to prove the checker is
     live and to set the floor G5 must beat:
       - first_sentence: return the input's first sentence;
       - keyword_overlap: return the sentence (or, for short
         inputs, the input itself) sharing the most content words
         with the instruction — for extract/qa, if the best
         sentence is the whole input, return it unchanged;
  3. writes results/clean_tasks_g4_rows.jsonl +
     results/clean_tasks_g4_summary.json.

Run: python eval/clean_tasks.py
"""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SUITE = ROOT / "data" / "clean_tasks.yaml"
TYPES = ("extract", "qa", "extractive_summary")


def normalise(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def exact_match(pred, expected):
    return normalise(pred) == normalise(expected)


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def content_words(s):
    stop = {"the", "a", "an", "of", "is", "was", "what", "which", "how",
            "many", "much", "return", "sentence", "that", "states", "in",
            "on", "at", "to", "does", "do", "it", "its"}
    return {w for w in normalise(s).split() if w not in stop}


def baseline_first_sentence(task):
    return sentences(task["input"])[0]


def baseline_keyword_overlap(task):
    sents = sentences(task["input"])
    if len(sents) == 1:
        return task["input"]
    q = content_words(task["instruction"])
    best = max(sents, key=lambda s: len(content_words(s) & q))
    return best


BASELINES = {"first_sentence": baseline_first_sentence,
             "keyword_overlap": baseline_keyword_overlap}


def validate(tasks):
    errors, seen = [], set()
    for t in tasks:
        for field in ("id", "type", "instruction", "input", "expected"):
            if field not in t or not str(t[field]).strip():
                errors.append(f"{t.get('id', '?')}: missing {field}")
        if t["id"] in seen:
            errors.append(f"{t['id']}: duplicate id")
        seen.add(t["id"])
        if t["type"] not in TYPES:
            errors.append(f"{t['id']}: unknown type {t['type']}")
        if t["expected"] not in t["input"]:
            errors.append(f"{t['id']}: expected is not an exact substring of input")
    return errors


def main():
    doc = yaml.safe_load(SUITE.read_text())
    tasks = doc["tasks"]
    errors = validate(tasks)
    if errors:
        raise SystemExit("VALIDATION FAILED:\n" + "\n".join(errors))
    rows, summary = [], {"n_tasks": len(tasks), "by_type": {}, "baselines": {}}
    for t in tasks:
        summary["by_type"][t["type"]] = summary["by_type"].get(t["type"], 0) + 1
        row = {"id": t["id"], "type": t["type"], "scores": {}}
        for name, fn in BASELINES.items():
            row["scores"][name] = exact_match(fn(t), t["expected"])
        rows.append(row)
    for name in BASELINES:
        per_type = {}
        for ttype in TYPES:
            sub = [r for r in rows if r["type"] == ttype]
            per_type[ttype] = f"{sum(r['scores'][name] for r in sub)}/{len(sub)}"
        summary["baselines"][name] = {
            "total": f"{sum(r['scores'][name] for r in rows)}/{len(rows)}",
            "by_type": per_type}
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with open(out / "clean_tasks_g4_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(out / "clean_tasks_g4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print("validation: OK (expected substring check passed for all tasks)")


if __name__ == "__main__":
    main()
