# Analysis

`analyze.py` (in ../harness) computes the primary contrasts (H1, H3), TOST equivalence,
verbosity correlation, and judge-reliability snapshot from the judgments.

Supplementary scripts here (read ../outputs/confirm_v2):
- `reliability.py` — ICC(2,1)/(2,k), Krippendorff α (ordinal), Gwet AC1, agreement, Friedman
- `tokens.py` — compute (token) sensitivity: medians, A/C ratio, verbosity ρ, covariate-adjusted contrast
- `mdes_ceiling.py` — sensitivity power / MDES and ceiling quantification

Result snapshots: `reliability_results.json`, `token_sensitivity_results.json`, `mdes_ceiling_results.json`.

Requires: pandas numpy scipy statsmodels pingouin krippendorff irrCAC
