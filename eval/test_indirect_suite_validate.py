#!/usr/bin/env python3
"""Unit tests for eval/indirect_suite_validate.py (ROADMAP task B5).

Run from the repo root:
    python3 -m unittest eval.test_indirect_suite_validate -v
(or: python3 eval/test_indirect_suite_validate.py)
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import indirect_suite_validate as v  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUITE = ROOT / "data" / "indirect_injection_tests.yaml"


class TestIndirectSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite, cls.errors = v.validate(SUITE)
        cls.rows = v.analyse(cls.suite["cases"])

    def test_no_structural_errors(self):
        self.assertEqual(self.errors, [])

    def test_fifteen_cases_five_categories(self):
        self.assertEqual(len(self.suite["cases"]), 15)
        from collections import Counter
        self.assertEqual(dict(Counter(c["category"] for c in self.suite["cases"])),
                         v.EXPECTED_CATEGORIES)

    def test_injected_instruction_is_exact_substring(self):
        for case in self.suite["cases"]:
            self.assertIn(case["injected_instruction"],
                          case["retrieved_document"], case["id"])

    def test_user_queries_are_benign_to_detector(self):
        # The defining property of indirect injection in this suite:
        # nothing in the user channel fires the A4 detector at all.
        for row in self.rows:
            self.assertEqual(row["user_query_score"], 0.0, row["id"])
            self.assertFalse(row["user_query_flagged"], row["id"])

    def test_no_case_flagged_on_any_channel(self):
        # Measured B5 result: detector_v1 (threshold 0.5) flags 0/15 on
        # user, document and assembled prompt alike, because every
        # payload is a single feature family (max lone-family score 0.40).
        for row in self.rows:
            self.assertFalse(row["document_flagged"], row["id"])
            self.assertFalse(row["prompt_flagged"], row["id"])
            self.assertLessEqual(row["document_score"], 0.40, row["id"])

    def test_some_document_signal_exists_below_threshold(self):
        fired = [r for r in self.rows if r["document_fired"]]
        self.assertEqual(len(fired), 6)


if __name__ == "__main__":
    unittest.main()
