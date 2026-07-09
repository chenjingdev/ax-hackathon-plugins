---
name: meditherapy-quickstart
description: meditherapy-seeding-screener 플러그인의 사용법·구조·샘플 시연 안내가 필요할 때(퀵스타트/quickstart/사용법/시작하기/온보딩/이 플러그인 뭐야 등) 사용. 플러그인 루트 docs/quickstart.html을 브라우저로 열고 핵심 요약과 샘플 시연을 제안한다.
---

# meditherapy-seeding-screener 퀵스타트 안내

**읽기 전용 온보딩 스킬이다. 파일을 수정하지 않고, 판정·수치를 즉석에서 창작하지 않는다.**
모든 사실(샘플 판정·명령어)은 아래 문서와 `sample/EXPECTED.md`에서 그대로 인용한다.

## 절차

### 1) 문서 위치 확인
이 SKILL.md의 **두 단계 상위**(`../..`)가 플러그인 루트다. 거기서 `docs/quickstart.html`이 있는지 확인한다.
(예: 이 파일이 `<루트>/skills/meditherapy-quickstart/SKILL.md`이면 문서는 `<루트>/docs/quickstart.html`.)

### 2) OS 브라우저로 열기 시도
플랫폼에 맞는 명령으로 문서를 연다. 실패하거나 헤드리스 환경이면 조용히 건너뛴다(에러로 중단하지 않음).
- macOS: `open "<루트>/docs/quickstart.html"`
- Windows: `Start-Process "<루트>\docs\quickstart.html"` (또는 `cmd /c start "" "<루트>\docs\quickstart.html"`)
- Linux: `xdg-open "<루트>/docs/quickstart.html"`

### 3) 채팅 출력 — 문서가 열렸으면 짧게, 못 열었을 때만 요약

**2)에서 브라우저 열기에 성공한 경우(기본)**: 문서가 곧 온보딩이다. **HTML에 이미 있는 내용(샘플 표·설치 명령·경제 효과 등)을 채팅에 다시 옮기지 않는다.** 채팅 출력은 아래 3줄을 넘지 않는다:
1. 소개 문서를 브라우저에 띄웠다는 확인 한 줄
2. 용도 한 줄: 시딩 후보의 공개 콘텐츠를 구매유발 5차원으로 채점해 팔로워 수 대신 콘텐츠 결로 후보를 고르는 도구
3. 시연 제안 한 줄: "`sample/input.kr.json`으로 시연해볼까요? 팔로워 1·2위 메가 후보가 바닥으로 내려가고 8.6k 마이크로 후보가 **1위(≈78)** 로 역전되는 데모입니다."

**브라우저 열기에 실패한 경우(헤드리스/무GUI)에만** `docs/quickstart.html`을 직접 읽어 채팅에 요약한다:
- **용도** 1~2줄: 시딩 후보의 공개 콘텐츠가 구매유발 콘텐츠 결에 얼마나 부합하는지 한국 동료심사 5차원으로 glass-box 스코어링.
- **샘플 표**: `input.kr.json`(헤드라인 역전 데모) · `input.low.json`(음성 N=12) · `input.rescan.json`(재스캔 delta) · `input.sagraph.json`(DROP)과 각 기대 판정.
- **사용법 3경로**: ① 앱 "사용해 보기" ② 채팅 복붙 프롬프트 ③ CLI 설치+실행.
- 마지막에 위 시연 제안 한 줄.

### 4) 시연 수락 시
사용자가 수락하면 **seeding-screener** 스킬로 진행한다(해당 샘플을 입력으로 스크리닝 실행).

## 주의
- 이 스킬은 안내만 한다. 스코어링·리포트 생성은 seeding-screener 스킬과 `scoring/cli.py`가 수행한다.
- 기대 판정·점수는 `sample/EXPECTED.md`의 골든 값을 인용하고, 없는 수치를 지어내지 않는다.
