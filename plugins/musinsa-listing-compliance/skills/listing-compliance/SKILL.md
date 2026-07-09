---
name: "listing-compliance"
description: "무신사 입점·운영 상품의 표시정보(상품명·소재/혼용률·원산지·친환경 표현·이종기관 시험성적서)를 무신사 그린워싱 가이드·표시광고법·성적서에 대조해 위반을 탐지·재판정하고 준법 표기/카피·반려 사유서·이의제기 재심사 메모·셀러 응대 초안을 생성한다. 등록·상세 수정·시즌 갱신·정책(룰) 갱신 시 전 코퍼스 소급 재스캔, 그린워싱 진화표현(신조어 변형) 의미 판단, 성적서↔상품↔클레임 정합성(정상/부분커버/불일치/외래키불명) 매칭 검수 요청 시 사용."
---

# Listing Compliance — 표시정보 상시 컴플라이언스 에이전트

표시정보 클레임(혼용률·원산지·친환경 표현)의 증빙 정합성과 진화하는 표현 위반을, **변경 이벤트(등록·수정·시즌 갱신·정책 갱신)마다** 교차참조·판정·문서화한다. 단순 탐지가 아니라 **정정 + 출력단 3종 초안**까지 생성한다(린터 아님).

**권위 사본**: 규칙·파라미터·렉시콘·임계는 `rules/ruleset.json`에 있다(15룰·layer·`fuzzy_link.min_confidence`·`certifier_whitelist`·`lexicons`·`match_status_taxonomy`). 이 SKILL은 절차 지시문이고, **수치/표현 목록은 항상 ruleset.json을 로드해 사용**한다(여기에 박제하지 않는다).

**비목표**: 자동 게시·발송 없음. 모든 정정·문서는 **제안**이며 `reviewed_by="human-MD-required"`. BLOCK은 "게시 보류 권고"(자동 차단 아님). OCR·이미지 유사도는 비목표(성적서는 구조화 JSON으로 입력). 의미 추론은 외부 임베딩 API가 아니라 **너(Codex) 자신**이 수행한다.

---

## 0. 시작: ruleset 로드 + 규칙 ID 바인딩
먼저 `rules/ruleset.json`을 읽어 `rules`, `parameters`, `lexicons`, `match_status_taxonomy`, `evidence`(E1~E6 근거 URL)를 메모리에 올린다. 모든 위반은 `evidence`의 공개 URL로 추적 가능해야 한다(비공개·미검증 수치 단정 금지).

**규칙 ID 바인딩(위조 금지·필수)**: 로드 후 `rules[].id` 집합(예: `GW-01`…`TS-02`)을 확정한다. 출력의 **모든 `rule_id`·「규칙 ID」·검증 푸터 `rule_ids_used`는 이 집합의 값만** 쓴다 — `LC-*`·`ENV-*` 같은 **즉석 ID를 새로 만들지 않는다**. ruleset을 읽지 못하면 규칙 ID를 지어내지 말고 리포트 §0에 "규칙셋 미로드 — 확정 판정 불가"로 명시하고 결정론 판정을 중단한다(에이전트 표면 후보만 상정 가능).

## 1. 입력 정규화 (§3)
입력은 두 모드. 자유 텍스트나 **상품 등록/상세 화면 캡처 이미지**로 와도 표시정보(상품명·브랜드·소재/혼용률·원산지·가격·카피·태그)를 추출해 아래 스키마로 정규화한 뒤 심사한다(예시: `sample/input.product.png`). 단, **시험성적서만은 이미지가 아니라 구조화 JSON**으로 받는다(§0 OCR 비목표 — 수치 판정 신뢰성). 캡처에 성적서가 없으면 TC/MX 증빙 규칙은 "성적서 미첨부" 기준으로 평가하고, 성적서 JSON이 별도로 오면 합쳐서 심사한다. **폴백**: 검수 대상 입력이 주어지지 않으면(예: "이 상품 검수해줘"처럼 대상 없이 트리거된 경우) 플러그인 루트의 `sample/input.product.json`을 로드해 시연하고, 리포트 서두에 **번들 샘플 시연**임을 명시한다(실데이터 검수와 혼동 방지).
- **단건(§3.2)**: `{product_id, product_name, brand, is_own_brand?, category, price_krw, origin?, style_no?, material_claims[{part,material,percent}], tags[]?, marketing_copy?, premium_material_claims[{brand,material}]?, test_certificates[]?}`. `mode:"single"`.
- **재스캔(§3.4)**: `{mode:"rescan", policy_update{added_rules[{id,delta,basis,severity,effective_date}], note}, corpus[ <단건 객체 배열> ]}`. 갱신 룰을 전 코퍼스에 소급 적용한다.
- **이종기관 성적서(§3.3)**: `test_certificates[]` = `{issuer, cert_no, product_ref?, issued_date, tested_part?, tested_composition[{material,percent}], issuer_fields_raw?}`. **기관마다 필드명·단위·소재명칭·포맷이 다르고 `product_ref`가 없을 수 있다** → 정규형으로 매핑(출처 `issuer_fields_raw` 추적)한 뒤 매칭한다.
- `marketing_copy`/`product_name`/`tags`에서 환경성 표현·소재 주장·생산국 연상어를 추출한다.

