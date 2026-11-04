#!/usr/bin/env python3
"""Unit tests for eval/many_shot_sim.py (ROADMAP task D1).

Model-free except one tokenizer-boundary test that skips when the
distilgpt2 tokenizer is not cached. Run:
    python -m pytest eval/test_many_shot_sim.py
or  python eval/test_many_shot_sim.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from many_shot_sim import (DEMO_PAIRS, OFFTASK_PAIRS, SHOT_COUNTS, TARGETS,
                           build_prompt, compliant_continuation,
                           fit_power_law, refusal_continuation, shot_text)


def test_pools_disjoint_and_complete():
    demo_countries = {c for c, _ in DEMO_PAIRS}
    assert len(DEMO_PAIRS) == 32 and len(OFFTASK_PAIRS) == 32
    for country, _ in TARGETS:
        assert country not in demo_countries


def test_prompts_are_nested_prefixes():
    for n in SHOT_COUNTS[:-1]:
        p_n = build_prompt("compliant", n, "Norway")
        p_next = build_prompt("compliant", n + 1, "Norway")
        body_n = p_n.rsplit("Human: What is the capital of Norway?", 1)[0]
        assert p_next.startswith(body_n) and len(p_next) > len(p_n)


def test_zero_shot_identical_across_conditions():
    prompts = {build_prompt(c, 0, "Japan")
               for c in ("compliant", "refusal", "offtask")}
    assert len(prompts) == 1


def test_shot_counts_within_each_condition():
    for cond in ("compliant", "refusal", "offtask"):
        p = build_prompt(cond, 4, "Canada")
        assert p.count("Human:") == 5  # 4 demos + target query
        assert p.count("Assistant:") == 5


def test_condition_formats():
    assert "Sure, the capital of France is Paris." in shot_text("compliant", 0)
    assert "Sorry, I can't answer that." in shot_text("refusal", 0)
    assert "It is yellow." in shot_text("offtask", 0)
    assert compliant_continuation("Norway", "Oslo") == \
        " Sure, the capital of Norway is Oslo."
    assert refusal_continuation() == " Sorry, I can't answer that."


def test_fit_recovers_synthetic_power_law():
    ns = [1, 2, 4, 8, 16, 32]
    ys = [2.0 * n ** -0.5 + 1.0 for n in ns]
    fit = fit_power_law(ns, ys)
    assert abs(fit["alpha"] - 0.5) < 0.05
    assert abs(fit["K"] - 1.0) < 0.1
    assert fit["r2_log"] > 0.99


def test_tokenizer_boundary():
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("distilgpt2")
    except Exception:
        return  # tokenizer not cached: skip silently in this runner
    prompt = build_prompt("compliant", 2, "Norway")
    cont = compliant_continuation("Norway", "Oslo")
    p_ids = tok(prompt)["input_ids"]
    f_ids = tok(prompt + cont)["input_ids"]
    assert f_ids[: len(p_ids)] == p_ids
    assert len(f_ids) > len(p_ids)
    # 32-shot prompt must fit distilgpt2's 1,024-token context
    full32 = build_prompt("compliant", 32, "Norway") + cont
    assert len(tok(full32)["input_ids"]) < 1024


if __name__ == "__main__":
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"PASS {name}")
    print(f"{len(tests)} tests passed")
