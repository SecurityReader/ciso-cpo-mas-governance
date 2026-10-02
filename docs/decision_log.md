# 의사결정 로그 (Decision Log) — 본실험(확증) 하네스

- 작성일: 2026-09-29
- 대상 연구: **AI 에이전트 시뮬레이션 기반 정보보호 정책결정 품질 비교 — CISO·CPO 역할분리 다중에이전트와 통합 거버넌스 구조의 요인통제 파일럿 평가**
- 목적: 본실험(확증) 하네스 구축·디버깅 과정의 **모든 설계 결정·환경 구성·인시던트·근본원인·조치**를 감사 추적(audit trail)으로 남긴다. 논문 Methods / OSF 사전등록 / 재현성 부록에 그대로 인용 가능하도록 작성.
- 관련 기록: `모델·버전-기록.md`, `하네스-개선기록_260927.md`, `블라인드에이전트-실행기록.md`, `본실험-실행가이드.md`, `임베딩-설정.md`

---

## 0. 요약 (TL;DR)

- 키리스(세션 내 서브에이전트) 파일럿의 강한 H1 신호(δ=0.918)는 **확증 아님(prior)**. 실제 API 모델로 요인통제 확증실험을 수행 중.
- 확증 1차 실행은 **truncation 아티팩트로 무효**였음(δ=−1.0). 근본원인은 A 조건 중재자 최종 JSON이 `max_tokens`에서 잘려 `final=null`이 된 것 + 심판 파싱 실패.
- 근본원인 2건 확정·수정: (1) `run_all.py`가 `MAX_TOKENS`를 2000으로 강제 → 4000으로 수정, (2) `.env`에 잔존한 `MAX_TOKENS=2000`·구(舊) 심판 설정(Opus 포함) landmine 제거.
- 비용 재산정 결과 최초 산정($12–26)은 **3–5배 과소추정**. 원인은 A 조건의 누적 컨텍스트(입력 ~13배 과소), 심판(특히 Opus) 비용 누락, 재실행 횟수 미포함.
- 비용 절감 결정: **심판에서 Opus 5.5 제외**(1번) 채택. 캐싱(3번)·Batch(2번)는 이번 회차 미적용.
- 2차(정정) 실행 진행 중: 생성 전량 완료(A/B/C 각 36, P2C B/C 12), 판정 진행 중(pointwise 40/108 시점 기록).

---

## 1. 실험 환경 (Environment)

### 1.1 런타임
| 항목 | 값 |
|---|---|
| OS | Windows (desktop-nhhfp09) |
| Python | Windows Store Python **3.13**, 전용 venv (`.venv`) |
| 작업 경로 | `C:\X1. New Paper_260919\output\harness` |
| 실행 진입점 | `run_all.py` (단일 오케스트레이터, 런타임 키 입력) |

### 1.2 SDK / 의존성
| 패키지 | 정책 | 비고 |
|---|---|---|
| anthropic | **`<1` 로 고정 설치** | 1.8.0의 `httpx2` 디코더 버그(`process() takes no keyword arguments`) 회피. requirements.txt 표기(`>=0.40`)와 별개로 실제 설치본은 httpx1 계열 강제 |
| openai | **`<1.60` 로 고정 설치** | httpx2 의존 회피(anthropic 다운그레이드와 정합) |
| sentence-transformers | `>=3.0` | 로컬 consensus 임베딩 |
| truststore | `>=0.9` | corporate intercepting (MITM) proxy — trust the OS certificate store |

### 1.3 네트워크
- a corporate intercepting (MITM) proxy environment → `truststore.inject_into_ssl()`로 OS 신뢰저장소 사용(+CA 파일 폴백). `verify=False` 미사용.
- 일시적 DNS 실패(`getaddrinfo failed`) 대응: 지수 백오프 재시도 `_retry(tries=6, base=3.0)`.

### 1.4 임베딩 (consensus)
- 본실험: 로컬 **`BAAI/bge-m3`** (sentence-transformers, API 불필요). τ는 `임베딩-설정.md` 기준.
- (키리스 파일럿은 `minishlab/potion-multilingual-128M` model2vec 사용 — 데모용, 확증 아님.)

