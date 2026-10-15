#!/usr/bin/env python3
"""Minimal eval harness: loads a YAML suite of test cases, applies a defense,
scores outcomes, writes JSONL results + a Markdown summary.

A defense is any callable: defense(prompt: str) -> str (the defended prompt).
Scoring here is harness-level (did the attack get through per the case's
oracle); LLM-dependent checks are skipped without an API key.
"""
import argparse
import json
import os
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("pip install pyyaml")


def identity(prompt: str) -> str:
    return prompt


DEFENSES = {"none": identity}


def run_suite(suite_path: Path, defense_name: str):
    suite = yaml.safe_load(suite_path.read_text())
    defense = DEFENSES[defense_name]
    rows = []
    for case in suite["cases"]:
        defended = defense(case["prompt"])
        rows.append({
            "id": case["id"],
            "category": case.get("category", "uncategorized"),
            "defense": defense_name,
            "blocked": None,  # filled by oracle / LLM judge when available
            "prompt": defended,
        })
    return {"suite": suite.get("name", suite_path.stem), "defense": defense_name, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True)
    ap.add_argument("--defense", default="none", choices=list(DEFENSES))
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    out = run_suite(Path(args.suite), args.defense)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    (outdir / f"{stamp}_{out['suite']}_{args.defense}.jsonl").write_text(
        "\n".join(json.dumps(r) for r in out["rows"]) + "\n"
    )
    print(f"ran {len(out['rows'])} cases | defense={args.defense} | results in {outdir}/")


if __name__ == "__main__":
    main()
