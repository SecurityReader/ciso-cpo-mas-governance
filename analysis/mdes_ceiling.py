"""Sensitivity power (MDES) + ceiling quantification.
pip install pandas numpy scipy statsmodels"""
import json, numpy as np, pandas as pd
from statsmodels.stats.power import TTestPower
from scipy.stats import wilcoxon, skew
from _paths import POINTWISE
nc=lambda c:(c or "").upper()[:1]
pw=json.load(open(POINTWISE,encoding="utf-8"))
rec=[dict(scenario=r["scenario_id"],grp=r["scenario_id"].split("-")[0],cond=nc(r["condition"]),
     S=np.mean([sum(s.get(m,0) for m in ("M1","M2","M3","M4","M5")) for s in r["scores"]])) for r in pw]
d=pd.DataFrame(rec); cfl=d[d.grp=="CFL"].groupby(["scenario","cond"]).S.mean().reset_index()
w=cfl.pivot_table(index="scenario",columns="cond",values="S"); diff=(w.A-w.C).dropna()
n,sd=len(diff),diff.std(ddof=1)
for a in (0.05,0.025):
    dz=TTestPower().solve_power(nobs=n,alpha=a,power=0.8,alternative="two-sided")
    print(f"alpha={a}: MDES dz={dz:.2f} ~ {dz*sd:.2f} S pts")
rng=np.random.default_rng(20260930); cen=(diff-diff.mean()).values
for sh in np.arange(0,2.01,0.25):
    hits=sum(wilcoxon(rng.choice(cen,n,replace=True)+sh,zero_method="zsplit").pvalue<0.05 for _ in range(5000) if not np.allclose(rng.choice(cen,n,replace=True)+sh,0))
    print(f"true diff={sh:.2f} power~{hits/5000:.2f}")
mm=pd.DataFrame([dict(cond=nc(r["condition"]),metric=m,score=s.get(m)) for r in pw for s in r["scores"] for m in ("M1","M2","M3","M4","M5")])
print(mm.groupby("metric").score.agg(prop_max=lambda x:(x==5).mean(),headroom=lambda x:(5-x.mean())/4,skew=skew).round(3).to_string())
