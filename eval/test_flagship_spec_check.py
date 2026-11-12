#!/usr/bin/env python3
"""Unit tests for eval/flagship_spec_check.py (ROADMAP task E2).

Run:  python -m pytest eval/test_flagship_spec_check.py
      (or plain `python eval/test_flagship_spec_check.py`)
No model, no network: AUROC/median logic on synthetic fixtures, plus
the frozen-reference and template checks against the committed files.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flagship_spec_check import (  # noqa: E402
    EXPECTED_NEW_SCORINGS,
    EXPECTED_TOTAL_ROWS,
    auroc,
    check_reference,
    check_template,
)

ROOT = Path(__file__).resolve().parent.parent


def test_auroc_perfect_separation():
    assert auroc([10.0, 20.0], [1.0, 2.0]) == 1.0


def test_auroc_reversed():
    assert auroc([1.0, 2.0], [10.0, 20.0]) == 0.0


def test_auroc_ties_count_half():
    assert auroc([5.0], [5.0]) == 0.5
    assert auroc([5.0, 6.0], [5.0, 5.0]) == 0.75


def test_frozen_reference_recomputes():
    problems = check_reference(ROOT / "results" / "perplexity_rows.jsonl")
    assert problems == [], problems


def test_template_arms_and_schema():
    problems = check_template(ROOT / "data" / "flagship_manifest_template.yaml")
    assert problems == [], problems


def test_arm_arithmetic_constants():
    # Spec section 4: 50 frozen-reuse + 9 rescore + 30 constructed
    # + 70 gated-external = 159 rows, of which 109 are new scorings.
    assert EXPECTED_TOTAL_ROWS == 50 + 9 + 30 + 70
    assert EXPECTED_NEW_SCORINGS == 9 + 30 + 70


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)} tests passed")
