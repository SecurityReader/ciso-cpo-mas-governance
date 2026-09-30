#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
offline 응답 생성기 (키리스 전 라운드 채움, 병합 방식).
- 시나리오별 '결정 프로파일'에서 R1~R3 / Step1~3 / C라운드 / Phase2 4단계까지 실내용으로 확장.
- 병합: 기존 파일에 이미 있는 태그(손으로 채운 CFL-05/08 등)는 보존하고, 빠진 태그만 채움.
주의: 저자 생성 '예시'로 파이프라인 검증용이며 실제 연구 결과가 아니다.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "offline_responses"; OUT.mkdir(exist_ok=True)
scen = {s["scenario_id"]: s for s in json.loads((BASE/"scenarios_min.json").read_text('utf-8'))["scenarios"]}

# 결정 프로파일(핵심 필드). CFL-05/08은 phase1 손작성본 보존, 여기선 P2 및 빠진 태그 보강용.
P = {
 "CFL-01": {"decision":"전직원 이메일 본문 상시 자동스캔은 도입하지 않는다. 사전 고지·동의 및 목적·범위를 특정한 한정적 룰기반 탐지(첨부·외부전송 메타데이터)로 대체하고, 본문 열람은 승인 시에만 예외 허용한다.","status":"CONDITIONAL_APPROVE","conflicts":["통신비밀보호 vs 내부자탐지","본문 자동열람 오탐 사생활 침해"],"sec":["첨부·외부전송 메타데이터 탐지","DLP 룰 한정","승인 기반 예외 열람"],"priv":["사전 고지·동의","목적·범위 특정","열람 로그 감사","본문 상시열람 금지"],"rr":{"security":"medium","privacy":"medium"},"bias":"balanced","ciso_conc":["본문 상시 자동열람 포기","메타데이터 중심 탐지 수용"],"ciso_nn":["첨부·외부전송 탐지 유지"],"cpo_conc":["승인 기반 예외 열람 수용"],"cpo_nn":["사전 고지·동의 없는 본문 열람 금지","목적·범위 특정"]},
 "CFL-02": {"decision":"비식별화 없는 실고객데이터 직접 학습 불허. 가명·합성데이터로 1차 학습, 재식별 위험평가 통과 시 보안구역에서 최소범위 원본 예외 사용.","status":"CONDITIONAL_APPROVE","conflicts":["탐지 정확도 vs 목적외이용","원본 학습 재식별 위험"],"sec":["보안구역 내 학습","접근권한 최소화","학습데이터 보존기간"],"priv":["가명·합성 우선","재식별 위험평가","목적 범위 제한"],"rr":{"security":"medium","privacy":"medium"},"bias":"privacy","ciso_conc":["가명·합성 1차 학습 수용"],"ciso_nn":["성능검증 위한 제한적 원본 예외"],"cpo_conc":["위험평가 통과 시 보안구역 최소 원본 예외 수용"],"cpo_nn":["재식별 위험평가 필수","목적외 광범위 사용 금지"]},
 "CFL-04": {"decision":"IP·위치·단말·행동 결합 이상탐지 도입하되 자동 계정잠금은 고위험 신호 한정, 오탐 구제(재인증·이의절차) 의무화, 프로파일링 고지·최소보존 병행.","status":"CONDITIONAL_APPROVE","conflicts":["이상탐지 vs 프로파일링 규제","오탐 대량잠금"],"sec":["결합 이상탐지","고위험 한정 자동조치","이상징후 로깅"],"priv":["프로파일링 고지","오탐 구제·이의절차","신호 최소보존"],"rr":{"security":"medium","privacy":"medium"},"bias":"balanced","ciso_conc":["자동잠금 고위험 한정 축소"],"ciso_nn":["결합 이상탐지 유지"],"cpo_conc":["고위험 한정 자동조치 수용"],"cpo_nn":["프로파일링 고지","오탐 구제절차 필수"]},
 "CFL-05": {"decision":"생체 거부권 없는 필수화 배제. FIDO2 보안키 기본 + 생체 선택(단말 보관·서버 미전송), 거부자 동등 대체수단·불이익 금지.","status":"CONDITIONAL_APPROVE","conflicts":["강력인증 vs 특수범주 강제수집","생체DB 침해 재발급 불가"],"sec":["FIDO2 기본","고위험 다요소 상향","키관리 강화"],"priv":["생체 선택·별도 동의","단말 보관·서버 미전송","거부 불이익 금지"],"rr":{"security":"medium","privacy":"medium"},"bias":"balanced","ciso_conc":["생체 필수화 철회"],"ciso_nn":["FIDO2 강력인증 적용"],"cpo_conc":["단말보관 전제 생체 선택 수용"],"cpo_nn":["실질 거부권","생체 서버전송 금지"]},
 "CFL-06": {"decision":"동의 없는 상시 국외이전 불가. 국내 1차 관제·가명화 후 최소 로그만 SCC 기반 이전, 별도 고지·동의·수사기관 대응절차.","status":"CONDITIONAL_APPROVE","conflicts":["관제 효율 vs 국외이전 규제","해외 수사기관 접근"],"sec":["국내 1차 관제","전송구간 암호화","이전 로그 최소화"],"priv":["별도 고지·동의","SCC·적정성","가명화 후 이전","수사기관 대응절차"],"rr":{"security":"medium","privacy":"high"},"bias":"privacy","ciso_conc":["전량 상시 이전 포기"],"ciso_nn":["24h 관제 연속성"],"cpo_conc":["가명화·최소범위 이전 수용"],"cpo_nn":["국외이전 별도 동의","동의없는 상시이전 금지"]},
 "CFL-08": {"decision":"전면차단·무기한 비공개 배제. 취약 계정 표적 격리+핫픽스 후 72h 내 단계적 통지.","status":"CONDITIONAL_APPROVE","conflicts":["즉시차단 vs 비공개패치","통지 시점"],"sec":["표적 계정 격리","레이트리밋","핫픽스","증적 보존"],"priv":["범위 특정","72h 내 신고·통지","재발방지 문서화"],"rr":{"security":"medium","privacy":"medium"},"bias":"balanced","ciso_conc":["전면차단 대신 표적 격리"],"ciso_nn":["패치 전 격리 유지"],"cpo_conc":["표적 격리 수용"],"cpo_nn":["72h 내 통지 개시"]},
 "CFL-09": {"decision":"개인정보 포함 로그 외부 즉시 제공은 위탁계약·최소범위·가명화 전제로만 허용, 계약 미비 시 비식별 요약본 우선.","status":"CONDITIONAL_APPROVE","conflicts":["신속 대응 vs 제3자제공","재위탁·목적외"],"sec":["최소범위 제공","대응 신속성"],"priv":["위탁계약","가명화·요약 우선","재위탁 금지"],"rr":{"security":"medium","privacy":"medium"},"bias":"balanced","ciso_conc":["가명화·최소범위 제공 수용"],"ciso_nn":["대응 지연 최소화"],"cpo_conc":["계약 전제 최소범위 제공 수용"],"cpo_nn":["위탁계약 필수","재위탁·목적외 금지"]},
 "CFL-10": {"decision":"상담녹취 5년 일괄보존 과도. 분쟁 개연성 건만 분리 암호화 연장, 일반 녹취는 법정기간 후 파기.","status":"CONDITIONAL_APPROVE","conflicts":["증거보존 vs 최소보유","장기보관 유출 확대"],"sec":["분쟁건 분리 암호화","접근통제"],"priv":["일반 녹취 법정기간 후 파기","연장 사유·범위 특정"],"rr":{"security":"low","privacy":"medium"},"bias":"privacy","ciso_conc":["전건 5년 보존 포기"],"ciso_nn":["분쟁건 증거보존"],"cpo_conc":["분쟁건 한정 연장 수용"],"cpo_nn":["일반 녹취 최소보유·파기"]},
 "IND-01": {"decision":"L7 DDoS 시 레이트리밋·챌린지 우선, 확증된 악성 대역만 한시 차단, 정상 트래픽 오차단 모니터링.","status":"APPROVE","conflicts":["가용성 확보(단일 도메인)"],"sec":["레이트리밋","챌린지 완화","악성대역 한시 차단","오차단 모니터링"],"priv":[],"rr":{"security":"low","privacy":"low"},"bias":"security","ciso_conc":[],"ciso_nn":["서비스 가용성 유지"],"cpo_conc":[],"cpo_nn":[]},
 "IND-07": {"decision":"보유기간 만료 개인정보 자동삭제·검증 도입, 삭제 로그·검증 리포트, 법정 보존 예외 분리.","status":"APPROVE","conflicts":["파기의무 이행(단일 도메인)"],"sec":["삭제 로그 무결성"],"priv":["만료 자동삭제","삭제 검증 리포트","법정 보존 예외 분리"],"rr":{"security":"low","privacy":"low"},"bias":"privacy","ciso_conc":[],"ciso_nn":[],"cpo_conc":[],"cpo_nn":["보유기간 만료 파기"]},
 "COL-02": {"decision":"모의침투+PIA 통합 승인관문 운영하되 보안·개인정보 체크리스트 분리 유지·상호 서명으로 이중검증 실효성 유지.","status":"APPROVE","conflicts":["절차 통합 시 이중검증 약화 우려"],"sec":["모의침투 통과 기준","보안 체크리스트"],"priv":["PIA 통과 기준","개인정보 체크리스트"],"rr":{"security":"low","privacy":"low"},"bias":"balanced","ciso_conc":["통합 관문 참여"],"ciso_nn":["보안 체크리스트 독립 유지"],"cpo_conc":["통합 관문 참여"],"cpo_nn":["PIA 체크리스트 독립 유지"]},
 "COL-06": {"decision":"개발·테스트는 가명·합성데이터 기본, 원본 필요 시 예외 승인·마스킹·접근통제 의무화.","status":"APPROVE","conflicts":["테스트 현실성 vs 원본 사용 위험(협업 해소)"],"sec":["테스트망 접근통제","예외 승인 통제"],"priv":["가명·합성 기본","원본 마스킹","예외 최소화"],"rr":{"security":"low","privacy":"low"},"bias":"balanced","ciso_conc":["가명·합성 기본 수용"],"ciso_nn":["테스트 유효성 확보"],"cpo_conc":["예외 승인 시 원본 제한 사용 수용"],"cpo_nn":["원본 무통제 사용 금지"]},
}

