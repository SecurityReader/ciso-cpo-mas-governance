# Data Availability

All code, frozen scenarios, raw traces, per-judge scores, token-usage logs, and analysis
scripts needed to reproduce the results are provided in this repository and archived at:

- Source code & data (versioned): https://github.com/SecurityReader/ciso-cpo-mas-governance
- Archived snapshot (version DOI): https://doi.org/10.5281/zenodo.23348744 — archives release **v1.0.5** (git tag `v1.0.5`, commit `90f415a`), the replication package for this paper.
- Earlier record: https://doi.org/10.5281/zenodo.23094852 archives the superseded **v1.0.4** release, which predates and does not include the controlled confirmatory run reported here.

Cite the **v1.0.5 version DOI** (10.5281/zenodo.23348744) for the exact snapshot underlying this paper.

## What is included
- `scenarios/` — 12 frozen scenarios + SHA-256 freeze hashes
- `outputs/confirm_v3/` — the confirmatory run reported in the paper (confound-controlled:
  uniform 8,000-token cap, zero mid-deliberation truncation). 108 Phase-1 traces (regenerated),
  1,620 pointwise scores, and the Q03 rubric-sensitivity re-scoring; 36 Phase-2c trajectories,
  pairwise and `phase2_continuous.json` judgments carried over unchanged from `confirm_v2`.
- `outputs/confirm_v2/` — superseded confounded run (mixed per-call caps, 12 C-condition
  truncations), retained for transparency (do not cite).
- `harness/`, `analysis/`, `reproduce/` — all generation, judging, and analysis code
- **English reader guide** (the raw data is Korean, grounded in Korea's PIPA): scenario
  translations `scenarios/scenarios_min.en.json` and `scenarios/scenarios_phase2_hardened.en.json`,
  prompt translations `docs/PROMPTS_EN.md`, and the field-by-field `docs/DATA_DICTIONARY.md`.
  The Korean originals remain the authoritative, hash-frozen record; numeric fields are language-independent.
- `analysis/make_figures.py` — regenerates Figures 1–3 (300 dpi PNG + PDF, in `docs/figures/`)
  from the frozen analysis snapshots and pointwise scores (no API calls)
- `requirements-lock.txt` — full pinned dependency snapshot (`pip freeze`) of the confirmatory-run
  virtual environment; `harness/requirements.txt` gives the exact-pinned direct dependencies, and
  `docs/model_versions.md` records the hardware and SDK versions

## Scoring, aggregation, and known gaps
- Reported statistics are computed from the per-judge metric scores **without intermediate
  rounding**; the sign test and Cliff's δ treat paired differences within a 1e−9 tolerance as
  ties (see `CHANGELOG.md` v1.0.1, `docs/harness_changes.md`). `analysis/analyze.py` reproduces
  `outputs/confirm_v3/eval/analysis.json` from `pointwise.json`.
- The confirmatory `pointwise.json` is complete (324 judge responses = 108 answers × 3 judges;
  1,620 metric scores). The Q03 corrected-rubric re-scoring is complete (324/324); three corrected-rubric responses
  (`CFL-05_A_3`, `CFL-06_A_2` for gpt-5.1; `CFL-09_A_3` for claude-haiku-4-5) that initially failed
  JSON parsing were re-queried and recovered. The corrected-rubric A-C estimate is +0.167
  (equivalent within +/-1 point).
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
- `outputs/confirm_v1_invalid/` and `outputs/confirm_v2/` are superseded earlier runs retained
  for transparency; do not cite them.
