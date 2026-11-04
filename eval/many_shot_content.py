#!/usr/bin/env python3
"""Content-token follow-up for D1 (companion to many_shot_sim.py).

The headline NLL in many_shot_sim.py averages over the whole
continuation " Sure, the capital of T is C." -- most of those tokens
are FORMAT (" Sure, the capital of ... is"), only the capital-name
tokens carry content. The n=32 greedy generations in the main run
reproduced the format perfectly but answered "Reykjavik" (the LAST
demonstration's capital) for every target, so this follow-up scores
the capital tokens alone:

  - NLL of the correct capital tokens, compliant demos, all n.
  - At n=8 and n=32: NLL of the same continuation with the capital
    replaced by "Reykjavik" (recency competitor), same targets.

Output: results/many_shot_content_rows.jsonl + printed table.
Run after many_shot_sim.py:  python eval/many_shot_content.py
"""
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from many_shot_sim import (MODEL_NAME, ROOT, SHOT_COUNTS, TARGETS,
                           build_prompt, compliant_continuation)

RECENCY_CAPITAL = "Reykjavik"  # capital of the 32nd (last) demo pair


def capital_token_nll(prompt, continuation, capital, model, tok):
    """Mean NLL over only the tokens spelling `capital`."""
    p_ids = tok(prompt)["input_ids"]
    f_ids = tok(prompt + continuation)["input_ids"]
    assert f_ids[: len(p_ids)] == p_ids
    cont_ids = f_ids[len(p_ids):]
    # Locate the capital span: tokens after the " is" token, before
    # the final "." token, identified by cumulative decoding.
    decoded = [tok.decode([t]) for t in cont_ids]
    start = next(i for i, d in enumerate(decoded) if d.strip() == "is") + 1
    span = cont_ids[start:-1]  # drop trailing "."
    assert tok.decode(span).strip() == capital, (decoded, capital)
    ids = torch.tensor([f_ids])
    with torch.no_grad():
        logits = model(ids).logits[0]
    logp = torch.log_softmax(logits.float(), dim=-1)
    base = len(p_ids) - 1 + start
    return sum(-logp[base + j, t].item() for j, t in enumerate(span)) / len(span)


def main():
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    rows = []
    for n in SHOT_COUNTS:
        for country, capital in TARGETS:
            prompt = build_prompt("compliant", n, country)
            nll = capital_token_nll(prompt,
                                    compliant_continuation(country, capital),
                                    capital, model, tok)
            rows.append({"n": n, "target": country, "capital": capital,
                         "capital_nll": round(nll, 4)})
            print(f"correct  n={n:2d} {country:6s} capital_nll={nll:.4f}",
                  flush=True)
            if n in (8, 32):
                wrong = compliant_continuation(country, RECENCY_CAPITAL)
                wnll = capital_token_nll(prompt, wrong, RECENCY_CAPITAL,
                                         model, tok)
                rows.append({"n": n, "target": country,
                             "capital": RECENCY_CAPITAL,
                             "capital_nll": round(wnll, 4),
                             "note": "recency competitor"})
                print(f"recency  n={n:2d} {country:6s} "
                      f"capital_nll={wnll:.4f}", flush=True)
    out = ROOT / "results" / "many_shot_content_rows.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print("\n=== Mean capital-token NLL (correct capital) ===")
    for n in SHOT_COUNTS:
        vals = [r["capital_nll"] for r in rows
                if r["n"] == n and "note" not in r]
        print(f"n={n:2d}  {sum(vals) / len(vals):.4f}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
