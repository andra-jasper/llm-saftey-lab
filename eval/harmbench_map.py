"""D2: lab-category -> HarmBench mapping, kept honest by construction.

HarmBench (Mazeika et al., ICML 2024, arXiv:2402.04249) classifies
*behaviours* -- what harm is requested -- on two axes (7 semantic
categories, 4 functional categories) and evaluates *attacks* (18 red
teaming methods) separately. This lab classifies *attack mechanisms*
-- how an instruction hierarchy is violated -- in TAXONOMY.md (C7).
The axes are largely orthogonal, so most rows below are "none" or
"partial" BY DESIGN: the mapping's value is recording exactly where
the two schemes do and do not meet, not forcing a correspondence.

This module is the machine-checked source for the mapping table in
notes/harmbench.md. It fails (AssertionError) if:
  * a lab attack category from the C7 inventory is unmapped or
    mapped twice,
  * a HarmBench semantic/functional category is neither reached by
    some lab row nor listed as explicitly uncovered,
  * a verdict is outside {direct, partial, none}.

Lab inventory source: TAXONOMY.md (C7), whose own counts are
recomputed from data/*.yaml by eval/taxonomy.py. Counts here are
case counts per suite, kept suite-separate as in C3/C7.
"""

# --- Lab inventory (TAXONOMY.md, C7) -----------------------------------
# suite -> {category: n_cases}
LAB_SUITES = {
    "injection_tests.yaml (A2 direct)": {
        "direct_override": 5,
        "roleplay": 5,
        "encoded_payload": 5,
        "multi_turn": 5,
        "authority_claim": 5,
    },
    "indirect_injection_tests.yaml (B5 indirect)": {
        "exfiltration": 3,
        "task_hijack": 3,
        "manipulation": 3,
        "authority_spoof_in_document": 3,
        "hidden_encoded_in_document": 3,
    },
    "completion_tests.yaml (C6 completion)": {
        "completion_real_textual": 3,
        "completion_real_reserved": 3,
        "completion_close": 3,
        "completion_close_nested": 1,
        "completion_other": 3,
    },
    "spotlight_escape_probes.yaml (B2 probes)": {
        "delimiter_escape": 2,
        "delimiter_spoof_generic": 2,
        "datamark_separator_trick": 3,
        "delimiter_guess": 1,
    },
    "rag_escape_probes.yaml (B6 probes)": {
        "delimiter_escape": 3,
        "datamark_escape": 3,
    },
    "output_cases.yaml (B4 output stage, compromised only)": {
        "leak_verbatim": 5,
        "compliance": 5,
        "evasive_leak": 5,
    },
}

# --- HarmBench axes (paper Sec. 4.1) ------------------------------------
HARMBENCH_SEMANTIC = [
    "Cybercrime & Unauthorized Intrusion",
    "Chemical & Biological Weapons/Drugs",
    "Copyright Violations",
    "Misinformation & Disinformation",
    "Harassment & Bullying",
    "Illegal Activities",
    "General Harm",
]
HARMBENCH_FUNCTIONAL = {  # name: n_behaviours (paper Sec. 4.1)
    "standard": 200,
    "copyright": 100,
    "contextual": 100,
    "multimodal": 110,
}

