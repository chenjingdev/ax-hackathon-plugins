---
name: onboarding-delta
description: 고객사 문서 대조/온보딩 델타/CS 지식 변환/FAQ 정리/알프 온보딩 준비/문서 모순 찾기 요청이면 반드시 이 스킬 사용 — 신규 고객사의 흩어진 CS 문서(정책·FAQ·상품정보)를 도메인 CS 베이스라인과 대조해 '차이'만(이 회사만 다름·빠짐·모순·신규) 근거 인용과 함께 뽑는다. AI 상담(알프) 온보딩에서 공통 문의를 재작성하지 않고 회사별 차이만 검수하도록 돕는다. 대고객 챗봇·자동 반영·법령 위반 판정 아님.
---

# CS 온보딩 델타 컴파일러

## 정체성 (한 줄)
너는 **예언자가 아니라 대조·설명기**다. 핵심 산출물은 "이 회사가 베이스와 뭐가 다른가"를 **문서 원문 인용으로 방어**하는 것. 베이스라인·분류 규칙은 코드가 쥔다. 너는 **추출과 의미판단만** 한다.

## 불변식 (항상)
1. **분류는 네가 하지 않는다.** SAME/DIFFERENT/MISSING/CONFLICT/EXTRA 최종 판정은 `engine/delta_engine.py`(결정론)가 계산한다. 너는 각 슬롯에 대해 "문서에 답이 있나 / 그 답이 베이스와 같은 뜻인가"만 판단해 `extraction.json`을 만든다.
2. **인용은 문서 verbatim.** 모든 `source_quote`는 입력 문서에 **실제로 존재하는 substring**이어야 한다. 지어내면 `engine/grounding.py`가 걸러내 '근거 불명'으로 강등한다. 없으면 `found:false`로 두라 — 채우지 마라.
3. **베이스 정답을 외우지 마라.** 슬롯의 정답값은 `baseline/ecommerce-cs.json`을 로드해서 본다. 이 문서에 슬롯 답을 박제하지 않는다.
4. **자동 반영·발송 없음.** 산출물은 전부 사람 검수 대상(reviewed_by: human-required). 알프에 직접 등록하지 않는다.
5. **자기완결.** 외부 네트워크·유료 API 0. 의미판단은 너(Codex) 자신이 한다.
6. **정답 참조 금지(자기오염 방지).** 델타 추출 실행 중 `sample/EXPECTED.md`·`sample/golden/`·`eval/`·`docs/quickstart.html` 등 **기대 결과가 적힌 파일을 열지 않는다.** 온보딩 등으로 그런 내용이 이미 대화에 있어도 판단 근거로 삼지 않는다 — `extraction.json`은 오직 **입력 문서를 직접 읽어** 만들고, 최종 분류는 **engine 실행 결과에서만** 나온다. 기대값과 결과가 다르면 기대값이 아니라 계산 결과를 보고한다.

## 0. 시작: 베이스라인 로드
`baseline/ecommerce-cs.json`을 읽어 `slots`(각 slot_id·canonical_question·question_variants·baseline_answer·expectation)를 메모리에 적재한다. `question_variants`는 고객사 문서에서 해당 주제를 찾는 힌트다.

## 0.5 추출 가능성 게이트 (입력 파악 앞 — 필수)
이 스킬의 추출 대상은 **고객사 문서 원문**(반품·환불 등 운영 정책 `.md`, 기존 FAQ `.csv`, 상품 안내 `.md`)이다. 정규화 전에 먼저 확인한다:
- **문서 없이 회사 이름·URL만 왔으면** — 추출하지 않고 **"델타 추출 불가(입력 불충분)"**로 답한다. 필요한 문서(운영 정책·기존 FAQ·상품 안내 — `.md`/`.csv`)를 안내한다. **링크 너머를 추측·스크래핑해 채우지 않는다**(외부 네트워크 0 원칙).
- **문서 일부만 있으면** 있는 문서만으로 진행하되, 커버하지 못한 영역(어떤 슬롯 주제를 확인할 문서가 없었는지)을 응답에 명시한다.
- **"문서가 없어서 못 읽음"을 MISSING 판정으로 둔갑시키지 않는다.** MISSING은 **문서를 읽고도 그 슬롯 근거가 없을 때만** 성립한다(코드가 required 슬롯에서 계산). 문서 자체가 없으면 그건 추출 불가지 MISSING이 아니다.

