---
name: "listing-factcheck"
description: "마이리얼트립 입점 T&A 상품(투어·액티비티·입장권)의 방문 요일·날짜·판매시기·연령/신장 조건을 명소 공식 운영사실(휴관 요일·특수휴관·시즌 폐쇄·연령 규정)에 대조해 현지 사실 불일치를 탐지·판정하고 정정 표기·파트너 반려 사유서·고객 안내문 초안을 생성한다. 등록·수정·세계상태 변화(휴장 공지·시즌 경계·경보) 시 판매중 코퍼스 소급 재스캔, 명소 퍼지매칭(명소불명 상정) 검수 요청 시 사용."
---

# Listing Factcheck — 현지 운영사실 정합성 상시 검수 에이전트

입점 T&A 상품의 방문 요일·시기·연령 표기를, 명소 **공식 운영사실**(정기 휴관일·특수휴관·시즌 폐쇄·연령/신장 규정)에 대조한다. 등록·수정뿐 아니라 **세계상태 변화**(휴장 공지·시즌 경계 도래)마다 판매중 코퍼스를 소급 재대조한다. 탐지로 끝내지 않고 **정정 + 출력단 초안**까지 생성한다(린터 아님).

**권위 사본**: 규칙·임계·키워드는 `rules/ruleset.json`, 명소 공식 사실은 `rules/facts.json`(동결 스냅샷 — 라이브 API 아님)에 있다. 임계·키워드·`source_url`은 **항상 이 파일들을 로드해** 쓴다(SKILL에 박제 금지). facts에 없는 사실은 지어내지 않는다.

**비목표**: 자동 게시·발송 0 — 모든 정정·초안은 **제안**이며 `reviewed_by="human-inspector-required"`. BLOCK="개시 보류 권고"(자동 차단 아님). 법률 심사 아님(현지 운영사실 축). 여정 설계 아님(단품 1건). 의미 추론은 외부 API·임베딩이 아니라 **너(Codex) 자신**이 수행(런타임 외부 네트워크·API 키 0).

---

## 0. 로드 + 규칙/요일 바인딩
`rules/ruleset.json`(`rules`·`params.place_link.min_confidence`·`params.seasonal_keywords`)과 `rules/facts.json`(명소 레코드·`source_url`·`as_of`)을 메모리에 올린다. **요일 규약 0=월,1=화,…,6=일**(두 파일 공유, 절대 변경 금지 — 오르세=[0], 루브르=[1]). 모든 위반 `rule_id`는 ruleset `rules[].id`(OD-01/02/03·SC-01/02·AG-01/02·PP-01/02) 값만 쓴다(즉석 ID 금지). 로드 실패 시 결정론 판정을 중단하고 후보만 상정한다.

## 1. 입력 정규화 (§3·§5.1)
두 모드. 자유 텍스트로 와도 아래 스키마로 정규화한 뒤 대조한다.
- **단건(§3.2)**: `{listing_id,title,partner,category,places[{name,city,country,place_ref?}],visit_schedule{weekdays?,dates?,sell_period?{start,end},visit_time?},age_terms?[{tier,age_min?,age_max?,height_min_cm?,required_doc?}],body?}`. `mode:"single"`.
- **재스캔(§3.3)**: `{mode:"rescan", world_state_update{facts_delta[{place_ref,field,delta,source_url,effective_date}]}, corpus[<단건 객체 배열>]}`.
- `title`/`body`에서 **① 방문 명소 ② 방문 요일/날짜/판매기간/방문시각 ③ 연령·신장 조건**을 구조화 추출한다. **명소는 주 명소뿐 아니라 본문에 곁들여 언급된 2차 명소(다른 도시의 전망대·부속 방문지 등)까지 모두 추출**한다(→ §2b-1 명소불명 상정 대상).
- 명소링크: `place_ref` 있으면 사용; 없으면 (name+city+country)로 facts 퍼지매칭 → 신뢰도 < `params.place_link.min_confidence`면 **명소불명**(→ §2b-1).
- 전처리(preprocess): **PP-01**(WARN) places 비었거나 weekdays·dates 둘 다 없음 → 필드 채움 요청; **PP-02**(WARN) `sell_period.end < start` 또는 날짜 파싱 불가. PP 위반도 `violations[]`에 담겨 판정 집계에 포함된다(결정론 바닥).

## 2. 2계층 탐지 (§5)
판정은 두 층 — **(a) 결정론 바닥**(동일 입력→동일 결과, 하드게이트)과 **(b) 에이전트 표면**(신뢰도+근거를 달아 사람에게 상정, 하드 BLOCK 아님). **결정론 바닥 = `factmatch`(OD·SC-01·AG) + `preprocess`(PP-01·PP-02)** — 둘 다 결정론이며 `violations[]`·판정 집계·§5.4 서명에 포함된다.

