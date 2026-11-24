import sys; sys.path.insert(0, "eval")
from gen_sample_cross_model import auroc, spearman, median
def test_auroc():
    assert auroc([10,20],[1,2])==1.0 and auroc([1],[5])==0.0 and auroc([5],[5])==0.5
def test_spearman():
    assert spearman([1,2,3],[10,20,30])==1.0 and spearman([1,2,3],[30,20,10])==-1.0
def test_median():
    assert median([3,1,2])==2 and median([1,2,3,4])==2.5
