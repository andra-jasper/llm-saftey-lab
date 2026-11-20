import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from secalign_smoke import validate_subset, check_prerequisites

SRC = [{"id": "a", "category": "x", "prompt": "p"}, {"id": "b", "category": "y", "prompt": "p"}]

def test_validate_ok():
    checked, problems = validate_subset([{"id": "a", "category": "x"}], SRC)
    assert checked == ["a"] and problems == []

def test_validate_missing_and_mismatch():
    _, p1 = validate_subset([{"id": "zz", "category": "x"}], SRC)
    _, p2 = validate_subset([{"id": "a", "category": "WRONG"}], SRC)
    assert p1 and p2

def test_prereq_blocked_without_token_or_gpu():
    _, missing = check_prerequisites(env={}, cuda_available=False, free_gb=100.0)
    assert "hf_token_present" in missing and "cuda_gpu_available" in missing

def test_prereq_ready():
    prereqs, missing = check_prerequisites(env={"HF_TOKEN": "x"}, cuda_available=True, free_gb=50.0)
    assert missing == [] and all(prereqs.values())

if __name__ == "__main__":
    test_validate_ok(); test_validate_missing_and_mismatch()
    test_prereq_blocked_without_token_or_gpu(); test_prereq_ready()
    print("4 tests pass")
