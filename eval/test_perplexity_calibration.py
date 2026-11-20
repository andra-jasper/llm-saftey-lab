import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from perplexity_calibration import auroc, calibrate, detect

ROWS = [{"group": "benign", "perplexity": 10.0, "windowed_perplexity": 100.0},
        {"group": "benign", "perplexity": 20.0, "windowed_perplexity": 300.0},
        {"group": "suffix_attack", "perplexity": 15.0, "windowed_perplexity": 250.0},
        {"group": "suffix_attack", "perplexity": 25.0, "windowed_perplexity": 350.0}]

def test_threshold_is_benign_max():
    thr, _ = calibrate(ROWS, "windowed_perplexity"); assert thr == 300.0

def test_detect_counts():
    assert detect(ROWS, "windowed_perplexity", 300.0, group="suffix_attack") == (1, 2)
    assert detect(ROWS, "windowed_perplexity", 300.0, group="benign") == (0, 2)

def test_auroc():
    assert auroc([350.0], [100.0, 300.0]) == 1.0
    assert auroc([50.0], [100.0]) == 0.0

if __name__ == "__main__":
    test_threshold_is_benign_max(); test_detect_counts(); test_auroc()
    print("3 tests pass")
