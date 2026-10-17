#!/usr/bin/env python3
"""Corpus statistics for data/jailbreak_corpus.md (roadmap task A3).

Parses the structured ## JB-NNN entries, computes descriptive statistics,
and writes results/jailbreak_corpus_stats.md. Offline; stdlib only.

Usage:
    python3 eval/corpus_stats.py [corpus.md] [output.md]
"""
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def parse_corpus(path: Path):
    """Parse ## JB-NNN entries with '- Field: value' lines and one ```text block."""
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^## (JB-\d+)\s*[—:–-]\s*(.+)$", text)[1:]
    entries = []
    for i in range(0, len(chunks), 3):
        jid = chunks[i].strip()
        name = chunks[i + 1].strip()
        body = chunks[i + 2]
        fields = dict(re.findall(r"(?m)^- ([A-Za-z _]+):\s*(.+)$", body))
        m = re.search(r"```text\n(.*?)```", body, re.S)
        prompt = m.group(1).strip() if m else ""
        entries.append({
            "id": jid, "name": name, "prompt": prompt,
            "technique": fields.get("technique", "").strip(),
            "source": fields.get("source", "").strip(),
            "target": fields.get("target_category", "").strip(),
            "chars": len(prompt), "words": len(prompt.split()),
            "lines": prompt.count("\n") + 1 if prompt else 0,
        })
    return entries


def source_label(source: str) -> str:
    """Bucket the free-text source citations into short venue labels."""
    buckets = [
        ("JailbreakBench (Chao et al., 2024)", ["jailbreakbench", "chao et al., 2024"]),
        ("HarmBench (Mazeika et al., 2024)", ["harmbench", "mazeika"]),
        ("GCG (Zou et al., 2023)", ["gcg", "zou et al."]),
        ("PAIR (Chao et al., 2023)", ["pair"]),
        ("Wei et al., \"Jailbroken\" (2023)", ["wei et al."]),
        ("Andriushchenko et al. (2024)", ["andriushchenko"]),
        ("ArtPrompt (Jiang et al., 2024)", ["artprompt", "jiang et al."]),
        ("Many-shot jailbreaking (Anthropic, 2024)", ["many-shot", "anil et al."]),
        ("Crescendo (Russinovich et al., 2024)", ["crescendo", "russinovich"]),
        ("Low-resource languages (Yong et al., 2024)", ["yong et al.", "low-resource"]),
        ("FlowGPT / JailbreakChat (community)", ["flowgpt", "jailbreakchat", "alex albert"]),
        ("This lab's A2 suite", ["this lab"]),
    ]
    s = source.lower()
    for label, keys in buckets:
        if any(k in s for k in keys):
            return label
    return "Other"


def stats(entries):
    for e in entries:
        e["source_bucket"] = source_label(e["source"])
    n = len(entries)
    chars = [e["chars"] for e in entries]
    words = [e["words"] for e in entries]
    tokens = Counter()
    for e in entries:
        tokens.update(w.strip(".,;:!?\"'()[]{}").lower()
                      for w in e["prompt"].split()
                      if len(w.strip(".,;:!?\"'()[]{}")) > 3)
    stop = {"that", "this", "with", "from", "your", "have", "will", "they",
            "them", "what", "when", "then", "than", "into", "there", "their",
            "would", "which", "were", "been", "being", "does", "did", "the",
            "and", "for", "are", "but", "not", "you", "all", "can", "had",
            "her", "was", "one", "our", "out", "has", "there", "now"}
    top = [(t, c) for t, c in tokens.most_common() if t not in stop][:15]
    return {
        "n": n,
        "by_technique": Counter(e["technique"] for e in entries),
        "by_source": Counter(e["source_bucket"] for e in entries),
        "by_target": Counter(e["target"] for e in entries),
        "chars_min": min(chars), "chars_max": max(chars),
        "chars_mean": sum(chars) / n,
        "words_min": min(words), "words_max": max(words),
        "words_mean": sum(words) / n,
        "top_tokens": top,
        "longest": max(entries, key=lambda e: e["chars"]),
        "shortest": min(entries, key=lambda e: e["chars"]),
    }


def render(s, run_date: str) -> str:
    lines = [
        "# Jailbreak corpus statistics",
        "",
        f"Run date: {run_date} | Corpus: `data/jailbreak_corpus.md` | Tool: `eval/corpus_stats.py`",
        "",
        f"Total entries: **{s['n']}**",
        "",
        "## By technique family",
        "",
        "| Technique | Count |",
        "| --- | --- |",
    ]
    lines += [f"| {k} | {v} |" for k, v in s["by_technique"].most_common()]
    lines += [
        "",
        "## By source citation",
        "",
        "| Source | Count |",
        "| --- | --- |",
    ]
    lines += [f"| {k} | {v} |" for k, v in s["by_source"].most_common()]
    lines += [
        "",
        "## By target harm category",
        "",
        "| Target | Count |",
        "| --- | --- |",
    ]
    lines += [f"| {k or '(unspecified)'} | {v} |" for k, v in s["by_target"].most_common()]
    lines += [
        "",
        "## Prompt length (the representative excerpts, not full originals)",
        "",
        f"- Characters: min {s['chars_min']}, mean {s['chars_mean']:.0f}, "
        f"max {s['chars_max']} ({s['longest']['id']})",
        f"- Words: min {s['words_min']}, mean {s['words_mean']:.0f}, "
        f"max {s['words_max']} ({s['longest']['id']})",
        f"- Shortest entry: {s['shortest']['id']} ({s['shortest']['name']}), "
        f"{s['shortest']['chars']} chars",
        "",
        "## Top content tokens (length > 3, stopwords removed)",
        "",
        "| Token | Count |",
        "| --- | --- |",
    ]
    lines += [f"| {t} | {c} |" for t, c in s["top_tokens"]]
    lines += [
        "",
        "## Notes",
        "",
        "- Entries are hand-curated, representative excerpts for defensive-evaluation "
        "purposes; lengths reflect the excerpts, not the original full prompts.",
        "- `adversarial-suffix` (JB-017) is the only automated-optimization entry; "
        "the rest are human-written templates from public compilations.",
        "- Source bucketing is first-match on citation text: JB-017 (GCG suffix) is "
        "counted under JailbreakBench because its citation notes the suffixes ship in "
        "the JailbreakBench artifact set; the GCG paper itself is cited in its entry.",
    ]
    return "\n".join(lines) + "\n"


def main():
    corpus = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data" / "jailbreak_corpus.md"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "results" / "jailbreak_corpus_stats.md"
    entries = parse_corpus(corpus)
    assert entries, f"no entries parsed from {corpus}"
    assert len(entries) == 20, f"expected 20 entries, got {len(entries)}"
    report = render(stats(entries), date.today().isoformat())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"parsed {len(entries)} entries from {corpus}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
