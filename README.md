# Role-Separated vs. Unified LLM Pipelines for Security–Privacy Policy Decisions

Replication package for the study
*"Role-Separated versus Unified LLM Pipelines for Security–Privacy Policy Decisions:
A Conditional Equivalence Study."*

> **Scope.** This is a confound-controlled **comparison of three LLM pipelines**, not a
> claim about how human CISO/CPO functions should be organized. Results are conditional
> on the measured composite scores, the two primary contrasts, the eight conflict
> scenarios, and a post-hoc ±1.0-point equivalence margin.

## Summary of findings
We test whether separating the Chief Information Security Officer (CISO) and Chief
Privacy Officer (CPO) into distinct LLM agents improves information-security
policy-decision quality over a unified pipeline. Three conditions — **A** (role-separated,
3 rounds + mediator), **B** (unified 3-step), **C** (unified 3-round, deliberation-format
control) — are run on 12 frozen PIPA-grounded scenarios (8 conflict scenarios form the
primary analysis), each ×3 repetitions, and scored blind by a three-model judge ensemble
(claude-haiku-4-5, gpt-5.1, gpt-4.1-mini).

- The two primary contrasts fell within a **post-hoc ±1.0-point equivalence margin** on the 25-point
  composite (A−C p_TOST=0.0027; B−C p_TOST=0.0025). This concerns the A−C and B−C
  contrasts, not a joint claim over all three conditions.
- A large keyless-pilot effect (Cliff's δ=0.918) **did not replicate** under the controlled
  design (δ=0.297, Holm p=0.69) after multiple protocol changes (schema symmetry, length,
  self-preference, judge configuration), whose individual contributions were **not** isolated.
- **Rubric sensitivity (Q03):** re-scoring all 108 answers with a corrected rubric that
  penalizes omissions leaves both contrasts equivalent (A−C +0.028, B−C −0.250; both within
  ±1.0), while lowering the ceiling from 92.3% to 87.3% of metric scores at maximum. The
  re-scoring uses the complete three-judge ensemble (324/324); five GPT-5.1 responses that
  initially failed to parse were re-queried under the same corrected rubric
  (reproduce/q03_backfill.py).
- Compute was **measured, not matched** (A used ~1.6× the tokens of C); the result is not an
  artifact of A being under-resourced.

> **Aggregation note.** All reported statistics are computed from the per-judge metric scores
> **without intermediate rounding**; values are rounded only for display, and the sign test
> and Cliff's δ treat paired differences within a 1e−9 tolerance as ties, so exact ties are
> preserved (two of the eight A−C scenario differences are exactly zero). See `CHANGELOG.md`
> (v1.0.1) and `docs/harness_changes.md`.

See the manuscript for the full interpretation, threats to validity, and the ceiling-effect
and single-generator limitations.

## Repository layout
- `scenarios/` — frozen scenarios + SHA-256 freeze hashes (`FREEZE_HASHES.txt`)
- `harness/` — generation & judging code (`run_all.py`, `run_harness.py`, `judge.py`,
  `analyze.py`, `requirements.txt`)
- `analysis/` — standalone analysis scripts and cached results
  (`reliability.py` → ICC/Krippendorff/Gwet AC1; `mdes_ceiling.py` → sensitivity power &
  ceiling; `tokens.py` → token usage)
- `outputs/confirm_v2/` — the confirmatory run used in the paper
  - `eval/` — `pointwise.json` (1,620 scores), `pairwise.json`, `phase2_continuous.json`,
    `analysis.json` (no-intermediate-rounding; regenerated v1.0.1)
  - `traces/` — all 108 Phase-1 traces + 36 Phase-2c trajectories
  - `rubric_sensitivity/` — Q03 corrected-rubric re-scoring (`q03_pointwise.json`,
    `q03_analysis.json`)
  - `_token_usage.csv`
  - `confirm_v1_invalid/` — a superseded earlier run, kept for transparency (do not cite)
- `reproduce/` — helper scripts to reproduce generation/judging behind a corporate
  intercepting (MITM) proxy on Python 3.13 (see `README_r41.md`); includes the Q03
  re-scoring (`q03_rescore.py`, `q03_analyze.py`) and the no-round re-aggregation used for
  verification (`reanalyze_noround.py`)
- `docs/` — decision log, model/version provenance, embedding config, harness-change log,
  and `figures/` (Figures 1–3)

## Reproduce
1. `cd harness && pip install -r requirements.txt`
2. Provide API keys at run time (interactive; never written to disk).
3. `python run_all.py` — generate → judge → Phase-2c → analyze (writes to `outputs/`).
4. **Statistics only, no API** (all paths are package-relative; run from the repository root
   or the stated folder). The analysis code computes the composite from per-judge raw scores
   **without intermediate rounding** and preserves exact ties:
   - Table V (original rubric): `cd analysis && python analyze.py`
     → writes `outputs/confirm_v2/eval/analysis.json`; reproduces A−C mean +0.194, δ 0.297,
     Holm p 0.688, TOST p 0.0027; B−C +0.139, δ 0.188, TOST p 0.0025.
   - Table X (corrected rubric, 324/324): `python reproduce/q03_analyze.py`
     → writes `outputs/confirm_v2/rubric_sensitivity/q03_analysis.json`; reproduces
     A−C +0.028, δ 0.094, TOST p 0.0006; B−C −0.250, δ −0.375, TOST p 0.0013.
   - Independent no-round cross-check of both (prints parametric 90% CIs):
     `python reproduce/reanalyze_noround.py`.
5. Optional API steps: `reproduce/q03_rescore.py` (re-score all 108 under the corrected rubric)
   and `reproduce/q03_backfill.py` (re-query only unparsed GPT-5.1 responses). The shipped
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
See `DATA_AVAILABILITY.md` (to be completed with the archival DOI) and `CITATION.cff`.

## License
See `LICENSE`.
