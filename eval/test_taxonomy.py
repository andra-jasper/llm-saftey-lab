"""Tests for eval/taxonomy.py (C7). Run: python3 -m pytest eval/test_taxonomy.py
or plain: python3 eval/test_taxonomy.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from taxonomy import inventory  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_suite_totals():
    inv = inventory()
    assert inv["injection_tests.yaml"]["total"] == 25
    assert inv["indirect_injection_tests.yaml"]["total"] == 15
    assert inv["completion_tests.yaml"]["total"] == 13
    assert inv["output_cases.yaml"]["total"] == 30
    assert sum(v["total"] for v in inv.values()) == 117


def test_direct_categories_balanced():
    cats = inventory()["injection_tests.yaml"]["categories"]
    assert cats == {
        "authority_claim": 5,
        "direct_override": 5,
        "encoded_payload": 5,
        "multi_turn": 5,
        "roleplay": 5,
    }


def test_taxonomy_covers_inventory():
    text = (ROOT / "TAXONOMY.md").read_text()
    for name, v in inventory().items():
        assert name in text
        for cat in v["categories"]:
            assert cat in text, cat
    assert "117 cases" in text


def test_taxonomy_has_paper_links():
    text = (ROOT / "TAXONOMY.md").read_text()
    for arxiv in ["2307.15043", "2307.02483", "2306.05499", "2310.12815",
                  "2302.12173", "2403.14720", "2309.00614", "2402.06363",
                  "2410.05451"]:
        assert f"https://arxiv.org/abs/{arxiv}" in text, arxiv


if __name__ == "__main__":
    test_suite_totals()
    test_direct_categories_balanced()
    test_taxonomy_covers_inventory()
    test_taxonomy_has_paper_links()
    print("4 tests pass")