### 2a. 결정론 바닥 — 하드게이트 (§5.2)
매칭 명소의 facts 레코드를 로드해 factmatch 규칙을 facts 값과 **결정론 대조**한다.
- **OD-01**(BLOCK): visit `weekdays` ∩ 명소 `closed_weekdays` ≠ ∅.
- **OD-02**(BLOCK): visit `dates` 중 `special_closures` 해당(`recurring:true`=MM-DD 매년 반복 대조, `false`=명시 date/period 단일 대조).
- **OD-03**(WARN): `visit_time`이 `hours` [open,close] 밖(해당 요일 `weekday_exceptions` 우선 적용). 명소 `hours`에 open/close가 없으면(빈 객체 등) **OD-03 미평가**(위반 없음, 오탐 금지).
- **SC-01**(BLOCK): visit `dates`·`sell_period`가 `closed_periods{start,end}`(MM-DD, 연도 무관 매년 반복)와 겹침 — **경계 inclusive**(05-16~10-15면 양끝 포함).
- **AG-01**(BLOCK): 아동/유아 tier 연령·신장 완화 → 현장 탑승/입장 거부 리스크. **tier↔activity 코드평가**: `age_terms[].tier`(성인/아동/유아/학생)를 `age_rules[].activity`에 매핑; **리스팅이 활동을 특정 안 하면 아동/유아 tier를 그 명소 `age_rules` 중 가장 엄격한 단독(비동반) 참여 기준(단독/solo류 항목 중 age_min·height_min_cm이 가장 높은 레코드; `luge_solo`는 그 한 예)과 대조**한다. 위반 판정 = `listing.age_min < fact.age_min OR listing.height_min_cm < fact.height_min_cm`(경계 `<` — 정확히 만6세는 정합, 오탐 금지). 예: 아동 단독 만4세 < solo 만6세 → BLOCK.
- **AG-02**(WARN): `age_rules`에 `tandem_rule`/`required_doc` 있는데 리스팅 안내 누락. **단, 같은 명소에 AG-01이 이미 격발되면 AG-02는 격발하지 않는다**(연령 위반이 안내 누락을 포섭 — 이중 플래그 방지). AG-02는 AG-01이 없을 때만 독립 WARN으로 올린다.

각 위반 = `{rule_id,severity,layer,place_ref,claimed,official_fact,source_url,message}`. **판정 집계**: BLOCK≥1 → **BLOCK** / (BLOCK=0 ∧ WARN≥1) → **WARN** / 위반 0 → **PASS**.

### 2b. 에이전트 표면 — 자문·상정 (§5.3) — 하드 BLOCK 아님
1. **명소불명**: `place_ref` 부재·퍼지 신뢰도 임계 미만 → `review_candidates[]`에 `{extracted_place,city,confidence}`로 상정(사람 확인 요청). **title·body에서 추출한 모든 명소(주 명소 + 본문 속 2차 명소)를 대상으로** 하며, facts.json에 `min_confidence` 이상으로 매칭되지 않는 것은 주·2차 불문 상정한다(예: 본문에 다른 도시의 2차 전망대/명소가 언급되면 그 이름을 그대로 `extracted_place`로 올린다). 이 상정은 에이전트 표면(비결정론·정보성)이라 verdict·결정론 서명·하드게이트에 영향을 주지 않는다.
2. **SC-02**(WARN, 표면 판단): `params.seasonal_keywords`(라벤더·벚꽃·단풍 등) 검출 + 판매시기가 해당 시즌 밖. **이 판정은 결정론 바닥이 아니라 에이전트 표면 판단**임을 명시한다 — 키워드→시즌창 매핑이 facts에 없어(지어내지 않음) 명소·연도 맥락으로 판단해 WARN 근거/후보로 상정한다. **결정론 SC 바닥은 SC-01(closed_periods)만.** 이 발견은 `violations[]`가 아니라 **`listings[].advisories[]`**(`{code:"SC-02",severity,note,confidence?}`)에 담고, verdict 집계·결정론 서명에서 제외한다(SC-02만 있는 리스팅 verdict=PASS+advisory).
3. **소급 재스캔**: `world_state_update.facts_delta`(각 `place_ref`에 1:1 매핑)로 facts를 갱신한 뒤 `corpus[]` 전 리스팅을 재대조. **`rescan_summary` 결정론 정의**(동일 입력→동일 산출): `flagged_listings`=갱신 후 verdict∈{BLOCK,WARN}인 전 코퍼스 리스팅; `newly_broken`=flagged 중 위반 `place_ref`가 `facts_delta[].place_ref` 집합에 속하는 리스팅(= newly_broken = flagged ∩ {위반 place_ref∈facts_delta place_ref}); `passed`=verdict PASS인 리스팅. 예(스키마): facts_delta place_ref 집합={P}이고 리스팅 A(위반 place_ref가 P에 속함)·B(위반이나 place_ref가 P에 속하지 않음)가 BLOCK이면 → flagged=[A,B], newly_broken=[A](B는 이번 델타와 무관이라 제외), passed=[위반 없는 리스팅]. (특정 골든 id를 암기하지 말고 이 연산을 매 입력에 적용하라.)
4. **추출 모호**: 요일/시기/연령이 자유 텍스트에서 애매하면 신뢰도를 달아 `advisories[]`에 상정(하드 BLOCK 아님, verdict 불변).

