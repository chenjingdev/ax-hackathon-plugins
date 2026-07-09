> **schema_ref**: SPEC.md §7.2(골든 리포트 골격)·§8.2(기대 출력)·§7.1(섹션 순서). 대상 입력=`src/sample/input.rescan.json`(재스캔 킬러 데모). `src/sample/input.pass.json`(PASS 음성)의 기대 출력은 본 문서 말미 별도 섹션.
>
> 텍스트 표현은 변형 가능하나 다음 **서명**은 정확히 일치해야 한다: `flagged_listings` 집합, 각 리스팅의 `verdict`, `rule_set`(OD-01/SC-01/AG-01), 각 위반의 `source_url`, `review_candidate`(명소불명), `newly_broken` 집합. M3.5의 `eval/expected/*.expected.json`, M4의 `codex exec` 산출 대조가 이 서명을 채점 기준으로 삼는다.

## 현지 운영사실 정합성 검수 리포트
- 모드: 재스캔(코퍼스) — 세계상태 변화 트리거
- 상품: 코퍼스 4건 (PARIS-ORSAY-MON, SIMILAN-SEP-01, SENTOSA-LUGE-KID, TOKYO-SKYTREE-OK)
- 판정: 코퍼스 4건 중 **BLOCK 3 / PASS 1**

### 1) 결정론 바닥 — 탐지된 불일치
| # | listing | 규칙 | 심각도 | 주장 vs 공식사실 | 근거(공식 URL) |
|---|---|---|---|---|---|
| 1 | PARIS-ORSAY-MON | OD-01 | BLOCK | 매주 월요일(`weekdays=[0]`) 출발 vs 오르세 월요일(`closed_weekdays=[0]`) 정기 휴관 | https://www.musee-orsay.fr/en/visit |
| 2 | SIMILAN-SEP-01 | SC-01 | BLOCK | 9월(`dates=["2026-09-15"]`, `sell_period` 9/1~9/30) 스노클링 판매 vs 시밀란 `closed_periods` 05-15~10-15(2026 시즌; per-year, 2025=05-16~10-14) 우기 전면 폐쇄(경계 inclusive) | https://www.nationthailand.com/news/tourism/40066673 |
| 3 | SENTOSA-LUGE-KID | AG-01 | BLOCK | 아동 단독탑승 만4세(`age_terms.age_min=4`, 활동 미특정→단독 기준 대조) vs 공식 단독탑승 만6세·110cm 미만 단독 불가(`luge_solo age_min=6`) | https://sentosa.skylineluge.com/luge/safety-faq/ |

TOKYO-SKYTREE-OK: 위반 0 → **PASS**(표에 행 없음 — 오탐 금지. `closed_weekdays=[]`·`closed_periods=[]`·`age_rules=[]`·`hours={}`이라 OD-03도 미평가).

### 2) 에이전트 표면 — 상정
- **명소불명**: `"리버사이드 전망대"(방콕)` — SIMILAN-SEP-01 `body`에서 추출된 2차 명소 언급(`places[]`에는 미등재). `facts.json`에 해당 레코드 없음 → 퍼지매칭 신뢰도 < `params.place_link.min_confidence`(0.6) → `review_candidates`에 `{extracted_place:"리버사이드 전망대", city:"방콕", confidence:<0.6}` 상정, 사람 확인 요청. (신뢰도 수치는 에이전트 표면 비결정론 산출이라 게이트 대상 아님 — **예시 ≈0.4**, SPEC §7.2 원문 예시 0.41 참고)
- 기타 SC-02·추출모호 자문 없음(코퍼스 4건 모두 `body`에 `params.seasonal_keywords` 미검출).

### 3) 소급 재스캔 결과
- 사실 델타: `world_state_update.facts_delta` = `[{place_ref:"similan", field:"closed_periods", delta:"시즌 폐쇄중(현재 10/15 이전)", source_url:"https://www.nationthailand.com/news/tourism/40050202", effective_date:"2026-07-07"}]` — **similan 1건만**.
- `flagged_listings`: `[PARIS-ORSAY-MON, SIMILAN-SEP-01, SENTOSA-LUGE-KID]` (갱신 후 verdict∈{BLOCK,WARN} 전체)
- `newly_broken`: `[SIMILAN-SEP-01]` (flagged 중 위반 `place_ref`가 `facts_delta`의 `{similan}`에 속하는 리스팅만 — orsay·sentosa_luge는 델타 무관이라 제외)
- `passed`: `[TOKYO-SKYTREE-OK]`

