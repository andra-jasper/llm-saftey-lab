import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"eval"))
from dilution_second_model import build_rep_prompt, BASES, SUFFIXES
def test_rrep_construction():
    assert build_rep_prompt("B.", "S", 2) == "B. B. S"
    assert build_rep_prompt("B.", "S", 4) == "B. B. B. B. S"
    assert len(BASES)==5 and len(SUFFIXES)==15
def test_summary_internal_consistency():
    S=json.loads((ROOT/"results"/"dilution_second_model_h2_summary.json").read_text())
    assert S["n"]==30 and S["pooled_n"]==30 and S["j2_n"]==15 and S["j4_n"]==15
    assert S["pooled_det_win_gpt2"]==S["j2_det_win_gpt2"]+S["j4_det_win_gpt2"]
    assert S["pooled_det_win_distil"]==26  # G8's committed figure
    assert S["gpt2_thr_windowed"]==690.13  # G9's committed benign max
if __name__=="__main__":
    test_rrep_construction(); print("construction ok")
    try: test_summary_internal_consistency(); print("summary ok")
    except FileNotFoundError: print("summary not yet written (pre-run)")
