import json
import tempfile
import unittest
from pathlib import Path

from engine.cli import run


class TestCli(unittest.TestCase):
    def test_end_to_end(self):
        d = Path(tempfile.mkdtemp())
        (d / "product.md").write_text("배송 안내\n단순변심도 무료 반품 가능합니다\n", encoding="utf-8")
        extraction = {
            "company": "acme",
            "findings": [{
                "slot_id": "return-shipping-fee", "found": True,
                "extracted_answer": "단순변심 무료 반품", "matches_baseline": False,
                "source_file": "product.md", "source_line": 2,
                "source_quote": "단순변심도 무료 반품", "confidence": 0.9,
            }],
            "extra_candidates": [],
        }
        ext_path = d / "extraction.json"
        ext_path.write_text(json.dumps(extraction, ensure_ascii=False), encoding="utf-8")

        res = run(str(d), "ecommerce-cs", str(ext_path), out_dir=str(d / "out"))
        self.assertEqual(res["json"]["summary"]["DIFFERENT"], 1)
        self.assertIn("단순변심 무료 반품", res["md"])
        self.assertTrue((d / "out" / "acme.report.md").exists())
        # required 슬롯 다수는 문서에 없으므로 MISSING 이 잡혀야 함
        self.assertGreater(res["json"]["summary"]["MISSING"], 0)

    def test_hallucinated_quote_dropped(self):
        d = Path(tempfile.mkdtemp())
        (d / "product.md").write_text("배송 안내\n", encoding="utf-8")
        extraction = {
            "company": "acme", "extra_candidates": [],
            "findings": [{
                "slot_id": "return-shipping-fee", "found": True,
                "extracted_answer": "무료 반품", "matches_baseline": False,
                "source_file": "product.md", "source_line": 2,
                "source_quote": "이 문장은 문서에 없다 지어냄", "confidence": 0.9,
            }],
        }
        ext_path = d / "extraction.json"
        ext_path.write_text(json.dumps(extraction, ensure_ascii=False), encoding="utf-8")
        res = run(str(d), "ecommerce-cs", str(ext_path))
        self.assertEqual(len(res["json"]["grounding_violations"]), 1)

    def test_extraction_with_utf8_bom_does_not_crash(self):
        # codex 출력이 UTF-8 BOM(EF BB BF)으로 와도 JSONDecodeError 없이 파싱돼야 한다.
        d = Path(tempfile.mkdtemp())
        (d / "product.md").write_text("배송 안내\n단순변심도 무료 반품 가능합니다\n", encoding="utf-8")
        extraction = {
            "company": "acme", "extra_candidates": [],
            "findings": [{
                "slot_id": "return-shipping-fee", "found": True,
                "extracted_answer": "단순변심 무료 반품", "matches_baseline": False,
                "source_file": "product.md", "source_line": 2,
                "source_quote": "단순변심도 무료 반품", "confidence": 0.9,
            }],
        }
        ext_path = d / "extraction.json"
        # BOM 포함 저장(utf-8-sig)
        ext_path.write_text(json.dumps(extraction, ensure_ascii=False), encoding="utf-8-sig")
        res = run(str(d), "ecommerce-cs", str(ext_path))
        self.assertEqual(res["json"]["summary"]["DIFFERENT"], 1)


if __name__ == "__main__":
    unittest.main()
