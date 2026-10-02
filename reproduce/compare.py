# -*- coding: utf-8 -*-
"""R41 부분 재실행 — 비교/판정.
정본(4000-절단본, rep1)과 재실행본(8000)을 같은 (시나리오,조건)에서 비교:
  - 최종정책 길이(chars): 절단이 실제로 내용을 얼마나 잘랐는지
  - 복합점수 S 및 M1~M5: 상한 완화가 채점을 바꾸는지
판정: |ΔS| 가 SESOI(±1.0) 안이면 '절단은 결론에 영향 없음' 근거.
실행:  python compare.py
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
Mk = ["M1","M2","M3","M4","M5"]
def S(agg): return sum(float(agg.get(k,0) or 0) for k in Mk)

old_pw = {r["file"]: r for r in json.loads((HARNESS/"output"/"eval"/"pointwise.json").read_text("utf-8"))}
new_pw = {r["file"]: r for r in json.loads((HERE/"eval"/"pointwise.json").read_text("utf-8"))}

def flen(trace_path):
    try:
        tr = json.loads(Path(trace_path).read_text("utf-8"))
        return len(json.dumps(tr.get("final"), ensure_ascii=False))
    except Exception:
        return None

rows = sorted(new_pw.keys())
print(f"{'file':<18}{'old_len':>8}{'new_len':>8}{'Δlen%':>7}   {'old_S':>6}{'new_S':>6}{'ΔS':>6}   per-metric ΔM(old→new)")
dS=[]
for f in rows:
    if f not in old_pw:
        print(f"{f:<18}  (정본에 없음 — 건너뜀)"); continue
    o, n = old_pw[f], new_pw[f]
    ol = flen(HARNESS/"output"/"traces"/f); nl = flen(HERE/"traces"/f)
    oS, nS = S(o["aggregate"]), S(n["aggregate"])
    dS.append(nS-oS)
    dlen = f"{(nl-ol)/ol*100:+.0f}%" if (ol and nl) else "  -"
    dm = " ".join(f"{k}:{o['aggregate'].get(k)}→{n['aggregate'].get(k)}" for k in Mk
                  if float(o['aggregate'].get(k,0) or 0)!=float(n['aggregate'].get(k,0) or 0)) or "변화없음"
    print(f"{f:<18}{str(ol):>8}{str(nl):>8}{dlen:>7}   {oS:>6.2f}{nS:>6.2f}{nS-oS:>+6.2f}   {dm}")

if dS:
    import statistics as st
    mad = st.mean(abs(x) for x in dS); mx = max(abs(x) for x in dS)
    print(f"\n요약: n={len(dS)}  평균|ΔS|={mad:.3f}  최대|ΔS|={mx:.3f}  (SESOI ±1.0)")
    verdict = "통과 — 상한 완화가 점수를 실질적으로 바꾸지 않음(절단은 결론에 영향 없음)" if mx < 1.0 else \
              "주의 — 일부 답변에서 |ΔS|≥1.0. 개별 확인 필요"
    print("판정:", verdict)
