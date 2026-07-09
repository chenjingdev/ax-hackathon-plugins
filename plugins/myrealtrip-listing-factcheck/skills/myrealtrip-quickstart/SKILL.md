---
name: "myrealtrip-quickstart"
description: "myrealtrip-listing-factcheck 플러그인의 사용법·구조·샘플 시연 안내가 필요할 때(퀵스타트/quickstart/사용법/시작하기/온보딩/이 플러그인 뭐야 등) 사용. 플러그인 루트 docs/quickstart.html을 브라우저로 열고 핵심 요약과 샘플 시연을 제안한다."
---

# myrealtrip-quickstart — 온보딩 안내 스킬

이 플러그인(myrealtrip-listing-factcheck)의 용도·구조·샘플 시연 방법을 처음 만난 사용자에게 안내한다.
**읽기 전용 안내 스킬**이다 — 파일을 수정하지 않고, 판정·수치를 즉석에서 창작하지 않는다(모든 사실은 문서에서 인용).

## 절차

### 1. 문서 위치 확인
이 `SKILL.md`의 두 단계 상위(`../..`)가 **플러그인 루트**다. 거기서 `docs/quickstart.html`이 있는지 확인한다.

### 2. OS 브라우저로 열기 시도 (best-effort)
플러그인 루트의 `docs/quickstart.html`을 사용자 OS 기본 브라우저로 연다. 실패하거나 헤드리스 환경이면 건너뛴다(치명적 아님).
- **macOS**: `open docs/quickstart.html`
- **Windows**: `Start-Process docs/quickstart.html` (또는 `cmd /c start "" docs\quickstart.html`)
- **Linux**: `xdg-open docs/quickstart.html`

### 3. 문서를 직접 읽어 채팅 요약
`docs/quickstart.html`을 직접 읽고(브라우저가 열렸든 아니든) 채팅에 아래를 요약한다:
- **용도** 1~2줄: 입점 T&A 상품(투어·액티비티·입장권)의 방문 요일·시기·연령을 명소 공식 운영사실에 3축(운영일·시즌·연령)으로 결정론 대조해, 지금 팔면 현장에서 노쇼·입장거부 나는 리스팅을 사전 차단·소급 재스캔.
- **샘플 표**: 문서의 샘플 카탈로그(파일 → 리스팅 → 기대 판정)를 그대로 옮긴다.

| 샘플 | 리스팅 | 기대 판정 |
|---|---|---|
| `sample/input.rescan.json` | PARIS-ORSAY-MON | BLOCK {OD-01} |
| (재스캔 코퍼스 4건) | SIMILAN-SEP-01 | BLOCK {SC-01} (newly_broken) |
| | SENTOSA-LUGE-KID | BLOCK {AG-01} |
| | TOKYO-SKYTREE-OK | PASS |
| `sample/input.pass.json` | TOKYO-SKYTREE-PASS-01 | PASS |

- **사용법 3경로**: ① 앱 “사용해 보기” 기본 프롬프트 ② 채팅에 프롬프트 복붙 ③ Codex CLI 설치+실행.

### 4. 다음 행동 제안
가장 인상적인 번들 샘플로 시연을 제안한다: **`sample/input.rescan.json` 재스캔** — 시즌 경계 변화 1건으로 판매중 코퍼스에서 3건이 소급 BLOCK({OD-01},{SC-01},{AG-01})되고 1건은 PASS로 남는 킬러 데모.
사용자가 수락하면 **listing-factcheck 스킬**로 넘겨 실제 검수 리포트를 생성한다.

## 주의
- 파일 수정 금지(읽기 전용). 브라우저 열기는 best-effort — 실패해도 3~4단계는 계속 진행한다.
- 판정·수치·근거 URL을 즉석 창작하지 않는다. 기대 판정은 `docs/quickstart.html`·`sample/EXPECTED.md`에서만 인용한다.
