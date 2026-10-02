# 하네스 개선 기록 (2026-09-27)

세션 내 2회 재현에서 드러난 진단(조건 A가 M1 상충식별에서 반복 열위)을 바탕으로, **시나리오(TC)는 건드리지 않고** 하네스의 측정 공정성만 개선했다. 모든 변경은 A·B·C에 **대칭 적용**되어 요인통제(격리만 다름)를 훼손하지 않는다.

## 문제 진단
1. **조건 간 상충필드 스키마 비대칭(교란).** 최종 스키마가 A=`resolved_conflicts`, B=`conflicts_identified`, C=상충필드 없음 이었다. judge.py의 `normalize()`는 `conflicts_identified`만 추출 → 정규화 후 **A·C는 상충정보가 통째로 누락**되어 M1(상충식별)에서 부당 감점되는 구조. (앞서 제거한 risk_owner 비대칭과 동종 문제)
2. **3축 보존 미강제.** 중재자·자기중재 종합 시 법·기술·운영 3축 중 일부를 압축·누락 → M1 하락.

## 변경 사항 (run_harness.py, judge.py)
1. **상충필드 통일:** A(MEDIATOR_FINAL_SCHEMA)·B(B_STEP3)·C(C_SELFMED) 최종 스키마를 모두 `conflicts_identified:[{"axis":"legal|technical|operational", ...}]` 로 통일. C에는 상충필드를 신설.
2. **3축 필수규칙 대칭 삽입:** 세 최종 스키마에 "법·기술·운영 3축을 각각 최소 1개씩 누락 없이 포함(해당 없으면 근거와 함께 '해당 없음')" 규칙 동일 삽입.
3. **시스템 프롬프트 대칭 강화:** SYSTEM_MEDIATOR·SYSTEM_UNIFIED_3ROUND·SYSTEM_UNIFIED_3STEP 각각에 "종합 시 3축 상충을 압축·병합·누락하지 말고 최종 결정문에 보존" 클로즈를 동일 취지로 삽입.
4. **judge.py normalize 하위호환:** 구 스키마(A의 `resolved_conflicts`)를 `conflicts_identified` 로 폴백 매핑 → 기존 trace 재채점 시에도 A가 손해 안 봄.

## 공정성(요인통제) 보증
- 모든 변경은 A·B·C에 동일하게 적용 → A vs C(역할분리)·B vs C(형식) 비교에 새 편향을 넣지 않음.
- 시나리오 세트(scenarios_min.json)는 **불변**. 사전등록·재현성 유지.

## 백업
- 원본: `run_harness.py.bak`, `judge.py.bak` (동일 폴더).

## 본실행 시 기대 효과
- A·C의 상충정보가 정규화에서 보존되어 **M1 측정의 조건 간 공정성 확보**.
- 중재자/자기중재가 3축을 보존하도록 강제되어, in-session 진단에서 본 "M4↑/M1↓ 상쇄" 중 **M1 하락분이 완화**될 가능성. (효과 방향은 본실행에서 확증)

---

# 분석 집계 수정 (2026-10-01) — 중간 반올림 제거

외부 3차 검토(T01)에서, 보고된 평균차 0.193/0.137이 1/3/5 균등평균 격자와 맞지 않는 원인이 **집계 단계의 중간 반올림**임을 확인했다.

## 원인
- `judge.py`의 `_aggregate_points`가 각 지표의 **심판 평균을 `round(mean, 2)`로 저장**했고, `analyze.py`가 이 반올림된 aggregate를 그대로 합산했다.
- 균형자료에서 3단계 평균은 전체 평균과 같아야 하나, 중간 반올림이 CFL-04·CFL-09의 **정확한 동률(0)을 약 −0.003으로 변질**시켰다. 그 결과 A−C 부호분할이 4/4/0 → 4/2/2로, Cliff δ가 0.22 → 0.30으로 바뀌었다.

## 변경
1. **`analyze.py`:** 복합점수 S를 **심판 원점수(`scores`)에서 직접 무반올림 집계**하도록 변경. 부호검정과 Cliff δ는 **1e−9 허용오차**로 대응차를 동률 처리해 정확한 동률을 보존. 반올림은 **표 출력 시점에만** 적용.
2. **`judge.py`:** `_aggregate_points`가 지표 평균을 **전정밀로 저장**(참고용; 집계는 analyze.py가 원점수에서 수행).
3. **재생성:** `outputs/confirm_v2/eval/analysis.json`, `outputs/confirm_v2/rubric_sensitivity/q03_analysis.json`.

## 영향
- 주 대비: A−C 평균 **+0.194**, δ **0.297**, 부호검정 p 0.344(Holm 0.688), TOST p **0.0027**; B−C 평균 **+0.139**, δ **0.188**, TOST p **0.0025**. **±1.0 동등성 결론은 불변.**
- Q03(수정 루브릭) 데이터에서 GPT-5.1 응답 5건 미파싱(319/324) → 해당 답변은 2심판 평균; 2완전심판 민감도(A−C 0.000, B−C −0.167)도 동등.

## 검증 스크립트
- `reproduce/reanalyze_noround.py` — 원점수에서 무반올림으로 두 대비의 전 통계를 재생성(원래/수정 평가, 2완전심판 민감도 포함).

## 백업
- 원본: `harness/analyze.py.bak_tost`, `harness/judge.py.bak*` (원본 작업 폴더 기준).
