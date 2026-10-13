#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_figures.py — regenerate the manuscript figures from FROZEN data only.

No API calls. Reads only committed artifacts in this repository:
  - analysis/mdes_ceiling_results.json              (ceiling by metric; SD of A-C diff)
  - outputs/confirm_v3/eval/analysis.json           (observed primary A-C difference)
  - outputs/confirm_v3/rubric_sensitivity/q03_pointwise.json  (corrected-rubric M5 ceiling)

Outputs (300 dpi PNG + vector PDF) into docs/figures/:
  - Figure1.{png,pdf}  pipeline schematic (A role-separated / C unified-3-round / B unified-3-step)
  - Figure2.{png,pdf}  ceiling by metric under the primary rubric (data-driven)
  - Figure3.{png,pdf}  sensitivity power for H1 (A vs C) (data-driven)

Usage:  python make_figures.py        # from anywhere inside the repo
Deps:   matplotlib, numpy, scipy
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats

# ---------- paths (repo-root relative, like analysis/_paths.py) ----------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # analysis/ -> repo root
MDES = os.path.join(ROOT, "analysis", "mdes_ceiling_results.json")
EVAL = os.path.join(ROOT, "outputs", "confirm_v3", "eval", "analysis.json")
Q03  = os.path.join(ROOT, "outputs", "confirm_v3", "rubric_sensitivity", "q03_pointwise.json")
OUT  = os.path.join(ROOT, "docs", "figures")
os.makedirs(OUT, exist_ok=True)

mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans",
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.05})
NAVY = "#1F3A5F"; RED = "#b03a3a"; GREY = "#6b6b6b"; BLUE = "#3a6ea5"; GREEN = "#2E7D53"

