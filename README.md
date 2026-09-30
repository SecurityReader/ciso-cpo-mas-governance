# Confound-Controlled Evaluation of Multi-Agent LLM Governance (CISO–CPO)

Replication package for the study *"When Role Separation Does Not Help: A
Confound-Controlled Evaluation of Multi-Agent LLM Governance for Security–Privacy
Policy Decisions."*

## Summary
We test whether separating the CISO and CPO roles into distinct LLM agents improves
information-security policy-decision quality over a unified architecture. Under a
factorially controlled design (A = role-separated 3-round; B = unified 3-step;
C = unified 3-round, format control) on 12 frozen PIPA-grounded conflict scenarios,
scored blind by a bias-controlled three-model judge ensemble, **role separation was
statistically equivalent to the unified conditions** (TOST, SESOI ±1.0 point;
H1 p_TOST=0.0027). A large pilot effect (Cliff's δ=0.918) disappeared under control
(δ=0.219, Holm p=1.0), showing it arose from schema asymmetry, verbosity, and
self-preference.

## Repository layout
- `scenarios/` — frozen scenarios + SHA-256 freeze hashes (`FREEZE_HASHES.txt`)
- `harness/` — generation & judging code (`run_all.py`, `run_harness.py`, `judge.py`,
  `preflight.py`, `analyze.py`). API keys are supplied at runtime only.
- `analysis/` — analysis script(s) and result files (reliability, tokens, MDES, ceiling)
- `outputs/confirm_v2/` — the valid confirmatory run: 144 traces + judgments (`eval/`)
- `outputs/confirm_v1_invalid/` — the first confirmatory run, **invalidated by a
  truncation artifact** (kept for transparency; do not use for results)
- `docs/` — decision log, model & version provenance, harness change log, embedding config
- `MANIFEST.sha256` — hash of every published file

## Frozen scenario hashes
- scenarios_min.json: `3caa70daefc46943ef9521db06f08fbe86ed61d9b67bc92bfd72a9f8cdf664a9`
- scenarios_phase2_hardened.json: `318779db5d669253e5f92438fdc77aeb90ae74ea76d3104c691667e1b0a8c3b2`

## Reproducing the analysis (no API keys needed)
The judgments are included, so the statistics can be regenerated offline:
```
pip install -r harness/requirements.txt
python harness/analyze.py        # reads outputs/confirm_v2/eval/pointwise.json
```
Regenerating the model outputs themselves requires API keys and is not guaranteed to
reproduce (models are deprecated over time); we therefore publish all raw outputs and
per-judge scores to guarantee **analysis reproducibility**.

## Models & parameters
Generator: claude-sonnet-5 (temperature 0.7, max_tokens 4000). Judges:
claude-haiku-4-5, gpt-5.1, gpt-4.1-mini (generator ≠ judge; ≥1 non-Anthropic to control
self-preference). Local embedding for consensus: BAAI/bge-m3. See `docs/model_versions.md`.

## Data availability statement
All scenarios (with freeze-time SHA-256 hashes), prompts, harness code, raw model outputs
for both confirmatory runs (including the invalidated run), per-judge scores, token-usage
logs, and analysis scripts are included here and archived at [Zenodo DOI — to be added].
API keys are supplied at runtime and are not included.

## License
Code: MIT. Data/scenarios/prompts/outputs/docs: CC BY 4.0. Model outputs are subject to
the respective providers' terms. See `LICENSE`.

## Disclaimer
This is independent academic research by the author(s); it does not represent the views of,
and is not endorsed by, any employer. Scenarios are constructed research vignettes.

## Citation
See `CITATION.cff`.
