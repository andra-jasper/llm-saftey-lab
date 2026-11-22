#!/usr/bin/env python3
"""Unit tests for eval/reproduce.py (G10). Stdlib only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reproduce


class TestReproduce(unittest.TestCase):
    def test_auroc_perfect_and_chance(self):
        self.assertEqual(reproduce.auroc([10, 11], [1, 2]), 1.0)
        self.assertEqual(reproduce.auroc([1, 2], [1, 2]), 0.5)

    def test_all_headline_checks_match(self):
        rc = reproduce.main()
        self.assertEqual(rc, 0)
        self.assertTrue(all(ok for *_, ok in reproduce.CHECKS))
        self.assertGreaterEqual(len(reproduce.CHECKS), 40)


if __name__ == "__main__":
    unittest.main()
