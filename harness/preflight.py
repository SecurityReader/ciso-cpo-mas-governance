#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""본실험 착수 전 점검 (과금 없음: import·환경변수·설정만 확인, API 호출·모델 다운로드 안 함)."""
import os, importlib.util, sys
ok = True
def chk(cond, good, bad):
    global ok
    print(("  ✅ " if cond else "  ❌ ") + (good if cond else bad))
    ok = ok and cond
def has(mod): return importlib.util.find_spec(mod) is not None

print("── 1) 파이썬 패키지 ──")
chk(has("anthropic"), "anthropic 설치됨", "anthropic 없음 → pip install -r requirements.txt")
chk(has("openai"), "openai 설치됨", "openai 없음(비-Anthropic 심판용) → pip install openai")
chk(has("sentence_transformers"), "sentence-transformers 설치됨",
    "sentence-transformers 없음(consensus 임베딩) → pip install sentence-transformers")

print("── 1b) SDK 무결성(환경 오염 점검) ──")
# 아래는 정보/경고만(통과를 막지 않음). 실제 create() 호환은 코드의 런타임 폴백이 처리.
try:
    import anthropic, inspect
    ver = getattr(anthropic, "__version__", "?")
    try:
        sig = inspect.signature(anthropic.Anthropic().messages.create)
        temp = "temperature" in sig.parameters
    except Exception:
        temp = None  # 래퍼로 시그니처가 가려질 수 있음(판단 불가)
    print(f"  · anthropic {ver} (temperature 시그니처 노출: {temp} — None/False라도 런타임 폴백 있음)")
except Exception as e:
    print(f"  · [경고] anthropic 점검 실패: {e}")
try:
    import httpx; print(f"  · httpx {getattr(httpx,'__version__','?')}")
except Exception:
    print("  · [경고] httpx import 이상")
if importlib.util.find_spec("httpx2"):
    print("  · [경고] httpx2 감지 — 응답 압축해제 오류(process() takes no keyword arguments) 가능. "
          "발생 시 zstandard/brotli 재설치 또는 anthropic<1 다운그레이드.")
for br in ("brotli","brotlicffi","zstandard"):
    if importlib.util.find_spec(br):
        print(f"  · 압축 backend {br} 설치됨")

print("── 2) 백엔드/모델 설정 ──")
backend = os.environ.get("LLM_BACKEND", "api")
chk(backend == "api", f"LLM_BACKEND={backend}", f"LLM_BACKEND={backend} (본실험은 api여야 함)")
gen = os.environ.get("GEN_MODEL", "")
chk(bool(gen) and "3-5" not in gen, f"GEN_MODEL={gen or '(미설정)'}",
    "GEN_MODEL 미설정/구버전 → 현재 유효 ID 명시(docs.claude.com/en/docs/about-claude/models)")
judges = [m.strip() for m in os.environ.get("JUDGE_MODELS", "").split(",") if m.strip()]
chk(len(judges) >= 3, f"JUDGE_MODELS {len(judges)}종: {judges}", "심판 3종 이상 지정 필요")
chk(gen not in judges, "생성모델이 심판 집합에서 제외됨(자기선호 완화)", "생성모델을 심판에서 제외할 것")
def is_openai(m): 
    m=m.lower(); return m.startswith(("gpt","o1","o3","o4","chatgpt","openai/"))
non_anthropic = [m for m in judges if is_openai(m)]
chk(len(non_anthropic) >= 1, f"비-Anthropic 심판 {non_anthropic} 포함(자기선호 통제)",
    "심판 3종이 전부 Anthropic → 1종 이상 비-Anthropic(OpenAI 등) 권장, 아니면 Discussion에 한계 명시")

print("── 3) API 키 ──")
chk(bool(os.environ.get("ANTHROPIC_API_KEY")), "ANTHROPIC_API_KEY 설정됨", "ANTHROPIC_API_KEY 미설정")
if non_anthropic:
    chk(bool(os.environ.get("OPENAI_API_KEY")), "OPENAI_API_KEY 설정됨", "OPENAI_API_KEY 미설정(OpenAI 심판 사용 중)")

print("── 4) 임베딩(consensus, 로컬·과금無) ──")
print(f"  · EMBED_MODEL={os.environ.get('EMBED_MODEL','BAAI/bge-m3')} EMBED_TAU={os.environ.get('EMBED_TAU','0.75')}"
      "  (최초 1회 모델 다운로드 발생 가능)")

print("── 5) 시나리오 동결본 ──")
import pathlib, hashlib
sc = pathlib.Path(__file__).resolve().parent / "scenarios_min.json"
if sc.exists():
    h = hashlib.sha256(sc.read_bytes()).hexdigest()[:16]
    print(f"  · scenarios_min.json sha256[:16]={h}  ← OSF 동결 해시로 기록")
else:
    chk(False, "", "scenarios_min.json 없음")

print("\n" + ("✅ 통과 — 다음: `python run_harness.py --scenario CFL-08` 실측(<$0.5)" if ok
              else "❌ 위 항목 해결 후 재실행"))
sys.exit(0 if ok else 1)
