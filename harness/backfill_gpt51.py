# -*- coding: utf-8 -*-
# backfill_gpt51.py — pointwise.json에서 gpt-5.1 판정이 빠진 답변만 gpt-5.1로 재판정해 채운다.
# - 정확히 '누락된 건 × gpt-5.1' 만 호출(최소 비용). 다른 심판 점수는 건드리지 않는다.
# - API 키는 런타임 입력(getpass, 화면 미표시). 파일/코드/깃에 저장하지 않는다.
import os, json, getpass, sys
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OPENAI_API_KEY 입력(화면 미표시): ").strip()
os.environ.setdefault("MAX_TOKENS", "4000")
os.environ.setdefault("JUDGE_MODELS", "claude-haiku-4-5-20251001,gpt-5.1,gpt-4.1-mini")

import judge as J  # truststore 주입·ask·normalize·_ground_truth·POINT_SYS 재사용

TARGET = "gpt-5.1"
rows = J._load_rows("pointwise.json")
if not rows:
    print("pointwise.json 없음/비어있음 — 중단"); sys.exit(1)

need = [r for r in rows if TARGET not in {s.get("_judge") for s in r.get("scores", [])}]
print(f"대상: {len(need)}건 (gpt-5.1 누락) →", [r["file"] for r in need])
patched = 0
for r in need:
    f = J.TRACES / r["file"]
    tr = json.loads(f.read_text(encoding="utf-8"))
    payload = json.dumps(J.normalize(tr.get("final")), ensure_ascii=False)
    gt = J._ground_truth(tr["scenario_id"])
    prompt = (f"[정책안]\n{payload}\n[상충 정답셋(M1 참고)]\n{gt}\n"
              '출력: {"M1":1|3|5,...,"M5":..,"rationale":{"M1":"",..},"length_chars":<정책안 길이>}')
    print("재판정:", r["file"], flush=True)
    ov = J.ask(TARGET, J.POINT_SYS, prompt)
    if not ov:
        print("  ! 빈 응답 — 건너뜀(재실행 시 다시 시도)", flush=True); continue
    ov["_judge"] = TARGET
    # 혹시 중복 방지: 기존 gpt-5.1 있으면 교체
    r["scores"] = [s for s in r.get("scores", []) if s.get("_judge") != TARGET] + [ov]
    r["aggregate"] = J._aggregate_points(r["scores"])
    patched += 1
    J._save_rows("pointwise.json", rows)   # 매 건 저장(중단 안전)

# 검증
rows = J._load_rows("pointwise.json")
full = sum(1 for r in rows if len(r.get("scores", [])) >= 3)
miss = [r["file"] for r in rows if TARGET not in {s.get("_judge") for s in r.get("scores", [])}]
print(f"완료: {patched}건 채움 | 3심판 완비 답변 {full}/{len(rows)} | gpt-5.1 잔여누락 {len(miss)} {miss}")
