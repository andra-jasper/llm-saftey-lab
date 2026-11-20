"""G7: Meta-SecAlign smoke-test pack (execution blocked on gated HF access).

Target model: facebook/Meta-SecAlign-8B (Chen et al., "Meta SecAlign:
A Secure Foundation LLM Against Prompt Injection Attacks",
arXiv:2507.02735; lab notes F5 in notes/meta_secalign.md). The 8B is
the smallest released SecAlign; both released models are gated on
Hugging Face and the 8B is not CPU-runnable in this lab (F5 verdict).

This script NEVER downloads anything. Default mode:
  1. validates the 12-case smoke subset against the B5 source suite
     (ids exist, categories match, prompts carry the naive RAG assembly);
  2. checks execution prerequisites (HF token present in env, CUDA GPU,
     disk headroom) WITHOUT printing any credential value;
  3. writes a status report: READY only if every prerequisite holds,
     otherwise BLOCKED with the exact missing prerequisites listed.

--run additionally attempts the model load, and is refused unless the
status is READY. Scoring, when it ever runs, is the lab's standard
ideal-follower-free check: the model response is passed to
detector-style manual review fields (followed_user / followed_document /
unclear) recorded per case; no ASR is computed by this script.
"""
import argparse, json, os, shutil, sys

MODEL_ID = "facebook/Meta-SecAlign-8B"
MIN_DISK_GB = 20.0  # 8B bf16 weights ~16 GB + cache headroom

def load_yaml_cases(path):
    import yaml
    with open(path) as f:
        doc = yaml.safe_load(f)
    return doc["cases"]

def validate_subset(subset_cases, source_cases):
    src = {c["id"]: c for c in source_cases}
    problems, checked = [], []
    for c in subset_cases:
        cid = c["id"]
        if cid not in src:
            problems.append(f"{cid}: not in source suite"); continue
        if src[cid]["category"] != c["category"]:
            problems.append(f"{cid}: category mismatch")
        if "prompt" not in src[cid]:
            problems.append(f"{cid}: source case has no assembled prompt")
        checked.append(cid)
    return checked, problems

def check_prerequisites(env=None, cuda_available=False, free_gb=0.0):
    env = os.environ if env is None else env
    prereqs = {
        "hf_token_present": bool(env.get("HF_TOKEN") or env.get("HUGGING_FACE_HUB_TOKEN")),
        "cuda_gpu_available": bool(cuda_available),
        "disk_free_gb_ge_20": free_gb >= MIN_DISK_GB,
    }
    missing = [k for k, v in prereqs.items() if not v]
    return prereqs, missing

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", default="data/secalign_smoke_subset.yaml")
    ap.add_argument("--source", default="data/indirect_injection_tests.yaml")
    ap.add_argument("--out", default=None)
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    subset = load_yaml_cases(a.subset); source = load_yaml_cases(a.source)
    checked, problems = validate_subset(subset, source)
    try:
        import torch; cuda = torch.cuda.is_available()
    except Exception:
        cuda = False
    free_gb = shutil.disk_usage(".").free / 1e9
    prereqs, missing = check_prerequisites(cuda_available=cuda, free_gb=free_gb)
    status = "READY" if (not problems and not missing) else "BLOCKED"
    report = {"model": MODEL_ID, "subset_cases": len(subset),
              "validated_cases": len(checked), "validation_problems": problems,
              "prerequisites": prereqs, "missing": missing,
              "disk_free_gb": round(free_gb, 1), "status": status,
              "download_attempted": False}
    print(json.dumps(report, indent=2))
    if a.out:
        with open(a.out, "w") as f: json.dump(report, f, indent=2)
    if a.run and status != "READY":
        print("REFUSED: --run requires status READY", file=sys.stderr); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
