#!/usr/bin/env python3
"""Unit tests for the pure helpers in flagship_variant_g1 (no model load).

Run: python -m pytest eval/test_flagship_variant_g1.py
(or plain: python eval/test_flagship_variant_g1.py)
"""
import importlib.util
import sys
from pathlib import Path

# Import only the helper functions without executing main / model load:
# the module imports torch/transformers at top level but loads no model
# at import time, so a plain import is safe where those are installed.
spec = importlib.util.spec_from_file_location(
    "g1", Path(__file__).parent / "flagship_variant_g1.py")
g1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g1)


def test_auroc_perfect():
    assert g1.auroc([10, 20, 30], [1, 2, 3]) == 1.0


def test_auroc_reversed():
    assert g1.auroc([1, 2], [10, 20]) == 0.0


def test_auroc_ties_half():
    assert g1.auroc([5], [5]) == 0.5


def test_stats_median_even():
    s = g1.stats([4, 1, 3, 2])
    assert s["n"] == 4 and s["median"] == 2.5 and s["min"] == 1 and s["max"] == 4


def test_bootstrap_deterministic_and_bounded():
    a = g1.bootstrap_ci([100, 200, 300], [1, 2, 3], n_resamples=50)
    b = g1.bootstrap_ci([100, 200, 300], [1, 2, 3], n_resamples=50)
    assert a == b and a[0] <= a[1] and 0.0 <= a[0] and a[1] <= 1.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print(f"{len(fns)} tests passed")
