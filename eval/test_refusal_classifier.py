import refusal_classifier as rc


def test_dataset_is_synthetic_balanced_and_deterministic():
    rows = rc.build_dataset()
    assert len(rows) == 600  # 10 families x 3 templates x 20 topics
    labels = {r["label"] for r in rows}
    assert labels == {"refusal", "compliance"}
    assert sum(1 for r in rows if r["label"] == "refusal") == 300
    assert [r["text"] for r in rows] == [r["text"] for r in rc.build_dataset()]


def test_same_topic_pool_for_both_classes():
    # Design choice 1: topics must not carry the label.
    for label in ("refusal", "compliance"):
        texts = " ".join(r["text"] for r in rc.build_dataset()
                         if r["label"] == label)
        for topic in rc.TOPICS:
            assert topic in texts, (label, topic)


def test_splits_are_disjoint_and_cover_the_intended_rows():
    rows = rc.build_dataset()
    tr, te = rc.stratified_random_split(rows)
    assert not {id(r) for r in tr} & {id(r) for r in te}
    assert len(tr) + len(te) == len(rows)
    held = [r for r in rows if r["family"] in rc.HELD_OUT_FAMILIES]
    assert len(held) == 240  # 4 families x 3 templates x 20 topics


def test_keyword_baseline_known_weaknesses():
    # P3's mechanism, pinned: "sorry" fires on apologetic compliance,
    # and a terse refusal with no listed keyword is missed.
    assert rc.keyword_predict("Sorry for the wait — here is the guide.") == 1
    assert rc.keyword_predict("That isn't something I'll do.") == 0


def test_trained_model_beats_chance_on_held_out_families():
    rows = rc.build_dataset()
    tr = [r for r in rows if r["family"] not in rc.HELD_OUT_FAMILIES]
    te = [r for r in rows if r["family"] in rc.HELD_OUT_FAMILIES]
    out, _ = rc.run_split("t", tr, te)
    assert out["logreg"]["accuracy"] > 0.5
    assert out["logreg"]["accuracy"] >= out["keyword"]["accuracy"]
