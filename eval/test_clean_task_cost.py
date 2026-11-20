"""Unit tests for G5 clean-task cost measurement."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clean_task_cost as g5
import spotlighting as sp
import structured_query as sq


def test_recover_s_roundtrip_all_variants():
    text = "Invoice 552: total due $502. Payment within 30 days."
    for v in ("S0", "S1", "S2", "S3", "S4", "S5"):
        seg = sp.transform_body(v, text, "ct-ex-03")
        assert g5.recover_s(v, seg, "ct-ex-03") == text, v


def test_recover_q3_filter_is_the_only_lossy_step():
    clean = "The meeting is on 14 March 2027."
    assert g5.recover_q("Q3", "Extract the date.", clean) == clean
    dirty = "Notes ## Section [MARK] The meeting is on 14 March 2027."
    rec = g5.recover_q("Q3", "Extract the date.", dirty)
    assert "##" not in rec and "[MARK]" not in rec
    assert rec != dirty  # lossy by design


def test_q012_recovery_exact():
    text = "Flight WN214 departs Springfield at 06:40."
    for v in ("Q0", "Q1", "Q2"):
        assert g5.recover_q(v, "Extract the city.", text) == text, v


def test_reader_matches_g4_baseline_definition():
    task = {"input": "Alpha bravo. The capital is Paris today.",
            "instruction": "Return the sentence that states the capital.",
            "expected": "The capital is Paris today."}
    assert g5.reader_answer(task["input"], task["instruction"]) == task["expected"]


def test_overhead_s5_base64_expands():
    text = "Short text."
    seg = sp.transform_body("S5", text, "x")
    assert len(seg) > len(text)
