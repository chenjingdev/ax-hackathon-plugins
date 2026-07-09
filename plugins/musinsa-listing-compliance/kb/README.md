# kb/ — 로컬 컴플라이언스 지식베이스 (라이선스 정리본)

위반 판정의 **법적 근거를 출처와 함께** 제공하는 오프라인 문서 DB. `mcp_server/compliance_kb_server.py`(MCP 서버)가 이 폴더를 읽어 `search_legal_basis`·`get_ftc_precedent`·`verify_citation` 등으로 노출한다. **외부 네트워크·API 키 0** — 심사 환경에서도 그대로 동작하고, 심사자가 제출물 안에서 출처를 즉시 확인할 수 있다.

## 레코드 스키마
`{ doc_id, type, title, body, body_kind, source_org, provenance_url, license, attribution_required, attribution, pii_masked, keywords[], rule_refs[] }`

- `type`: `statute`(법령) · `guideline`(심사지침/행정규칙) · `ftc_decision`(공정위 의결례) · `test_lab`(시험기관) · `*_placeholder`(라이선스 확정 대기)
- `rule_refs`: 이 문서가 뒷받침하는 `ruleset.json` 룰 ID
- `provenance_url`: 심사자·MD가 1차 출처를 직접 열람

## 수록 라이선스 근거 (deep-research 1차 검증)
| 문서군 | 라이선스 | 동봉 |
|---|---|---|
| 법령 본문(표시광고법 등) | 저작권법 §7①(비보호) | ✅ 자유 |
| 행정규칙·심사지침 | §7② 추정 / §24-2 backstop | ✅ (출처표시 부착) |
| 공정위 의결서·결정문 | §7③ 비보호 / **data.go.kr 15103301 '제한 없음'** | ✅ 자유 |
| 법제처 법령정보(open.law.go.kr) | 영리이용 OK, **출처='법제처' 표기 의무** | ⚠️ 조건부 |
| KOLAS 인정시험기관 명부(knab.go.kr) | 저작권 표시·공공누리 없음 | 🚫 **DB 동봉 불가** → 명칭 화이트리스트(사실)+공식명부 인간검증 |
| KIPRIS 상표(KIPRIS Plus) | 약관 §17·§19 재배포·DB화 금지 | 🚫 **동봉 불가** → 인간검증 URL 포인터·TS-02로 대체 |

## 운용 원칙 (비저작권 제약 — 저작권과 별개로 준수)
1. **1차 채널 직접 수집**: data.go.kr·법제처 OPEN API 등 원본에서 수집(제3자 큐레이션 DB 통째 복제 금지 — DB제작자 권리 §91~98).
2. **개인정보 마스킹**: 의결서 인제스트 시 비식별 처리(개인정보보호법).
3. **크롤링 회피**: case.ftc.go.kr 대량 자동수집 대신 data.go.kr 일괄 다운로드 사용.
4. **출처표시**: `attribution_required=true` 문서는 인용 시 `attribution` 문구 동반.

## BYO 라이선스 데이터 어댑터 (저작권 미해결 소스용)
KOLAS 명부·KIPRIS 상표처럼 **현재 라이선스상 동봉할 수 없는 검증 소스**는 데이터를 싣지 않는다. 대신 **법령 KB와 동일한 로컬 MCP+KB 형태**라는 점을 살려, 도구를 *드롭인 어댑터*로 구성했다:

- 도구(`check_test_lab`·`lookup_trademark`)는 **(1) 동봉된 라이선스 레코드가 있으면 그것으로 서빙, (2) 없으면 인간검증 URL/화이트리스트로 폴백**한다.
- 따라서 **라이선스(KIPRIS Plus 기관협의 / KOLAS 공식채널)를 확보하면, `kb/labs/`·`kb/trademarks/` 에 같은 스키마로 레코드를 넣기만 하면 즉시 작동한다(코드 변경 0).**
- 스키마 견본: `kb/_templates/*.template.json` (서빙 안 됨 — `*_template` 타입).

> **한 줄 안내(심사자/도입사용)**: *"이 검증 소스는 법령 KB와 동일한 방식이다. 본 제출물은 저작권 보호 데이터를 동봉하지 않고 어댑터 슬롯과 동작만 시연한다. 라이선스를 해결하면 같은 슬롯에 데이터를 넣어 그대로 쓸 수 있다."*

## 현재 시드(스켈레톤)
`body_kind="요지(skeleton seed)"` 레코드는 end-to-end 동작 시연용 요지다. 정식 인제스트 시 1차 출처 원문(verbatim)으로 대체한다.
