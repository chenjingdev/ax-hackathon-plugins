import unittest

from engine.delta_engine import Cite, Delta
from engine.report import render_json, render_md


def _deltas():
    return [
        Delta("refund-period", "CONFLICT", "환불", "환불 언제?", "3영업일", "3일 / 7영업일",
              citations=[Cite("faq.csv", 2, "환불 3일"), Cite("policy.md", 5, "환불 7영업일")]),
        Delta("return-shipping-fee", "DIFFERENT", "반품", "반품 배송비?", "구매자 부담", "무료 반품",
              citations=[Cite("product.md", 8, "단순변심 무료 반품")]),
        Delta("exchange-process", "MISSING", "교환", "교환 절차?", "회수 후 재발송", None, citations=[]),
        Delta("cs-hours", "SAME", "CS", "운영시간?", "평일", "평일 10-6", citations=[Cite("policy.md", 1, "평일")]),
    ]


class TestReport(unittest.TestCase):
    def test_md_conflict_first_and_cited(self):
        md = render_md(_deltas(), company="acme")
        # 섹션 헤더(마커) 기준 순서 — 요약 라인의 단어가 아니라
        self.assertLess(md.index("### ⚠"), md.index("### ✎"))
        self.assertIn('faq.csv:2', md)
        self.assertIn("환불 3일", md)

    def test_md_same_is_count_only(self):
        md = render_md(_deltas())
        self.assertIn("SAME (베이스 그대로", md)
        self.assertIn("cs-hours", md)

    def test_md_reviewed_by_present(self):
        self.assertIn("human-required", render_md(_deltas()))

    def test_json_shape(self):
        j = render_json(_deltas(), company="acme")
        self.assertEqual(j["reviewed_by"], "human-required")
        self.assertEqual(j["summary"]["CONFLICT"], 1)
        self.assertEqual(len(j["deltas"]), 4)

    def test_md_violations_section(self):
        md = render_md(_deltas(), violations=[{"slot_id": "x", "label": "DIFFERENT",
                       "bad": [{"file": "a.md", "line": 3, "quote": "지어낸 인용"}]}])
        self.assertIn("근거 불명", md)


if __name__ == "__main__":
    unittest.main()
