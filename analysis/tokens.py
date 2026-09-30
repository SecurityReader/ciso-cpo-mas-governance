"""Compute (token) sensitivity: condition medians, A/C ratio, verbosity corr, covariate-adjusted contrast.
pip install pandas numpy scipy statsmodels"""
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.stats import spearmanr, friedmanchisquare
from _paths import POINTWISE, TOKENS
nc=lambda c:(c or "").upper()[:1]
pw=json.load(open(POINTWISE,encoding="utf-8"))
sr=[dict(answer_id=r["file"],scenario=r["scenario_id"],cond=nc(r["condition"]),
        S=np.mean([sum(s.get(m,0) for m in ("M1","M2","M3","M4","M5")) for s in r["scores"]]),
        length_chars=r.get("length_chars")) for r in pw]
S=pd.DataFrame(sr); tok=pd.read_csv(TOKENS); tok["cond"]=tok["condition"].map(nc)
D=S.merge(tok[["answer_id","tok_total","tok_out","n_calls"]],on="answer_id")
for c in "ABC": print(c,"median tok_total",int(D[D.cond==c].tok_total.median()))
w=D.pivot_table(index="scenario",columns="cond",values="tok_total")
print("A/C=",round((w.A/w.C).median(),2),"A/B=",round((w.A/w.B).median(),2),"Friedman",friedmanchisquare(w.A,w.B,w.C))
print("verbosity Spearman rho=",round(spearmanr(D.length_chars,D.S)[0],3))
D["log_tok"]=np.log(D.tok_total.clip(lower=1)); D["cond"]=pd.Categorical(D.cond,["C","A","B"])
m0=smf.mixedlm("S ~ C(cond)",D,groups=D.scenario).fit(reml=True)
m1=smf.mixedlm("S ~ C(cond)+log_tok",D,groups=D.scenario).fit(reml=True)
print("cond coef unadj:",{k:round(v,3) for k,v in m0.params.items() if "cond" in k})
print("cond coef adj  :",{k:round(v,3) for k,v in m1.params.items() if "cond" in k})
