import unittest

from engine.delta_engine import classify, counts


def _finding(slot, ans, matches, file="doc.md", line=1, quote=None):
    return {"slot_id": slot, "found": True, "extracted_answer": ans,
            "matches_baseline": matches, "source_file": file, "source_line": line,
            "source_quote": quote or ans}


class TestDelta(unittest.TestCase):
    def test_conflict_when_two_sources_differ(self):
        base = [{"slot_id": "refund-period", "expectation": "required", "baseline_answer": "7영업일"}]
        ext = {"findings": [
            _finding("refund-period", "3일", False, "faq.csv", 2, "환불 3일"),
            _finding("refund-period", "7영업일", True, "policy.md", 5, "환불 7영업일"),
        ], "extra_candidates": []}
        d = [x for x in classify(base, ext) if x.slot_id == "refund-period"][0]
        self.assertEqual(d.label, "CONFLICT")
        self.assertEqual(len(d.citations), 2)

    def test_missing_when_required_absent(self):
        base = [{"slot_id": "exchange-process", "expectation": "required", "baseline_answer": "x"}]
        d = classify(base, {"findings": [], "extra_candidates": []})[0]
        self.assertEqual(d.label, "MISSING")

    def test_optional_absent_not_reported(self):
        base = [{"slot_id": "coupon-point", "expectation": "optional", "baseline_answer": "x"}]
        self.assertEqual(classify(base, {"findings": [], "extra_candidates": []}), [])

    def test_same_when_matches_baseline(self):
        base = [{"slot_id": "withdrawal-period", "expectation": "required", "baseline_answer": "7일 이내"}]
        ext = {"findings": [_finding("withdrawal-period", "7일 이내", True)], "extra_candidates": []}
        self.assertEqual(classify(base, ext)[0].label, "SAME")

    def test_different_when_not_matches(self):
        base = [{"slot_id": "return-shipping-fee", "expectation": "required", "baseline_answer": "구매자 부담"}]
        ext = {"findings": [_finding("return-shipping-fee", "무료 반품", False, "product.md", 8)], "extra_candidates": []}
        d = classify(base, ext)[0]
        self.assertEqual(d.label, "DIFFERENT")
        self.assertEqual(d.company_answer, "무료 반품")

    def test_extra_candidate(self):
        base = [{"slot_id": "a", "expectation": "optional", "baseline_answer": "x"}]
        ext = {"findings": [], "extra_candidates": [
            {"topic": "정기구독 해지", "source_file": "policy.md", "source_line": 20, "source_quote": "정기구독 해지는"}]}
        labels = [d.label for d in classify(base, ext)]
        self.assertIn("EXTRA", labels)

    def test_coverage_all_required_present(self):
        base = [{"slot_id": "a", "expectation": "required", "baseline_answer": "x"},
                {"slot_id": "b", "expectation": "required", "baseline_answer": "y"}]
        covered = {d.slot_id for d in classify(base, {"findings": [], "extra_candidates": []})}
        self.assertEqual(covered, {"a", "b"})

    def test_counts_helper(self):
        base = [{"slot_id": "a", "expectation": "required", "baseline_answer": "x"}]
        c = counts(classify(base, {"findings": [], "extra_candidates": []}))
        self.assertEqual(c["MISSING"], 1)

    def test_same_meaning_different_wording_is_not_conflict(self):
        # 프로브: 표현만 다른 동일의미(둘 다 baseline과 같은 뜻) → CONFLICT 아님(SAME).
        # 옛 로직(정규화 문자열 distinct>=2)은 이걸 거짓 CONFLICT로 올렸다.
        base = [{"slot_id": "cs-hours", "expectation": "required", "baseline_answer": "평일 운영"}]
        ext = {"findings": [
            _finding("cs-hours", "평일 10시~18시 운영", True, "policy.md", 17),
            _finding("cs-hours", "평일 오전10시-오후6시", True, "faq.csv", 5),
        ], "extra_candidates": []}
        d = [x for x in classify(base, ext) if x.slot_id == "cs-hours"][0]
        self.assertEqual(d.label, "SAME")

    def test_conflict_uses_matches_baseline_not_string_distinctness(self):
        # 프로브: extracted_answer 문자열은 동일하지만 baseline 부합 판단이 갈리면 → CONFLICT.
        # 옛 로직(문자열 distinct=1)은 이 모순을 놓쳤다.
        base = [{"slot_id": "refund-period", "expectation": "required", "baseline_answer": "3영업일"}]
        ext = {"findings": [
            _finding("refund-period", "3일 이내", True, "faq.csv", 2, "환불 3일"),
            _finding("refund-period", "3일 이내", False, "policy.md", 13, "환불 3영업일"),
        ], "extra_candidates": []}
        d = [x for x in classify(base, ext) if x.slot_id == "refund-period"][0]
        self.assertEqual(d.label, "CONFLICT")


if __name__ == "__main__":
    unittest.main()
