# -*- coding: utf-8 -*-
"""Q03 결측 보완 — q03_eval/pointwise.json 에서 gpt-5.1 판정이 빠진 답변만
'수정 루브릭(A.8, 누락 감점)'으로 gpt-5.1 재판정해 채운다.

- q03_rescore.py 와 동일한 환경·시프트·키·채점지침(POINT_SYS)을 사용 → 기존 q03 점수와 동일 기준.
- 누락 건 × gpt-5.1 만 호출(최소 비용, ~5콜). 다른 심판 점수는 건드리지 않는다.
- 정본 output/traces(읽기)만 사용, 결과는 r41_recheck/q03_eval/pointwise.json 에만 기록.
- API 키는 런타임 입력(getpass, 화면 미표시). 파일/코드/깃에 저장하지 않는다.

실행:  cd r41_recheck && python q03_backfill.py   (OPENAI 키 입력)
이후:  python q03_analyze.py   (324 기준 재분석)
"""
import os, sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; HARNESS = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HARNESS))
from _netfix import neutralize_truststore, export_windows_ca
from _keyutil import load_env, ensure_key
from _shim import OpenAIShim

neutralize_truststore(); export_windows_ca()
load_env(HARNESS / ".env"); os.environ.setdefault("LLM_BACKEND", "api")
ensure_key("OPENAI_API_KEY")           # gpt-5.1 만 필요

import judge as J
J._openai_client = OpenAIShim()
J.TRACES = HARNESS / "output" / "traces"          # 정본 108개 읽기(쓰지 않음)
J.EVAL   = HERE / "q03_eval"                        # q03 결과 읽기/쓰기

# === 수정된 채점 지침(누락 감점) — q03_rescore.py 와 동일 ===
J.POINT_SYS = ("당신은 CISO/CPO 정책결정 품질을 평가하는 독립 심사위원이다. 어떤 구조/형식에서 나왔는지 모른다(블라인드).\n"
"M1 상충식별, M2 규제준수정밀도, M3 절충구체성, M4 편향억제, M5 잔여위험명시 를 각 1/3/5점으로만 채점.\n"
"시나리오의 요구사항과 채점 기준에 비추어 정책을 평가하라. 필수 보호조치·상충분석·잔여위험 공개의 누락은 감점하라. "
"다만 시나리오와 그 법적 참고자료가 뒷받침하지 않는 사실을 지어내거나 요구사항을 임의로 부과하지는 말라. "
"근거를 함께 제시. 순수 JSON만 출력.")

TARGET = "gpt-5.1"
rows = J._load_rows("pointwise.json")
if not rows:
    print("q03_eval/pointwise.json 없음/비어있음 — 먼저 q03_rescore.py 실행"); sys.exit(1)

need = [r for r in rows if TARGET not in {s.get("_judge") for s in r.get("scores", [])}]
print(f"[Q03-backfill] gpt-5.1 누락 대상: {len(need)}건 →", [r["file"] for r in need])
if not need:
    print("[Q03-backfill] 결측 없음(이미 324) — 종료"); sys.exit(0)

patched = 0
for r in need:
    f = J.TRACES / r["file"]
    if not f.exists():
        print("  ! 정본 trace 없음, 건너뜀:", r["file"]); continue
    tr = json.loads(f.read_text(encoding="utf-8"))
    payload = json.dumps(J.normalize(tr.get("final")), ensure_ascii=False)
    gt = J._ground_truth(tr["scenario_id"])
    prompt = (f"[정책안]\n{payload}\n[상충 정답셋(M1 참고)]\n{gt}\n"
              '출력: {"M1":1|3|5,...,"M5":..,"rationale":{"M1":"",..},"length_chars":<정책안 길이>}')
    print("재판정(수정 루브릭):", r["file"], flush=True)
    ov = J.ask(TARGET, J.POINT_SYS, prompt)
    if not ov:
        print("  ! 빈 응답 — 건너뜀(재실행 시 다시 시도)", flush=True); continue
    ov["_judge"] = TARGET
    r["scores"] = [s for s in r.get("scores", []) if s.get("_judge") != TARGET] + [ov]
    r["aggregate"] = J._aggregate_points(r["scores"])   # 무반올림(현 judge.py)
    patched += 1
    J._save_rows("pointwise.json", rows)   # 매 건 저장(중단 안전)

# 검증
rows = J._load_rows("pointwise.json")
tot = sum(len(r.get("scores", [])) for r in rows)
byj = {}
for r in rows:
    for s in r.get("scores", []):
        byj[s.get("_judge")] = byj.get(s.get("_judge"), 0) + 1
print(f"\n[Q03-backfill] 완료: {patched}건 채움 | 총 심판응답 {tot}/324 | 심판별 {byj}")
print("[Q03-backfill] 다음: python q03_analyze.py  (324 기준 A-C/B-C 재계산)")
