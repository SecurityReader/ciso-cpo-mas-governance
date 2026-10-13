# -*- coding: utf-8 -*-
"""Q03 결측 3건 보완(타깃형) — 수정 루브릭 재채점에서 JSON 파싱 실패로 비었던
(답변×심판) 3쌍만 재질의해 324/324를 완성한다. 멱등(이미 324면 변경 없음).
대상: CFL-05_A_3(gpt-5.1), CFL-06_A_2(gpt-5.1), CFL-09_A_3(claude-haiku-4-5-20251001)
정본: outputs/confirm_v3/rubric_sensitivity/q03_pointwise.json (append), traces는 읽기전용.
키: 환경변수 ANTHROPIC_API_KEY + OPENAI_API_KEY (미저장). 회사 프록시 환경은 q03_backfill.py 처럼
    _netfix/_shim 적용 가능. 실행: python reproduce/q03_backfill_3.py → python reproduce/q03_analyze.py
"""
import os, sys, json
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; HARNESS=ROOT/"harness"
sys.path.insert(0, str(HARNESS)); os.environ.setdefault("LLM_BACKEND","api")
import judge as J
TRACES = ROOT/"outputs"/"confirm_v3"/"traces"
PWF    = ROOT/"outputs"/"confirm_v3"/"rubric_sensitivity"/"q03_pointwise.json"
J.POINT_SYS = ("당신은 CISO/CPO 정책결정 품질을 평가하는 독립 심사위원이다. 어떤 구조/형식에서 나왔는지 모른다(블라인드).\n"
"M1 상충식별, M2 규제준수정밀도, M3 절충구체성, M4 편향억제, M5 잔여위험명시 를 각 1/3/5점으로만 채점.\n"
"시나리오의 요구사항과 채점 기준에 비추어 정책을 평가하라. 필수 보호조치·상충분석·잔여위험 공개의 누락은 감점하라. "
"다만 시나리오와 그 법적 참고자료가 뒷받침하지 않는 사실을 지어내거나 요구사항을 임의로 부과하지는 말라. "
"근거를 함께 제시. 순수 JSON만 출력.")
MISS={"CFL-05_A_3.json":"gpt-5.1","CFL-06_A_2.json":"gpt-5.1","CFL-09_A_3.json":"claude-haiku-4-5-20251001"}
rows=json.load(open(PWF,encoding="utf-8")); idx={r["file"]:r for r in rows}
done=all((f in idx) and (MISS[f] in {s.get("_judge") for s in idx[f]["scores"]}) for f in MISS)
tot=sum(len(r["scores"]) for r in rows)
if done:
    print(f"[q03-backfill-3] 이미 완전({tot}/324) — 변경 없음"); sys.exit(0)
for fn,judge in MISS.items():
    r=idx.get(fn)
    if not r or judge in {s.get("_judge") for s in r["scores"]}: continue
    tr=json.loads((TRACES/fn).read_text(encoding="utf-8"))
    payload=json.dumps(J.normalize(tr.get("final")),ensure_ascii=False)
    gt=J._ground_truth(tr["scenario_id"])
    prompt=(f"[정책안]\n{payload}\n[상충 정답셋(M1 참고)]\n{gt}\n"
            '출력: {"M1":1|3|5,...,"M5":..,"rationale":{"M1":"",..},"length_chars":<정책안 길이>}')
    ov=J.ask(judge,J.POINT_SYS,prompt)
    if not ov: print("  ! 빈 응답:",fn); continue
    ov["_judge"]=judge
    r["scores"]=[s for s in r["scores"] if s.get("_judge")!=judge]+[ov]
    r["aggregate"]=J._aggregate_points(r["scores"])
    json.dump(rows,open(PWF,"w",encoding="utf-8"),ensure_ascii=False,indent=2); print("재판정:",fn,judge)
print(f"[q03-backfill-3] 완료 — 총 {sum(len(r['scores']) for r in rows)}/324")
