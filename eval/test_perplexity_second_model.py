#!/usr/bin/env python3
"""Unit tests for G9: pin the gpt2 vs distilgpt2 headline numbers.

Reads the committed rows only (no model run). Stdlib only.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    return [json.loads(l) for l in
            (ROOT / "results" / name).read_text().splitlines() if l.strip()]


def auroc(pos, neg):
    wins = ties = 0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


class TestSecondModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gpt2 = load("perplexity_gpt2_rows.jsonl")
        cls.ref = load("perplexity_rows.jsonl")

    def test_same_cases_same_order(self):
        self.assertEqual([r["id"] for r in self.gpt2],
                         [r["id"] for r in self.ref])
        self.assertEqual(len(self.gpt2), 50)

    def test_windowed_suffix_auroc_not_distilgpt2_artefact(self):
        def grp(rows, g, k):
            return [r[k] for r in rows if r["group"] == g]
        a_gpt2 = auroc(grp(self.gpt2, "suffix_attack", "windowed_perplexity"),
                       grp(self.gpt2, "benign", "windowed_perplexity"))
        a_ref = auroc(grp(self.ref, "suffix_attack", "windowed_perplexity"),
                      grp(self.ref, "benign", "windowed_perplexity"))
        self.assertAlmostEqual(a_ref, 0.887, places=3)
        self.assertAlmostEqual(a_gpt2, 0.927, places=3)

    def test_frozen_threshold_counts_identical(self):
        for rows, thr_exp in ((self.gpt2, 690.13), (self.ref, 1099.28)):
            thr = max(r["windowed_perplexity"] for r in rows
                      if r["group"] == "benign")
            self.assertAlmostEqual(thr, thr_exp, places=2)
            det_s = sum(r["windowed_perplexity"] > thr for r in rows
                        if r["group"] == "suffix_attack")
            det_n = sum(r["windowed_perplexity"] > thr for r in rows
                        if r["group"] == "natural_injection")
            self.assertEqual((det_s, det_n), (13, 14))


if __name__ == "__main__":
    unittest.main()
