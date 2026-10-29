#!/usr/bin/env python3
"""Unit tests for eval/leaderboard.py (C3).

Pins the aggregated headline cells to the values the original result
files reported (A4 17/25 & 0/10 FP; A6 AUROCs; B1 0/12/17/18; B2 25/25
with probes 6/8, 8/8, 5/8, 8/8, 8/8; B4 13/15 & 0/15, layers 9/8/4;
B5 detector 0/15; B6 15/15 with probes 4/6, 6/6, 3/6, 6/6).
Run: python3 -m pytest eval/test_leaderboard.py  (or plain python3).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import leaderboard as lb

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_auroc():
    assert lb.auroc([3.0, 4.0], [1.0, 2.0]) == 1.0
    assert lb.auroc([1.0], [1.0]) == 0.5
    assert abs(lb.auroc([2.0, 3.0], [1.0, 4.0]) - 0.5) < 1e-9


def test_perplexity_auroc_matches_a6():
    ppl = lb.load_rows(ROOT, "perplexity_rows.jsonl")
    ben = [r["perplexity"] for r in ppl if r["group"] == "benign"]
    suf = [r["perplexity"] for r in ppl if r["group"] == "suffix_attack"]
    benw = [r["windowed_perplexity"] for r in ppl if r["group"] == "benign"]
    sufw = [r["windowed_perplexity"] for r in ppl if r["group"] == "suffix_attack"]
    assert abs(lb.auroc(suf, ben) - 0.780) < 0.001   # A6 full-text
    assert abs(lb.auroc(sufw, benw) - 0.887) < 0.001  # A6 windowed


def test_headline_cells_in_generated_markdown():
    md = lb.build(ROOT)
    # A4 detector total + per-category extremes
    assert "17/25" in md and "0/10 benign flagged" in md
    # B1 progression
    for cell in ("12/25", "18/25"):
        assert cell in md
    # B5/B6 stark rows
    assert "0/15" in md and "15/15" in md
    # probe separators
    assert "6/8 blocked" in md and "5/8 blocked" in md
    assert "4/6 blocked" in md and "3/6 blocked" in md
    # B4 complementarity numbers are generated in prose
    assert "keywords alone 9/15" in md and "TF-IDF alone 8/15" in md
    # adaptive + clean-task views present (B3/C1 follow-ups)
    assert "SUCCEEDS" in md and "clean-task cost" in md
    # no cross-suite ranking language slipped in
    assert "never averaged or ranked across suites" in md


if __name__ == "__main__":
    test_auroc(); test_perplexity_auroc_matches_a6(); test_headline_cells_in_generated_markdown()
    print("all leaderboard tests passed")