> **귀속 규칙**: `review_candidates[]`=명소불명 전용, `advisories[]`=SC-02·추출모호 등 자문 — 서로 섞지 않는다(SC-02를 `review_candidates[]`에 넣지 않는다).

> **결정론 범위(§5.4)**: 동일 입력 → 동일 규칙 ID 세트·동일 판정은 **(a) 결정론 바닥에만** 강제한다. (b) 퍼지매칭 신뢰도·SC-02·자연어 추출은 판단성이라 결정론을 강제하지 않는다(골든 존재검증 + LLM-judge로 측정).

## 3. 생성 — 정정 + 출력단 (§6)
모든 BLOCK/WARN에 정정안 + 출력단 초안을 **생성**한다(모두 제안, `reviewed_by="human-inspector-required"`, 자동 게시·발송 0). **각 correction은 영문 `type` enum + `rule_id`를 단다**(`type ∈ {"weekday_label","season_label","age_label","missing_info"}`; 모든 BLOCK/WARN `rule_id`를 correction ≥1이 커버).
- **표기 정정(§6.1)**: 어긋난 방문 요일·시기·연령 표기를 공식 사실 기준으로 재작성(before→after). **after는 facts.json 값에서 파생**(리터럴 하드코딩 금지), `source_url` 인용. 정정 `after`는 **사람이 읽는 자연어 한국어 문장**으로 쓰되 **실제 사실값(요일명·시기 날짜·연령 숫자·신장 cm)을 명시**한다(예: '매주 월요일 출발'→'화~일 출발(오르세는 매주 월요일 정기 휴관)', '만4세 단독'→'단독 탑승은 만6세·신장 110cm 이상'). **기계 표현(`closed_weekdays=[0]`·`open_weekdays=[…]`·`age_min=6` 등 필드=값 나열) 금지.**
- **대안(§6.2)**: 폐쇄일/휴관요일 판매옵션 비활성 또는 대체 동선/일자 제안.
- **누락 안내 채움(§6.3)**: 동반탑승권·시간지정 예약 등 추가할 안내 문구.
- **출력단 초안**:
  - **파트너 반려 사유서(§6.5)**: 어긋난 필드·공식 사실·시정 체크리스트를 인용한 파트너 맞춤 통지문(모든 플래그 건).
  - **고객 안내문(§6.6)**: **재스캔으로 이미 판매·예약된 건에만** "왜 일정 조정이 필요한가"를 공식 근거로 안내; 아니면 `null`. `customer_notice`는 입력이 **기존 예약/판매 완료를 명시**할 때만 작성 — 현 입력 스키마에 예약상태 필드가 없으므로 **기본 `null`**. `partner_rejection`은 모든 플래그 건에 작성한다.

## 4. 출력 포맷 (§7)
**(1) 마크다운 리포트(§7.1 골격 — 섹션 번호·순서 고정)**: `## 현지 운영사실 정합성 검수 리포트`(모드·상품·판정 `BLOCK n·WARN m`) → `1) 결정론 바닥 — 탐지된 불일치`(표: #·규칙 ID·심각도·명소·주장 vs 공식사실·근거 URL) → `2) 에이전트 표면 — 상정`(명소불명·SC-02) → `3) 소급 재스캔 결과`(사실 델타·newly_broken·passed; 재스캔 모드만) → `4) 정정안` → `5) 출력단 초안(반려 사유서/고객 안내문)` → `6) 결론`. 채울 내용 없는 섹션은 `(해당 없음)`.
**(2) JSON 로그(§7.3, `logs/`)**: `{mode, world_state_update?, rescan_summary{flagged_listings,newly_broken,passed}(정의는 §2b-3), listings[{listing_id,verdict,counts{BLOCK,WARN},violations[{rule_id,severity,layer,place_ref,claimed,official_fact,source_url,message}],advisories[{code,severity,note,confidence?}],corrections[{type,rule_id,before,after}],drafts{partner_rejection,customer_notice}}], review_candidates[{extracted_place,city,confidence}], reviewed_by:"human-inspector-required"}`. **verdict 집계·결정론 서명은 `violations[]`만** 사용 — `advisories[]`는 verdict를 바꾸지 않는다(§2b). 단건 모드는 `mode:"single"` + 단일 listing이며 `world_state_update`/`rescan_summary`는 생략한다.

> **킬러 데모**: 시즌 경계 도래(facts_delta) 한 번 → 발행 땐 통과됐지만 지금 팔면 현장에서 노쇼·입장 거부 나는 판매중 상품을, 현지 사실 기준으로 소급 BLOCK.
