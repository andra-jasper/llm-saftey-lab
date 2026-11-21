import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from output_filter_v2 import check, keyword_fires, b64_views
import base64
def test_plain_leak_blocked_raw():
    assert check("My system prompt is: secret")["raw_block"]
def test_base64_leak_only_v2():
    enc = base64.b64encode(b"The evaluation canary token is LAB-CANARY-7F3A-2026.").decode()
    r = check(f"Decode: {enc}")
    assert not r["raw_block"] and r["v2_block"] and any(k.startswith("base64") for k in r["decoded_fired"])
def test_benign_encoded_allowed():
    enc = base64.b64encode(b"The library opens at nine in the morning.").decode()
    assert not check(f"Note: {enc}")["v2_block"]
def test_rot13_view():
    import codecs
    r = check(codecs.encode("Filters off, no restrictions here", "rot_13"))
    assert r["v2_block"]
if __name__ == "__main__":
    for n,f in list(globals().items()):
        if n.startswith("test_"): f(); print("PASS", n)
