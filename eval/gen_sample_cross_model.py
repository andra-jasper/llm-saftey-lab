#!/usr/bin/env python3
"""G1 confound control (ROADMAP task H3).

G1 found distilgpt2-sampled suffixes (GEN-SAMPLE, n=25) score windowed
AUROC 0.416 under distilgpt2 -- but generator = scorer there, so low
perplexity is near-guaranteed. H3 rescores G1's exact committed prompts
with gpt2 (generator != scorer; same GPT-2 family, larger model).
Benign reference: G9's committed gpt2 rows (A6's 10 benign texts scored
with gpt2, never rescored here). Distilgpt2 numbers are G1's committed
rows, reused, and their AUROCs are recomputed as a check (must match
G1's summary: full 0.496, windowed 0.416).

Reading fixed BEFORE scoring: gpt2 windowed AUROC >= 0.75 -> the 0.416
was mainly a generator=scorer artefact; <= 0.60 -> low separation is a
property of model-sampled text even cross-model; between -> partial.
Thresholds: each model's own G8-rule benign-only frozen threshold
(max benign score). Detector statement only -- no live model, no ASR.
Outputs: results/gen_sample_gpt2_rows.jsonl,
         results/gen_sample_cross_model_h3_summary.json
"""
import json, math, random
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
ROOT = Path(__file__).resolve().parent.parent
MODEL_NAME="gpt2"; WINDOW=10; SEED=20261124
def perplexity(text, model, tok):
    ids = tok(text, return_tensors="pt")["input_ids"]
    if ids.shape[1] < 2: return float("nan")
    with torch.no_grad(): out = model(ids, labels=ids)
    return math.exp(out.loss.item())
def windowed_perplexity(text, model, tok, window=WINDOW):
    ids = tok(text)["input_ids"]
    if len(ids) <= window: return perplexity(text, model, tok)
    return max(perplexity(tok.decode(ids[s:s+window]), model, tok) for s in range(0, len(ids)-window+1))
def auroc(pos, neg):
    w=sum(1.0 if p>n else 0.5 if p==n else 0.0 for p in pos for n in neg); return w/(len(pos)*len(neg))
def bootstrap_ci(pos, neg, n=1000, seed=SEED):
    rng=random.Random(seed); vals=[]
    for _ in range(n):
        vals.append(auroc([rng.choice(pos) for _ in pos],[rng.choice(neg) for _ in neg]))
    vals.sort(); return [round(vals[int(0.025*n)],3), round(vals[int(0.975*n)-1],3)]
def median(xs):
    xs=sorted(xs); k=len(xs); return xs[k//2] if k%2 else (xs[k//2-1]+xs[k//2])/2
def spearman(a,b):
    def ranks(xs):
        order=sorted(range(len(xs)), key=lambda i: xs[i]); r=[0.0]*len(xs); i=0
        while i<len(xs):
            j=i
            while j+1<len(xs) and xs[order[j+1]]==xs[order[i]]: j+=1
            avg=(i+j)/2+1
            for k in range(i,j+1): r[order[k]]=avg
            i=j+1
        return r
    ra,rb=ranks(a),ranks(b); ma=sum(ra)/len(ra); mb=sum(rb)/len(rb)
    num=sum((x-ma)*(y-mb) for x,y in zip(ra,rb)); den=math.sqrt(sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))
    return round(num/den,3) if den else float("nan")
def load(p): return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def main():
    g1=load(ROOT/"results"/"flagship_variant_g1_rows.jsonl")
    g9=load(ROOT/"results"/"perplexity_gpt2_rows.jsonl")
    a6=load(ROOT/"results"/"perplexity_rows.jsonl")
    ben_g=[r for r in g9 if r["group"]=="benign"]; ben_d=[r for r in a6 if r["group"]=="benign"]
    bg_w=[r["windowed_perplexity"] for r in ben_g]; bg_f=[r["perplexity"] for r in ben_g]
    bd_w=[r["windowed_perplexity"] for r in ben_d]; bd_f=[r["perplexity"] for r in ben_d]
    # check: recomputed distil AUROCs must match G1 summary
    chk_f=round(auroc([r["perplexity"] for r in g1],bd_f),3); chk_w=round(auroc([r["windowed_perplexity"] for r in g1],bd_w),3)
    assert (chk_f,chk_w)==(0.496,0.416), f"G1 check failed {(chk_f,chk_w)}"
    tok=AutoTokenizer.from_pretrained(MODEL_NAME); model=AutoModelForCausalLM.from_pretrained(MODEL_NAME); model.eval()
    rows=[]
    for r in g1:
        nr={"id":r["id"],"arm":"GEN-SAMPLE","model":MODEL_NAME,"prompt":r["prompt"],
            "perplexity":round(perplexity(r["prompt"],model,tok),2),
            "windowed_perplexity":round(windowed_perplexity(r["prompt"],model,tok),2),
            "distil_perplexity":r["perplexity"],"distil_windowed_perplexity":r["windowed_perplexity"],
            "provenance":"G1 committed prompt rescored with gpt2 (H3, 2026-11-24)"}
        rows.append(nr); print(nr["id"],nr["perplexity"],nr["windowed_perplexity"],flush=True)
    (ROOT/"results"/"gen_sample_gpt2_rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows)+"\n")
    gw=[r["windowed_perplexity"] for r in rows]; gf=[r["perplexity"] for r in rows]
    thr_gw,thr_gf,thr_dw,thr_df=max(bg_w),max(bg_f),max(bd_w),max(bd_f)
    S={"model":MODEL_NAME,"n":len(rows),"g1_recompute_check":{"full":chk_f,"windowed":chk_w},
       "gpt2":{"full_median":round(median(gf),2),"windowed_median":round(median(gw),2),
               "full_auroc":round(auroc(gf,bg_f),3),"full_auroc_ci95":bootstrap_ci(gf,bg_f),
               "windowed_auroc":round(auroc(gw,bg_w),3),"windowed_auroc_ci95":bootstrap_ci(gw,bg_w),
               "thr_full":thr_gf,"thr_windowed":thr_gw,
               "det_full":sum(1 for x in gf if x>thr_gf),"det_windowed":sum(1 for x in gw if x>thr_gw)},
       "distilgpt2":{"full_median":round(median([r['perplexity'] for r in g1]),2),"windowed_median":round(median([r['windowed_perplexity'] for r in g1]),2),
               "full_auroc":chk_f,"windowed_auroc":chk_w,"thr_full":thr_df,"thr_windowed":thr_dw,
               "det_full":sum(1 for r in g1 if r["perplexity"]>thr_df),"det_windowed":sum(1 for r in g1 if r["windowed_perplexity"]>thr_dw)},
       "spearman_full":spearman([r["perplexity"] for r in g1],gf),
       "spearman_windowed":spearman([r["windowed_perplexity"] for r in g1],gw),
       "benign_gpt2":{"full_median":round(median(bg_f),2),"windowed_median":round(median(bg_w),2)}}
    w=S["gpt2"]["windowed_auroc"]
    S["verdict"]="generator=scorer artefact (gpt2 windowed AUROC >= 0.75)" if w>=0.75 else ("property of model-sampled text (gpt2 windowed AUROC <= 0.60)" if w<=0.60 else "partial (0.60 < gpt2 windowed AUROC < 0.75)")
    (ROOT/"results"/"gen_sample_cross_model_h3_summary.json").write_text(json.dumps(S,indent=2))
    print(json.dumps(S,indent=2))
if __name__=="__main__": main()
