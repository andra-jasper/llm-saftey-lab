#!/usr/bin/env python3
"""Unit tests for eval/flagship_eval.py (ROADMAP task E3).

Run:  python -m pytest eval/test_flagship_eval.py
      (or plain `python eval/test_flagship_eval.py`)
No model, no network: the pure helpers only -- AUROC / bootstrap on
known fixtures, the R-REP construction rule, the D5-RESCORE selection,
and gate G1 against a drifted fixture.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flagship_eval import (  # noqa: E402
    auroc,
    bootstrap_auroc_ci,
    build_rep_prompt,
    check_g1,
    d5_rescore_id,
    select_d5_rescore,
    stats,
)


def test_auroc_extremes():
    assert auroc([10, 11], [1, 2]) == 1.0
    assert auroc([1, 2], [10, 11]) == 0.0
    assert auroc([5], [5]) == 0.5


def test_bootstrap_ci_brackets_point_estimate():
    lo, hi = bootstrap_auroc_ci([100, 200, 300, 400], [10, 20, 30, 40],
                                n_boot=200, seed=1)
    assert 0.0 <= lo <= hi <= 1.0
    assert hi == 1.0  # perfectly separated fixture


def test_build_rep_prompt_rule():
    assert build_rep_prompt("BASE", "SUF", 1) == "BASE SUF"
    assert build_rep_prompt("BASE", "SUF", 2) == "BASE BASE SUF"
    assert build_rep_prompt("BASE", "SUF", 4) == "BASE BASE BASE BASE SUF"


def test_select_d5_rescore_picks_nine():
    rows = ([{"condition": "random_gibberish", "base": 0, "suffix": "x"}] * 3
            + [{"condition": c, "base": b, "suffix": "s"}
               for c in ("hillclimb_mixed", "repetition_the", "repetition_!")
               for b in range(3)])
    sel = select_d5_rescore(rows)
    assert len(sel) == 9
    assert {d5_rescore_id(r) for r in sel} == {
        "d5r-fin-0", "d5r-fin-1", "d5r-fin-2",
        "d5r-rep-the-0", "d5r-rep-the-1", "d5r-rep-the-2",
        "d5r-rep-bang-0", "d5r-rep-bang-1", "d5r-rep-bang-2"}


def test_stats_median():
    s = stats([3.0, 1.0, 2.0])
    assert s == {"n": 3, "min": 1.0, "median": 2.0, "mean": 2.0, "max": 3.0}


def test_g1_detects_drift():
    good = ([{"group": "benign", "perplexity": 73.2,
              "windowed_perplexity": 609.1}] * 10
            + [{"group": "natural_injection", "perplexity": 129.8,
                "windowed_perplexity": 1271.9}] * 25
            + [{"group": "suffix_attack", "perplexity": 370.5,
                "windowed_perplexity": 7989.5}] * 15)
    assert check_g1(good) == []
    drifted = [dict(r) for r in good]
    drifted[0] = {"group": "benign", "perplexity": 999.0,
                  "windowed_perplexity": 609.1}
    # median of 10 with one drifted value is unchanged; drift the count
    assert check_g1(good[:-1]) != []


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)} tests passed")