### 4) 정정안 (생성)
- **PARIS-ORSAY-MON** (`type:"weekday_label"`, `rule_id:"OD-01"`): before=`"매주 월요일 출발"` → after=`"화~일 출발(월요일은 오르세 정기 휴관)"` — 근거: musee-orsay.fr/en/visit. 대안: 월요일 판매 옵션 비활성화 또는 화~일 대체 출발일 제시.
- **SIMILAN-SEP-01** (`type:"season_label"`, `rule_id:"SC-01"`): before=`"9월 출발 스노클링 데이투어"` → after=`"10/16~5/14 출발만 판매(시밀란 5/15~10/15 우기 전면 폐쇄, 2026 시즌)"` — 근거: nationthailand.com/news/tourism/40066673(2026). 대안: 9월 판매기간 비활성화, 우기 종료(10/15) 이후 재개일로 이관. (after 텍스트는 변형 가능 — 커밋된 골든 산출은 직전 시즌 경계(5/16~10/15) 표기를 쓸 수 있으나 서명·게이트에는 무관.)
- **SENTOSA-LUGE-KID** (`type:"age_label"`, `rule_id:"AG-01"`): before=`"아동(만4세~) 단독 탑승권"` → after=`"만6세·110cm↑ 단독 / 만2~6세는 성인 동반탑승권 필수"` — 근거: sentosa.skylineluge.com/luge/safety-faq. 누락 안내 채움: 동반탑승권(tandem) 필수 표기 삽입.

### 5) 출력단 초안 (반려 사유서 / 고객 안내문)
플래그 3건 전부 `partner_rejection` 작성, `customer_notice=null`(현 입력 스키마에 예약/판매완료 필드 부재 — 기본값), 모두 `reviewed_by:"human-inspector-required"`(자동 게시·발송 0).

- **PARIS-ORSAY-MON 파트너 반려 사유서**: "[오르세 투어] 매주 월요일 출발로 표기 — 오르세 미술관은 월요일 정기 휴관(공휴일 예외 없음). 현장 노쇼 리스크. 시정: 화~일 출발로 요일 수정. 근거: musee-orsay.fr/en/visit"
- **SIMILAN-SEP-01 파트너 반려 사유서**: "[시밀란 스노클링] 9월 판매기간 표기 — 시밀란 국립공원은 5/15~10/15(2026 시즌) 우기 전면 폐쇄(태국 DNP 규정). 현장 운항 불가 리스크. 시정: ①9월 판매 비활성화 ②10/16 이후 재개일로 판매기간 이관. 근거: nationthailand.com/news/tourism/40066673"
- **SENTOSA-LUGE-KID 파트너 반려 사유서**: "[센토사 루지 아동권] 단독탑승 연령을 만4세로 표기 — 운영사 공식 규정은 단독탑승 만6세·신장 110cm 이상이며, 만2~6세는 성인 동반탑승권 필수. 현장 탑승 거부 리스크. 시정: ①연령/신장 표기 수정 ②동반탑승권 안내 삽입. 근거: sentosa.skylineluge.com/luge/safety-faq"

### 6) 결론
- 권고: 3건 개시 보류/판매옵션 조정 — TOKYO-SKYTREE-OK는 정탐 유지(개입 없음).
- **"발행 땐 통과됐지만 지금 팔면 현장에서 노쇼·입장거부 나는 상품을 현지 사실 기준으로 소급 적발."**

---

## 음성 픽스처 기대 출력 — `input.pass.json` (§8.3)
- 대상: `TOKYO-SKYTREE-PASS-01`(단건, 금요일 오후 성인 입장권)
- **기대: `verdict:"PASS"`, `violations:[]`, `counts:{BLOCK:0,WARN:0}`.** (`tokyo_skytree`는 `closed_weekdays=[]`·`closed_periods=[]`·`age_rules=[]`·`hours={}` — 어떤 요일/시기/연령 조합으로도 위반 불가, OD-03도 `hours` 부재로 미평가.)
- `review_candidates:[]`, `advisories:[]`(`body`에 `seasonal_keywords` 미검출), `corrections:[]`, `drafts:{partner_rejection:null, customer_notice:null}`(플래그 없으므로 출력단 생성 대상 아님).
- 정탐 확인: 깨끗한 상품을 막지 않는다(오탐 0).

