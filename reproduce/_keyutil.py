# -*- coding: utf-8 -*-
"""공용: .env 로드 + 키 유효성 검사 + getpass 입력(파일 미저장)."""
import os, getpass
from pathlib import Path

def load_env(p: Path):
    if not p.exists():
        print(f"[R41][경고] .env 없음: {p}"); return
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln: continue
        k, v = ln.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    print(f"[R41] .env 로드됨: {p}  (placeholder 키는 무시하고 아래에서 입력받음)")

def _looks_placeholder(v: str) -> bool:
    return (not v) or len(v) < 20 or "..." in v

def ensure_key(name: str):
    """env 키가 없거나 placeholder면 getpass로 입력받아 설정."""
    v = os.environ.get(name, "")
    if _looks_placeholder(v):
        v = getpass.getpass(f"  {name} 입력(화면 미표시): ").strip()
        if _looks_placeholder(v):
            raise SystemExit(f"[R41] {name} 가 유효하지 않습니다(길이 부족). 중단.")
        os.environ[name] = v
        print(f"  [R41] {name} 입력됨(len={len(v)}).")
    else:
        print(f"  [R41] {name} 환경변수 사용(len={len(v)}).")
