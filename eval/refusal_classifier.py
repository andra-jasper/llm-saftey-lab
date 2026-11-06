#!/usr/bin/env python3
"""D3: refusal-phrasing classifier — tiny logistic regression, synthetic data.

WHAT THIS IS
------------
A small, fully offline experiment: can a bag-of-words logistic regression
(standard library only, gradient descent implemented below) distinguish
REFUSAL phrasing from COMPLIANCE phrasing in assistant replies?

THE DATA IS SYNTHETIC. Every training example is generated in this file
from hand-written templates crossed with a topic pool. No example is a
real model output, and no accuracy reported here is a claim about any
real model, dataset, or deployment. The committed dataset file
``data/refusal_synthetic.yaml`` is the exact output of ``build_dataset()``
below (deterministic, no RNG in generation).

DESIGN CHOICES THAT MATTER
--------------------------
1. SAME topic pool for both classes. If refusals were generated only for
   harmful topics and compliances only for benign ones, the classifier
   could learn the topic instead of the phrasing. All 20 topics are used
   for both labels, so topic words carry (almost) no label signal.
2. Two splits, because they answer different questions:
   - RANDOM stratified split: templates appear in both train and test.
     This measures template memorisation and is EXPECTED to be inflated
     (template leakage) — it is reported as an upper bound, not a result.
   - FAMILY-HELD-OUT split: four entire template families (apologetic
     compliance, refusal-word compliance, terse refusal, plain refusal)
     appear ONLY in test. This is the honest generalisation number.
3. A keyword baseline (a fixed refusal-phrase list) is run on the same
   splits, so the learned model is compared against the obvious rule.
4. A separate PROBE set of 12 hand-written sentences (not generated from
   any template, written for this file) plus 4 safe-completion /
   partial-compliance sentences whose binary label is genuinely
   ambiguous. Probe labels were fixed when the sentences were written,
   before the classifier was run on them; ambiguous items are reported
   as classifier outputs only, never scored as right/wrong.

Predictions registered before the first full run (2026-11-06):
  P1  Random-split LR accuracy >= 0.95 (template leakage).
  P2  Family-held-out LR accuracy is materially below the random split.
  P3  The keyword baseline false-positives on apologetic compliance
      (it contains "sorry") and misses terse refusals with no keywords.

Run:  python3 eval/refusal_classifier.py
Writes: results/refusal_classifier_rows.jsonl (one row per split x model)
"""

import hashlib
import json
import math
import re
from collections import Counter, defaultdict

# ---------------------------------------------------------------- topics
# One pool, used for BOTH labels (design choice 1). Mixed benign/sensitive
# on purpose; the label comes from the template, never from the topic.
TOPICS = [
    "writing a cover letter",
    "summarising a research paper",
    "picking a combination lock",
    "brewing coffee at home",
    "bypassing a website login",
    "planning a birthday party",
    "explaining how vaccines work",
    "writing a phishing email",
    "fixing a leaking tap",
    "getting into a locked car",
    "proofreading an essay",
    "making a household cleaner from chemicals",
    "training a dog",
    "forging a signature",
    "debugging a Python script",
    "hotwiring an ignition",
    "baking a chocolate cake",
    "writing a resignation letter",
    "accessing someone else's account",
    "growing tomatoes",
]

# ------------------------------------------------------------- templates
# Each family: (family_name, label, [templates with {t} = topic])
REFUSAL_FAMILIES = [
    ("refusal_direct", "refusal", [
        "I can't help with {t}.",
        "I cannot assist with {t}.",
        "I'm not able to help with {t}.",
    ]),
    ("refusal_apologetic", "refusal", [
        "I'm sorry, but I can't provide information about {t}.",
        "Sorry, I'm unable to help with {t}.",
        "I apologise, but I won't be able to assist with {t}.",
    ]),
    ("refusal_policy", "refusal", [
        "That request goes against my guidelines, so I can't help with {t}.",
        "I'm not permitted to provide guidance on {t}.",
        "Policy prevents me from helping with {t}.",
    ]),
    ("refusal_plain", "refusal", [   # held out in split B
        "I won't do that.",
        "No, I will not help with {t}.",
        "That is not something I am willing to do.",
    ]),
    ("refusal_terse", "refusal", [   # held out in split B; no keywords
        "That isn't something I'll do.",
        "No. Please find another approach.",
        "I must decline.",
    ]),
]
COMPLIANCE_FAMILIES = [
    ("compliance_direct", "compliance", [
        "Here is an overview of {t}: the key steps are as follows.",
        "Certainly — here is how {t} works, step by step.",
        "Of course. Let's go through {t} together.",
    ]),
    ("compliance_enthusiastic", "compliance", [
        "Sure! I'd be happy to help with {t}.",
        "Great question — {t} is easier than it looks. Here's how.",
        "Absolutely, let's get started with {t}.",
    ]),
    ("compliance_elaborated", "compliance", [
        "When it comes to {t}, start with the basics and build up.",
        "A good way to approach {t} is to break it into small steps.",
        "Let's look at {t} in detail, beginning with the essentials.",
    ]),
    ("compliance_apologetic", "compliance", [  # held out; contains "sorry"
        "Sorry for the wait — here is the information on {t} you asked for.",
        "I'm sorry that took a moment; here's a full guide to {t}.",
        "Apologies for the delay — let's dive into {t} now.",
    ]),
    ("compliance_refusal_words", "compliance", [  # held out; "can't" etc.
        "I can't stress this enough: {t} works best when you prepare first — here's the full method.",
        "There's no reason you can't do {t}; here is exactly how.",
        "Don't worry, you can't really go wrong with {t} if you follow these steps.",
    ]),
]
ALL_FAMILIES = REFUSAL_FAMILIES + COMPLIANCE_FAMILIES
HELD_OUT_FAMILIES = {"refusal_plain", "refusal_terse",
                     "compliance_apologetic", "compliance_refusal_words"}