def final(label, sid, p):
    return {"experiment_condition":label,"scenario_id":sid,"final_decision":p["decision"],
            "decision_status":p["status"],"conflicts_identified":[{"issue":c} for c in p["conflicts"]],
            "required_controls":{"security":p["sec"],"privacy":p["priv"]},
            "residual_risk":p["rr"],"bias_direction":p["bias"],"confidence":0.75}

def full_tags(sid, p):
    sev = "HIGH" if p["status"]=="CONDITIONAL_APPROVE" else "MEDIUM"
    ciso_r1={"role":"CISO","round":1,"position":"보안 관점: "+p["decision"][:60],"key_risks":[c for c in p["conflicts"]],"severity":sev,"required_controls":p["sec"],"question_to_counterpart":["대체·완화수단으로 목적 달성이 가능한가?"],"confidence":0.7}
    cpo_r1={"role":"CPO","round":1,"position":"프라이버시 관점: 최소수집·비례성 우선","key_risks":[c for c in p["conflicts"]],"data_sensitivity":"HIGH","required_controls":p["priv"],"question_to_counterpart":["보안 목적을 덜 침습적으로 달성할 수 있는가?"],"confidence":0.72}
    ciso_r2={"role":"CISO","round":2,"answer_to_counterpart":"완화·대체수단을 우선 적용하되 핵심 통제는 유지한다.","agreement_points":p["priv"][:1],"underestimated_risks":["대체수단 미비 시 보안 공백"],"alternatives":p["sec"][:2],"new_question":["잔여위험 책임 주체는?"],"revised_position":"조건부 통제 유지","confidence":0.74}
    cpo_r2={"role":"CPO","round":2,"answer_to_counterpart":"목적 범위·최소화·고지를 전제로 조건부 수용한다.","agreement_points":p["sec"][:1],"underestimated_risks":["형식적 통제의 실효성 부족"],"alternatives":p["priv"][:2],"new_question":["감사·구제 절차는?"],"revised_position":"조건부 수용","confidence":0.75}
    ciso_r3={"role":"CISO","round":3,"concessions":p["ciso_conc"],"non_negotiable":p["ciso_nn"],"acceptable_policy":"조건부 수용","residual_risk":"medium","final_stance":"CONDITIONAL_ACCEPT","confidence":0.77}
    cpo_r3={"role":"CPO","round":3,"concessions":p["cpo_conc"],"non_negotiable":p["cpo_nn"],"acceptable_policy":"조건부 수용","residual_risk":"medium","final_stance":"CONDITIONAL_ACCEPT","confidence":0.78}
    A={"A.ciso.r1":ciso_r1,"A.cpo.r1":cpo_r1,"A.ciso.r2":ciso_r2,"A.cpo.r2":cpo_r2,"A.ciso.r3":ciso_r3,"A.cpo.r3":cpo_r3,"A.med":final("A_SEPARATED_3ROUND",sid,p)}
    B={"B.s1":{"step":1,"security_view":{"goal":p["sec"][0] if p["sec"] else "보안 목적","threats":p["conflicts"],"severity":sev,"min_data_need":"최소","confidence":0.72},"privacy_view":{"principle":"최소수집·비례성","sensitivity":"HIGH","subject_rights_risk":p["conflicts"][0],"proportionality":"대체수단 우선","confidence":0.73},"need_legal_check":["관련 조항 확인"]},
       "B.s2":{"step":2,"conflict_matrix":[{"issue":c,"security_gain":"보안 이익","privacy_loss":"프라이버시 위험","level":"HIGH"} for c in p["conflicts"]],"hard_constraints":["법적 최소요건 준수"],"self_check":{"if_security_first":"프라이버시 위험 증가","if_privacy_first":"보안 공백 위험"},"mitigations":p["sec"][:1]+p["priv"][:1]},
       "B.s3":final("B_UNIFIED_3STEP",sid,p)}
    C={"C.r1":{"round":1,"perspectives":{"ciso":{k:ciso_r1[k] for k in ("position","key_risks","severity","required_controls","question_to_counterpart","confidence")},"cpo":{"position":cpo_r1["position"],"key_risks":cpo_r1["key_risks"],"sensitivity":"HIGH","required_controls":cpo_r1["required_controls"],"question_to_counterpart":cpo_r1["question_to_counterpart"],"confidence":cpo_r1["confidence"]}}},
       "C.r2":{"round":2,"perspectives":{"ciso":{k:ciso_r2[k] for k in ("answer_to_counterpart","agreement_points","underestimated_risks","alternatives","new_question","revised_position")},"cpo":{k:cpo_r2[k] for k in ("answer_to_counterpart","agreement_points","underestimated_risks","alternatives","new_question","revised_position")}}},
       "C.r3":{"round":3,"perspectives":{"ciso":{"concessions":p["ciso_conc"],"non_negotiable":p["ciso_nn"]},"cpo":{"concessions":p["cpo_conc"],"non_negotiable":p["cpo_nn"]}}},
       "C.med":final("C_UNIFIED_3ROUND_FORMAT",sid,p)}
    tags={}; tags.update(A); tags.update(B); tags.update(C)
    # Phase2 (해당 시나리오만): 4단계 대응
    if scen.get(sid,{}).get("phase2"):
        chs=scen[sid].get("phase2_challenges",[])
        for cond in ("A","B","C"):
            for ch in chs:
                tags[f"P2.{cond}.{ch['step']}"]={"action":"정책 유지하며 표적 대응(전면조치 회피)","rationale":f"{ch['pressure']} 상황에서도 최소침해·법적요건 우선","new_controls":p["sec"][:1]+p["priv"][:1],"residual_risk":p["rr"],"info_needed":["추가 사실관계 확인"],"confidence":0.65}
    return tags

def merge(sid, newtags):
    f = OUT / f"{sid}_{{}}.json"
    # 조건별 파일로 분리 저장
    by={"A":{}, "B":{}, "C":{}}
    for t,v in newtags.items():
        cond = t.split(".")[1] if t.startswith("P2.") else t.split(".")[0]
        by[cond][t]=v
    for cond,tags in by.items():
        p = OUT / f"{sid}_{cond}.json"
        cur = json.loads(p.read_text('utf-8')) if p.exists() else {}
        added=0
        for t,v in tags.items():
            if t not in cur:            # 기존(손작성) 보존, 빠진 것만 채움
                cur[t]=v; added+=1
        p.write_text(json.dumps(cur,ensure_ascii=False,indent=2),encoding="utf-8")
    return

n=0
for sid,p in P.items():
    merge(sid, full_tags(sid,p)); n+=1
print(f"merged/filled full-round offline responses for {n} scenarios → {OUT}")
