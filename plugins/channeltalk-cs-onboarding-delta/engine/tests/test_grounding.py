import unittest

from engine.delta_engine import Cite, Delta
from engine.grounding import verify
from engine.normalize import Unit


def _delta(quote, file="policy.md", line=5):
    return Delta("refund-period", "DIFFERENT", "환불", "환불 언제", "7영업일", "3일",
                 citations=[Cite(file, line, quote)])


class TestGrounding(unittest.TestCase):
    def test_real_quote_passes(self):
        units = [Unit("policy.md", 5, "환불은 7영업일 이내 처리됩니다")]
        ok, viol = verify([_delta("환불은 7영업일 이내")], units)
        self.assertEqual(len(ok), 1)
        self.assertEqual(viol, [])

    def test_hallucinated_quote_flagged(self):
        units = [Unit("policy.md", 5, "환불은 7영업일 이내 처리됩니다")]
        ok, viol = verify([_delta("무료 반품 100% 보장")], units)
        self.assertEqual(ok, [])
        self.assertEqual(len(viol), 1)
        self.assertEqual(viol[0]["slot_id"], "refund-period")

    def test_missing_delta_no_citations_ok(self):
        d = Delta("exchange-process", "MISSING", "교환", "교환 절차", "x", None, citations=[])
        ok, viol = verify([d], [Unit("policy.md", 1, "아무 텍스트")])
        self.assertEqual(len(ok), 1)

    def test_quote_in_wrong_file_flagged(self):
        units = [Unit("policy.md", 5, "환불 7영업일"), Unit("faq.csv", 2, "배송 문의")]
        ok, viol = verify([_delta("환불 7영업일", file="faq.csv")], units)
        self.assertEqual(len(viol), 1)


if __name__ == "__main__":
    unittest.main()
