# -*- coding: utf-8 -*-
"""Independent no-intermediate-rounding re-aggregation (verification), package-relative, no API.
Recomputes the two primary contrasts for the original and the corrected (Q03) evaluations
directly from per-judge raw scores, preserving exact ties."""
import json, sys, importlib.util
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as Fr
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
spec=importlib.util.spec_from_file_location("az", ROOT/"analysis"/"analyze.py")
az=importlib.util.module_from_spec(spec); spec.loader.exec_module(az)
Mk=["M1","M2","M3","M4","M5"]
def norm(c):
    c=str(c).upper()
    if c.startswith("A") or "SEPARATED" in c: return "A"
    if c.startswith("B") or "STEP" in c: return "B"
    if c.startswith("C") or "3ROUND_FORMAT" in c or "UNIFIED_3ROUND" in c: return "C"
    return c[:1]
def contrasts(path):
    rows=json.load(open(path,encoding="utf-8"))
    cell=defaultdict(list)
    for r in rows:
        js=[s for s in (r.get("scores") or []) if all(isinstance(s.get(k),(int,float)) for k in Mk)]
        if not js: continue
        cell[(r["scenario_id"],norm(r["condition"]))].append(sum(Fr(sum(s[k] for s in js),len(js)) for k in Mk))
    cm={k:sum(v)/len(v) for k,v in cell.items()}
    scen=sorted({s for (s,_) in cm if s.startswith("CFL")})
    out={}
    for cx,cy,alt in [("A","C","greater"),("B","C","two-sided")]:
        d=[float(cm[(s,cx)]-cm[(s,cy)]) for s in scen if (s,cx) in cm and (s,cy) in cm]
        eqv=az.equivalence(d,az.EQ_MARGIN); ps,pos,neg=az.sign_test(d,alt)
        out[f"{cx}-{cy}"]=dict(mean=round(az.mean(d),4),delta=round(az.cliffs_delta(
            [float(cm[(s,cx)]) for s in scen if (s,cx) in cm],[float(cm[(s,cy)]) for s in scen if (s,cy) in cm]),4),
            tost_p=eqv["tost_p"],ci90=eqv["ci90_parametric"],verdict=eqv["verdict"])
    return out
orig=ROOT/"outputs"/"confirm_v2"/"eval"/"pointwise.json"
rev =ROOT/"outputs"/"confirm_v2"/"rubric_sensitivity"/"q03_pointwise.json"
print("ORIGINAL :",contrasts(orig))
print("CORRECTED:",contrasts(rev))
