import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from refusal_metric_v2 import build_dataset, HELD_OUT
from collections import Counter
def test_dataset_balanced_900():
    rows=build_dataset(); assert len(rows)==900
    assert Counter(r["label"] for r in rows)=={"refusal":300,"compliance":300,"safe_completion":300}
def test_held_out_has_all_classes():
    rows=build_dataset(); held={r["label"] for r in rows if r["family"] in HELD_OUT}
    assert held=={"refusal","compliance","safe_completion"}
def test_topics_shared():
    rows=build_dataset()
    assert any("growing tomatoes" in r["text"] for r in rows if r["label"]=="safe_completion")
if __name__=="__main__":
    for n,f in list(globals().items()):
        if n.startswith("test_"): f(); print("PASS",n)
