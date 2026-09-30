#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
본실험 3층 통계 분석 (표준 라이브러리만 — scipy/numpy 불필요)

입력 : output/eval/pointwise.json (judge.py --mode pointwise 산출)
       output/eval/pairwise.json  (선택; judge.py --mode pairwise)
출력 : output/eval/analysis.json + 콘솔 요약

지표 : S = Σ wₖ·Mₖ  (기본 등가중치, WEIGHTS 환경변수로 교체)
일차가설(대립 CFL):
  H1  A vs C  역할분리 A > C   (단측, greater)
  H3  B vs C  형식 효과 B ≠ C  (양측)
  Holm 보정(일차 2개). 효과크기 Cliff's δ + 부트스트랩 95% CI.
보조 : 길이-점수 상관(장황함 편향), 심판 간 일치도(신뢰도 스냅샷).

사용 : python analyze.py
       WEIGHTS=1,1,1,1,1 TASK_PREFIX=CFL python analyze.py
"""
import json, os, math, random
from pathlib import Path
from collections import defaultdict
from math import comb, erfc, sqrt

BASE = Path(__file__).resolve().parent
EVAL = BASE / "output" / "eval"
random.seed(20260927)

Mk = ["M1", "M2", "M3", "M4", "M5"]
W = [float(x) for x in os.environ.get("WEIGHTS", "1,1,1,1,1").split(",")]
TASK_PREFIX = os.environ.get("TASK_PREFIX", "CFL")
# SESOI(동등성 여백): S척도 점수. 기본 ±1.0점(지표 1스텝=2점의 절반, 보수적). 환경변수 EQ_MARGIN로 조정.
EQ_MARGIN = float(os.environ.get("EQ_MARGIN", "1.0"))

def S_of(agg):
    return sum(w * float(agg.get(k, 0) or 0) for w, k in zip(W, Mk))

def mean(v):
    return sum(v) / len(v) if v else float("nan")

def cliffs_delta(x, y):
    gt = sum(1 for a in x for b in y if a > b)
    lt = sum(1 for a in x for b in y if a < b)
    n = len(x) * len(y)
    return (gt - lt) / n if n else float("nan")

def binom_cdf(k, n, p=0.5):
    if k < 0: return 0.0
    return sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(0, k + 1))

def sign_test(diffs, alternative="two-sided"):
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    n = pos + neg
    if n == 0: return 1.0, pos, neg
    if alternative == "greater":
        p = 1 - binom_cdf(pos - 1, n)
    elif alternative == "less":
        p = binom_cdf(pos, n)
    else:
        p = min(1.0, 2 * binom_cdf(min(pos, neg), n))
    return p, pos, neg

def wilcoxon(diffs):
    nz = [d for d in diffs if d != 0]
    n = len(nz)
    if n == 0: return float("nan"), float("nan")
    order = sorted(nz, key=lambda d: abs(d))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(order[j + 1]) == abs(order[i]): j += 1
        r = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1): ranks[k] = r
        i = j + 1
    Wp = sum(r for r, d in zip(ranks, order) if d > 0)
    Wm = sum(r for r, d in zip(ranks, order) if d < 0)
    Wstat = min(Wp, Wm)
    mu = n * (n + 1) / 4.0
    sd = sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    if sd == 0: return Wstat, float("nan")
    z = (Wstat - mu + 0.5) / sd
    p = 2 * (0.5 * erfc(abs(z) / sqrt(2)))
    return Wstat, min(1.0, p)

def bootstrap_ci(diffs, iters=2000, alpha=0.05):
    if not diffs: return (float("nan"), float("nan"))
    n = len(diffs); ms = []
    for _ in range(iters):
        ms.append(sum(diffs[random.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return (round(ms[int((alpha / 2) * iters)], 3),
            round(ms[int((1 - alpha / 2) * iters) - 1], 3))

def _betacf(a, b, x, itmax=200, eps=3e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0; d = 1.0 - qab * x / qap
    if abs(d) < 1e-30: d = 1e-30
    d = 1.0 / d; h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d;  c = 1.0 + aa / c
        if abs(d) < 1e-30: d = 1e-30
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d;  c = 1.0 + aa / c
        if abs(d) < 1e-30: d = 1e-30
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d; delta = d * c; h *= delta
        if abs(delta - 1.0) < eps: break
    return h

def _betai(a, b, x):
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b

def t_cdf(t, df):
    if df <= 0: return float("nan")
    x = df / (df + t * t)
    ib = 0.5 * _betai(df / 2.0, 0.5, x)
    return ib if t <= 0 else 1.0 - ib

def t_ppf(q, df, lo=-100.0, hi=100.0):
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_cdf(mid, df) < q: lo = mid
        else: hi = mid
    return (lo + hi) / 2.0

def equivalence(diffs, margin, alpha=0.05):
    """paired TOST(모수적 t) + 부트스트랩 (1-2α)CI 포함검정. SESOI=±margin(S척도)."""
    n = len(diffs)
    if n < 2:
        return {"sesoi_margin": margin, "n": n, "insufficient": True}
    md = mean(diffs)
    var = sum((d - md) ** 2 for d in diffs) / (n - 1)
    sd = sqrt(var); se = sd / sqrt(n); df = n - 1
    if se == 0:
        p_lower = 0.0 if md > -margin else 1.0
        p_upper = 0.0 if md <  margin else 1.0
        ci = (round(md, 3), round(md, 3))
    else:
        t_lower = (md - (-margin)) / se   # H0-: diff <= -margin
        t_upper = (md - ( margin)) / se   # H0+: diff >= +margin
        p_lower = 1.0 - t_cdf(t_lower, df)
        p_upper = t_cdf(t_upper, df)
        tcrit = t_ppf(1 - alpha, df)      # (1-2α) 양측 = 90% CI at α=0.05
        ci = (round(md - tcrit * se, 3), round(md + tcrit * se, 3))
    p_tost = max(p_lower, p_upper)
    equ_t = (p_tost < alpha)
    lo, hi = bootstrap_ci(diffs, alpha=2 * alpha)  # 90% CI
    equ_boot = (lo > -margin and hi < margin)
    return {
        "sesoi_margin": margin, "n": n, "mean_diff": round(md, 3), "sd": round(sd, 3),
        "tost_p_lower": round(p_lower, 4), "tost_p_upper": round(p_upper, 4),
        "tost_p": round(p_tost, 4), "equivalent_tost(a=0.05)": bool(equ_t),
        "ci90_parametric": list(ci), "ci90_bootstrap": [lo, hi],
        "equivalent_ci90_within_sesoi": bool(equ_boot),
        "verdict": ("EQUIVALENT" if (equ_t and equ_boot) else
                    "INDETERMINATE" if (equ_t or equ_boot) else "NOT_SHOWN"),
    }

def holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals); adj = [0.0] * m; run = 0.0
    for rank, i in enumerate(idx):
        run = max(run, (m - rank) * pvals[i]); adj[i] = min(1.0, run)
    return adj

def pearson(x, y):
    n = len(x)
    if n < 2: return float("nan")
    mx, my = mean(x), mean(y)
    sx = sum((a - mx) ** 2 for a in x); sy = sum((b - my) ** 2 for b in y)
    if sx == 0 or sy == 0: return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sqrt(sx * sy)

def main():
    p = EVAL / "pointwise.json"
    if not p.exists():
        raise SystemExit(f"{p} 없음 — 먼저 `python judge.py --mode pointwise` 실행")
    rows = json.loads(p.read_text(encoding="utf-8"))

    cell = defaultdict(list)       # (sid,cond) -> [S per rep-row]
    lengths, svals = [], []
    perjudge = defaultdict(lambda: defaultdict(list))
    def norm_cond(c):
        c = str(c).upper()
        if c.startswith("A") or "SEPARATED" in c: return "A"
        if c.startswith("B") or "3STEP" in c or "STEP" in c: return "B"
        if c.startswith("C") or "3ROUND_FORMAT" in c or "UNIFIED_3ROUND" in c: return "C"
        return c[:1]
    for r in rows:
        sid, cond = r["scenario_id"], norm_cond(r["condition"])
        s = S_of(r.get("aggregate") or {})
        cell[(sid, cond)].append(s)
        if isinstance(r.get("length_chars"), (int, float)):
            lengths.append(r["length_chars"]); svals.append(s)
        for sc in (r.get("scores") or []):
            perjudge[sc.get("_judge", "?")][cond].append(S_of({k: sc.get(k, 0) for k in Mk}))
    cellmean = {k: mean(v) for k, v in cell.items()}
    scen = sorted({sid for (sid, _) in cellmean if sid.startswith(TASK_PREFIX)})

    def paired(cx, cy):
        sids, xs, ys = [], [], []
        for sid in scen:
            if (sid, cx) in cellmean and (sid, cy) in cellmean:
                sids.append(sid); xs.append(cellmean[(sid, cx)]); ys.append(cellmean[(sid, cy)])
        return sids, xs, ys

    def contrast(cx, cy, alt):
        sids, xs, ys = paired(cx, cy)
        diffs = [a - b for a, b in zip(xs, ys)]
        eqv = equivalence(diffs, EQ_MARGIN)
        ps, pos, neg = sign_test(diffs, alt)
        _, pw = wilcoxon(diffs)
        return {
            "comparison": f"{cx}_vs_{cy}", "n_scenarios": len(sids),
            "mean_X": round(mean(xs), 3), "mean_Y": round(mean(ys), 3),
            "mean_diff": round(mean(diffs), 3),
            "cliffs_delta": round(cliffs_delta(xs, ys), 3),
            "sign_test_p": round(ps, 4), "pos": pos, "neg": neg,
            "wilcoxon_p_approx": (round(pw, 4) if pw == pw else None),
            "bootstrap_ci95_diff": bootstrap_ci(diffs),
            "per_scenario_diff": {s: round(d, 3) for s, d in zip(sids, diffs)},
            "equivalence_TOST": eqv,
        }

    H1 = contrast("A", "C", "greater")   # 역할분리
    H3 = contrast("B", "C", "two-sided") # 형식
    adj = holm([H1["sign_test_p"], H3["sign_test_p"]])
    H1["sign_test_p_holm"], H3["sign_test_p_holm"] = round(adj[0], 4), round(adj[1], 4)

    verbosity_r = round(pearson(lengths, svals), 3) if len(lengths) >= 2 else None
    judges = sorted(perjudge)
    rel = {}
    for jm in judges:
        allS = [s for cond in perjudge[jm].values() for s in cond]
        rel[jm] = {"n": len(allS), "mean_S": round(mean(allS), 3) if allS else None}

    out = {
        "spec": {"weights": W, "task_prefix": TASK_PREFIX,
                 "S_definition": "sum(w_k * M_k), M in {1,3,5}",
                 "analysis_unit": "(scenario x condition) mean over reps", "sesoi_margin_S": EQ_MARGIN},
        "H1_roleseparation_AvsC": H1,
        "H3_format_BvsC": H3,
        "verbosity_length_score_pearson": verbosity_r,
        "judge_reliability_snapshot": rel,
        "note": "sign-test가 일차 p(소표본 강건). Wilcoxon은 정규근사 참고. "
                "무효/약효는 TOST·SESOI로만 '작다/없다' 주장. TOST: SESOI=±%s점, 파라메트릭 t + 부트스트랩 90%%CI 포함.",
    }

    pw = EVAL / "pairwise.json"
    if pw.exists():
        pr = json.loads(pw.read_text(encoding="utf-8"))
        agg = defaultdict(lambda: defaultdict(int)); poscon = []
        for row in pr:
            if not row["scenario_id"].startswith(TASK_PREFIX): continue
            agg[row["comparison"]][row.get("consensus_winner", "확인필요")] += 1
            if row.get("position_consistent") is not None:
                poscon.append(1 if row["position_consistent"] else 0)
        out["pairwise_summary"] = {k: dict(v) for k, v in agg.items()}
        out["pairwise_position_consistency"] = (round(mean(poscon), 3) if poscon else None)

    (EVAL / "analysis.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    def line(h, c):
        star = "★유의" if c["sign_test_p_holm"] < 0.05 else "n.s."
        print(f"[{h}] {c['comparison']} n={c['n_scenarios']} | "
              f"평균 {c['mean_X']} vs {c['mean_Y']} (Δ{c['mean_diff']}) | "
              f"δ={c['cliffs_delta']} | 부호검정 p={c['sign_test_p']} (Holm {c['sign_test_p_holm']}, {star}) | "
              f"CI95Δ={c['bootstrap_ci95_diff']} | Wilcoxon≈{c['wilcoxon_p_approx']}")
        e = c.get("equivalence_TOST", {})
        if e and not e.get("insufficient"):
            print(f"      └ 동등성(TOST, SESOI±{e['sesoi_margin']}): p_TOST={e['tost_p']} | 90%CI={e['ci90_bootstrap']} | {e['verdict']}")
    print("=" * 70)
    print(f"본실험 분석 — S=Σw·M, 가중치 {W}, 대상 {TASK_PREFIX}")
    print("=" * 70)
    line("H1", H1); line("H3", H3)
    print(f"[보조] 길이-점수 Pearson r = {verbosity_r} (|r|↑ → 장황함 편향 점검)")
    print(f"[신뢰도] 심판별 평균 S: " + ", ".join(f"{j}={rel[j]['mean_S']}" for j in judges))
    if "pairwise_summary" in out:
        print(f"[Pairwise] {out['pairwise_summary']} | 위치일관성={out['pairwise_position_consistency']}")
    print(f"\n→ output/eval/analysis.json 저장")

if __name__ == "__main__":
    main()
