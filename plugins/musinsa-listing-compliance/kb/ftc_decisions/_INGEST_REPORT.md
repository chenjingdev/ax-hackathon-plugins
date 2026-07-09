# FTC decisions ingest report

## Result

- Collected records: 0
- JSON records written: none
- Existing skeleton record left unchanged: `ftc_musinsa_ecoleather.json`

No `ftc_decision` JSON was created or replaced because no official decision PDF or full open-document body was successfully saved/extracted for verbatim `body` use during this run. This follows the task rule that an empty report is preferable to fabricated legal text.

## Config load

- Project config file: not found
- `service_tier`: not found
- Expected `service_tier == "fast"`: not verified
- Search performed: repository files and environment variables for `service_tier`, `config`, `SERVICE_TIER`

## Sources tried

| Source | URL / endpoint | Result |
|---|---|---|
| case.ftc.go.kr listing | `https://case.ftc.go.kr/ocp/co/ltfr.do` | Browser access succeeded. Listing HTML was saved under `/private/tmp/musinsa_ingest/ltfr.html` for inspection. |
| case.ftc.go.kr direct curl | `https://case.ftc.go.kr/` | Blocked by repeated `307 Temporary Redirect` loop with `TMOSHCooKie`; skipped for curl/wget use. |
| case.ftc.go.kr PDF endpoint | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId={docId}&docSn=2` | Endpoint shape verified once as PDF in memory, but subsequent downloads failed with `getaddrinfo ENOTFOUND case.ftc.go.kr`; no PDF was saved. |
| case.ftc.go.kr open document view | `https://case.ftc.go.kr/ocp/co/openDocView.do?docTy=LTFR&docId={docId}&docCnvrMnNo={no}&id={id}` | Endpoint shape verified once as HTML shell, but subsequent full saves failed with `getaddrinfo ENOTFOUND case.ftc.go.kr`; no usable original body was saved. |
| data.go.kr dataset 15103301 | `https://www.data.go.kr/data/15103301/fileData.do` | Metadata page accessible via browser. It points to `https://case.ftc.go.kr/ocp/co/ltfr.do`; no separate keyless bulk file was available from the page. |
| law.go.kr FTC decision API | `https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=ftc&type=XML` | Blocked: `사용자 정보 검증에 실패하였습니다. OPEN API 호출 시 ... IP주소 및 도메인주소를 등록해 주세요.` Treated as API-key/IP registration required and skipped. |
| ftc.go.kr pages | `https://www.ftc.go.kr/` and board endpoints | HEAD access was intermittently successful, but DNS later failed in the sandbox; no official decision body retrieved. |

## Candidate official records identified but not ingested

These candidates were found in the official case listing, but their PDFs/open-document bodies were not saved, so no JSON records were written.

| Candidate | Decision no. | URL |
|---|---:|---|
| `(주)포스코 및 포스코홀딩스(주)의 부당한 광고행위에 대한 건` | `약식2025-053` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20251030141800570306&docSn=2` |
| `엘지전자(주)의 부당한 광고행위에 대한 건` | `의결2019-128` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20190911093553542471&docSn=2` |
| `3개 자동차 제조·판매사업자의 부당한 표시·광고행위에 대한 건` | `의결2017-024` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20221230161715780210&docSn=2` |
| `(사)한국공기청정협회의 부당한 광고행위에 대한 건` | `의결2008-210` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20080812153058631&docSn=2` |
| `3개 아기욕조 제조판매사업자의 부당한 표시광고 행위에 대한 건` | `의결2023-097` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20230818144950431692&docSn=2` |
| `데상트코리아(주)의 부당한 표시광고행위에 대한 건` | `약식2023-016` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20230312114051214795&docSn=2` |
| `(주)이랜드월드의 부당한 표시광고행위에 대한 건` | `약식2026-004` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20260528144636821184&docSn=2` |
| `(주)티클라우드의 부당한 광고행위에 대한 건` | `약식2026-003` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20260528144829453208&docSn=2` |
| `(주)아카이브코의 부당한 광고행위에 대한 건` | `약식2026-002` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20260128150033937245&docSn=2` |
| `(주)신원의 부당한 표시행위에 대한 건` | `약식2005-062` | `https://case.ftc.go.kr/ocp/co/getFileList.do?docId=20180101165245444394&docSn=2` |

## Gate results

| Gate | Result | Notes |
|---|---|---|
| `python3 eval/license_lint.py` | PASS | 6 KB JSON records checked. |
| `python3 eval/mcp_smoketest.py` | PASS | 10/10 checks passed. |
| `python3 eval/citation_gate.py` | PASS | 5/5 checks passed. |
| `python3 eval/structure_check.py` | FAIL | The exact command failed because `py_compile` attempted to write `.pyc` under `/Users/chenjing/Library/Caches/com.apple.python/...`, which is outside the writable sandbox. |
| `PYTHONPYCACHEPREFIX=/private/tmp/musinsa_pycache python3 eval/structure_check.py` | PASS | Same structure check passed when Python bytecode cache was redirected to a writable temp directory. |