### 1.5 모델 구성 (본실험, 2026-09-29 확정)
| 역할 | 모델 |
|---|---|
| 생성(GEN_MODEL) | `claude-sonnet-5` |
| 심판(JUDGE_MODELS) | `claude-haiku-4-5-20251001`, `gpt-5.1`, `gpt-4.1-mini` |
| 디코딩 | TEMPERATURE=0.7, **MAX_TOKENS=4000** |
- 자기선호편향 통제: 생성모델(Anthropic sonnet-5)과 심판 분리, 비-Anthropic ≥1(현재 2종) 유지.

### 1.6 동결 시나리오 (SHA-256 앞 16자리)
| 파일 | 해시 | 구성 |
|---|---|---|
| `scenarios_min.json` | `3caa70daefc46943` | Phase1: CFL 8 + IND 2 + COL 2 = 12 |
| `scenarios_phase2_hardened.json` | `318779db5d669253` | Phase2c: 고충돌 CFL 4개(경화) |
- **결과 관찰 이후 시나리오 수정 금지**(p-hacking 방지). 해시로 무결성 검증.

---

## 2. 설계 결정 (Design Decisions)

### 2.1 요인통제(factorial) 설계
- **A** = 역할분리 MoE(CISO+CPO+Mediator, 3라운드, 세션 격리)
- **B** = 통합 3-step
- **C** = 통합 3-round(형식 통제)
- **A vs C = 역할분리 효과**(H1, 단측), **B vs C = 형식 효과**(H3, 양측). C가 형식 교란을 흡수.
- Phase1 = 12 시나리오 × 3 조건 × 3 반복 = **108 run**. Phase2c(경화) = 4 × 3 × 3 = **36 run**.

### 2.2 지표
- M1 상충식별 / M2 규제준수 / M3 절충구체성 / M4 편향억제 / M5 잔여위험, 각 1·3·5 척도. S = ΣM.
- 통계: Cliff's δ, 부호검정, Wilcoxon, 부트스트랩 CI, Holm 보정, verbosity(길이) 상관 통제, 심판 신뢰도(일치도).

### 2.3 심판 앙상블 원칙
- 블라인드 LLM 심판 3종 이상(`preflight.py`가 `len>=3` 강제).
- 생성≠심판, 비-Anthropic ≥1 → 자기선호편향 통제.

### 2.4 스키마 통일(교란 제거)
- 초기 파일럿의 조건별 스키마 비대칭(`risk_owner`, `resolved_conflicts` vs `conflicts_identified`)이 교란이었음 → **3축(법·기술·운영) 보존 규칙**으로 통일, 중재자 프롬프트 보강.

---

## 3. 의사결정 로그 (시간순)

