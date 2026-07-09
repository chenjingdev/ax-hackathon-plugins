# sources.md — 규칙·사실 → 공개 출처 매핑

> 목적: `ruleset.json`(9개 규칙)과 `facts.json`(명소 운영사실 레코드)의 **모든 판정 근거가 공개·검증 가능한 출처로 추적됨**을 문서화한다(SPEC §11.2, 글로벌 불변식 "공개 근거만").
> 이 문서는 사람이 읽는 매핑표다. 기계가 읽는 권위 사본은 `ruleset.json`(규칙)과 `facts.json`(사실)이며, 이 문서는 **파생물**(둘을 섞지 않는다).

## 1. 문제 구조 근거 (P1·P2)

| 근거 ID | 내용 | 출처 |
|---|---|---|
| P1 (확인) | 마이리얼트립은 파트너 입점 마켓플레이스이며, 검수 담당자가 영업일 3일 내 검수 의견·개시 여부를 통보하는 human-in-the-loop 게이트가 실재. 검수가 제목·카테고리·태그·대표사진 등 메타데이터 항목을 다룸(현행 파트너센터 확인). | `research/org-persona-evidence.md` (현행 mrtpartners.zendesk 도움말 `articles/26481380757133`·`26485066927501`·`360059489352`·복수 채용공고 verbatim) |
| P1′ (추정) | 그 검수가 현지 운영사실(휴관요일·시즌폐쇄·연령규정)까지는 구조적으로 미포착한다는 부정명제는 **부재-근거 추론(가설)** — 확정 아님. PP-01/PP-02의 '사람 검토 요청' basis는 확인된 human-in-the-loop 구조(P1)에만 의존하고, 이 가설에는 의존하지 않는다. | 동상(negative claim 한계) |
| P2 | GMV 3대 부문(항공·숙박·T&A)이 모두 재판매/입점 모델. 표적은 T&A 파트너 입점 리스팅. | `research/research-verified.md:25` |

**P1을 basis로 쓰는 규칙**: `PP-01`, `PP-02` (전처리층 — "대조 불가/파싱 불가 시 사람 검토 요청"의 근거가 P1의 human-in-the-loop 구조).

## 2. 골든 명소 사실 근거 (F1~F4) — `facts.json`

| 근거 ID | place_ref | 명소 | 공식 출처 URL | as_of | 매핑 규칙 |
|---|---|---|---|---|---|
| F1 | `orsay` | 오르세 미술관 (Paris, France) | https://www.musee-orsay.fr/en/visit | 2026-07-07 | `OD-01`(closed_weekdays 대조), `OD-02`(special_closures 대조), `OD-03`(hours 대조) |
| F2 | `louvre` | 루브르 박물관 (Paris, France) | https://www.louvre.fr/en/visit/hours-admission | 2026-07-07 | `OD-01`(closed_weekdays 대조), `OD-03`(hours 대조) |
| F3 | `similan` | 시밀란 제도 국립공원 (Phang Nga, Thailand) | https://www.nationthailand.com/news/tourism/40066673 (2026 시즌) · https://www.nationthailand.com/news/tourism/40050202 (2025 시즌, history) | 2026-07-07 | `SC-01`(closed_periods 대조), `SC-02`(계절 키워드 참고) |

> **F3 경계 정직성 주의(신규)**: 시밀란 폐쇄일은 **연도별로 드리프트**하므로 `facts.json`의 `closed_periods`는 **per-year(source_year·as_of 명시, recurring=false)**로 기록한다 — 2026=**5/15~10/15**(nationthailand 40066673), 2025=**5/16~10/14**(40050202, `history[]`에 보존). 폐쇄종료일과 재개일 보도가 **±1일 상충**한 이력이 있어(2025 공식 종료 10/14 vs 재개 보도 10/16) 경계일(±1일) 리스팅은 하드 BLOCK보다 사람 확인을 권장한다. 소급 재스캔 가치가 facts 최신성에 의존하므로 **매 시즌 source_url로 재확인·갱신**이 필요하다(라이브 API 아님).
| F4 | `sentosa_luge` | 센토사 스카이라인 루지 (Sentosa, Singapore) | https://sentosa.skylineluge.com/luge/safety-faq/ | 2026-07-07 | `AG-01`(age_rules 완화 대조), `AG-02`(tandem_rule/required_doc 누락 대조) |