## 2. 2계층 탐지 (§5)
판정은 두 층. **(a) 결정론 바닥**은 동일 입력→동일 결과(하드게이트). **(b) 에이전트 표면**은 신뢰도+근거를 달아 사람에게 상정(하드 BLOCK 아님).

### 2a. 결정론 바닥 — 하드게이트 (§5.2)
1. **등재 규칙 결정론 평가**: ruleset에 **등재된** 금지표현(GW 알려진 표현·GW-04)과 전처리 구조검사(MX-02 part별 혼용률 합계≠100 / TC-03 product_ref·발급일 / OR-01 origin 누락)를 평가. **GW-01은 GW-02 합성어에 포함되지 않은 독립 환경성 표현**(별도 '친환경'/eco 단어·#친환경 태그 등)이 입증 없이 있을 때만 격발한다 — 환경성 신호가 전부 GW-02 합성어 안에만 있으면 GW-01 아님(GW-02만). '키워드 발화'가 아니라 '구분'으로 격발.
2. **성적서 정합성 4분류(`match_status`)** — **부위(part)별로** `material_claims`를 성적서 `tested_composition`과 **소재명칭·단위 정규화 후 수치 비교**해 산출(`match_status`는 **조성 커버리지만** 판단; 프리미엄 브랜드 증빙 부재는 TS-01로 별도 처리이지 match_status 강등 아님):
   - `정상(match)`: 그 부위 클레임 소재·함량이 성적서와 일치(허용오차 내).
   - `불일치(mismatch)`: 클레임 소재가 성적서에 **없거나** 함량 편차가 허용오차 초과(=MX-01 허위기재). 예: 안감 캐시미어/폴리 주장인데 성적서 아크릴100 → **불일치**.
   - `부분커버(partial)`: 그 부위·소재를 커버하는 성적서가 **미첨부/스코프 밖**(클레임≠성적서 모순은 아님). 고급소재 부위 성적서 누락=MX-03.
   - `외래키불명(unlinked)`: `product_ref` 부재 + 퍼지 신뢰도 임계 미만(에이전트 표면 §2b-3).
   평가 규칙: MX-01(불일치)·MX-03(부분커버/고급소재 미증빙)·MX-04(충전재 편차 `parameters.MX-04.tolerance_pp` ±5%p 초과)·TC-01(성적서 0건)·TC-02(비공인 발급기관=`certifier_whitelist` 밖).
3. **택갈이·프리미엄**: TS-01(프리미엄 브랜드 주장+근거 미첨부), TS-02(`price_krw ≥ parameters.TS-02.price_threshold_krw` + 저가 생산국 + 프리미엄 주장) 임계 평가.
4. 각 위반 기록: `{rule_id, severity, layer, part, claimed, observed, match_status, basis_url, message}`. **모든 평가된 기둥 B 부위의 match_status를 `match_status_by_part{part:status}`에 채운다(정상 부위 포함).**
5. **verdict 집계**: BLOCK≥1 → **BLOCK** / (BLOCK=0, WARN≥1) → **WARN** / 위반 0 → **PASS**. (외래키불명·변형후보는 에이전트 표면 상정이라 verdict 격상 안 함 — 조성 모순 없으면 PASS 가능.)

### 2b. 에이전트 표면 — 자문·상정 (§5.3)
1. **진화표현 변형후보 의미탐지**: ruleset **미등재** 신조어·변형(친환경 인상을 주는 합성 신조어를 `lexicons`의 등재 표현·금지개념과 대조해 추론)을 GW 금지개념(석유화학 합성소재≠친환경)의 변형으로 **의미추론** → `review_candidates[]`에 `{text, matched_concept, confidence, evidence_quote, proposed_rule, verdict_layer:"agent_surface"}` 산출(근거 문장 인용 필수). 하드 BLOCK 아님 → "다음 룰 갱신 후보". (정답 신조어를 SKILL에 박제하지 않는다 — 의미추론으로 발견.)
2. **소급 재스캔(§3.4)**: 정책갱신 재스캔은 **`policy_update.added_rules`의 룰 패밀리(예: GW)·BLOCK 심각도로 한정**해 전 코퍼스를 재평가한다 — 갱신 룰이 **새로 잡는** listing을 flag하고 그 패밀리의 **BLOCK 위반만** 보고한다(전처리·기둥 B·WARN(GW-03 등)은 정책갱신 재스캔 범위 밖 — 전수검수가 아니라 '갱신 룰이 닿는 것'). 새로 등재된 표현은 (a) 결정론 바닥 BLOCK으로 끌어올리고(**자사 PB 포함**), 미등재 변형은 (b) 후보로 상정(BLOCK 격발 listing이 0이면 flag 아님 → review_candidate만). `rescan_summary{flagged_listings[], own_brand_flagged, passed[]}` 산출. `is_own_brand:true`가 플래그되면 `own_brand_flagged=true`.
3. **성적서 퍼지매칭 경계건**: `product_ref` 부재 시 (브랜드+품번+소재+부위) 퍼지매칭 신뢰도 산출, `parameters.fuzzy_link.min_confidence`(0.7) 미만은 `match_status='외래키불명'`으로 상정(경계건 사람 확인).

> **결정론 범위(§5.5)**: 동일 입력→동일 규칙 ID 세트·동일 판정·동일 match_status는 **(a) 결정론 바닥에만** 강제한다. (b) 변형후보·퍼지매칭 신뢰도는 결정론을 강제하지 않는다(골든 존재검증+judge로 측정).

## 3. 생성 — 정정 + 출력단 3종 (§6)
모든 BLOCK/WARN에 정정안과 출력단 초안을 **생성**한다(모두 제안, `reviewed_by="human-MD-required"`). **각 correction은 머신리더블 `type` 영문 enum과 `rule_id`를 반드시 단다** — `type ∈ {"material_label","copy","tag","missing_info"}`(한국어 라벨 금지), `rule_id`=대응 위반 규칙 ID(모든 BLOCK/WARN rule_id가 ≥1 correction으로 커버돼야 함).
- **표기 정정 → `type:"material_label"`(§6.1)**: 허위 혼용률·소재를 **성적서 측정값 기준**으로 재작성(before→after, `cert_no` 인용).
- **카피 재작성 → `type:"copy"`(§6.2)**: 근거 없는 환경성·성능 표현 제거/완화(before→after). 환경성 표현은 근거 인증 있을 때만 유지.
- **태그 정정 → `type:"tag"`(§6.3)**: 위반 해시태그(#에코레더 등) 삭제 권고.
- **누락 표시정보 → `type:"missing_info"`(§6.4)**: 원산지 미표기·필수 성적서 누락·부분커버 미커버 부위 보완 요청.
- **심사 로그(§6.5)**: §7.3 JSON 로그 적재(재현 가능).
- **출력단 3종**(같은 파이프라인의 출력 레이어 — A·B 판정을 그대로 흘림):
  - **반려 사유서(§6.6)**: 위반필드·규정조항·누락증빙·시정 체크리스트를 인용한 셀러맞춤 반려 통지문 초안.
  - **이의제기 재심사 메모(§6.7)**: 소명/재제출 시 원심사 근거 + 신규 증빙을 소환·대조하고 다툼 필드 delta 하이라이트.
  - **셀러 응대(§6.8)**: "왜 반려/판매중지됐나"에 어느 표시값·어느 규정·필요 증빙·재개 조건을 1차 응답하는 초안.

### 3.5 법적근거 인용·검증 (MCP 검증층 §13 — 있으면 강화, 없으면 폴백)
**판정 후 출력단 작성 전에 반드시 도구 가용 여부를 확인한다** — 도구 목록에 `mcp__compliance_kb.*`(search_legal_basis 등)가 보이는지 실제로 본다. 추정으로 건너뛰지 마라. 가용하면 아래를 생략 없이 수행한다(키·네트워크 0, 오프라인):
- 각 BLOCK/WARN → `search_legal_basis(위반 요지)`로 근거 조문·심사지침을 **provenance_url과 함께** 인출해 **반려 사유서(§6.6)에 인용**한다.
- 그린워싱 건 → `get_ftc_precedent(위반)`로 유사 공정위 의결례를 첨부한다.
- 반려 사유서 초안 작성 후 → `verify_citation(초안)`로 인용을 **자가검증**한다. `NOT_FOUND`(환각)면 그 인용을 수정/삭제 후 재검증한다.
- TC/TS → `check_test_lab(발급기관)`·`lookup_trademark(브랜드)`의 인간검증 URL을 사유서에 동반한다.
**우아한 강등**: 도구가 없으면 ruleset `evidence`(E1~E6) URL로 그대로 인용한다(오프라인 결정론 바닥 불변). 근거 데이터는 `kb/`이고 정책(판정)은 여전히 ruleset이 권위다.
**사용 여부를 채팅에 명시**: 채팅 응답에 "법적근거 MCP 검증: 사용(verify_citation 통과)" 또는 "미사용(도구 미노출 — ruleset 공개 URL 인용)" 한 줄을 반드시 넣는다(§5 채팅 응답 4항). 리포트 템플릿·검증 푸터는 변경하지 않는다.

## 4. 출력 포맷 (§7)
**(1) 마크다운 리포트 — 고정 템플릿 필수(§7.1)**: 리포트는 **이 스킬 폴더의 `templates/report.template.md`**(SKILL.md와 같은 디렉토리 하위)를 로드해 **그 골격 그대로** 출력한다. 섹션 제목·번호(0~6)·순서·개수를 바꾸지 않고 `{{...}}` 슬롯만 채운다(섹션 추가·삭제·재배열 금지). 채울 내용이 없는 슬롯은 표 `(없음)` 행·블록 `해당 없음`으로 남긴다. §0 판정요약과 검증 푸터의 「규칙 ID/`rule_ids_used`」는 §0에서 확정한 ruleset `rules[].id`만 쓰고 서로 일치시킨다. 템플릿을 못 읽으면 동일 골격(0.판정요약→1.결정론바닥→2.에이전트표면→3.재스캔→4.정정→5.출력단3종→6.결론+검증푸터)을 재현한다.

**(2) JSON 로그**(§7.3 골격, `logs/`): `{mode, policy_update?, rescan_summary{flagged_listings,own_brand_flagged,passed}, listings[{product_id,is_own_brand,verdict,counts{BLOCK,WARN,INFO},match_status_by_part{part:status},violations[{rule_id,severity,layer,part,match_status,claimed,observed,basis_url,message}],corrections[{type,rule_id,before,after}],drafts{rejection_notice,appeal_memo,seller_reply}}], review_candidates[{text,matched_concept,confidence,evidence_quote,proposed_rule,verdict_layer}], reviewed_by:"human-MD-required"}`. 단건 모드는 `mode:"single"` + 단일 listing. **`match_status_by_part`는 기둥 B 평가 부위 전체(정상 포함)를 채운다**; `correction.rule_id`로 대응 위반을 태깅한다.

> **자증 킬러 데모**: 룰 갱신 한 번 → 무신사가 자사 PB 인조가죽('에코레더')을 소급 BLOCK(`own_brand_flagged=true`). "무신사조차 못 닿았던 자사 제품을 잡는다."

## 5. 채팅 응답 — 판정 옆에 근거를 붙여라
사용자는 리포트 파일을 바로 열어보지 않는다. 채팅 요약이 판정(BLOCK/PASS)만 나열하면 계산이 아니라 복사로 보인다. 채팅 응답에 반드시 포함:
1. **산출 경로 한 줄** — `ruleset.json` 규칙 대조(결정론 하드게이트) + 에이전트 표면 상정으로 나온 판정임을 밝힌다.
2. **판정별 "주장 vs 관측" 대조 1줄 + 규칙 ID** — 예: 안감 '캐시미어 30%' 주장 vs 시험성적서 미첨부 → 해당 규칙 ID로 BLOCK. 값은 방금 생성한 JSON 로그의 `violations[].claimed/observed/rule_id`에서 옮긴다(문서·기대값에서 옮기지 않는다).
3. 재스캔 모드면 **몇 건이 어느 규칙으로 뒤집혔는지** 1줄씩.
4. **법적근거 MCP 검증 사용 여부** 한 줄(§3.5) — "사용(verify_citation 통과)" 또는 "미사용(도구 미노출)".
