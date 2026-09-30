#!/usr/bin/env bash
# 본실험(확증) 실행 오케스트레이터. 각 단계 실패 시 중단.
set -euo pipefail
cd "$(dirname "$0")"

# .env 있으면 로드(키는 파일·git에 커밋 금지)
if [ -f .env ]; then set -a; . ./.env; set +a; echo "[.env 로드됨]"; fi

step(){ echo; echo "━━━ $* ━━━"; }

step "0) 프리플라이트(과금 0)"
python3 preflight.py

step "1) 실측 파일럿 1개 (CFL-08, 과금 <\$0.5)"
read -r -p "실제 API로 CFL-08 1건을 생성합니다. 진행? [y/N] " a; [ "${a:-N}" = "y" ] || { echo "중단"; exit 0; }
python3 run_harness.py --scenario CFL-08
echo "→ output/traces 의 CFL-08_* 확인. 토큰·JSON 준수·비용 점검 후 계속하세요."

step "2) τ 캘리브레이션(선택) — 필요 시 EMBED_TAU 조정 후 진행"
read -r -p "전체 본실험(Phase1 108 + Phase2)을 실행할까요? [y/N] " b; [ "${b:-N}" = "y" ] || { echo "여기서 멈춤(1건 결과만)"; exit 0; }

step "3) Phase1 전체 생성 (12×3×3=108)"
python3 run_harness.py --phase 1

step "4) 채점 — Pointwise / Pairwise"
python3 judge.py --mode pointwise
python3 judge.py --mode pairwise

step "5) Phase2 생성 + 강화 연속 채점(함정 게이트)"
python3 run_harness.py --phase 2
python3 judge.py --mode phase2c

step "6) 3층 통계 분석"
python3 analyze.py

step "완료"
echo "산출물: output/traces/ , output/eval/{pointwise,pairwise,phase2_continuous,analysis}.json"
