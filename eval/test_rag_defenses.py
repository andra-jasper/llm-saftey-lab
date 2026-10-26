#!/usr/bin/env python3
"""Unit tests for eval/rag_defenses.py (ROADMAP task B6)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rag_defenses as rd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASE = {
    "id": "t-01", "category": "task_hijack",
    "user_query": "Summarize this page.",
    "retrieved_document": "Benign facts about the page. Some more facts here.",
    "injected_instruction": "Benign facts about the page.",
}


def test_naive_and_hierarchy_have_no_data_channel():
    for v in ("R0", "R1"):
        data, trusted, _ = rd.split_rag(v, CASE)
        assert data == ""
        assert CASE["retrieved_document"] in trusted


def test_structural_variants_recover_document_exactly():
    for v in ("R2", "R3", "R4", "R5"):
        data, _, _ = rd.split_rag(v, CASE)
        assert data == CASE["retrieved_document"], v


def test_fixed_delimiter_escape_compromises_r2_not_r3():
    probes = {c["id"]: c for c in rd.load_cases(ROOT / "data" / "rag_escape_probes.yaml")}
    esc = probes["rag-esc-01"]
    assert rd.evaluate("R2", "probe", esc).compromised
    assert not rd.evaluate("R3", "probe", esc).compromised
    assert not rd.evaluate("R5", "probe", esc).compromised


def test_datamark_escapes_compromise_r4_not_r5():
    probes = {c["id"]: c for c in rd.load_cases(ROOT / "data" / "rag_escape_probes.yaml")}
    for pid in ("rag-esc-04", "rag-esc-05", "rag-esc-06"):
        assert rd.evaluate("R4", "probe", probes[pid]).compromised, pid
        assert not rd.evaluate("R5", "probe", probes[pid]).compromised, pid


def test_recover_document_multiparagraph_exact():
    case = dict(CASE)
    case["retrieved_document"] = "Para one has several words in it.\n\nPara two follows after a blank line.\nSingle line three."
    for v in ("R0", "R1", "R2", "R3", "R4", "R5"):
        seg = rd.transform_document(v, case["retrieved_document"], case["id"])
        assert rd.recover_document(v, seg, case["id"]) == case["retrieved_document"], v


def test_probes_schema_injected_is_exact_substring():
    for c in rd.load_cases(ROOT / "data" / "rag_escape_probes.yaml"):
        assert c["injected_instruction"] in c["retrieved_document"], c["id"]


def test_b5_all_structural_variants_contain_all_cases():
    cases = rd.load_cases(ROOT / "data" / "indirect_injection_tests.yaml")
    assert len(cases) == 15
    for v in ("R2", "R3", "R4", "R5"):
        bad = [c["id"] for c in cases if rd.evaluate(v, "attack", c).compromised]
        assert bad == [], (v, bad)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)} tests passed")