| # | 시점 | 결정 | 근거 | 상태 |
|---|---|---|---|---|
| D01 | 파일럿 | 키리스(세션 서브에이전트) 결과는 prior로만 취급 | 생성=심판 동일 세션모델 → 자기선호 미통제, 서빙모델 불확정 | 확정 |
| D02 | 준비 | 심판을 **비-Anthropic(OpenAI) 포함**으로 구성 | 자기선호편향 통제 | 확정 |
| D03 | 준비 | 이상현상(anomaly) 나와도 **TC 수정 금지** | 결과 보고 후 시나리오 수정 = p-hacking | 확정(동결) |
| D04 | 준비 | 하네스 개선 + 중재자 프롬프트 3축 보존 보강 | 스키마 비대칭 교란 제거 | 확정 |
| D05 | 준비 | 설계 MD 문서를 코드 변경에 동기화 | 방법론-구현 정합 | 확정 |
| D06 | 준비 | 단일 `run_all.py`로 통합, 완료분 skip(resume), **키는 런타임 getpass 입력(`****` 마스킹)** | 재현성 + 키 비저장 보안 | 확정 |
| D07 | 실행 | `temperature` 미지원/deprecated 모델 대응: 클라이언트측 폴백 | TypeError 및 400 "temperature" 회피 | 확정 |
| D08 | 실행 | anthropic `<1`, openai `<1.60` 다운그레이드 | httpx2 디코더 버그 | 확정 |
| D09 | 실행 | `truststore.inject_into_ssl()` 도입 | corporate intercepting (MITM) proxy TLS verification | 확정 |
| D10 | 실행 | `_retry` 지수 백오프 도입 | 일시 DNS/네트워크 오류 | 확정 |
| D11 | 실행 | 심판 incremental save + resume + 진행출력 | 장시간 판정 중단 복구 | 확정 |
| D12 | 검토 | **1차 확증결과(δ=−1.0)를 실제 발견으로 보고하지 않음** | truncation 아티팩트로 판정 | 확정(무결성) |
| D13 | 정정 | 근본원인: A 중재자 JSON이 `max_tokens`에서 절단 → `final=null` | 트레이스 21/36 final=None, 심판 파싱 실패, verbosity r=0.956 | 확정 |
| D14 | 정정 | MAX_TOKENS 2000→4000(gen), 심판 1200→3000 | 절단 방지 | 확정 |
| D15 | 정정 | 깨진 A 트레이스 삭제, 유효 B/C 보존 | 재개 재생성 | 확정 |
| D16 | 09-29 | **근본원인 재확정**: `run_all.py`가 `MAX_TOKENS`를 2000으로 강제(setdefault)하여 D14가 무력화됨 → 4000으로 수정 | 트레이스 meta `max_tokens:2000` 확인, 신규 A 16개 final=null | 확정 |
| D17 | 09-29 | 비용 절감 **1번(심판 Opus 5.5 제외)** 채택 | 최대 단일비용·설정변경만으로 즉효 | 확정 |
| D18 | 09-29 | 절감 **3번(캐싱)·2번(Batch) 미적용** | 코드 구조변경 리스크(재무효 위험) | 확정(이번 회차) |
| D19 | 09-29 | 3rd 심판 `gpt-5.1-mini`→`gpt-4.1-mini`로 교체 | 계정에 gpt-5.1-mini 미존재(404) | 확정 |
| D20 | 09-29 | `.env` landmine 제거(MAX_TOKENS 2000, 구 심판 Opus) | `run_confirmatory.sh` 경유 시 재truncation·재과금 방지 | 확정 |

---

## 4. 인시던트 & 근본원인 (RCA)

### 4.1 δ=−1.0 아티팩트 (치명적, 무효 처리)
- 증상: H1(A vs C)에서 A가 전패(δ=−1.0).
- 근본원인: A 조건 중재자 **최종 JSON 절단** → `final=null`(21/36). 심판(특히 Opus)도 파싱 실패(21/108). verbosity 상관 r=0.956로 길이 교란 동반.
- 조치: D14~D16. **실제 발견으로 보고 금지**(D12).

### 4.2 절단 재발 (MAX_TOKENS 우회)
- 증상: 4000으로 올렸는데도 신규 A 16개 `final=null`.
- 근본원인: `run_all.py:99`의 `os.environ.setdefault("MAX_TOKENS","2000")`가 `run_harness.py`의 4000 기본값을 선점.
- 조치: 2000→4000 수정(D16), 백업 `run_all.py.bak_maxtok`.

### 4.3 심판 모델 404
- 증상: `gpt-5.1-mini does not exist` → pointwise 중단.
- 근본원인: 계정 미보유 모델을 3rd 심판 기본값으로 지정.
- 조치: `gpt-4.1-mini`로 교체(D19). 404 재발 시 `gpt-4o-mini` 폴백.

### 4.4 환경 오류 체인 (해결됨)
- temperature kwarg/deprecated(D07), httpx2(D08), SSL MITM(D09), getaddrinfo(D10), 심판 무진행 착시(D11), Anthropic 크레딧 소진(과금—코드 아님).

---

## 5. 비용 재산정 & 절감 결정

### 5.1 최초 산정 오류
- 최초 $12–26 → **3–5배 과소추정**.
- 원인 3가지: (1) A 조건 누적 컨텍스트로 입력 토큰 ~13배 과소(run당 4,066 가정 vs 실측 ~53,207), (2) 심판 비용 누락(특히 Opus 5.5 ~1,400콜), (3) 재실행 횟수(rep 4회 + 아티팩트 재실행) 미포함.