def save(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{stem}.{ext}"), dpi=300)
    plt.close(fig)

# ======================================================================
# Figure 1 — deliberation pipelines (schematic; no data)
# ======================================================================
def figure1():
    fig, ax = plt.subplots(figsize=(12.5, 7.0)); ax.set_xlim(0, 22); ax.set_ylim(0, 12)
    ax.axis("off")
    def box(x, y, w, h, text, fc, ec, tc, fs=12, bold=True):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    linewidth=2, facecolor=fc, edgecolor=ec))
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", color=tc,
                fontsize=fs, fontweight="bold" if bold else "normal")
    def arrow(x1, y1, x2, y2, color=GREY):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                                     linewidth=1.8, color=color))
    def rowlabel(letter, text, y, color):
        ax.text(0.2, y, letter, fontsize=19, fontweight="bold", color=color, va="center")
        ax.text(1.1, y, text, fontsize=15, fontweight="bold", color=color, va="center")

    # ---- A: role-separated (7 calls) ----
    rowlabel("A", "Role-separated (7 calls)", 11.3, NAVY)
    xs = [2.4, 7.2, 12.0]; w = 4.0; hh = 0.95
    yC, yP = 10.0, 8.7
    for i, x in enumerate(xs):
        box(x, yC, w, hh, f"CISO R{i+1}", NAVY, NAVY, "white", 12)
        box(x, yP, w, hh, f"CPO R{i+1}",  NAVY, NAVY, "white", 12)
        if i < 2:
            arrow(x + w, yC + hh/2, xs[i+1], yC + hh/2)
            arrow(x + w, yP + hh/2, xs[i+1], yP + hh/2)
        # intra-round coupling (agents see each other's prior turn)
        ax.plot([x + w/2, x + w/2], [yC, yP + hh], color="#9aa6b2", lw=1.2, ls=(0, (2, 2)))
    box(16.3, 9.15, 2.5, 1.5, "Mediator", NAVY, NAVY, "white", 12)
    arrow(xs[2] + w, yC + hh/2, 16.3, 9.9 + 0.2)
    arrow(xs[2] + w, yP + hh/2, 16.3, 9.9 - 0.2)
    ax.text(11.0, 7.9, "agents see each other's prior turn each round; consensus via bge-m3 embedding",
            ha="center", va="center", color=GREY, fontsize=10.5, style="italic")

    # ---- C: unified three-round (4 calls) ----
    rowlabel("C", "Unified three-round, format control (4 calls)", 6.7, BLUE)
    xc = [2.4, 6.6, 10.8, 15.0]; wc = 3.7; yR = 5.1
    labels = ["Round 1", "Round 2", "Round 3", "Self-\nmediation"]
    for i, x in enumerate(xc):
        box(x, yR, wc, 1.1, labels[i], BLUE, BLUE, "white", 12)
        if i < 3:
            arrow(x + wc, yR + 0.55, xc[i+1], yR + 0.55)
    ax.text(10.0, 4.2, "single agent, same round format as A, then a self-mediation call "
            "(deliberation-format control; compute not matched)",
            ha="center", va="center", color=GREY, fontsize=10.5, style="italic")

    # ---- B: unified three-step (3 calls) ----
    rowlabel("B", "Unified three-step (3 calls)", 3.0, GREEN)
    xb = [2.4, 7.2, 12.0]; wb = 4.0; yS = 1.4
    for i, x in enumerate(xb):
        box(x, yS, wb, 1.1, f"Step {i+1}", GREEN, GREEN, "white", 12)
        if i < 2:
            arrow(x + wb, yS + 0.55, xb[i+1], yS + 0.55)
    arrow(xb[2] + wb, yS + 0.55, 16.3, yS + 0.55)
    ax.add_patch(FancyBboxPatch((16.3, yS), 2.5, 1.1, boxstyle="round,pad=0.02,rounding_size=0.18",
                                linewidth=2, facecolor="white", edgecolor=GREEN))
    ax.text(16.3 + 1.25, yS + 0.55, "Final", ha="center", va="center", color=GREEN, fontsize=12, fontweight="bold")

    # outlined "Final" boxes for A and C, with connecting arrows
    arrow(18.8, 9.9, 19.2, 9.9)                       # Mediator -> Final (A)
    arrow(xc[3] + wc, yR + 0.55, 19.2, yR + 0.55)     # Self-mediation -> Final (C)
    for (fx, fy, ec, tc) in [(19.2, 9.35, NAVY, NAVY), (19.2, 5.1, BLUE, BLUE)]:
        ax.add_patch(FancyBboxPatch((fx, fy), 2.3, 1.1, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    linewidth=2, facecolor="white", edgecolor=ec))
        ax.text(fx + 1.15, fy + 0.55, "Final", ha="center", va="center", color=tc, fontsize=12, fontweight="bold")

    # ---- legend ----
    ax.add_patch(FancyBboxPatch((2.4, -0.1), 1.2, 0.7, boxstyle="round,pad=0.02,rounding_size=0.12",
                                linewidth=1.5, facecolor="#b8c2cc", edgecolor="#b8c2cc"))
    ax.text(3.9, 0.25, "filled = model call", fontsize=11, va="center", color="#333")
    ax.add_patch(FancyBboxPatch((9.0, -0.1), 1.2, 0.7, boxstyle="round,pad=0.02,rounding_size=0.12",
                                linewidth=1.8, facecolor="white", edgecolor="#333"))
    ax.text(10.5, 0.25, "outlined = final output (not a separate call)", fontsize=11, va="center", color="#333")
    save(fig, "Figure1")
    print("Figure1 (pipeline schematic) written")

