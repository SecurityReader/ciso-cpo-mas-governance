# 모델·버전 기록 (Model & Version Provenance)

- 갱신일: 2026-10-02
- 목적: 키리스 파일럿에서 실제로 무엇이 생성·채점했는지, 본실험에서 무엇을 쓸지 투명 기록. 재현·논문 Methods·OSF 동결 파라미터에 그대로 인용.

---

## 1. 키리스 파일럿 (이미 수행) — 실제 사용 모델

생성·심판 실행 주체
: 세션 내 **Task 서브에이전트**. 별도 API 키·과금 없음.

기반 모델(설정 식별자)
: **`claude-opus-4-8`** (이 세션 어시스턴트의 설정 식별자). 단, 실제 서빙 모델은 런타임 폴백·전환으로 **다를 수 있어 확정 불가**하며, 세션 정책상 정확한 서빙 버전은 조회되지 않는다.

대상 모델과의 관계
: 이 세션 기반 모델은 **연구가 선언할 대상 API 모델이 아니다.** → 파일럿 수치는 **강한 사전 신호(prior)**이지 확증이 아님.

생성·심판 동일성
: 생성과 심판이 **모두 같은 세션 기반 모델** → 자기선호편향 미통제(구조적 한계).

temperature / seed
: 서브에이전트 경로라 **하네스 수준의 temperature·seed 고정이 적용되지 않음**(각 서브에이전트 기본 디코딩). 반복은 rep1·rep2 두 회차로만 관리.

임베딩(consensus)
: 로컬 정적 임베딩 `minishlab/potion-multilingual-128M`(model2vec) — 키리스 데모용, τ(model2vec)≈0.35. 본실험은 `BAAI/bge-m3` 로컬 권장.

수행 범위
: Phase1 A/B/C × CFL 7개 × rep1·rep2 / Phase2 A·C × 고충돌 4개(6단계+함정). 상세: `블라인드에이전트-실행기록.md`.

---

## 2. 본실험 (확정) — 사용한 모델 파라미터

생성 모델(GEN_MODEL)
: **`claude-sonnet-5`** (temperature=0.7, max_tokens=4000). 하네스 기본값(`claude-3-5-sonnet-latest`)은 실행 시 명시적으로 덮어썼다. 단, 실제 서빙 버전은 런타임 폴백·전환으로 다를 수 있으며, 정확한 설치 SDK 버전은 가용 실험 기록에 보존되어 있지 않다(의존성 범위: `anthropic<1`, `openai<1.60`).

심판 모델 3종(JUDGE_MODELS)
: **`claude-haiku-4-5`, `gpt-5.1`, `gpt-4.1-mini`** — 서로 다른 제공자의 3종(Anthropic 1 + OpenAI 2). **생성 모델(`claude-sonnet-5`)은 심판 집합에서 제외**(생성≠심판)하여 자기선호편향을 구조적으로 완화.

temperature / seed
: temperature=0.7, seed는 실행별 기록(`make_seed(sid,cond,rep)`), 반복 3회.

임베딩
: **로컬** `BAAI/bge-m3`(sentence-transformers) — API 불필요, τ=0.75.

동결·분석 시점
: 확증 실행은 결과 관측 전 시나리오·하이퍼파라미터를 동결(해시 `scenarios/FREEZE_HASHES.txt`). 동등성 검정(TOST)·±1.0 SESOI는 확증 null 관측 후 추가된 **사후·탐색적** 분석(`CHANGELOG`·원고 III-F). 모델 버전 드리프트는 한계로 명시.

---

## 3. 자기선호편향 관련 정직한 주석

Claude-only 심판의 한계
: 심판을 전부 Claude로 두면 **모델군 수준의 자기선호**는 완전히 통제되지 않는다(생성도 Claude일 경우). 서로 다른 Claude 모델 사용 + 생성≠심판 교차로 **부분 완화**는 되나, 완전 통제는 **비-Anthropic 1종** 또는 **로컬 모델 1종**을 심판에 포함해야 달성된다.

권장 최소 구성
: 생성 Claude + 심판 3종 중 **최소 1종을 비-Claude/로컬**로 → 확증력 확보.

확증 실행에서의 실제 구성
: 생성 `claude-sonnet-5`, 심판 3종 중 **2종이 비-Anthropic(`gpt-5.1`, `gpt-4.1-mini`)** + Anthropic 1종(`claude-haiku-4-5`). 생성≠심판이며 제공자 교차가 확보되어, 위 권장 최소 구성을 충족한다(모델군 수준 자기선호의 부분 완화; 완전 통제는 아님).
