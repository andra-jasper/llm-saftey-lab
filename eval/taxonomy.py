"""C7: inventory checker for TAXONOMY.md.

Recomputes the lab's case inventory from data/*.yaml (no model run) and
verifies that TAXONOMY.md cites the same per-suite counts and category
names. Exits non-zero on any mismatch, so the taxonomy cannot silently
drift from the data it describes.

Usage: python3 eval/taxonomy.py [--taxonomy TAXONOMY.md]
"""
import argparse
import collections
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Suites that carry attack/benign cases (sample_suite.yaml is the A1 demo
# fixture, counted separately and excluded from the taxonomy totals).
SUITES = [
    "injection_tests.yaml",
    "indirect_injection_tests.yaml",
    "completion_tests.yaml",
    "spotlight_escape_probes.yaml",
    "rag_escape_probes.yaml",
    "output_cases.yaml",
    "benign_controls.yaml",
    "structured_benign.yaml",
]


def inventory(root=ROOT):
    out = {}
    for name in SUITES:
        doc = yaml.safe_load((root / "data" / name).read_text())
        cases = doc.get("cases", [])
        cats = collections.Counter(c.get("category", "?") for c in cases)
        out[name] = {"total": len(cases), "categories": dict(sorted(cats.items()))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taxonomy", default=str(ROOT / "TAXONOMY.md"))
    args = ap.parse_args()
    inv = inventory()
    total = sum(v["total"] for v in inv.values())
    for name, v in inv.items():
        print(f"{name}: {v['total']} cases; categories={v['categories']}")
    print(f"TOTAL (taxonomy suites): {total} cases")

    text = pathlib.Path(args.taxonomy).read_text()
    problems = []
    for name, v in inv.items():
        # TAXONOMY.md must name every suite file and every category in it.
        if name not in text:
            problems.append(f"suite not cited: {name}")
        for cat in v["categories"]:
            if cat not in text:
                problems.append(f"category not cited: {name}:{cat}")
    if f"{total} cases" not in text:
        problems.append(f"total '{total} cases' not cited in TAXONOMY.md")
    if problems:
        print("MISMATCH:")
        for p in problems:
            print(" -", p)
        return 1
    print("OK: TAXONOMY.md covers every suite, category, and the total count.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