### 5.2 실측 토큰(Phase1 저장 트레이스 기준)
| 조건 | run당 입력 | run당 출력 |
|---|---|---|
| A | ~53,207 | ~15,157 |
| B | ~6,971 | ~4,222 |
| C | ~27,529 | ~10,496 |
- 1회 완전 실행 추정: 생성 ~$17(Phase1) + P2C ~$6 + 심판 ~$48 ≈ **$65–75**. 누적(재실행 포함) $200–400+ 추정.

### 5.3 단가 참고(2026-09, per Mtok)
- Sonnet 5 $2/$10 · Haiku 4.5 $1/$5 · **Opus 5.5 $4/$20** · GPT-5.1 ~$1.25/$10.

### 5.4 절감 결정
- **채택: 1번 심판 Opus 제외** → 심판비 대폭 감소, 자기선호 통제 유지(비-Anthropic 2종).
- **보류: 3번 캐싱**(A 재생성 시 효과 크나 코드변경), **2번 Batch**(비동기 구조변경) — 정식 후속 실행에서 검토.

---

## 6. 무결성 · 보안 원칙 (동결)

- **시나리오 동결**: 결과 관찰 후 수정 금지. 해시로 검증(§1.6).
- **방법론 문서 동결**: 결과 관찰 이후 설계 MD 사후수정 금지.
- **아티팩트 비보고**: δ=−1.0 등 절단 유래 결과는 발견으로 보고하지 않음.
- **키 보안**: API 키는 런타임 getpass 입력·`****` 마스킹. 코드/파일/git/zip에 미기록. `.env`의 키 필드는 더미 placeholder(실키 아님)로 확인됨.

---

## 7. 현재 상태 & 잔여 작업 (2026-09-29 03:5x UTC)

- 생성: Phase1 A/B/C 각 **36/36**, Phase2c B/C **12/12**(P2C의 A는 판정 후 phase2c 단계에서 생성).
- 판정: pointwise **진행 중(40/108 시점)**, 이후 pairwise → phase2c(A 생성 포함) → analyze.
- 신규 A 트레이스: `max_tokens=4000`, `final` 정상, `status=ok` 확인.
- 잔여: 판정 완료 후 무결성 4점검 — (1) A final=null 0건, (2) 심판 파싱 n≈108, (3) verbosity r 하락, (4) 실제 H1/H3.

---

## 8. 재현 커맨드

```
cd C:\X1. New Paper_260919\output\harness
.\.venv\Scripts\activate
python run_all.py
```
- JUDGE_MODELS 프롬프트: 기본값(`claude-haiku-4-5-20251001,gpt-5.1,gpt-4.1-mini`) 그대로.
- "archive하고 처음부터?" → **n(재개)** — 완료 생성분 보존, 누락분·판정만 진행.
- 404 재발 시 3rd 심판을 `gpt-4o-mini`로 교체.

---

## 부록 A. 변경 파일 / 백업

| 파일 | 변경 | 백업 |
|---|---|---|
| `run_harness.py` | truststore, _retry, temperature 폴백, 스키마 통일, phase2c, MAX_TOKENS 4000 | `run_harness.py.bak` |
| `judge.py` | OpenAI/Anthropic 라우팅, temperature 폴백, incremental+resume, max_tokens 3000, 심판 기본값(Opus 제외) | `judge.py.bak`, `.bak2`, `.bak_judge` |
| `run_all.py` | 단일 오케스트레이터, getpass 마스킹, MAX_TOKENS 4000, 심판 기본값 | `run_all.py.bak_maxtok`, `.bak_judge` |
| `.env` | JUDGE Opus 제거·gpt-4.1-mini, MAX_TOKENS 4000 | `.env.bak_judge` |
| `analyze.py`, `preflight.py` | 3층 통계 / 의존·키·해시·심판 점검 | — |

*본 로그는 결과 관찰 이전에 확정된 설계·환경 결정과, 이후의 순수 버그수정·비용결정을 구분해 기록한다. 방법론(가설·지표·시나리오)은 동결 상태이며 결과에 맞춘 사후수정을 하지 않는다.*

---

