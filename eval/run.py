#!/usr/bin/env python3
"""Eval harness for llm-saftey-lab (ROADMAP task A1).

Loads a YAML suite of attack test cases, applies a named defense,
records per-case rows, and writes JSONL results + a Markdown summary.

A *defense* is any callable:  defense(prompt: str) -> str
(the defended prompt). The registry is in DEFENSES below; new defenses
plug in as plain functions.

Scoring honesty policy: the harness NEVER guesses whether an attack
would succeed. `blocked` stays null unless an explicit oracle fills it
(e.g. the heuristic detector in A4, or an LLM judge). Rows the harness
cannot score get verdict "pending-no-oracle".

Suite schema (YAML):
    name: str
    description: str (optional)
    cases:
      - id: str (unique)
        category: str
        prompt: str
        notes: str (optional)
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("pyyaml is required: pip install pyyaml")


def identity(prompt: str) -> str:
    """Baseline defense: no transformation."""
    return prompt


DEFENSES = {"none": identity}


def load_suite(suite_path: Path) -> dict:
    """Load and strictly validate a suite YAML file."""
    if not suite_path.exists():
        raise FileNotFoundError(f"suite not found: {suite_path}")
    suite = yaml.safe_load(suite_path.read_text())
    if not isinstance(suite, dict):
        raise ValueError("suite YAML must be a mapping")
    cases = suite.get("cases")
    if not cases:
        raise ValueError("suite must contain a non-empty 'cases' list")
    seen = set()
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case #{i} must be a mapping")
        for field in ("id", "category", "prompt"):
            if not case.get(field):
                raise ValueError(f"case #{i} is missing required field '{field}'")
        if case["id"] in seen:
            raise ValueError(f"duplicate case id: {case['id']!r}")
        seen.add(case["id"])
    return suite


def run_suite(suite: dict, defense_name: str) -> dict:
    """Apply `defense_name` to every case; return a results dict."""
    defense = DEFENSES[defense_name]
    suite_name = suite.get("name") or "unnamed-suite"
    rows = []
    for case in suite["cases"]:
        defended = defense(case["prompt"])
        if not isinstance(defended, str):
            raise TypeError(f"defense {defense_name!r} must return str")
        rows.append({
            "id": case["id"],
            "category": case["category"],
            "defense": defense_name,
            "blocked": None,          # filled by an explicit oracle only
            "verdict": "pending-no-oracle",
            "original_prompt": case["prompt"],
            "defended_prompt": defended,
        })
    return {
        "suite": suite_name,
        "defense": defense_name,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }


def write_results(result: dict, outdir: Path) -> tuple[Path, Path]:
    """Write JSONL rows + Markdown summary; return both paths."""
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = result["run_at"][:10]
    base = f"{stamp}_{result['suite']}_{result['defense']}"
    jsonl_path = outdir / f"{base}.jsonl"
    md_path = outdir / f"{base}.md"
    jsonl_path.write_text("\n".join(json.dumps(r) for r in result["rows"]) + "\n")

    rows = result["rows"]
    cats: dict[str, int] = {}
    for r in rows:
        cats[r["category"]] = cats.get(r["category"], 0) + 1

    lines = [
        f"# Eval summary: {result['suite']} (defense: {result['defense']})",
        "",
        f"- run at: {result['run_at']}",
        f"- total cases: {len(rows)}",
        "- scored: 0 (no oracle attached; see `verdict`)",
        "",
        "## Cases per category",
        "",
        "| category | n |",
        "| --- | --- |",
    ]
    lines += [f"| {c} | {n} |" for c, n in sorted(cats.items())]
    lines += [
        "",
        "## Rows",
        "",
        "| id | category | verdict |",
        "| --- | --- | --- |",
    ]
    lines += [f"| {r['id']} | {r['category']} | {r['verdict']} |" for r in rows]
    lines += ["", f"Full rows: `{jsonl_path.name}`", ""]
    md_path.write_text("\n".join(lines))
    return jsonl_path, md_path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run an attack suite through a defense.")
    ap.add_argument("--suite", required=True, help="path to suite YAML")
    ap.add_argument("--defense", default="none", choices=sorted(DEFENSES),
                    help="defense to apply (default: none)")
    ap.add_argument("--out", default="results", help="output dir (default: results)")
    args = ap.parse_args(argv)

    try:
        suite = load_suite(Path(args.suite))
        result = run_suite(suite, args.defense)
        jsonl_path, md_path = write_results(result, Path(args.out))
    except (FileNotFoundError, ValueError, TypeError) as e:
        sys.exit(f"error: {e}")

    print(f"ran {len(result['rows'])} cases | defense={args.defense}")
    print(f"  jsonl: {jsonl_path}")
    print(f"  summary: {md_path}")


if __name__ == "__main__":
    main()