# ======================================================================
# Figure 2 — ceiling by metric (data-driven)
# ======================================================================
def figure2():
    mdes = json.load(open(MDES, encoding="utf-8"))
    cm = {d["metric"]: d["prop_max"] for d in mdes["ceiling_by_metric"]}
    order = ["M1", "M2", "M3", "M4", "M5"]
    vals = [cm[m] for m in order]
    # corrected-rubric M5 ceiling, computed from frozen pointwise scores
    pw = json.load(open(Q03, encoding="utf-8"))
    tot = mx = 0
    for rec in pw:
        for sc in rec["scores"]:
            v = sc.get("M5")
            if v is not None:
                tot += 1; mx += (v == 5)
    m5_corr = mx / tot
    labels = ["M1\nConflict", "M2\nCompliance", "M3\nSpecificity", "M4\nBias supp.", "M5\nResidual risk"]
    cols = [NAVY]*4 + [RED]
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.bar(range(5), vals, color=cols, width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.012, f"{v*100:.1f}%", ha="center", color=cols[i], fontsize=12)
    ax.set_xticks(range(5)); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1.12); ax.set_ylabel("Proportion at maximum (score = 5)", fontsize=12)
    ax.set_title("Ceiling by metric (original rubric): only M5 discriminates", color=NAVY, fontsize=13)
    ax.text(2.0, 1.06,
            f"M5 (residual-risk disclosure) is the only metric with headroom: {vals[4]*100:.1f}% at max\n"
            f"(→ {m5_corr*100:.1f}% under the corrected rubric); this is where role separation (A) gains.",
            color=RED, fontsize=9.3, va="bottom", ha="center")
    ax.grid(axis="y", ls="-", color="#eee")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    save(fig, "Figure2")
    print(f"Figure2 (ceiling) written; primary M5={vals[4]:.3f}, corrected M5={m5_corr:.4f}")

# ======================================================================
# Figure 3 — sensitivity power for H1 (data-driven)
# ======================================================================
def figure3():
    mdes = json.load(open(MDES, encoding="utf-8"))
    ev = json.load(open(EVAL, encoding="utf-8"))
    SD = mdes["mdes_sd_diff"]                       # 0.471
    n = mdes["n_cfl"]; df = n - 1
    obs = ev["H1_roleseparation_AvsC"]["mean_diff"] # 0.722
    def power(delta, alpha=.05):
        nc = (delta / SD) * np.sqrt(n); tc = stats.t.ppf(1 - alpha/2, df)
        return 1 - stats.nct.cdf(tc, df, nc) + stats.nct.cdf(-tc, df, nc)
    # solve MDES at 80% power (bisection)
    lo, hi = 0.0, 2.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if power(mid) < 0.80: lo = mid
        else: hi = mid
    mdes_pt = (lo + hi) / 2
    xs = np.linspace(0, 1.6, 200); ys = [power(x) for x in xs]
    dz_obs = obs / SD; dz_mdes = mdes_pt / SD
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.plot(xs, ys, "-", color=NAVY, lw=2.4,
            label=f"Parametric power (paired $t$, $n$={n}, SD={SD:.3f})")
    ax.axhline(0.8, ls="--", color="#9aa6b2", lw=1.4)
    ax.text(1.58, 0.815, "80% power", ha="right", color=GREY, fontsize=11)
    ax.axvline(mdes_pt, ls=":", color=RED, lw=1.8)
    ax.text(mdes_pt - 0.015, 0.45,
            f"MDES (80%)\n$\\approx$ {mdes_pt:.3f} pt\n($d_z$={dz_mdes:.2f}, two-sided $\\alpha$=.05)",
            color=RED, fontsize=10, ha="right", va="center")
    ax.axvline(obs, ls="-", color=GREEN, lw=2.0, alpha=0.8)
    ax.text(obs + 0.02, 0.30, f"observed A$-$C\n= {obs:.3f} pt ($d_z$={dz_obs:.2f})",
            color=GREEN, fontsize=10.5, va="center")
    ax.set_xlim(0, 1.6); ax.set_ylim(0, 1.03)
    ax.set_xlabel("True mean difference A$-$C (points on 25-pt S scale)", fontsize=12)
    ax.set_ylabel("Power ($\\alpha$=.05, two-sided)", fontsize=12)
    ax.set_title("Sensitivity power for H1 (A vs C): observed effect exceeds MDES", color=NAVY, fontsize=13)
    ax.grid(axis="y", ls="-", color="#eee"); ax.legend(loc="lower right", fontsize=10, frameon=False)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    save(fig, "Figure3")
    print(f"Figure3 (power) written; SD={SD}, observed={obs}, MDES={mdes_pt:.3f}")

if __name__ == "__main__":
    figure1(); figure2(); figure3()
    print("All figures written to", OUT)
