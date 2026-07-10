## 온보딩 차이점 리포트 — acme-shop (도메인: 이커머스 CS)
기준: 첨부된 표준 CS 매뉴얼(compiled-baseline.json)
요약: 표준과 동일(SAME) 10 · 이 회사만 다름(DIFFERENT) 1 · 문서에 없음(MISSING) 2 · 서로 어긋남(CONFLICT) 1 · 신규 주제(EXTRA) 1

### ⚠ 안내가 서로 어긋남 (CONFLICT) — 먼저 확인 — 1
- [refund-period] 환불은 언제까지 처리되나요?
    · 상충 값: 7영업일 이내 / 3일 이내
    · acme-shop.md:17  "7영업일 이내에 처리"
    · acme-shop.md:29  "3일 이내 처리"

### ✎ 이 회사만 다른 정책 (DIFFERENT) — 검수 후 반영 — 1
- [return-shipping-fee] 단순변심 반품 시 배송비는 누가 부담하나요?
    · 표준: 단순변심 반품은 구매자가 반품 배송비를 부담합니다.
    · 이 회사: 단순변심도 반품 배송비 무료
    · acme-shop.md:43  "단순변심의 경우에도 반품 배송비를 무료"

### ▢ 문서에 없는 항목 (MISSING) — 고객사에 질문 — 2
- [order-change] 주문 정보(옵션·주소)를 변경할 수 있나요?
    · 문서에 근거 없음 → 고객사 확인 필요
- [exchange-process] 교환 절차는 어떻게 되나요?
    · 문서에 근거 없음 → 고객사 확인 필요

### ＋ 표준에 없는 신규 주제 (EXTRA) — 슬롯 후보 — 1
- [정기구독 해지] 정기구독 해지
    · 신규 주제: 정기구독 해지
    · acme-shop.md:24  "정기구독 해지는 마이페이지"

### ✓ 표준과 동일 (SAME) — 재작성 불필요 — 10
    delivery-lead-time, delivery-tracking, delivery-fee, order-cancel, withdrawal-period, defect-return, refund-method, member-withdrawal, cs-hours, overseas-shipping

---
_모든 항목은 사람 검수 필요(reviewed_by: human-required). 자동 반영·발송 없음._