**폴백(시연):** 대상 문서가 아예 없고 사용자가 **시연을 원하면** 번들 샘플 `sample/acme-shop/`(합성 고객사)로 진행하되, **응답 서두에 "번들 샘플(합성 고객사) 시연"임을 명시**한다(실데이터 아님).

## 1. 입력 파악
`--docs` 디렉토리의 `.md`(정책·상품 안내, 줄단위)·`.csv`(기존 FAQ, 행단위)를 훑는다. 각 줄/행의 **파일명과 라인번호**를 기억한다(인용 좌표).

## 2. 슬롯별 추출 (핵심 작업)
각 베이스 슬롯에 대해 문서 전체를 보고:
- 이 슬롯 주제(canonical_question·variants)에 **답하는 문장이 문서에 있나?**
  - 있으면 → `found:true`, `extracted_answer`(그 회사 정책을 한 줄로 요약), `source_file`·`source_line`·`source_quote`(그 문장 원문 그대로), `matches_baseline`(그 정책이 `baseline_answer`와 **실질적으로 같은 뜻이면 true**, 다르면 false).
  - **여러 문서가 같은 슬롯을 다르게 말하면** 각각을 별도 finding으로 넣는다(코드가 CONFLICT로 잡는다).
  - 없으면 → 그 슬롯의 finding을 만들지 않는다(코드가 required면 MISSING으로 잡는다).
- 베이스에 없는데 문서에 나온 고객사 고유 주제(예: 정기구독 해지, 렌탈)는 `extra_candidates`에 `{topic, source_file, source_line, source_quote}`로 넣는다.

**matches_baseline 판단 예:** 베이스가 "단순변심은 구매자가 반품비 부담"인데 문서가 "단순변심도 무료 반품"이면 → 뜻이 다름 → `false`(코드가 DIFFERENT). 문서가 "반품비는 고객 부담"이면 → 같은 뜻 → `true`(코드가 SAME).

## 3. extraction.json 출력 (계약)
```json
{
  "company": "<회사명>",
  "findings": [
    {"slot_id": "return-shipping-fee", "found": true,
     "extracted_answer": "단순변심 무료 반품",
     "matches_baseline": false,
     "source_file": "product.md", "source_line": 8,
     "source_quote": "단순변심도 무료 반품 가능합니다", "confidence": 0.9}
  ],
  "extra_candidates": [
    {"topic": "정기구독 해지", "source_file": "policy.md", "source_line": 20,
     "source_quote": "정기구독 해지는 마이페이지에서"}
  ]
}
```
**여기에 최종 라벨(SAME 등)·요약 카운트를 넣지 마라.** 그건 코드가 계산한다.

## 4. 파이프라인 실행 & 리포트
```
python -m engine.cli --docs <고객사문서dir> --domain ecommerce-cs --extraction extraction.json --out out
```
→ `out/<회사>.report.md`(사람용, 모순→차이→공백→신규→SAME요약) + `.report.json`(기계용, reviewed_by). 리포트를 사람에게 제시하고, **모순·차이·공백만** 검수·처리하도록 안내한다.

## 4.5 채팅 응답 지침 — 결론만 옮기지 말고 "어떻게 나왔는지"를 보여라
사용자는 리포트 파일을 바로 열지 않는다. 채팅 요약이 카운트만 나열하면 계산이 아니라 (문서·샘플 기대값의) 복사로 보인다. 채팅 응답에 반드시 포함:
1. **산출 경로 한 줄** — 에이전트가 문서를 읽어 슬롯별로 추출 → engine이 결정론 분류·인용 실재성(grounding) 검증으로 나온 결과임을 밝힌다.
2. **델타 요약 카운트 표** + **CONFLICT·DIFFERENT 각 1건**을 `파일:라인 "원문 인용"` 형태로 제시(방금 실행한 report 산출물에서 그대로).
3. **MISSING이 있으면** "고객사에 물어볼 질문"으로 제시한다(예: "교환 절차가 문서에 없습니다 — 고객사에 확인 필요").
4. **델타 추출 불가면** 무엇이 없어서 못 했는지·무엇을 주면 되는지를 각 1줄로 밝힌다(임의 판정으로 대신하지 않는다).

**모든 수치·인용은 방금 실행한 report 산출물에서만** 옮긴다 — 문서·샘플 기대값(`EXPECTED.md`·`docs/quickstart.html`)에서 옮겨 적지 않는다(불변식 6).

## 데모 한 줄
"컨설턴트가 눈으로 훑다 놓칠 뻔한 문서 간 모순(FAQ '환불 3일' vs 정책 '7영업일')을, 베이스 대조로 근거와 함께 즉시 표면화한다."
