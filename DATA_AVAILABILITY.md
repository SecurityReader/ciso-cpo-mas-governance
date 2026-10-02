# Data Availability

All code, frozen scenarios, raw traces, per-judge scores, token-usage logs, and analysis
scripts needed to reproduce the results are provided in this repository and archived at:

- Source code & data (versioned): https://github.com/<ORG-OR-USER>/ciso-cpo-mas-governance
- Archived snapshot (DOI): https://doi.org/10.5281/zenodo.<ZENODO-ID>   <!-- fill after release -->

The archived snapshot corresponds to git tag `v1.0.1` (commit `<COMMIT-SHA>`).

## What is included
- `scenarios/` — 12 frozen scenarios + SHA-256 freeze hashes
- `outputs/confirm_v2/` — the confirmatory run reported in the paper
  (108 Phase-1 traces, 36 Phase-2c trajectories, 1,620 pointwise scores, pairwise and
  Phase-2c judgments, `analysis.json`), plus the Q03 rubric-sensitivity re-scoring
- `harness/`, `analysis/`, `reproduce/` — all generation, judging, and analysis code

## Scoring, aggregation, and known gaps
- Reported statistics are computed from the per-judge metric scores **without intermediate
  rounding**; the sign test and Cliff's δ treat paired differences within a 1e−9 tolerance as
  ties (see `CHANGELOG.md` v1.0.1, `docs/harness_changes.md`). `harness/analyze.py` reproduces
  `outputs/confirm_v2/eval/analysis.json` from `pointwise.json`.
- The confirmatory `pointwise.json` is complete (324 judge responses = 108 answers × 3 judges;
  1,620 metric scores). The Q03 corrected-rubric re-scoring is complete (324/324); five GPT-5.1 responses that
  initially failed to parse (`CFL-01_B_2`, `CFL-05_C_2`, `CFL-10_C_2`, `COL-02_C_3`, `IND-07_A_1`)
  were re-queried under the same corrected rubric (`reproduce/q03_backfill.py`).
- Phase-2c trap-step judgments include cases where a single judge assigned a legal-red-line
  (D1) score of 0 with a rationale affirming refusal; these are judge scoring inconsistencies
  (not policy collapse) and are flagged for adjudication.

## Integrity
File integrity is verifiable via `MANIFEST.sha256`:
```
sha256sum -c MANIFEST.sha256
```

## Notes
- API keys are supplied interactively at run time and are never stored in this repository.
- The corporate CA bundle (`corp_ca.pem`) and any `.env` are environment-specific secrets
  and are intentionally excluded (see `.gitignore`).
- `outputs/confirm_v1_invalid/` is a superseded earlier run retained for transparency; do
  not cite it.
