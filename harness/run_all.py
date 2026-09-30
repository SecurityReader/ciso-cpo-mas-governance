#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
본실험(확증) 원클릭 실행기 — 하나의 파이썬으로 생성→채점→Phase2c→통계까지.

특징
- API 키는 **실행 시 입력**(getpass, 화면 미표시). 파일·env에 저장하지 않음.
- **완료된 부분은 자동 제외(스킵)**: 이미 생성된 trace는 건너뛰고, 이미 산출된
  채점(eval)이 최신이면 재채점하지 않음(재개 가능). --force 로 강제 재실행.
- 실측 비용 안전장치: 전체 실행 전 1개 시나리오(CFL-08) 실측 후 확인.

사용
    python run_all.py                 # 대화형 전체 실행
    python run_all.py --plan          # 실행 계획만 출력(무료, 아무것도 안 함)
    python run_all.py --force         # 기존 채점 결과 무시하고 재채점
    python run_all.py --yes           # 확인 프롬프트 자동 승인(비대화)
    python run_all.py --skip-smoke    # CFL-08 실측 단계 건너뛰기
환경
    LLM_BACKEND=dry python run_all.py --plan   # 키 없이 로직 점검
"""
import os, sys, json, glob, time, subprocess, argparse, getpass

def secret_input(prompt):
    """입력 중 * 로 마스킹해서 보여줌(Windows: msvcrt). 폴백: getpass(무에코)."""
    try:
        import msvcrt
    except ImportError:
        return getpass.getpass(prompt)
    print(prompt, end="", flush=True)
    buf = []
    while True:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            print("")
            break
        if ch == "\003":            # Ctrl-C
            print(""); raise KeyboardInterrupt
        if ch in ("\b", "\x7f"):   # Backspace
            if buf:
                buf.pop(); print("\b \b", end="", flush=True)
            continue
        if ch == "\x00" or ch == "\xe0":  # 특수키 prefix — 다음 바이트 소비
            msvcrt.getwch(); continue
        buf.append(ch); print("*", end="", flush=True)
    return "".join(buf)
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRACES = BASE/"output"/"traces"
EVAL = BASE/"output"/"eval"
PY = sys.executable

def ask(q, default="y"):
    if ARGS.yes: return True
    a = input(f"{q} [{'Y/n' if default=='y' else 'y/N'}] ").strip().lower() or default
    return a == "y"

def prompt(label, default):
    if ARGS.yes: return default
    v = input(f"{label} (기본 {default}): ").strip()
    return v or default

def newest_mtime(patterns):
    files = []
    for p in patterns: files += glob.glob(str(TRACES/p))
    return max((os.path.getmtime(f) for f in files), default=0), len(files)

def out_fresh(outfile, trace_patterns):
    """채점 산출물이 존재하고, 관련 trace보다 최신이면 True(=스킵 가능)."""
    of = EVAL/outfile
    if not of.exists() or ARGS.force: return False
    tm, n = newest_mtime(trace_patterns)
    return n > 0 and os.path.getmtime(of) >= tm

def run(cmd, stage, allow_fail=False):
    print(f"\n━━━ {stage} ━━━\n$ {' '.join(cmd)}")
    if ARGS.plan: print("  (계획 모드 — 실행 안 함)"); return
    r = subprocess.run(cmd, env=os.environ.copy())
    if r.returncode != 0:
        if allow_fail:
            print(f"  [경고] {stage} 비정상 종료(exit {r.returncode}) — 계속 진행"); return
        sys.exit(f"[중단] {stage} 실패 (exit {r.returncode})")

def count(pattern): return len(glob.glob(str(TRACES/pattern)))

def main():
    backend = os.environ.get("LLM_BACKEND", "api")
    print("="*64); print("본실험 원클릭 실행기 (run_all.py)"); print("="*64)
    print(f"백엔드: {backend}   |   작업폴더: {BASE}")

    # ── 설정 & 키 (api일 때만 입력받음) ──
    if backend == "api":
        os.environ["GEN_MODEL"] = prompt("생성 모델 GEN_MODEL", os.environ.get("GEN_MODEL","claude-sonnet-5"))
        dj = os.environ.get("JUDGE_MODELS","claude-haiku-4-5-20251001,gpt-5.1,gpt-4.1-mini")
        os.environ["JUDGE_MODELS"] = prompt("심판 3종 JUDGE_MODELS(콤마)", dj)
        os.environ["REPS"] = prompt("반복 REPS", os.environ.get("REPS","3"))
        os.environ["EMBED_MODEL"] = prompt("consensus 임베딩 EMBED_MODEL", os.environ.get("EMBED_MODEL","BAAI/bge-m3"))
        os.environ["EMBED_TAU"] = prompt("임베딩 임계 EMBED_TAU", os.environ.get("EMBED_TAU","0.75"))
        os.environ.setdefault("TEMPERATURE","0.7"); os.environ.setdefault("MAX_TOKENS","4000")
        judges = [m.strip().lower() for m in os.environ["JUDGE_MODELS"].split(",")]
        need_openai = any(m.startswith(("gpt","o1","o3","o4","chatgpt","openai/")) for m in judges)
        if not ARGS.plan:
            k = secret_input("ANTHROPIC_API_KEY 입력(입력 시 *로 표시): ").strip()
            if not k: sys.exit("ANTHROPIC_API_KEY 필요")
            os.environ["ANTHROPIC_API_KEY"] = k
            if need_openai:
                ok = secret_input("OPENAI_API_KEY 입력(비-Anthropic 심판용, 입력 시 *로 표시): ").strip()
                if not ok: sys.exit("OpenAI 심판을 쓰려면 OPENAI_API_KEY 필요")
                os.environ["OPENAI_API_KEY"] = ok
    else:
        os.environ.setdefault("GEN_MODEL","claude-sonnet-5"); os.environ.setdefault("REPS","3")

    REPS = int(os.environ.get("REPS","3"))
    print(f"\n설정 확정: GEN={os.environ.get('GEN_MODEL')} | JUDGE={os.environ.get('JUDGE_MODELS')} | REPS={REPS}")

    # ── 프리플라이트 ──
    run([PY, "preflight.py"], "0) 프리플라이트(과금 0)", allow_fail=(backend != "api"))

    # ── 기존 결과 처리: 새로 시작(archive) vs 재개(skip) ──
    existing = count("*_[ABC]_*.json")
    if existing and backend == "api" and not ARGS.plan:
        print(f"\n기존 trace {existing}개가 output/traces 에 있습니다.")
        if ask("새 본실험을 위해 기존 traces/eval 를 archive(이동)하고 처음부터 시작할까요? (아니오=재개)", "y"):
            ts = time.strftime("%Y%m%d_%H%M%S"); arch = BASE/"output"/f"_archive_{ts}"
            (arch/"traces").mkdir(parents=True, exist_ok=True); (arch/"eval").mkdir(parents=True, exist_ok=True)
            for f in glob.glob(str(TRACES/"*.json")): os.replace(f, arch/"traces"/os.path.basename(f))
            for f in glob.glob(str(EVAL/"*.json")): os.replace(f, arch/"eval"/os.path.basename(f))
            print(f"  → {arch} 로 이동 완료. 새로 시작합니다.")
        else:
            print("  → 재개 모드: 기존 trace는 건너뛰고 누락분만 생성합니다.")

    # ── 실측 스모크(1개 시나리오) ──
    if backend == "api" and not ARGS.skip_smoke and not ARGS.plan:
        if ask("실제 API로 CFL-08 1건 실측(<$0.5)을 먼저 수행할까요?", "y"):
            run([PY, "run_harness.py", "--scenario", "CFL-08"], "1) 실측 파일럿 CFL-08")
            if not ask("실측 결과(토큰·JSON·비용) OK. 전체 본실험을 진행할까요?", "y"):
                print("여기서 멈춥니다(1건만 생성됨)."); return

    # ── 전체 파이프라인 ──
    run([PY, "run_harness.py", "--phase", "1"], "2) Phase1 생성 (12×3×%d)" % REPS)
    if out_fresh("pointwise.json", ["[!P]*_[ABC]_*.json"]):
        print("\n━━━ 3) Pointwise 채점 — 최신 결과 존재, 스킵 ━━━")
    else:
        run([PY, "judge.py", "--mode", "pointwise"], "3) Pointwise 채점")
    if out_fresh("pairwise.json", ["[!P]*_[ABC]_*.json"]):
        print("\n━━━ 4) Pairwise 채점 — 최신 결과 존재, 스킵 ━━━")
    else:
        run([PY, "judge.py", "--mode", "pairwise"], "4) Pairwise 채점")

    run([PY, "run_harness.py", "--phase", "2c"], "5) Phase2 강화판(P2C) 생성")
    if out_fresh("phase2_continuous.json", ["P2C_*.json"]):
        print("\n━━━ 6) Phase2c 채점 — 최신 결과 존재, 스킵 ━━━")
    else:
        run([PY, "judge.py", "--mode", "phase2c"], "6) Phase2c 연속 채점(함정 게이트)")

    run([PY, "analyze.py"], "7) 3층 통계 분석")  # 무료 — 항상 실행

    print("\n" + "="*64)
    print("완료. 산출물:")
    print("  output/traces/            생성 trajectory")
    print("  output/eval/pointwise.json, pairwise.json, phase2_continuous.json")
    print("  output/eval/analysis.json  ← H1/H3·효과크기·CI 요약")
    print("="*64)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="실행 계획만 출력(무료)")
    ap.add_argument("--force", action="store_true", help="기존 채점 무시하고 재채점")
    ap.add_argument("--yes", action="store_true", help="모든 확인 자동 승인(비대화)")
    ap.add_argument("--skip-smoke", action="store_true", help="CFL-08 실측 스모크 생략")
    ARGS = ap.parse_args()
    main()
