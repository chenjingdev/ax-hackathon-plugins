---
name: "musinsa-quickstart"
description: "musinsa-listing-compliance 플러그인의 사용법·구조·샘플 시연 안내가 필요할 때(퀵스타트/quickstart/사용법/시작하기/온보딩/이 플러그인 뭐야/뭘 할 수 있어 등) 사용. 플러그인 루트 docs/quickstart.html을 브라우저로 열고 핵심 요약과 샘플 시연을 제안한다."
---

# musinsa-quickstart — 퀵스타트 온보딩 안내

이 스킬은 **읽기 전용 안내 스킬**이다. 어떤 파일도 수정하지 않는다. 판정·수치를 즉석에서 창작하지 않고, `docs/quickstart.html`·`rules/ruleset.json`·`sample/EXPECTED.md`에 실제로 있는 것만 인용한다.

## 절차

### 1. 플러그인 루트 찾기
이 `SKILL.md`가 있는 디렉토리의 **두 단계 상위(`../..`)**가 플러그인 루트다(`skills/musinsa-quickstart/SKILL.md` → 루트). 루트에서 `docs/quickstart.html`이 존재하는지 확인한다. 없으면 3)의 요약만 수행한다.

### 2. 사람 사용자를 위해 브라우저로 열기 시도
OS에 맞춰 `docs/quickstart.html`을 기본 브라우저로 연다(사람이 보면 가장 좋은 온보딩):
- macOS: `open <루트>/docs/quickstart.html`
- Windows(PowerShell): `Start-Process <루트>\docs\quickstart.html` — 또는 `cmd /c start "" <루트>\docs\quickstart.html`
- Linux: `xdg-open <루트>/docs/quickstart.html`

명령이 실패하거나 헤드리스/무GUI 환경이면 조용히 건너뛰고 3)으로 진행한다(오류로 중단하지 않는다).

### 3. 채팅 출력 — 문서가 열렸으면 짧게, 못 열었을 때만 요약

**2)에서 브라우저 열기에 성공한 경우(기본)**: 문서가 곧 온보딩이다. **HTML에 이미 있는 내용(샘플 표·설치 명령·경제 효과 등)을 채팅에 다시 옮기지 않는다.** 채팅 출력은 아래 3줄을 넘지 않는다:
1. 소개 문서를 브라우저에 띄웠다는 확인 한 줄
2. 용도 한 줄: 무신사 상품 표시정보(혼용률·원산지·친환경 표현·시험성적서) 컴플라이언스를 검수·재판정하는 도구
3. 시연 제안 한 줄: "번들 샘플 `sample/input.product.json`으로 바로 시연해볼까요? (기대 판정: **BLOCK**)"

**브라우저 열기에 실패한 경우(헤드리스/무GUI)에만** `docs/quickstart.html`을 직접 읽어 채팅으로 요약한다:
- **용도 1~2줄**(위와 동일)
- **샘플 파일 표**(파일 → 시나리오 → 기대 판정) — 문서/`sample/EXPECTED.md`에 있는 값 그대로:

  | 파일 | 시나리오 | 기대 판정 |
  |---|---|---|
  | `sample/input.product.json` | 기둥 B 단건 정합성(안감 주장 vs 성적서 불일치) | **BLOCK** |
  | `sample/input.product.png` | 같은 상품의 등록 화면 캡처 — 실사용 이미지 입력 데모(성적서 미첨부) | **BLOCK** |
  | `sample/input.pass.json` | 오탐 방지 대조군(면 100% = 성적서 일치) | **PASS** |
  | `sample/input.rescan.json` | 정책(룰) 갱신 → 전 코퍼스 소급 재스캔 | 코퍼스 4건: **BLOCK 2 / PASS 1 / REVIEW 1**(자사 PB 포함) |

- **사용법 3경로 요약**: ① 앱에서 "사용해 보기" 클릭 ② 채팅에 프롬프트 복붙(예: `listing-compliance 스킬로 sample/input.product.json을 검수해줘`) ③ CLI(`codex plugin marketplace add …` → `codex plugin add …` → `codex exec`).
- 마지막에 위 시연 제안 한 줄.

### 4. 시연 수락 시
사용자가 수락하면 **listing-compliance** 스킬 절차로 넘겨 검수를 진행한다(이 스킬은 검수를 직접 수행하지 않는다).
