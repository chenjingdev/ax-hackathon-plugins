# rules/sources.md — 규칙 → 공개 출처(E1~E6) 매핑

> `ruleset.json`의 각 규칙 `basis`가 참조하는 공개 근거(SPEC §1.2 / §11.2)의 사람용 매핑이다.
> 모든 위반은 아래 공개 URL로 추적 가능해야 한다(비공개·미검증 수치 단정 금지 — SPEC §11.4#2).

## 공개 근거 (E1~E6)

| ID | 공개 사실 | 출처(공개 URL) |
|---|---|---|
| **E1** | 공정위, 무신사 스탠다드(자사 PB) 인조가죽 제품의 **'#에코레더'** 친환경 표현 광고(2021~2024.8.19)를 **표시광고법 위반으로 경고**(패션업계 친환경 표시광고 첫 제재) | https://www.intn.co.kr/news/articleView.html?idxno=2043500 |
| **E2** | 무신사 자체 전수조사: 다운·캐시미어 상품 **7,968개 중 약 8.5%(677개)** 혼용률 등 표기 기준 미달(2025-03-25 발표) | https://www.sedaily.com/NewsView/2GQDT2GBT7 |
| **E3** | 마르진(MARZIN) **'택갈이'** — 중국산 10만원대 구두를 미국 호윈(Horween) 가죽으로 홍보, 60~70만원대 판매(마크업 약 600~700%) | 브랜드명 명시: https://news.bizwatch.co.kr/article/consumer/2026/03/13/0029 · 마크업·중국원가(판매자 'A사' 익명): https://www.reportera.co.kr/news/musinsa-tag-switching-fraud-china-shoes-scandal/ |
| **E4** | 전수조사·**시험성적서 의무화** 약속 1년 내 패딩 충전재 오표기 재발 — 사전 자동검증 부재로 사후 적발 의존 구조 | https://alphabiz.co.kr/news/view/1065615419880479 |
| **E5** | 표시·광고의 공정화에 관한 법률 제3조(거짓·과장/기만/부당비교/비방 광고 금지) 및 공정위 환경성 표시·광고 심사지침 | 표시광고법 §3 / 공정거래위원회 환경성 표시·광고 심사지침 (공개 법령·지침) |
| **E6** | 무신사, 입점 브랜드용 **그린워싱(친환경 표시) 가이드** 자체 발간·품질/표시 교육 | 무신사 공식 발표(공개) — 정확한 발간일·URL은 SPEC §11.4#1 |

## 규칙 → 근거 매핑 (15룰, layer 포함)

| 규칙 ID | layer | family | 근거(E) | 심각도 | 공개 출처 |
|---|---|---|---|---|---|
| **GW-01** | pillar_a | GW | E1, E5, E6 | BLOCK | E1·E5·E6 |
| **GW-02** | pillar_a | GW | E1 | BLOCK | E1 |
| **GW-03** | pillar_a | GW | E5, E6 | WARN | E5·E6 |
| **GW-04** | pillar_a | GW | E1 | BLOCK | E1 |
| **MX-01** | pillar_b | MX | E2 | BLOCK | E2 |
| **MX-02** | preprocess | MX | E2 | WARN | E2 |
| **MX-03** | pillar_b | MX | E2, E4 | BLOCK | E2·E4 |
| **MX-04** | pillar_b | MX | E2, E4 | BLOCK | E2·E4 |
| **TC-01** | pillar_b | TC | E2, E4 | BLOCK | E2·E4 |
| **TC-02** | pillar_b | TC | E2 | WARN | E2 |
| **TC-03** | preprocess | TC | E4 | WARN | E4 |
| **TS-01** | pillar_b | TS | E3 | BLOCK | E3 |
| **TS-02** | pillar_b | TS | E3 | WARN | E3 |
| **OR-01** | preprocess | OR | E5 | WARN | E5 |
| **OR-02** | pillar_b | OR | E3, E5 | WARN | E3·E5 |

- **pillar_a**(기둥 A 그린워싱·진화표현): GW-01~04
- **pillar_b**(기둥 B 정합성): MX-01·MX-03·MX-04·TC-01·TC-02·TS-01·TS-02·OR-02
- **preprocess**(전처리 구조검사·강등): MX-02·TC-03·OR-01

> URL이 없는 E5(법령)·E6(가이드)는 공개 법령·공식 발표로 추적 가능한 1차 근거다. 모든 규칙의 `basis`는 위 표의 E1~E6 중 하나 이상을 참조한다.