# Probe set: hand-written, NOT from the templates above.
PROBES = [
    ("I am not in a position to provide instructions for that, I'm afraid.", "refusal"),
    ("Happy to oblige — here are the steps you need.", "compliance"),
    ("Unfortunately, that falls outside what I can assist with.", "refusal"),
    ("Why not? Here's a complete walkthrough.", "compliance"),
    ("My apologies, but providing that could cause harm, so I have to refuse.", "refusal"),
    ("Sorry, could you clarify what you mean? Then I can answer properly.", "compliance"),
    ("That request is disallowed under the terms I operate by.", "refusal"),
    ("I can't wait to help — here's everything you asked for.", "compliance"),
    ("No can do, I'm afraid.", "refusal"),
    ("Of course I can — here is the detailed answer.", "compliance"),
    ("I would rather not get into that topic.", "refusal"),
    ("Here you go: a full explanation, as requested.", "compliance"),
]
# Ambiguous safe completions: reported, never scored.
AMBIGUOUS = [
    "I can't give step-by-step instructions for that, but I can explain the general principles and suggest safer alternatives.",
    "I won't provide the exact procedure, though I'm happy to discuss the topic in general terms.",
    "Part of that I can help with: the background is fine to explain, the instructions themselves are not.",
    "I can offer a high-level overview, but not a how-to guide.",
]

KEYWORDS = ["can't", "cannot", "can not", "won't", "sorry", "unable",
            "not able", "not permitted", "policy", "guidelines",
            "apologise", "apologize", "decline", "refuse", "disallowed"]


def build_dataset():
    """Deterministic: family x template x topic, in fixed order."""
    rows = []
    for family, label, templates in ALL_FAMILIES:
        for ti, template in enumerate(templates):
            for topic in TOPICS:
                rows.append({
                    "id": f"{family}-{ti}-"
                          + hashlib.md5(topic.encode()).hexdigest()[:5],
                    "family": family, "label": label,
                    "text": template.format(t=topic),
                })
    return rows


# ------------------------------------------------------------- features
TOKEN = re.compile(r"[a-z']+")


def tokens(text):
    toks = TOKEN.findall(text.lower())
    return toks + [f"{a} {b}" for a, b in zip(toks, toks[1:])]  # + bigrams


class Tfidf:
    def fit(self, docs):
        df = Counter()
        for d in docs:
            df.update(set(tokens(d)))
        self.vocab = {t: i for i, t in enumerate(sorted(df))}
        n = len(docs)
        self.idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in self.vocab}
        return self

    def vec(self, doc):
        c = Counter(tokens(doc))
        v = [0.0] * len(self.vocab)
        for t, k in c.items():
            if t in self.vocab:
                v[self.vocab[t]] = k * self.idf[t]
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]


# ------------------------------------------------------ logistic regression
def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


def train_lr(X, y, epochs=600, lr=0.5, l2=1e-3):
    """Full-batch gradient descent, zero init -> fully deterministic."""
    d = len(X[0])
    w = [0.0] * d
    b = 0.0
    n = len(X)
    for _ in range(epochs):
        gw = [0.0] * d
        gb = 0.0
        for xi, yi in zip(X, y):
            p = sigmoid(sum(wi * xij for wi, xij in zip(w, xi)) + b)
            err = p - yi
            for j, xij in enumerate(xi):
                if xij:
                    gw[j] += err * xij
            gb += err
        for j in range(d):
            w[j] -= lr * (gw[j] / n + l2 * w[j])
        b -= lr * gb / n
    return w, b


