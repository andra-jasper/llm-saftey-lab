#!/usr/bin/env python3
"""Unit tests for eval/redteam_blueteam.py -- generator logic only.

Uses a deterministic fake scorer (no model download): perplexity is a
fixed function of the suffix units, so hill-climb behaviour can be
checked exactly. Run: python -m pytest eval/test_redteam_blueteam.py
or plain: python eval/test_redteam_blueteam.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from redteam_blueteam import FLUENT, GIBBERISH, hill_climb, median, random_suffix

# Fake scorer: each unit contributes a fixed "surprisal"; "the" is cheap,
# gibberish is expensive. PPL = exp(mean cost) over suffix units only.
COST = {"the": 0.1, "of": 0.5, "and": 0.5}


def fake_scorer(text):
    units = text.split(" ", 1)[1].split() if " " in text else []
    costs = [COST.get(u, 3.0) for u in units]
    import math
    return math.exp(sum(costs) / len(costs)) if costs else 1.0


def test_random_suffix_deterministic_and_in_pool():
    a = random_suffix(random.Random(7), GIBBERISH)
    b = random_suffix(random.Random(7), GIBBERISH)
    assert a == b and len(a) == 12 and all(u in GIBBERISH for u in a)


def test_hill_climb_never_increases():
    rng = random.Random(1)
    start = random_suffix(rng, GIBBERISH + FLUENT)
    final, traj = hill_climb(fake_scorer, "BASE", start,
                             GIBBERISH + FLUENT, rng, steps=40)
    ppls = [p for _, p in traj]
    assert all(b <= a for a, b in zip(ppls, ppls[1:]))
    assert fake_scorer("BASE " + " ".join(final)) == ppls[-1]
    assert ppls[-1] < ppls[0]  # the cheap unit "the" is reachable


def test_hill_climb_preserves_length_and_pool():
    rng = random.Random(2)
    pool = GIBBERISH + FLUENT
    final, _ = hill_climb(fake_scorer, "BASE", random_suffix(rng, pool),
                          pool, rng, steps=10)
    assert len(final) == 12 and all(u in pool for u in final)


def test_median():
    assert median([3, 1, 2]) == 2
    assert median([4, 1, 2, 3]) == 2.5


if __name__ == "__main__":
    test_random_suffix_deterministic_and_in_pool()
    test_hill_climb_never_increases()
    test_hill_climb_preserves_length_and_pool()
    test_median()
    print("4 tests pass")
