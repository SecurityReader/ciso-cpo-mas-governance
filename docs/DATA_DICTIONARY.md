# Data Dictionary

This document describes every data file and field in the replication package so
that an English-speaking reader can interpret the dataset without reading Korean.

> **Language of the raw data.** The study concerns security–privacy policy decisions
> grounded in Korea's Personal Information Protection Act (PIPA). The scenarios, the
> model-generated policies, and the judges' free-text rationales are therefore in
> **Korean** — that is the language the models were prompted in and responded in, and
> those Korean artifacts are the authoritative experimental record. For English
> readers we provide: English scenario translations (`scenarios/*.en.json`), English
> prompt translations (`docs/PROMPTS_EN.md`), and this dictionary. All **numeric**
> fields (scores, token counts, statistics) are language-independent and need no
> translation. Where a field holds Korean free text (e.g., a judge `rationale`), that
> is noted below.

---

## 1. Scenarios — `scenarios/scenarios_min.json` (+ `.en.json`)

12 frozen scenarios (8 CONFLICTING "CFL", 2 INDEPENDENT "IND", 2 COOPERATIVE "COL").
SHA-256 hashes are recorded in `scenarios/FREEZE_HASHES.txt`.

| Field | Type | Meaning |
|---|---|---|
| `scenario_id` | string | Stable ID, e.g. `CFL-01`, `IND-07`, `COL-02`. |
| `category` | enum | `CONFLICTING` / `INDEPENDENT` / `COOPERATIVE`. |
| `domain` | string | Short slug of the security/privacy topic (e.g. `authentication`). |
| `question` | string (KR) | The policy question the agents must decide. |
| `context.urgency` | enum | `low` / `medium` / `high`. |
| `context.data_type` | list (KR) | Types of data involved. |
| `context.legal_context` | list (KR) | Relevant statutes/guidelines (e.g. PIPA articles). |
| `context.business_context` | string (KR) | The operational situation prompting the decision. |
| `context.difficulty` | enum | `low` / `medium` / `high`. |
| `conflict_type` | enum | `DUAL_CONFLICT` / `SECURITY_DOMINANT` / `PRIVACY_DOMINANT` / `COOPERATIVE`. |
| `task_type_agreement` | string | Labeling-provenance tag (`solo_classified`). |
| `ground_truth_conflicts` | list | **M1 scoring key**: the legal/technical/operational conflicts a good answer should identify. Each: `{axis: legal\|technical\|operational, desc: (KR)}`. Present only for CONFLICTING scenarios. |
| `phase2` | bool | Whether this scenario has a Phase-2 stress trajectory. |
| `phase2_challenges` | list | Phase-2 steps (see below). In `scenarios_min.json` this is a 4-step pilot sequence; the confirmatory Phase 2 uses the 6-step hardened set. |

**Phase-2 challenge step** (`phase2_challenges[]`), and the hardened file
`scenarios_phase2_hardened.json` (+ `.en.json`):

| Field | Type | Meaning |
|---|---|---|
| `step` | int | Step index (1..4 pilot; 1..6 hardened). |
| `trap` | bool | *(hardened only)* `true` = a temptation a sound policy must refuse (illegality / cover-up / regulatory deception). |
| `pressure` | string (KR) | The type of pressure applied at this step. |
| `agent` | enum | Which adversarial role poses the step: `red_team` / `shadow_user` / `auditor` / `executive`. |
| `q` | string (KR) | The challenge posed to the policy. |

The hardened file's `meta.scoring_rubric` defines the Phase-2 resilience scoring
(dimensions D1–D4, step score, hard gate); see `docs/PROMPTS_EN.md` §3.4.

---

## 2. Generation traces — `outputs/confirm_v3/traces/<scenario>_<cond>_<rep>.json`

One file per answer (108 total = 12 scenarios × 3 conditions × 3 reps). Filename
encodes `scenario_id`, condition letter (`A`/`B`/`C`), and rep (`1`/`2`/`3`). Each
file records the full multi-call trajectory and the **final policy JSON** emitted by
the pipeline. The final policy object's field names are English (see
`docs/PROMPTS_EN.md` §2 for each condition's schema: `final_decision`,
`decision_status`, `conflicts_identified[{axis,issue,resolution,...}]`,
`required_controls{security,privacy}`, `residual_risk{security,privacy}`,
`risk_owner`, `bias_direction`, `confidence`); the free-text **values** are Korean.
Condition codes: `A_SEPARATED_3ROUND`, `B_UNIFIED_3STEP`, `C_UNIFIED_3ROUND_FORMAT`.

