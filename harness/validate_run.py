#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_run.py - confirmatory-run integrity gate.

One GREEN/RED verdict so you regenerate ONCE and verify ONCE.
Reads the truncation signal from each trace's meta (meta.truncated_calls,
written by the patched run_harness.py). Falls back to _token_usage.csv's
hit_max only for older traces that lack the field.

Usage (from the harness venv):
    python validate_run.py --traces output\\traces --cap 8000
    python validate_run.py --traces output\\traces            # just require ONE shared cap
    python validate_run.py --traces output\\traces --csv output\\_token_usage.csv

Exit 0 = ALL PASS (clean; stop regenerating). Non-zero = at least one FAIL.
"""
import argparse, csv, glob, json, os, re, sys
from collections import defaultdict

EXPECT_N     = 108
EXPECT_CALLS = {"A": 7, "B": 3, "C": 4}
PREFIXES     = ("CFL", "IND", "COL")   # Phase-1 only (excludes P2C_* Phase-2c)

def is_phase1(name):
    return not name.startswith("P2C") and name.split("-")[0] in PREFIXES

def round_outputs(d):
    lg = d.get("logs", {})
    if isinstance(lg, dict):
        for k in ("rounds", "steps"):
            if isinstance(lg.get(k), list):
                return [x for x in lg[k] if isinstance(x, str)]
    return []

def parses_json(s):
    s2 = re.sub(r"```$", "", re.sub(r"^```(json)?", "", s.strip()).strip()).strip()
    try:
        json.loads(s2); return True
    except Exception:
        return False

def truncated_text(s):
    t = s.rstrip()
    return (not parses_json(s)) and not t.endswith("}") and not t.endswith("]")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", required=True)
    ap.add_argument("--csv", default=None, help="_token_usage.csv (fallback hit_max for old traces)")
    ap.add_argument("--cap", type=int, default=None, help="required uniform max_tokens (optional)")
    a = ap.parse_args()

    results = []
    def check(name, ok, detail=""):
        results.append((name, ok, detail))

    files = [f for f in glob.glob(os.path.join(a.traces, "*.json"))
             if re.search(r"_[ABC]_[123]\.json$", os.path.basename(f))
             and is_phase1(os.path.basename(f).replace(".json", ""))]
    traces = {}
    for f in files:
        try:
            traces[os.path.basename(f).replace(".json", "")] = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            check(f"parse {os.path.basename(f)}", False, str(e))

    # 1) count
    check("count == 108 Phase-1 traces", len(traces) == EXPECT_N, f"found {len(traces)}")

    # 2) uniform cap
    caps = defaultdict(int)
    for d in traces.values():
        caps[d.get("meta", {}).get("max_tokens")] += 1
    detail = ", ".join(f"{k}:{v}" for k, v in sorted(caps.items(), key=lambda x: str(x[0])))
    if a.cap is not None:
        check(f"all max_tokens == {a.cap}", list(caps.keys()) == [a.cap], detail)
    else:
        check("all traces share ONE max_tokens", len(caps) == 1, detail)

    # 3) THE truncation gate -- prefer trace meta (authoritative), else CSV hit_max
    meta_tr = [d.get("meta", {}).get("truncated_calls") for d in traces.values()]
    if traces and all(x is not None for x in meta_tr):
        total = sum(meta_tr)
        hits = [n for n, d in traces.items() if d["meta"].get("truncated_calls", 0)]
        check("no truncated calls (stop_reason!=max_tokens)", total == 0,
              f"{total} truncated calls in {len(hits)} traces: {hits[:12]}")
    elif a.csv and os.path.exists(a.csv):
        rows = [r for r in csv.DictReader(open(a.csv, encoding="utf-8"))
                if is_phase1(str(r.get("answer_id", "")).replace(".json", ""))]
        hm = sum(int(r.get("hit_max", 0)) for r in rows)
        check("hit_max == 0 (CSV fallback)", hm == 0, f"{hm} of {len(rows)} answers hit the cap")
    else:
        check("truncation signal present", False,
              "traces lack meta.truncated_calls and no --csv given (regenerate with patched run_harness.py)")

    # 4) rounds/steps parse cleanly
    trunc = [f"{n}#r{i}" for n, d in traces.items()
             for i, s in enumerate(round_outputs(d)) if truncated_text(s)]
    check("no truncated rounds/steps (JSON)", len(trunc) == 0, f"{len(trunc)}: {trunc[:12]}")

    # 5) finals valid
    bad_final = [n for n, d in traces.items() if d.get("final") in (None, {})]
    check("final parsed (final=null == 0)", len(bad_final) == 0, f"{len(bad_final)}: {bad_final[:12]}")

    # 6) n_calls per condition
    bad_calls = [f"{n}:{d.get('meta',{}).get('n_calls')}"
                 for n, d in traces.items()
                 if d.get("meta", {}).get("n_calls") != EXPECT_CALLS.get(n.split("_")[-2])]
    check("n_calls per condition (A7/B3/C4)", len(bad_calls) == 0, f"{bad_calls[:12]}")

    # report
    print("\n" + "=" * 64)
    print("  CONFIRMATORY-RUN INTEGRITY GATE")
    print("=" * 64)
    allok = True
    for name, ok, detail in results:
        allok &= ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"   -> {detail}" if (detail and not ok) else ""))
    print("=" * 64)
    print("  RESULT: " + ("GREEN - clean. Do NOT regenerate again."
                          if allok else "RED - fix the FAIL items (only the listed traces) and re-run."))
    print("=" * 64 + "\n")
    sys.exit(0 if allok else 1)

if __name__ == "__main__":
    main()
