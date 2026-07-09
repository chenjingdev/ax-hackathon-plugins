# 베이스라인 슬롯 → 공개 출처 매핑

> `ecommerce-cs.json`의 각 슬롯 `baseline_answer`가 어디서 왔는지. **공개 1차 조문 기반**과 **[SYNTH] 업계 관행 자작**을 정직하게 구분한다. 자작 표준값은 "일반적으로 이렇다"는 기준선일 뿐, 법적 강제가 아니다 — 고객사가 다르면 고객사 값이 이긴다(DIFFERENT).

## 공개 1차 조문 기반 (법령·고시)
| 슬롯 | 근거 | 공개 출처 |
|---|---|---|
| withdrawal-period | 전자상거래법 제17조(청약철회 7일) | law.go.kr 전자상거래 등에서의 소비자보호에 관한 법률 |
| return-shipping-fee | 표준약관·소비자분쟁해결기준(단순변심=구매자 부담) | ftc.go.kr 소비자분쟁해결기준 · 전자상거래 표준약관 |
| defect-return | 소비자분쟁해결기준(하자·오배송=판매자 부담) | ftc.go.kr 소비자분쟁해결기준 |
| refund-period | 전자상거래법 제18조(3영업일 환급) | law.go.kr 전자상거래법 |
| order-cancel | 전자상거래 표준약관 | 공정위 표준약관 |
| as-warranty | 소비자분쟁해결기준(품질보증) | ftc.go.kr 소비자분쟁해결기준 |

## [SYNTH] 업계 관행 자작 표준값 (공개 조문 아님 — 정직성 라벨)
delivery-lead-time · delivery-tracking · delivery-fee · order-change · exchange-process · refund-method · payment-methods · receipt-proof · soldout-restock · member-withdrawal · privacy-optout · cs-hours · overseas-shipping · coupon-point

> 이들은 이커머스 CS에서 관행적으로 통용되는 기본값을 조사자가 표준화한 것이다. 실제 온보딩에서는 AX 컨설턴트가 축적한 도메인 베이스로 대체·정련된다. 예선 데모에서는 공개/합성 근거로만 방어한다.