# --- The mapping ----------------------------------------------------------
# (suite, lab category) -> (verdict, harmbench target, note)
# verdict: direct = same construct; partial = overlaps one aspect;
# none = no counterpart in HarmBench (recorded, not hidden).
MAPPING = {
    ("injection_tests.yaml (A2 direct)", "direct_override"):
        ("partial", "attack: Direct Request",
         "Same surface move (ask plainly, override prior context) but a different target: lab cases override a system prompt to leak/hijack; HarmBench Direct Request asks for the harmful behaviour itself with no hierarchy to override."),
    ("injection_tests.yaml (A2 direct)", "roleplay"):
        ("partial", "attack: PAP / Human Jailbreaks",
         "Persona framing exists in HarmBench only as an *attack method* (PAP persuasion, human jailbreak templates), never as a behaviour category; the lab treats it as a data category instead."),
    ("injection_tests.yaml (A2 direct)", "encoded_payload"):
        ("none", "-",
         "HarmBench has no encoding axis: its attacks are optimised or templated prompts, and its success criteria require the *completion* to be identifiable in English (App. C.1), so an encoded payload that stays encoded would not even score."),
    ("injection_tests.yaml (A2 direct)", "multi_turn"):
        ("none", "-",
         "HarmBench test cases are single prompts by construction (Sec. 3.1: a method emits a set of test cases per behaviour); there is no multi-turn functional category. Closest relative is many-shot (Anil et al., C8/D1), which HarmBench hosts as an external replication, not a category."),
    ("injection_tests.yaml (A2 direct)", "authority_claim"):
        ("none", "-",
         "Forged developer/admin priority has no HarmBench counterpart: HarmBench models have no privileged instruction channel in the threat model, so there is no authority to forge."),
    ("indirect_injection_tests.yaml (B5 indirect)", "exfiltration"):
        ("none", "-",
         "System-prompt / context exfiltration is not a HarmBench behaviour: no semantic category covers disclosing the model's own instructions. The nearest neighbour, Copyright Violations, protects third-party text, judged by hashing -- a different secret and a different judge."),
    ("indirect_injection_tests.yaml (B5 indirect)", "task_hijack"):
        ("none", "-",
         "Replacing the user's task with a document's task presupposes a benign original task plus a data channel; HarmBench behaviours are the harmful task itself, requested directly. No counterpart."),
    ("indirect_injection_tests.yaml (B5 indirect)", "manipulation"):
        ("partial", "semantic: Misinformation & Disinformation",
         "The one B5 family whose *goal* can be a HarmBench semantic category: a document that steers the answer toward false claims aims at misinformation. The delivery (via retrieved document) is still outside HarmBench's functional axes."),
    ("indirect_injection_tests.yaml (B5 indirect)", "authority_spoof_in_document"):
        ("none", "-",
         "Authority forged inside a retrieved document: doubly outside HarmBench (no data channel, no authority channel)."),
    ("indirect_injection_tests.yaml (B5 indirect)", "hidden_encoded_in_document"):
        ("none", "-",
         "Hidden/encoded payload in a document combines the two axes HarmBench lacks (data channel, encoding)."),
    ("completion_tests.yaml (C6 completion)", "completion_real_textual"):
        ("partial", "attack: GCG-adjacent completion framing",
         "Faking a completed turn resembles the completion-style attacks StruQ measured; in HarmBench the closest scored relative is the optimisation family (GCG targets a compliant *opening*), but HarmBench defines no completion functional category."),
    ("completion_tests.yaml (C6 completion)", "completion_real_reserved"):
        ("none", "-",
         "Reserved-token forgery is specific to structured-query front-ends (StruQ, C5/C6); HarmBench predates that defense surface and has no token-channel category."),
    ("completion_tests.yaml (C6 completion)", "completion_close"):
        ("none", "-",
         "Near-miss delimiters are an adaptive attack on a named defense (the lab's probe tier); HarmBench attacks are defense-agnostic methods, not per-defense probes."),
    ("completion_tests.yaml (C6 completion)", "completion_close_nested"):
        ("none", "-",
         "Nested-delimiter assembly targets the C6 filter specifically; no HarmBench counterpart."),
    ("completion_tests.yaml (C6 completion)", "completion_other"):
        ("partial", "attack: Human Jailbreaks",
         "A fake response in a *different* formatting convention is closest to hand-crafted jailbreak templates; the match is in spirit (human ingenuity) not in mechanism."),
    ("spotlight_escape_probes.yaml (B2 probes)", "delimiter_escape"):
        ("none", "-",
         "Probes exist to break a named defense (B2); HarmBench reports ASR per attack x model, with defenses being whole models, so per-transform escape probes have no slot."),
    ("spotlight_escape_probes.yaml (B2 probes)", "delimiter_spoof_generic"):
        ("none", "-",
         "As above: defense-specific, no HarmBench slot."),
    ("spotlight_escape_probes.yaml (B2 probes)", "datamark_separator_trick"):
        ("none", "-",
         "Separator tricks defeat space-based datamarking specifically; HarmBench has no datamarked defense among its 33 targets."),
    ("spotlight_escape_probes.yaml (B2 probes)", "delimiter_guess"):
        ("none", "-",
         "Guessing a delimiter is meaningful only against delimiting defenses; no counterpart."),
    ("rag_escape_probes.yaml (B6 probes)", "delimiter_escape"):
        ("none", "-",
         "RAG variant of the B2 probe; same reasoning, plus the data channel HarmBench lacks."),
    ("rag_escape_probes.yaml (B6 probes)", "datamark_escape"):
        ("none", "-",
         "As above."),
    ("output_cases.yaml (B4 output stage, compromised only)", "leak_verbatim"):
        ("partial", "functional: copyright (judge only)",
         "The only place the two labs' *judges* meet: HarmBench scores verbatim reproduction of copyrighted text by hashing, B4 scores verbatim leakage of a system prompt by TF-IDF similarity. Same measurement shape (reproduction of protected text), different protected text."),
    ("output_cases.yaml (B4 output stage, compromised only)", "compliance"):
        ("partial", "metric: ASR success criteria (App. C.1)",
         "A B4 'compliance' output -- the model visibly carrying out the injected instruction -- is what HarmBench's success criteria describe ('the model either exhibited the behaviour or clearly tried to'), but HarmBench applies them to harmful behaviours, not injected ones."),
    ("output_cases.yaml (B4 output stage, compromised only)", "evasive_leak"):
        ("none", "-",
         "Paraphrased/translated leakage evades verbatim judges in both schemes; HarmBench's hashing judge would miss it by construction and its LLM judge is not asked about prompt leakage at all."),
}

