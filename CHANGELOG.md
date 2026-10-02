# Changelog

## v1.0.4 (2026-10-02) — Holm on unrounded p-values
- `analysis/analyze.py`: the Holm adjustment now uses the **unrounded** sign-test p-values
  (`sign_test_p_raw`); values are rounded only for display/JSON. Previously the 4-digit
  rounded p was fed into Holm (original A−C printed 0.6876 instead of exact 0.6875).
- Re-generated `outputs/confirm_v2/eval/analysis.json` (A−C Holm 0.6875; B−C 1.0) and
  `outputs/confirm_v2/rubric_sensitivity/q03_analysis.json` (A−C / B−C Holm 0.9062 = 0.90625).
- No change to means, Cliff's δ, TOST p, CIs, or any value reported in the manuscript
  (Holm 0.688 at three decimals).
- `docs/model_versions.md`: Section 2 finalized from "planned" to the **confirmatory run as executed** (generation `claude-sonnet-5`; judges `claude-haiku-4-5`, `gpt-5.1`, `gpt-4.1-mini`; T=0.7; `BAAI/bge-m3`, τ=0.75); notes that exact installed SDK versions were not retained (ranges `anthropic<1`, `openai<1.60`).
- `docs/decision_log.md`: proxy wording neutralized to "corporate intercepting (MITM) proxy" (no org/host/cert details).
- `CITATION.cff`: version bumped to 1.0.4. `MANIFEST.sha256` regenerated.

## v1.0.3 (2026-10-02) — reproducibility fixes (no-API analysis paths)
- `analysis/analyze.py` is now the corrected analyzer (no intermediate rounding, exact-tie
  tolerance) and resolves data **package-relative** to `outputs/confirm_v2/eval` (override via
  `EVAL_DIR` / `POINTWISE_NAME` / `OUT_NAME`). The previous copy here was the old rounding
  version and did not point at the packaged data; it is replaced.
- `reproduce/q03_analyze.py` reproduces Table X from `outputs/confirm_v2/rubric_sensitivity/
  q03_pointwise.json` (A−C +0.028/δ0.094/TOST0.0006, B−C −0.250/δ−0.375/TOST0.0013).
- `reproduce/reanalyze_noround.py` is package-relative (absolute `/mnt/...` paths removed) and
  cross-checks both evaluations, printing parametric 90% CIs.
- README "Reproduce" rewritten so `cd analysis && python analyze.py`, `python reproduce/
  q03_analyze.py`, and `python reproduce/reanalyze_noround.py` reproduce Tables V and X with no API.
- `MANIFEST.sha256` regenerated.

## v1.0.2 (2026-10-02) — equivalence framing and legal citations
- **Equivalence analysis relabeled as post-hoc / exploratory.** The project decision log shows the
  equivalence test (TOST) and its ±1.0-point SESOI were added after the confirmatory null result; the
  two A–C and B–C contrasts were planned, but the equivalence test and margin were not pre-specified.
  Manuscript text (abstract, Related Work, Methods, Results, Discussion, Conclusion) updated accordingly.
- **Legal citations corrected** against official Korean amendment texts: the 2019 concurrent-duty
  restriction is Act No. 15628 (art. 45-3 effective 2019-06-13), not Act No. 16021 (a separate
  amendment effective 2019-06-25); the 2021 enumeration of CPO duties a CISO may concurrently perform
  is Act No. 18201, art. 45-3(4)2(d) (effective 2021-12-09); the 2026 PIPA amendment (Act No. 21445)
  moved the duties provision from art. 31(3) to art. 31(4). Financial-sector rules (EFTA, Act No. 12837)
  restrict *other IT duties*, not CISO–CPO combination per se. References expanded to [20]–[27] and
  Table I split by regime (financial vs. general).
- Reported the parametric t 90% CI for the primary contrasts (A–C [−0.191, 0.580], B–C [−0.266, 0.544]).
- Consensus score described as a single pooled score computed once after Round 3.

## v1.0.1 (2026-10-01) — analysis correction (no intermediate rounding)
- **Removed intermediate rounding.** `judge.py` `_aggregate_points` previously stored each
  metric's across-judge mean as `round(mean, 2)`; `analyze.py` now computes the composite
  from the per-judge raw scores **without intermediate rounding** and preserves exact ties
  (sign test and Cliff's δ use a 1e−9 tolerance; `judge.py` stores full precision). Values
  are rounded only for display. Regenerated `outputs/confirm_v2/eval/analysis.json`.
- **Primary contrasts (equivalence unchanged):** A−C mean **+0.194**, Cliff δ **0.297**,
  one-sided sign-test p 0.344 (Holm 0.688), bootstrap 95% CI [−0.194, 0.556], TOST p
  **0.0027**; B−C mean **+0.139**, δ **0.188**, Holm p 1.0, TOST p **0.0025**. Both remain
  within the ±1.0 margin. (Rounding had turned two exact A−C ties into small negatives,
  changing the sign split 4/4/0 → 4/2/2 and δ 0.22 → 0.30.)
- **Q03 rubric-sensitivity (complete 324/324):** the corrected-rubric re-scoring now covers the
  full three-judge ensemble; five GPT-5.1 responses that initially failed to parse were
  re-queried under the same corrected rubric (`reproduce/q03_backfill.py`). Corrected A−C +0.028
  (δ 0.094, TOST 0.0006), B−C −0.250 (δ −0.375, TOST 0.0013); ceiling 92.3%→87.3% (M5 →59%).
  Regenerated `outputs/confirm_v2/rubric_sensitivity/q03_analysis.json`.
- **Phase-2c collapse rule** documented to match the implementation (a step is flagged as
  collapsed when its mean score < 0.5; at a trap step a mean legal-red-line (D1) of zero
  additionally caps the step score). Trap-step score/rationale inconsistencies, where a single
  judge assigned D1=0 with a rationale affirming refusal, are flagged for adjudication.
- Added `reproduce/reanalyze_noround.py` (no-round re-aggregation used for verification).
- `MANIFEST.sha256` regenerated to reflect the above.

## v1.0.0 (2026-10-01) — submission package
- Reframed as a conditional three-pipeline comparison (equivalence of the two pre-specified
  contrasts), not a claim of full-architecture equivalence or of human-organization design.
- Added rubric-sensitivity re-scoring (Q03): corrected rubric penalizes omissions; both
  contrasts remain equivalent; ceiling 92.3%→87.6%. Results in
  `outputs/confirm_v2/rubric_sensitivity/`.
- Added behavioral scoring anchors (1/3/5) and consensus-score edge-case rules to the paper
  appendices.
- Added descriptive statistics (per condition / CFL-IND-COL) and a Phase-2c robustness table.
- Regenerated Figures 1–3 (removed "compute control" from Fig. 1; distinguished MDES vs.
  bootstrap-80% in Fig. 2; fixed overlapping annotation in Fig. 3) → `docs/figures/`.
- Clarified estimands, compute-measured-not-matched, and pre-specified vs. exploratory status.
- Corrected reference metadata (KCI volumes/pages, CAMEL title, DOIs).
- Reproduction helpers for corporate-proxy / Python-3.13 environments added under `reproduce/`.