---

## 3. Pointwise judge scores

- `outputs/confirm_v3/eval/pointwise.json` — **primary (lenient) rubric**.
- `outputs/confirm_v3/rubric_sensitivity/q03_pointwise.json` — **corrected (omission-penalizing) rubric**.

Both are a list of 108 records (one per answer); each record holds 3 judge responses.

| Field | Type | Meaning |
|---|---|---|
| `file` | string | Answer filename, e.g. `CFL-01_A_1.json`. |
| `scenario_id` | string | Scenario ID. |
| `condition` | enum | `A_SEPARATED_3ROUND` / `B_UNIFIED_3STEP` / `C_UNIFIED_3ROUND_FORMAT`. |
| `rep` | int | Repetition 1–3. |
| `scores` | list | One object per judge (3 judges). |
| `scores[].M1..M5` | int ∈ {1,3,5} | Per-metric score. M1 conflict identification, M2 regulatory-compliance precision, M3 compromise specificity, M4 bias suppression, M5 residual-risk disclosure. |
| `scores[].rationale.M1..M5` | string (KR) | The judge's free-text justification per metric. |
| `scores[].length_chars` | int | Character length of the scored policy (verbosity monitor). |

The composite score S (25-point scale) = sum of M1–M5, averaged over judges and reps;
no intermediate rounding. Judges: `claude-haiku-4-5-20251001`, `gpt-5.1`,
`gpt-4.1-mini` (the generator `claude-sonnet-5` is excluded from judging).

---

## 4. Analysis outputs

- `outputs/confirm_v3/eval/analysis.json` — primary-rubric contrasts.
- `outputs/confirm_v3/rubric_sensitivity/q03_analysis.json` — corrected-rubric contrasts.

Each holds `H1_roleseparation_AvsC` and `H3_format_BvsC` objects with (all numeric):
`n_scenarios`, `mean_X`, `mean_Y`, `mean_diff`, `cliffs_delta`, `sign_test_p` (+ `_raw`,
`_holm`), `pos`/`neg` (sign counts), `wilcoxon_p_approx`, `bootstrap_ci95_diff`,
`per_scenario_diff{CFL-xx: diff}`, and `equivalence_TOST{sesoi_margin, mean_diff, sd,
tost_p_lower, tost_p_upper, tost_p, ci90_parametric, ci90_bootstrap, verdict}`.
`analysis/analyze.py` recomputes these from `pointwise.json` (stdlib only).

- `analysis/mdes_ceiling_results.json` — `mdes_sd_diff` (SD of the A–C paired diff),
  `mdes_dz`/`mdes_points` (minimum detectable effect), `power_curve`, and
  `ceiling_by_metric[{metric, mean, prop_max, headroom, skew}]`, `prop_score_max`.
  Consumed by `analysis/make_figures.py` for Figures 2 and 3.
- `analysis/reliability_results.json` — ICC(2,1)/(2,k), Krippendorff α (ordinal),
  Gwet AC1, raw agreement, Friedman (all numeric).
- `analysis/token_sensitivity_results.json` — token medians, A/C ratio, verbosity ρ.

---

## 5. Token usage — `outputs/confirm_v3/_token_usage.csv`

| Column | Meaning |
|---|---|
| `answer_id` | Answer filename. |
| `scenario_id`, `condition`, `rep` | Keys as above. |
| `tok_in`, `tok_out`, `tok_total` | Input / output / total tokens for the whole trajectory. |
| `n_calls` | Number of model calls (A=7, B=3, C=4). |
| `max_tokens` | Per-call output cap (uniform 8000 in the confirmatory run). |
| `hit_max` | Count of calls that hit the cap (0 in the clean run = no truncation). |

---

## 6. Other English references

- `scenarios/scenarios_min.en.json`, `scenarios/scenarios_phase2_hardened.en.json` — English translations of the scenarios (companion to the authoritative Korean originals).
- `docs/PROMPTS_EN.md` — English translation of all generation and judging prompts.
- `docs/model_versions.md` — models, hardware, and pinned SDK versions.
