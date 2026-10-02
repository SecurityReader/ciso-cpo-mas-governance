# -*- coding: utf-8 -*-
"""R41 생성부(정본 미변경). urllib shim 으로 httpx2 우회. 상한 8000/반복 1."""
import os, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; HARNESS=HERE.parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HARNESS))
from _netfix import neutralize_truststore, export_windows_ca
from _keyutil import load_env, ensure_key
from _shim import AnthropicShim

# HuggingFace(bge-m3 합의점수)의 업데이트-확인 HEAD 호출이 회사 MITM에서 SSL 실패 → 캐시만 사용
os.environ.setdefault("HF_HUB_OFFLINE","1")
os.environ.setdefault("TRANSFORMERS_OFFLINE","1")
os.environ.setdefault("REQUESTS_CA_BUNDLE", str((HERE/"corp_ca.pem")))
os.environ.setdefault("CURL_CA_BUNDLE", str((HERE/"corp_ca.pem")))
neutralize_truststore(); export_windows_ca()
load_env(HARNESS/".env"); ensure_key("ANTHROPIC_API_KEY")
os.environ["MAX_TOKENS"]="8000"; os.environ["REPS"]="1"
os.environ.setdefault("GEN_MODEL","claude-sonnet-5"); os.environ.setdefault("LLM_BACKEND","api")

SUBSET={"CFL-01","CFL-05","CFL-06","CFL-08"}
import run_harness as H
H.client = AnthropicShim()                   # httpx2 SDK 대신 stdlib shim 주입
H.OUTDIR = HERE/"traces"; H.OUTDIR.mkdir(parents=True, exist_ok=True)
print(f"[R41] GEN_MODEL={H.GEN_MODEL} MAX_TOKENS={H.MAX_TOKENS} REPS={H.REPS} BACKEND={H.BACKEND}")
print(f"[R41] 대상={sorted(SUBSET)} 출력={H.OUTDIR}")
H.phase1(SUBSET)
print("[R41] 생성 완료 → python run_judge.py")