# HarmBench semantic categories no lab row reaches, stated explicitly.
UNCOVERED_SEMANTIC = [
    "Cybercrime & Unauthorized Intrusion",
    "Chemical & Biological Weapons/Drugs",
    "Copyright Violations",
    "Harassment & Bullying",
    "Illegal Activities",
    "General Harm",
]
# (Misinformation & Disinformation is the one semantic category a lab
# row -- B5 manipulation -- partially reaches.)

VERDICTS = {"direct", "partial", "none"}


def check():
    # every lab category mapped exactly once
    lab_keys = {(s, c) for s, cats in LAB_SUITES.items() for c in cats}
    assert set(MAPPING) == lab_keys, (
        f"unmapped={lab_keys - set(MAPPING)} extra={set(MAPPING) - lab_keys}")
    # verdicts valid
    for k, (v, _t, _n) in MAPPING.items():
        assert v in VERDICTS, (k, v)
    # every semantic category reached-partially or listed uncovered
    reached = {t.split(": ", 1)[1] for v, t, _n in MAPPING.values()
               if v in ("direct", "partial") and t.startswith("semantic: ")}
    assert reached | set(UNCOVERED_SEMANTIC) == set(HARMBENCH_SEMANTIC), reached
    assert not (reached & set(UNCOVERED_SEMANTIC))
    # functional totals are the paper's
    assert sum(HARMBENCH_FUNCTIONAL.values()) == 510
    counts = {}
    for v, _t, _n in MAPPING.values():
        counts[v] = counts.get(v, 0) + 1
    return counts


def main():
    counts = check()
    total_cases = sum(n for cats in LAB_SUITES.values() for n in cats.values())
    print(f"lab categories mapped: {len(MAPPING)} "
          f"({total_cases} attack cases across {len(LAB_SUITES)} suites)")
    print(f"verdicts: {counts.get('direct', 0)} direct, "
          f"{counts.get('partial', 0)} partial, {counts.get('none', 0)} none")
    print("HarmBench semantic categories reached (even partially): "
          "Misinformation & Disinformation only")
    print(f"HarmBench semantic categories uncovered by any lab suite: "
          f"{len(UNCOVERED_SEMANTIC)} of 7")
    print("OK: mapping is complete and every gap is explicit")


if __name__ == "__main__":
    main()
