# -*- coding: utf-8 -*-
"""Q03 재채점 — 기존 108개 출력을 '수정된 루브릭'으로 다시 채점(생성 재실행 없음).
변경점: 심판 지침에서 '명시되지 않은 사항 감점 금지' → '필수 보호조치·상충분석·잔여위험 공개의 누락은 감점'
정본 output/traces(읽기)만 사용, 결과는 r41_recheck/q03_eval 에만 기록.
실행:  python q03_rescore.py   (ANTHROPIC + OPENAI 키 입력)   비용 ~0.5~0.9M 토큰
"""
import os, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; HARNESS=HERE.parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HARNESS))
from _netfix import neutralize_truststore, export_windows_ca
from _keyutil import load_env, ensure_key
from _shim import AnthropicShim, OpenAIShim

neutralize_truststore(); export_windows_ca()
load_env(HARNESS/".env"); os.environ.setdefault("LLM_BACKEND","api")
ensure_key("ANTHROPIC_API_KEY"); ensure_key("OPENAI_API_KEY")

import judge as J
J._anthropic_client = AnthropicShim(); J._openai_client = OpenAIShim()
J.TRACES = HARNESS/"output"/"traces"          # 정본 108개 읽기(쓰지 않음)
J.EVAL   = HERE/"q03_eval"; J.EVAL.mkdir(parents=True, exist_ok=True)

# === 수정된 채점 지침(누락 감점) ===
J.POINT_SYS = ("당신은 CISO/CPO 정책결정 품질을 평가하는 독립 심사위원이다. 어떤 구조/형식에서 나왔는지 모른다(블라인드).\n"
"M1 상충식별, M2 규제준수정밀도, M3 절충구체성, M4 편향억제, M5 잔여위험명시 를 각 1/3/5점으로만 채점.\n"
"시나리오의 요구사항과 채점 기준에 비추어 정책을 평가하라. 필수 보호조치·상충분석·잔여위험 공개의 누락은 감점하라. "
"다만 시나리오와 그 법적 참고자료가 뒷받침하지 않는 사실을 지어내거나 요구사항을 임의로 부과하지는 말라. "
"근거를 함께 제시. 순수 JSON만 출력.")

print("[Q03] 수정 루브릭으로 재채점 시작 (정본 108 → q03_eval)")
print("[Q03] 변경: '미명시 감점 금지' → '필수항목 누락 감점'")
J.pointwise()
print("[Q03] 재채점 완료 → python q03_analyze.py")
