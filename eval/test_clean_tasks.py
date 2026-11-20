#!/usr/bin/env python3
"""Unit tests for clean_tasks helpers. Run: python eval/test_clean_tasks.py"""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "ct", Path(__file__).parent / "clean_tasks.py")
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)


def test_normalise_ignores_case_and_punct():
    assert ct.normalise("Bristol Temple Meads.") == "bristol temple meads"
    assert ct.normalise("  $502 ") == "502"


def test_exact_match():
    assert ct.exact_match("4 PM", "4 pm")
    assert not ct.exact_match("4 PM", "9 AM")


def test_validate_catches_non_substring():
    bad = [{"id": "x", "type": "qa", "instruction": "q",
            "input": "some text", "expected": "not in the text"}]
    assert any("substring" in e for e in ct.validate(bad))


def test_validate_catches_duplicate():
    t = {"id": "x", "type": "qa", "instruction": "q",
         "input": "some text", "expected": "some"}
    assert any("duplicate" in e for e in ct.validate([t, dict(t)]))


def test_sentences_split():
    assert len(ct.sentences("One. Two? Three!")) == 3


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print(f"{len(fns)} tests passed")
