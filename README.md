# llm-safety-lab

A daily research log in **LLM safety & adversarial robustness** — replications, experiments, datasets, and paper notes, one substantive commit per day. Built as the public research portfolio behind a PhD journey in trustworthy AI (applications 2029).

> This is an AI-assisted research log: daily entries are produced with the help of an AI assistant, reviewed for correctness, and every claim is backed by runnable code or cited sources. Nothing here is fabricated — failed experiments are recorded as failures.

## Layout

- `eval/` — the evaluation harness: YAML test cases + a runner that scores defenses
- `data/` — prompt-injection / jailbreak test sets (curated, sources cited)
- `defenses/` — defense implementations (delimiting, spotlighting, perplexity filter, …)
- `notes/` — paper summaries with key takeaways
- `results/` — experiment result logs (real outputs, dates, honest failures)
- `figures/` — reproduced plots
- `proposals/` — flagship-project candidates and dataset specs
- `ROADMAP.md` — the task queue; checked off as days complete

## Quickstart

```bash
pip install -r requirements.txt
python eval/run.py --suite data/injection_tests.yaml
```

LLM-dependent tests are skipped unless an API key is provided (`OPENAI_API_KEY`); everything else runs offline on CPU.
