"""meditherapy-seeding-screener 결정론 스코어링 엔진 (순수 stdlib).

모듈:
- normalize: 입력 정규화(영상 병합·modality_loss·도메인 바인딩) + canonicalize(§4.4)
- features:  결정론 바닥 피처 추출(§4.3, 100% 재현)
- aggregate: 고정 공식 합산(§5.4, 에이전트 총점 금지·A6)
- report:    §7.1 마크다운 + §7.3 JSON 로그 렌더
- cli:       normalize→features→combine→aggregate→report 결정론 오케스트레이션(SKILL이 shell로 호출)

가중치·블렌드비·D1 배분은 rules/rubric.json 동결값 — 이 코드는 읽기만 한다(SPEC §4.2·§5.4).
네트워크 import 0(자기완결, SPEC §10.3).
"""