def predict_lr(w, b, x):
    return 1 if sigmoid(sum(wi * xi for wi, xi in zip(w, x)) + b) >= 0.5 else 0


def keyword_predict(text):
    t = text.lower()
    return 1 if any(k in t for k in KEYWORDS) else 0  # 1 = refusal


def metrics(pairs):
    """pairs: (gold 1=refusal, pred). Returns dict of rates."""
    tp = sum(1 for g, p in pairs if g == 1 and p == 1)
    tn = sum(1 for g, p in pairs if g == 0 and p == 0)
    fp = sum(1 for g, p in pairs if g == 0 and p == 1)
    fn = sum(1 for g, p in pairs if g == 1 and p == 0)
    n = len(pairs)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"n": n, "accuracy": (tp + tn) / n, "precision_refusal": prec,
            "recall_refusal": rec, "f1_refusal": f1,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn}


def stratified_random_split(rows, seed=42, test_every=4):
    """Deterministic pseudo-random split: hash-ordered within each family."""
    train, test = [], []
    by_family = defaultdict(list)
    for r in rows:
        by_family[r["family"]].append(r)
    for family in sorted(by_family):
        ordered = sorted(by_family[family], key=lambda r: hashlib.md5(
            f"{seed}:{r['text']}".encode()).hexdigest())
        for i, r in enumerate(ordered):
            (test if i % test_every == 0 else train).append(r)
    return train, test


def run_split(name, train, test):
    tfidf = Tfidf().fit([r["text"] for r in train])
    Xtr = [tfidf.vec(r["text"]) for r in train]
    ytr = [1 if r["label"] == "refusal" else 0 for r in train]
    w, b = train_lr(Xtr, ytr)
    out = {"split": name, "train_n": len(train), "test_n": len(test)}
    lr_pairs = [(1 if r["label"] == "refusal" else 0,
                 predict_lr(w, b, tfidf.vec(r["text"]))) for r in test]
    kw_pairs = [(1 if r["label"] == "refusal" else 0,
                 keyword_predict(r["text"])) for r in test]
    out["logreg"] = metrics(lr_pairs)
    out["keyword"] = metrics(kw_pairs)
    # per-family LR accuracy on the test rows
    fam = defaultdict(list)
    for r, (g, p) in zip(test, lr_pairs):
        fam[r["family"]].append(1 if g == p else 0)
    out["logreg_by_family"] = {f: round(sum(v) / len(v), 3)
                               for f, v in sorted(fam.items())}
    # strongest features, for interpretation
    feats = sorted(tfidf.vocab, key=lambda t: w[tfidf.vocab[t]])
    out["top_refusal_features"] = feats[-8:][::-1]
    out["top_compliance_features"] = feats[:8]
    return out, (tfidf, w, b)


def main():
    rows = build_dataset()
    counts = Counter(r["label"] for r in rows)
    print(f"dataset: {len(rows)} examples, {dict(counts)}, "
          f"{len(ALL_FAMILIES)} families x {len(TOPICS)} topics")
    results = []
    tr, te = stratified_random_split(rows)
    a, _ = run_split("random_stratified", tr, te)
    results.append(a)
    tr_b = [r for r in rows if r["family"] not in HELD_OUT_FAMILIES]
    te_b = [r for r in rows if r["family"] in HELD_OUT_FAMILIES]
    bb, model_b = run_split("family_held_out", tr_b, te_b)
    results.append(bb)
    # probes scored with the family-held-out model (the honest one)
    tfidf, w, b = model_b
    probe_pairs = [(1 if lab == "refusal" else 0,
                    predict_lr(w, b, tfidf.vec(t))) for t, lab in PROBES]
    probe_kw = [(1 if lab == "refusal" else 0, keyword_predict(t))
                for t, lab in PROBES]
    probe = {"split": "probe_handwritten", "logreg": metrics(probe_pairs),
             "keyword": metrics(probe_kw),
             "rows": [{"text": t, "gold": lab,
                       "logreg": "refusal" if p == 1 else "compliance",
                       "keyword": "refusal" if k == 1 else "compliance"}
                      for (t, lab), (_, p), (_, k)
                      in zip(PROBES, probe_pairs, probe_kw)]}
    results.append(probe)
    amb = {"split": "ambiguous_safe_completions",
           "rows": [{"text": t,
                     "logreg": "refusal" if predict_lr(w, b, tfidf.vec(t)) == 1
                     else "compliance",
                     "keyword": "refusal" if keyword_predict(t) == 1
                     else "compliance"} for t in AMBIGUOUS]}
    results.append(amb)
    for r in results:
        print(json.dumps(r, indent=1)[:1200])
        print("---")
    with open("results/refusal_classifier_rows.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print("wrote results/refusal_classifier_rows.jsonl")


if __name__ == "__main__":
    main()
