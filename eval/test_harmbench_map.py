import harmbench_map as hm


def test_every_lab_category_mapped_once():
    lab = {(s, c) for s, cats in hm.LAB_SUITES.items() for c in cats}
    assert set(hm.MAPPING) == lab
    assert len(hm.MAPPING) == 24


def test_no_direct_verdicts():
    # The honest headline of D2: the two schemes share no construct
    # exactly. If a future edit claims a "direct" match, this test
    # forces a deliberate justification.
    assert all(v != "direct" for v, _t, _n in hm.MAPPING.values())


def test_verdict_counts():
    counts = hm.check()
    assert counts == {"partial": 7, "none": 17}, counts


def test_semantic_coverage_is_explicit():
    reached = {t.split(": ", 1)[1] for v, t, _n in hm.MAPPING.values()
               if v in ("direct", "partial") and t.startswith("semantic: ")}
    assert reached == {"Misinformation & Disinformation"}
    assert reached | set(hm.UNCOVERED_SEMANTIC) == set(hm.HARMBENCH_SEMANTIC)
    assert len(hm.UNCOVERED_SEMANTIC) == 6


def test_functional_totals_match_paper():
    assert hm.HARMBENCH_FUNCTIONAL == {
        "standard": 200, "copyright": 100,
        "contextual": 100, "multimodal": 110}
    assert sum(hm.HARMBENCH_FUNCTIONAL.values()) == 510


def test_case_total():
    total = sum(n for cats in hm.LAB_SUITES.values() for n in cats.values())
    # 25 A2 + 15 B5 + 13 C6 + 8 B2 probes + 6 B6 probes + 15 B4 compromised
    assert total == 82, total