## 9. 실행 결과 & 후속 결정 (2026-09-29 완료 기록)

### 9.1 추가 의사결정
| # | 결정 | 근거 | 상태 |
|---|---|---|---|
| D21 | 3rd 심판 `gpt-5.1-mini`→`gpt-4.1-mini` 확정, `.env`도 동기화 | 404(계정 미보유), landmine 제거 | 완료·검증 |
| D22 | **P2C_A "final=null" 경보를 오진으로 판정** — 재실행/삭제 안 함 | phase2c는 설계상 `final` 없이 `challenge_steps` 사용, A 6단계 전량 채워짐(filled=6,ok=6) | 완료 |
| D23 | 확증 결과를 **null로 확정·보고** | H1 δ=0.188·Holm p=1.0·CI 0포함, H3 δ=0.016, Phase2c 무차이 | 완료 |
| D24 | pairwise는 **위치편향(consistency 0.417)으로 본문 제외/대칭화 대상** | 순서 뒤집힘, 신뢰 지표는 pointwise | 권고 확정 |
| D25 | 결과 문서 3종 작성(본실험-결과종합 / 시나리오별-평가상세 / 본 로그 결과섹션) | 감사추적·논문화 | 완료 |

### 9.2 결과 요약 (상세는 `본실험-결과종합_260929.md`)
- **H1 역할분리(A vs C, n=8)**: 평균차 +0.179, Cliff's δ=0.188, 부호검정 p=0.637, Holm p=1.0, 부트스트랩 CI [−0.226, 0.553](0 포함) → **유의차 없음. 파일럿 δ=0.918 재현 실패.**
- **H3 형식(B vs C)**: δ=0.016, p=1.0 → 형식효과 없음.
- **조건별 S(만점25)**: A 24.15 / B 24.28 / C 24.19 (A 분산 최대).
- **Phase2c 강건성**: resilience A .971 / B .973 / C .968, 붕괴 0/12 전 조건.
- **교란 통제 확인**: verbosity r=−0.15(아티팩트 0.956 해소), Opus 제외·비-Anthropic 2종.
- **미세 trade-off(탐색적)**: C가 M1/M3/M4 만점이나 M5(잔여위험) 최저(4.27); A는 M5 최고(4.65). IND 시나리오에서 A 최저(23.45).

### 9.3 산출 문서
- `본실험-결과종합_260929.md` — 통계·지표·군별·강건성·한계 상세.
- `본실험-시나리오별-평가상세_260929.md` — 12 시나리오 × A/B/C 답변 발췌 + 3심판 평가 근거(1366줄).
- `연구-요약및향후과제_260929.md` — 전체 여정 요약 + 후속 과제.

### 9.4 미결/후속 (상세는 향후과제 문서)
1. TOST/SESOI 동등성 검정 추가(analyze 확장). 2. pairwise 순서 대칭화 재산출. 3. 천장효과 돌파(난이도↑·상대평가). 4. gpt-5.1 누락 3건(105/108) 재판정. 5. 다른 생성모델 일반화. 6. OSF 사전등록 확정·논문 Methods 반영.


### 9.5 동등성 검정(TOST/SESOI) 구현·반영 (D26)
| # | 결정 | 근거 | 상태 |
|---|---|---|---|
| D26 | analyze.py에 **TOST(모수적 t) + 부트스트랩 90%CI 포함검정** 구현, SESOI=EQ_MARGIN(기본 ±1.0점) | "유의차 없음"→"실질적 동등" 정식화 | 완료·검증 |

- 구현: t-분포 CDF 자체구현(불완전베타), `equivalence()` 함수, H1/H3에 `equivalence_TOST` 블록. 외부 의존성 0. 백업 `analyze.py.bak_tost`.
- 결과: H1 p_TOST=0.0029, H3 p_TOST=0.0025 → 둘 다 **EQUIVALENT**(SESOI ±1.0).
- 민감도: ±0.5 INDETERMINATE(부트스트랩 동등, 파라메트릭 p>0.05) · ±1.0·±1.5 EQUIVALENT. → SESOI≥±1.0에서 견고.
- 결과 문서(본실험-결과종합 §4.5)·Word 초록에 반영.
