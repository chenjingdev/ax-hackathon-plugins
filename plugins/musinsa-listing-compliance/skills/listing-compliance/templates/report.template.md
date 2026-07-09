<!--
  무신사 표시정보 컴플라이언스 리포트 — 고정 템플릿 (v1)
  ────────────────────────────────────────────────────────────
  이 파일은 출력 리포트의 유일한 골격이다. 스킬은 이 구조를 그대로 복제하고
  {{...}} 슬롯만 채운다. 섹션 제목·번호·순서·개수를 절대 바꾸지 않는다(추가·삭제·재배열 금지).

  · 채울 내용이 없는 슬롯: 표는 `| — | (없음) | | | | | | |` 한 줄, 블록은 `해당 없음`으로 남긴다(섹션 자체를 지우지 않는다).
  · 모든 「규칙 ID」 슬롯에는 rules/ruleset.json 에 실제 등재된 rule.id 만 쓴다. ID를 새로 만들지 않는다(위조 금지).
    ruleset 미등재 표현/개념은 확정 위반이 아니라 §2 에이전트 표면(후보)으로만 적는다.
  · 이 주석(<!-- -->)과 마지막 검증 푸터는 출력에 그대로 유지한다.
-->

# 무신사 표시정보 컴플라이언스 리포트
> 자동 생성 **초안** · 모든 정정·문서는 제안이며 사람(MD) 확정 전 게시·발송 금지 · `reviewed_by: human-MD-required`

## 0. 판정 요약
| 항목 | 값 |
|---|---|
| 리포트 ID | {{report_id}} |
| 검수 모드 | {{mode}} |
| 대상 | {{target_summary}} |
| **최종 판정** | **{{verdict}}** · {{verdict_detail}} |
| 적용 규칙 ID | {{rule_ids_csv}} |
| 근거 데이터 | rules/ruleset.json · evidence E1~E6 (공개 URL) |

> 「적용 규칙 ID」는 ruleset.json 등재 ID만 나열한다. 등재되지 않은 표현/개념은 §2 후보이며 verdict를 격상하지 않는다.

## 1. 결정론 바닥 — 탐지된 위반
| # | listing | 규칙 ID | 심각도 | 부위 | 정합성 | 주장 vs 관측 | 근거 URL |
|---|---|---|---|---|---|---|---|
{{deterministic_violation_rows}}

## 2. 에이전트 표면 — 상정(자문 · 하드 BLOCK 아님)
{{agent_surface_candidates}}

## 3. 소급 재스캔 결과
{{rescan_result}}

## 4. 정정안 (생성 · 제안)
{{corrections}}

## 5. 출력단 초안 (사람 검토·확정)
### 5-1. 반려 사유서
{{rejection_notice}}

### 5-2. 이의제기 재심사 메모
{{appeal_memo}}

### 5-3. 셀러 응대
{{seller_reply}}

## 6. 결론
- 권고: {{conclusion}}

---
<!-- 검증 푸터 — 기계 판독용. 값은 위 본문과 일치해야 한다. rule_ids_used 는 반드시 ruleset.json 등재 ID. -->
```verify
report_id: {{report_id}}
verdict: {{verdict}}
rule_ids_used: {{rule_ids_csv}}
rule_ids_source: rules/ruleset.json
match_status_by_part: {{match_status_by_part}}
own_brand_flagged: {{own_brand_flagged}}
reviewed_by: human-MD-required
```
