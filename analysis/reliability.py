"""Inter-judge reliability: ICC(2,1)/(2,k), Krippendorff alpha (ordinal), Gwet AC1, agreement.
pip install pandas numpy scipy pingouin krippendorff irrCAC"""
import json, numpy as np, pandas as pd, pingouin as pg, krippendorff
from irrCAC.raw import CAC
from scipy.stats import friedmanchisquare
from _paths import POINTWISE
pw=json.load(open(POINTWISE,encoding="utf-8"))
nc=lambda c:(c or "").upper()[:1]
rec=[]
for r in pw:
    for s in r["scores"]:
        for m in ("M1","M2","M3","M4","M5"):
            rec.append(dict(answer_id=r["file"],group=r["scenario_id"].split("-")[0],
                            condition=nc(r["condition"]),judge=s.get("_judge"),metric=m,score=s.get(m)))
df=pd.DataFrame(rec)
S=df.groupby(["answer_id","group","condition","judge"])["score"].sum().rename("S").reset_index()
icc=pg.intraclass_corr(data=S,targets="answer_id",raters="judge",ratings="S").set_index("Type")
print("ICC(2,1)=",round(icc.loc["ICC(A,1)","ICC"],3)," ICC(2,k)=",round(icc.loc["ICC(A,k)","ICC"],3))
for m,g in df.groupby("metric"):
    w=g.pivot_table(index="answer_id",columns="judge",values="score")
    a=krippendorff.alpha(reliability_data=w.T.values,level_of_measurement="ordinal")
    ac1=CAC(w).gwet()["est"]["coefficient_value"]
    print(m,"alpha_ord=",round(a,3),"AC1=",round(ac1,3),"full_agree=",round((w.nunique(axis=1)==1).mean(),3),"prop_max=",round((w==5).values.mean(),3))
wS=S.pivot_table(index="answer_id",columns="judge",values="S")
print("Friedman(leniency):",friedmanchisquare(*[wS[c] for c in wS.columns]))
