# AX 인재전쟁 — Codex Plugins

AX 인재전쟁 해커톤 예선 제출물. 참여 기업의 공개·검증 가능한 실무 문제를 푸는 OpenAI Codex 플러그인 3종을 하나의 마켓플레이스로 배포합니다.

| 플러그인 | 대상 기업 | 하는 일 |
|---|---|---|
| `musinsa-listing-compliance` | 무신사 | 상품 표시정보(소재·혼용률·친환경 표현·시험성적서)를 표시광고법·그린워싱 가이드에 대조해 변경 이벤트마다 위반 탐지·재판정, 정정·반려 사유서 생성 |
| `myrealtrip-listing-factcheck` | 마이리얼트립 | T&A 상품의 요일·시즌·연령 조건을 명소 공식 운영사실과 대조해 현지 사실 불일치 탐지, 정정·파트너 반려·고객 안내문 생성 |
| `meditherapy-seeding-screener` | 메디테라피 | 인플루언서 시딩 후보 콘텐츠를 한국 동료심사 근거 가중 5차원 온톨로지로 스코어링, 근거 원문 인용 glass-box 랭킹 숏리스트 산출 |

## 설치 (Codex CLI)

클론 없이 URL로 바로 추가·설치됩니다 (codex-cli 0.142.5에서 검증):

```bash
codex plugin marketplace add https://github.com/chenjingdev/ax-hackathon-plugins
codex plugin add musinsa-listing-compliance@ax-hackathon-plugins      # 필요한 것만 골라 설치
codex plugin add myrealtrip-listing-factcheck@ax-hackathon-plugins
codex plugin add meditherapy-seeding-screener@ax-hackathon-plugins
```

## 구조

- `plugins/<이름>/` — 각 플러그인 본체 (`.codex-plugin/plugin.json`, `skills/`, 룰셋·샘플 입력 포함)
- `.agents/plugins/marketplace.json` — 마켓플레이스 매니페스트

각 플러그인의 `sample/` 골든 입력으로 바로 시연할 수 있습니다. 모든 판정 근거는 공개 자료(법령·공식 운영정보·동료심사 논문) 기반이며, 결정론 바닥 + 에이전트 표면의 2계층 구조로 재현 가능합니다.
