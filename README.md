# Role Separation Helps, Conditionally: A Rubric-Sensitive Multi-Agent Large Language Model (LLM) Study of Security–Privacy Policy Decisions under Korea's PIPA

[![DOI](https://zenodo.org/badge/1400227740.svg)](https://doi.org/10.5281/zenodo.23348744)

Replication package for the study
*"Role Separation Helps, Conditionally: A Rubric-Sensitive Multi-Agent Large Language Model (LLM) Study of Security–Privacy Policy Decisions under Korea's PIPA."*

> **Scope.** This is a confound-controlled **comparison of three LLM pipelines**, not a
> claim about how human CISO/CPO functions should be organized. Results are conditional
> on the measured composite scores, the two primary contrasts, the eight conflict
> scenarios, and a post-hoc ±1.0-point equivalence margin.

> **Language.** The scenarios are grounded in Korea's Personal Information Protection Act
> (PIPA), so the models were prompted in Korean and the generated policies and judge
> rationales are in Korean — that is the authoritative experimental record. English
> readers can follow the full study without Korean: scenario translations are in
> `scenarios/*.en.json`, all prompts in `docs/PROMPTS_EN.md`, and every data field in
> `docs/DATA_DICTIONARY.md`. All numeric fields (scores, tokens, statistics) are
> language-independent.

## Summary of findings
We test whether separating the Chief Information Security Officer (CISO) and Chief
Privacy Officer (CPO) into distinct LLM agents improves information-security
policy-decision quality over a unified pipeline. Three conditions — **A** (role-separated,
3 rounds + mediator), **B** (unified 3-step), **C** (unified 3-round, deliberation-format
control) — are run on 12 frozen PIPA-grounded scenarios (8 conflict scenarios form the
primary analysis), each ×3 repetitions, and scored blind by a three-model judge ensemble
(claude-haiku-4-5, gpt-5.1, gpt-4.1-mini).

- Under the primary rubric, role separation (A−C) shows a **significant advantage** on the 25-point
  composite: **+0.722 points, Cliff's δ=0.812, sign-test Holm p=0.0078**, consistent across 8/8
  conflict scenarios (post-hoc ±1.0-point TOST indeterminate). The deliberation-format contrast
  (B−C) is null/equivalent (+0.25; TOST p=0.0024). This concerns the A−C and B−C contrasts,
  not a joint claim over all three conditions.
- The large keyless-pilot effect (Cliff's δ=0.918) is **largely recovered** under the
  confound-controlled design on the primary rubric (δ=0.812, Holm p=0.0078). The earlier mixed-cap
  run gave a smaller estimate (δ=0.297, Holm p=0.69); under the uniform per-call cap (v1.0.5) the
  estimate changed (see `CHANGELOG.md`). Protocol changes between pilot and
  confirmatory run (schema symmetry, length, self-preference, judge configuration) were **not**
  individually isolated.
- **Rubric sensitivity (Q03) — the key caveat:** re-scoring all 108 answers with a corrected rubric
  that penalizes omissions **attenuates the A−C advantage to equivalence** (+0.167, δ 0.328, Holm
  p=1.0, TOST p=0.0008); B−C stays equivalent (−0.083). The role-separation benefit is therefore
  **rubric-conditional** and localized to M5 (residual-risk disclosure — the least-saturated metric,
  ~76% at maximum vs ≥93% for M1–M4). The
  re-scoring uses the complete three-judge ensemble (324/324); three corrected-rubric responses
  (CFL-05_A_3, CFL-06_A_2 for gpt-5.1; CFL-09_A_3 for claude-haiku-4-5) that initially failed JSON
  parsing were re-queried and recovered. The corrected-rubric A-C estimate is +0.167 (δ 0.328,
  Holm p 1.0, TOST p 0.0008), equivalent within ±1 point.
- Compute was **measured, not matched** (A used ~1.9× the total tokens of C, medians); the result
  is not an artifact of A being under-resourced.

> **Aggregation note.** All reported statistics are computed from the per-judge metric scores
> **without intermediate rounding**; values are rounded only for display, and the sign test
> and Cliff's δ treat paired differences within a 1e−9 tolerance as ties, so exact ties are
> preserved (under the primary rubric all eight A−C scenario differences are positive; exact zeros
> arise in the B−C and corrected-rubric contrasts). See `CHANGELOG.md`
> (v1.0.1) and `docs/harness_changes.md`.

See the manuscript for the full interpretation, threats to validity, and the ceiling-effect
and single-generator limitations.

## Repository layout
- `scenarios/` — frozen scenarios + SHA-256 freeze hashes (`FREEZE_HASHES.txt`);
  English translations in `scenarios_min.en.json` and `scenarios_phase2_hardened.en.json`
- `harness/` — generation & judging code (`run_all.py`, `run_harness.py`, `judge.py`,
  `analyze.py`, `requirements.txt`)
- `analysis/` — standalone analysis scripts and cached results
  (`reliability.py` → ICC/Krippendorff/Gwet AC1; `mdes_ceiling.py` → sensitivity power &
  ceiling; `tokens.py` → token usage)
- `outputs/confirm_v3/` — the confirmatory run used in the paper (confound-controlled: uniform
  8,000-token cap, zero mid-deliberation truncation; Phase-1 regenerated)
  - `eval/` — `pointwise.json` (1,620 scores), `pairwise.json`, `phase2_continuous.json`,
    `analysis.json` (no-intermediate-rounding; regenerated v1.0.1)
  - `traces/` — all 108 Phase-1 traces (regenerated at uniform cap) + 36 Phase-2c trajectories
    (carried over unchanged from `confirm_v2`)
  - `rubric_sensitivity/` — Q03 corrected-rubric re-scoring (`q03_pointwise.json`,
    `q03_analysis.json`)
  - `_token_usage.csv`
- `outputs/confirm_v2/`, `outputs/confirm_v1_invalid/` — superseded earlier runs, kept for
  transparency (do not cite)
- `reproduce/` — helper scripts to reproduce generation/judging behind a corporate
  intercepting (MITM) proxy on Python 3.13 (see `README_r41.md`); includes the Q03
  re-scoring (`q03_rescore.py`, `q03_analyze.py`) and the no-round re-aggregation used for
  verification (`reanalyze_noround.py`)
- `docs/` — decision log, model/version provenance, embedding config, harness-change log,
  `PROMPTS_EN.md` (English translation of all generation/judging prompts),
  `DATA_DICTIONARY.md` (every data file and field explained for English readers),
  and `figures/` (Figures 1–3, regenerated from frozen data by `analysis/make_figures.py`)

## Reproduce
1. `cd harness && pip install -r requirements.txt`
2. **Set API keys and run config as environment variables** (never hard-code or commit them).
   Two providers are used: **Anthropic** (generation + one judge) and **OpenAI** (two judges).

   PowerShell (Windows):
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-..."
   $env:OPENAI_API_KEY    = "sk-proj-..."
   $env:GEN_MODEL    = "claude-sonnet-5"
   $env:JUDGE_MODELS = "claude-haiku-4-5-20251001,gpt-5.1,gpt-4.1-mini"
   $env:MAX_TOKENS   = "8000"        # uniform cap for ALL conditions (prevents mid-deliberation truncation)
   $env:TEMPERATURE  = "0.7"; $env:REPS = "3"; $env:LLM_BACKEND = "api"
   ```

   bash / zsh (macOS/Linux):
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OPENAI_API_KEY="sk-proj-..."
   export GEN_MODEL="claude-sonnet-5"
   export JUDGE_MODELS="claude-haiku-4-5-20251001,gpt-5.1,gpt-4.1-mini"
   export MAX_TOKENS=8000            # uniform cap for ALL conditions
   export TEMPERATURE=0.7 REPS=3 LLM_BACKEND=api
   ```

   Keys live only in your shell session (or a local, **git-ignored** `.env`). **Never commit keys** —
   `.gitignore` already excludes `.env`, `*.env`, `*api_key*`, `*.key`. Verify everything before any
   paid call with `python harness/preflight.py` (checks both keys, the 3-judge ensemble incl. a
   non-Anthropic judge, and the frozen-scenario hash). No keys? set `LLM_BACKEND=offline` to replay
   the shipped traces for a cost-free pipeline check.

   After generation, confirm run integrity (uniform cap, zero truncation) with the gate:
   `python harness/validate_run.py --traces harness/output/traces --cap 8000` → must print **GREEN**.
3. `python run_all.py` — generate → judge → Phase-2c → analyze (writes to `outputs/`).
4. **Statistics only, no API** (all paths are package-relative; run from the repository root
   or the stated folder). The analysis code computes the composite from per-judge raw scores
   **without intermediate rounding** and preserves exact ties:
   - Table V (primary rubric): `cd analysis && python analyze.py`
     → writes `outputs/confirm_v3/eval/analysis.json`; reproduces A−C mean +0.722, δ 0.812,
     Holm p 0.0078 (significant, 8/8 scenarios), TOST p 0.0698 (indeterminate); B−C +0.25,
     δ 0.328, TOST p 0.0024 (equivalent).
   - Table X (corrected rubric, 324/324): `python reproduce/q03_analyze.py`
     → writes `outputs/confirm_v3/rubric_sensitivity/q03_analysis.json`; reproduces
     A−C +0.167, δ 0.328, Holm p 1.0 (n.s.), TOST p 0.0008 (equivalent); B−C −0.083,
     δ −0.203, TOST p 0.0 (equivalent).
   - Independent no-round cross-check of both (prints parametric 90% CIs):
     `python reproduce/reanalyze_noround.py`.
5. Optional API steps: `reproduce/q03_rescore.py` (re-score all 108 under the corrected rubric)
   and `reproduce/q03_backfill.py` (re-query unparsed GPT-5.1 responses). The final set shipped here
   was completed to 324/324 with `reproduce/q03_backfill_3.py`, which re-queries the three specific
   (answer×judge) pairs that remained unparsed — CFL-05_A_3 and CFL-06_A_2 for gpt-5.1, and
   CFL-09_A_3 for claude-haiku-4-5 — reading `outputs/confirm_v3/traces` and writing the recovered
   scores into `outputs/confirm_v3/rubric_sensitivity/q03_pointwise.json` (idempotent; run on
   2026-10-13 under the corrected rubric prompt in Appendix A.3). Note on paths: `q03_rescore.py`/
   `q03_backfill.py` are the original author-environment scripts (they read `output/traces` and write
   a working `q03_eval/`); the canonical shipped scores live in `outputs/confirm_v3/rubric_sensitivity/`,
   which `q03_analyze.py` and `q03_backfill_3.py` read directly. No-API re-analysis uses only the
   shipped scores. The shipped
   `analysis/analyze.py` is the single corrected analysis entry point; the older rounding
   behavior is not used anywhere in this package.

**Behind a corporate MITM proxy / on Python 3.13:** if the vendored HTTP client fails with
`process() takes no keyword arguments`, use the stdlib-based shim in `reproduce/` (`_shim.py`
+ `_netfix.py`), which trusts the OS certificate store and bypasses the incompatible client.
Do **not** commit the generated `corp_ca.pem` or any `.env` (see `.gitignore`).

## Model & version provenance
Generation `claude-sonnet-5` (T=0.7); judges `claude-haiku-4-5`, `gpt-5.1`, `gpt-4.1-mini`;
consensus embedding `BAAI/bge-m3` (local, τ=0.75). Exact identifiers and the pilot-vs-
confirmatory distinction are in `docs/model_versions.md`.

## Data availability / citation
Archived snapshot: **https://doi.org/10.5281/zenodo.23348744** (Zenodo, release v1.0.5; git tag `v1.0.5`, commit `90f415a`). An earlier record (10.5281/zenodo.23094852) archives the superseded v1.0.4. See `DATA_AVAILABILITY.md` and `CITATION.cff`.

## License
See `LICENSE`.