---

## 정합성 자기점검 (SKILL 규칙 손대조 — M2 §2a/§2b-3 기준)

1. **PARIS-ORSAY-MON**: `visit_schedule.weekdays=[0]` ∩ `facts.json.orsay.closed_weekdays=[0]` = `{0}` ≠ ∅ → **OD-01 BLOCK**. `age_terms`는 성인뿐이고 orsay `age_rules=[]`이라 AG 계열 무관. → verdict=BLOCK, rule_set={OD-01}. ✅ EXPECTED 1행과 일치.
2. **SIMILAN-SEP-01**: `dates=["2026-09-15"]` → MM-DD=`09-15`. `facts.json.similan.closed_periods=[{start:"05-15",end:"10-15", source_year:2026}]`(per-year 스냅샷; 2025=05-16~10-14, `history[]` 보존). `05-15 ≤ 09-15 ≤ 10-15`(같은 해 내 정상 구간, 랩어라운드 없음) → 겹침 참 → **SC-01 BLOCK**(9/15는 구간 깊숙한 내부값이라 경계 드리프트(±1일)와 무관하게 판정 불변 — golden 서명 영향 없음). `body`의 "리버사이드 전망대"는 `places[]` 밖의 자유텍스트 2차 명소 언급이라 SC-01 판정에는 영향 없고, 명소불명 `review_candidates` 1건만 별도 상정. `seasonal_keywords`(라벤더/벚꽃/단풍/설경/반딧불/오로라) 미검출 → SC-02 없음. → verdict=BLOCK, rule_set={SC-01}. ✅ EXPECTED 2행 + 섹션 2 일치.
3. **SENTOSA-LUGE-KID**: `age_terms`의 `{tier:"아동", age_min:4}`는 활동 미특정 → `facts.json.sentosa_luge.age_rules` 중 가장 엄격한 단독 기준 `luge_solo{age_min:6, height_min_cm:110}`과 대조. `4 < 6` → **AG-01 BLOCK**(경계 `<` 이므로 정확히 6세는 정합·오탐 없음 — 이 리스팅은 4세라 경계 미해당, 명확한 위반). `tandem_rule` 관련 AG-02는 아동권이 이미 BLOCK(단독 자체가 위반)이라 별도 WARN 산정 불필요(정정안에서 동반탑승권 안내는 대안 제시로 흡수). → verdict=BLOCK, rule_set={AG-01}. ✅ EXPECTED 3행과 일치.
4. **TOKYO-SKYTREE-OK**: `weekdays=[2]`(수) ∩ `tokyo_skytree.closed_weekdays=[]` = ∅. `closed_periods=[]`이므로 어떤 날짜·판매기간도 겹칠 수 없음. `hours={}` → OD-03 미평가(오탐 금지 규칙). `age_terms`=성인뿐이고 `age_rules=[]` → AG 계열 무관. PP-01/PP-02: `places` 비어있지 않고 `weekdays` 존재, `sell_period.end(2026-12-31) ≥ start(2026-07-01)` → 전처리 위반 없음. → **위반 0 → PASS**. ✅ EXPECTED "PASS 1" 및 섹션 3 `passed` 일치.
5. **재스캔 집계**: `facts_delta` place_ref 집합 = `{similan}`. `flagged_listings` = 갱신 후 verdict∈{BLOCK,WARN} 전체 = `{PARIS-ORSAY-MON, SIMILAN-SEP-01, SENTOSA-LUGE-KID}`(3건, TOKYO 제외). `newly_broken` = flagged ∩ {위반 `place_ref` ∈ `facts_delta` place_ref} = orsay∉{similan}→제외, similan∈{similan}→포함, sentosa_luge∉{similan}→제외 = **`{SIMILAN-SEP-01}`** 단 1건. ✅ 브리프 필수 제약("facts_delta는 similan만 → newly_broken=[SIMILAN-SEP-01]") 충족.
6. **`input.pass.json`**: `TOKYO-SKYTREE-PASS-01`도 동일 논리(3번 항목과 동형, `weekdays=[4]`)로 위반 0 → PASS. ✅

**결론**: 위 5개 항목 모두 손으로 규칙을 적용한 결과가 본 문서 상단 EXPECTED 서명(판정·rule_set·source_url·review_candidate·newly_broken 집합)과 정확히 일치한다. 입력·기대출력·SKILL·facts.json 간 정합 확인 완료.
