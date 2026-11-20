"""G8: perplexity-filter calibration — benign-only threshold, frozen,
then re-report A6/E3 detection under it.

Method (rule fixed before touching attack rows): the threshold is the
MAXIMUM windowed_perplexity among the benign calibration rows of A6
(results/perplexity_rows.jsonl, group=benign, n=10). No attack row is
consulted when choosing it. The same rule is applied to full-text
perplexity as a secondary readout. The frozen thresholds are then
applied unchanged to: A6 natural_injection (n=25), A6 suffix_attack
(n=15), and the E3 flagship rows (results/flagship_rows.jsonl, n=39).

Honest limits: the benign set IS the calibration set, so benign FP
under the max rule is 0 by construction on these 10 rows — that is a
property of the rule, not evidence about unseen benign text. n=10 is
small; the threshold inherits the benign max's variance (one benign
outlier, ben-02 at 1099.28 windowed, sets it). Detector statement
only — no live model, no ASR.
"""
import json, sys
from pathlib import Path

def auroc(pos, neg):
    wins = sum(1 for p in pos for n in neg if p > n)
    ties = sum(1 for p in pos for n in neg if p == n)
    return (wins + 0.5 * ties) / (len(pos) * len(neg))

def calibrate(rows, key):
    benign = [r[key] for r in rows if r["group"] == "benign"]
    return max(benign), benign

def detect(rows, key, thr, group=None, arm=None):
    sel = [r for r in rows if (group is None or r["group"] == group)
           and (arm is None or r.get("arm") == arm)]
    return sum(1 for r in sel if r[key] > thr), len(sel)

def main(a6_path="results/perplexity_rows.jsonl", e3_path="results/flagship_rows.jsonl"):
    a6 = [json.loads(l) for l in Path(a6_path).read_text().splitlines() if l.strip()]
    e3 = [json.loads(l) for l in Path(e3_path).read_text().splitlines() if l.strip()]
    out = {"calibration": {}, "detection": {}, "auroc_check": {}}
    for key in ("windowed_perplexity", "perplexity"):
        thr, benign = calibrate(a6, key)
        out["calibration"][key] = {"rule": "max over benign calibration rows",
                                   "n_benign": len(benign), "threshold": round(thr, 2)}
        d = {}
        for g in ("natural_injection", "suffix_attack"):
            k, n = detect(a6, key, thr, group=g); d[f"a6_{g}"] = f"{k}/{n}"
        for arm in sorted({r["arm"] for r in e3}):
            k, n = detect(e3, key, thr, arm=arm); d[f"e3_{arm}"] = f"{k}/{n}"
        kb, nb = detect(a6, key, thr, group="benign"); d["a6_benign_fp"] = f"{kb}/{nb}"
        out["detection"][key] = d
    ben_w = [r["windowed_perplexity"] for r in a6 if r["group"] == "benign"]
    suf_w = [r["windowed_perplexity"] for r in a6 if r["group"] == "suffix_attack"]
    out["auroc_check"]["windowed_suffix_vs_benign"] = round(auroc(suf_w, ben_w), 3)
    return out

if __name__ == "__main__":
    res = main(*sys.argv[1:3])
    print(json.dumps(res, indent=2))