> 주: SPEC §4 표의 "근거" 열은 규칙별로 F1/F2 조합이 다르다(예: `OD-02`는 F1만, `OD-03`은 F1·F2 모두) — `ruleset.json`의 각 규칙 `basis` 필드가 SPEC §4 표를 verbatim으로 반영하며, 이 표는 그 위에 명소·출처 관점을 얹은 것이다.

## 3. PASS 대조군 지원 사실 (골든 F 아님)

| place_ref | 명소 | 공식 출처 URL | as_of | 용도 |
|---|---|---|---|---|
| `tokyo_skytree` | 도쿄 스카이트리 (Tokyo, Japan) | https://www.tokyo-skytree.jp/en/ | 2026-07-07 | M3 `TOKYO-SKYTREE-OK`(평일 성인권)가 명소불명이 아니라 진짜 **PASS**로 판정되도록 지원(A5). 연중무휴·성인권 연령제약 없음. |

> 의도적 누락: "리버사이드 전망대(방콕)" 등 명소불명 데모용 place는 `facts.json`에 **일부러 넣지 않는다**(M3에서 `place_link.min_confidence` 미만 매칭 → `review_candidates[]` 상정 데모).

## 4. 규칙 → 근거 → 출처 전체 매핑 (`ruleset.json` 9개 규칙)

| 규칙 ID | family | layer | severity | basis | 출처(facts.json.source_url 경유) |
|---|---|---|---|---|---|
| OD-01 | OD | factmatch | BLOCK | F1, F2 | musee-orsay.fr/en/visit · louvre.fr/en/visit/hours-admission |
| OD-02 | OD | factmatch | BLOCK | F1 | musee-orsay.fr/en/visit |
| OD-03 | OD | factmatch | WARN | F1, F2 | musee-orsay.fr/en/visit · louvre.fr/en/visit/hours-admission |
| SC-01 | SC | factmatch | BLOCK | F3 | nationthailand.com/news/tourism/40050202 |
| SC-02 | SC | factmatch | WARN | F3 | nationthailand.com/news/tourism/40050202 |
| AG-01 | AG | factmatch | BLOCK | F4 | sentosa.skylineluge.com/luge/safety-faq |
| AG-02 | AG | factmatch | WARN | F4 | sentosa.skylineluge.com/luge/safety-faq |
| PP-01 | PP | preprocess | WARN | P1 | research/org-persona-evidence.md |
| PP-02 | PP | preprocess | WARN | P1 | research/org-persona-evidence.md |

## 5. 추적성 원칙

모든 BLOCK/WARN 판정은 런타임에 `{rule_id, severity, place_ref, claimed, official_fact, source_url, message}`로 기록되며(SPEC §5.2), 이때 `source_url`은 **반드시 `facts.json`의 해당 `place_ref` 레코드에서 그대로 파생**된다(SKILL이 새 URL을 생성/추정하지 않음). 즉 "모든 위반이 `facts.json.source_url`로 추적 가능"이 성립한다(A7 — M3.5 grader가 `source_url ∈ facts.json 허용집합`으로 검증).

## 6. 파라미터 (SPEC §4.4 하단·§3.5) — 위치는 `ruleset.json`

- `params.place_link.min_confidence` = 0.6 — (name+city+country) 퍼지매칭 신뢰도 임계. 미만이면 '명소불명' → `review_candidates[]` 상정.
- `params.seasonal_keywords` = `["라벤더","벚꽃","단풍","설경","반딧불","오로라"]` — `SC-02` 계절성 볼거리 키워드셋.

파라미터·임계값은 `ruleset.json`에만 존재하며 SKILL.md(M2)에 하드코딩하지 않는다(글로벌 불변식).
