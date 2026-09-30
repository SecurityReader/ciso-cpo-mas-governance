# 임베딩 설정 방법 (consensus 의미매칭)

임베딩은 **직접 만드는 게 아니라 로컬 오픈모델을 설치·다운로드해서 쓰는 것**이다. API 키가 필요 없다(완전 키리스, 로컬 연산). 하네스는 설치된 것을 **자동 감지**해 consensus 매칭에 쓴다.

## 자동 선택 순서 (하네스 `_get_embedder`)
1. **sentence-transformers + bge-m3** — 권장·본실행(품질 최상, KO+EN 혼용 강함). `τ≈0.75`
2. **model2vec 정적 임베딩** — 경량·키리스 데모(torch 불필요, 초경량·빠름). `τ≈0.35`
3. 둘 다 없으면 **문자 3-gram 코사인** fallback(근사). `τ≈0.45`

## 설치

### A. 본실행용 — bge-m3 (권장)
```bash
pip install sentence-transformers        # torch 포함(수백MB~), 모델 최초 다운로드 ~2.3GB
# 최초 1회 다운로드(캐시됨). 오프라인 환경이면 미리 받아 HF 캐시에 두기.
```
설치만 하면 하네스가 자동으로 `EMBED_MODEL=BAAI/bge-m3`로 사용. 임계는 `EMBED_TAU`(기본 0.75).

### B. 키리스 데모용 — model2vec (초경량, torch 불필요)
```bash
pip install model2vec                     # 정적 임베딩, torch 불필요, 수십MB
```
하네스가 sentence-transformers가 없으면 자동으로 `EMBED_MODEL_M2V=minishlab/potion-multilingual-128M` 사용. 임계는 `EMBED_TAU_M2V`(기본 0.35).

## 이 환경에서 실측 확인 (키리스)
- 설치: `pip install model2vec` 성공(torch 불필요).
- CFL-08 consensus: **char3gram fallback 0.25 → model2vec 임베딩 0.5** 로 상승.
- 개별 유사도(정적 임베딩):
  - "인지 후 72시간 내 통지 개시" ~ "규제기관 72시간 내 통지 수용" = **0.606** (매칭)
  - "격리 유지" ~ "표적 계정 격리+모니터링 수용" = **0.365** (fallback은 0.0로 놓침 → 임베딩이 잡음)
  - "증적 무결성 보존" ~ "범위 특정 최소 조사기간" = **-0.02** (무관 → 정확히 배제)
- → 어휘 매칭이 놓치는 의미적 동치를 임베딩이 잡는다는 점이 실증됨.

## 임계(τ) 캘리브레이션 — 모델마다 다름
- 절대 코사인값의 스케일이 모델마다 달라(bge-m3 高, 정적 임베딩 低) **임계는 반드시 모델별로 보정**한다.
- 권장 절차: consensus 항목쌍 10~20개를 사람이 "동치/비동치"로 라벨 → 유사도 분포에서 F1 최대 지점을 τ로 채택 → 부록에 τ와 근거 기록.
- 환경변수로 조정: `EMBED_TAU`(bge-m3) / `EMBED_TAU_M2V`(model2vec) / `FALLBACK_TAU`(char3gram).

## 오프라인(폐쇄망) 사용
- 모델 최초 다운로드는 HuggingFace 접속 필요. 폐쇄망이면 미리 받아 캐시 디렉터리(`HF_HOME`)에 넣고 `HF_HUB_OFFLINE=1` 설정.

## 실행 예 (키리스)
```bash
pip install model2vec
LLM_BACKEND=offline python run_harness.py --phase 1 --scenario CFL-08   # 임베딩 consensus 자동 사용
```

## 정리
- **키리스 데모**: model2vec (설치 한 줄, torch 불필요) → 실제 의미매칭 consensus 확인.
- **본실행**: bge-m3 (sentence-transformers) → 최고 품질, `τ` 캘리브레이션 후 사용.
- 하네스 코드 수정 불필요 — 설치된 라이브러리를 자동 감지·전환.
