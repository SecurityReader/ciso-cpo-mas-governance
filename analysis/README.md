# Analysis

`analyze.py` (in ../harness) computes the primary contrasts (H1, H3), TOST equivalence,
verbosity correlation, and judge-reliability snapshot from the judgments.

Supplementary scripts here (read ../outputs/confirm_v2):
- `reliability.py` — ICC(2,1)/(2,k), Krippendorff α (ordinal), Gwet AC1, agreement, Friedman
- `tokens.py` — compute (token) sensitivity: medians, A/C ratio, verbosity ρ, covariate-adjusted contrast
- `mdes_ceiling.py` — sensitivity power / MDES and ceiling quantification

Result snapshots: `reliability_results.json`, `token_sensitivity_results.json`, `mdes_ceiling_results.json`.

Figures:
- `make_figures.py` — regenerate the three manuscript figures (300 dpi PNG + vector PDF) into
  `../docs/figures/` from frozen data only (no API calls): Figure 1 (pipeline schematic),
  Figure 2 (ceiling by metric; reads `mdes_ceiling_results.json` and the corrected-rubric
  `../outputs/confirm_v3/rubric_sensitivity/q03_pointwise.json`), Figure 3 (sensitivity power;
  reads `mdes_ceiling_results.json` and `../outputs/confirm_v3/eval/analysis.json`). Deps: matplotlib numpy scipy.

Requires: pandas numpy scipy statsmodels pingouin krippendorff irrCAC
