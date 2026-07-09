# 골든 기대 리포트 — acme-shop (합성 고객사)

> `python -m engine.cli --docs sample/acme-shop --domain ecommerce-cs --extraction sample/golden/acme-shop.extraction.json` 의 기대 출력. 합성 데이터(정직성 라벨). 심은 것: CONFLICT 1(환불 3일 vs 7영업일)·DIFFERENT 1(무료반품)·MISSING 2(주문변경·교환절차)·EXTRA 1(정기구독).

## 온보딩 델타 리포트 — acme-shop (도메인: 이커머스 CS)
요약: 공통 SAME 10 · 회사고유 DIFFERENT 1 · 공백 MISSING 2 · 모순 CONFLICT 1 · 신규 EXTRA 1

### ⚠ CONFLICT (문서끼리 모순 — 먼저 확인) — 1
- [refund-period] 환불은 언제까지 처리되나요?
    · 상충 값: 7영업일 이내 / 3일 이내
    · policy.md:13  "7영업일 이내에 처리"
    · faq.csv:2  "3일 이내 처리"

### ✎ DIFFERENT (이 회사만 다름 — 반영) — 1
- [return-shipping-fee] 단순변심 반품 시 배송비는 누가 부담하나요?
    · 베이스: 단순변심 반품은 구매자가 반품 배송비 부담(표준)
    · 이 회사: 단순변심도 반품 배송비 무료
    · product.md:7  "단순변심의 경우에도 반품 배송비를 무료"

### ▢ MISSING (공백 — 고객사에 질문) — 2
- [order-change] 주문 정보(옵션·주소)를 변경할 수 있나요?
    · 문서에 근거 없음 → 고객사 확인 필요
- [exchange-process] 교환 절차는 어떻게 되나요?
    · 문서에 근거 없음 → 고객사 확인 필요

### ＋ EXTRA (베이스에 없는 신규 — 슬롯 후보) — 1
- [정기구독 해지] 정기구독 해지
    · 신규 주제: 정기구독 해지
    · policy.md:20  "정기구독 해지는 마이페이지"

### ✓ SAME (베이스 그대로 — 재작성 불필요) — 10
    delivery-lead-time, delivery-tracking, delivery-fee, order-cancel, withdrawal-period, defect-return, refund-method, member-withdrawal, cs-hours, overseas-shipping

---
_모든 항목은 사람 검수 필요(reviewed_by: human-required). 자동 반영·발송 없음._