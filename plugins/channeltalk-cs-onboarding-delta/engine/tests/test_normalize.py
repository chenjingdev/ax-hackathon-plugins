import tempfile
import unittest
from pathlib import Path

from engine.normalize import Unit, load_docs, normalize_text


class TestNormalize(unittest.TestCase):
    def _dir(self, files: dict) -> Path:
        d = Path(tempfile.mkdtemp())
        for name, content in files.items():
            (d / name).write_text(content, encoding="utf-8")
        return d

    def test_load_md_lines(self):
        d = self._dir({"policy.md": "첫 줄\n\n환불은 7영업일 이내\n"})
        units = load_docs(d)
        self.assertTrue(any(u.file == "policy.md" and "7영업일" in u.text for u in units))

    def test_load_csv_rows(self):
        d = self._dir({"faq.csv": "질문,답변\n환불 언제,3일 내\n"})
        units = load_docs(d)
        self.assertTrue(any(u.file == "faq.csv" and "3일" in u.text for u in units))

    def test_line_numbers_1indexed(self):
        d = self._dir({"policy.md": "A\nB\n환불 7영업일\n"})
        units = [u for u in load_docs(d) if "7영업일" in u.text]
        self.assertEqual(units[0].line, 3)

    def test_blank_lines_skipped(self):
        d = self._dir({"a.md": "X\n\n\nY\n"})
        lines = [u.line for u in load_docs(d)]
        self.assertEqual(lines, [1, 4])

    def test_normalize_text_loose(self):
        self.assertEqual(normalize_text("  환불 7-영업일!! "), normalize_text("환불 7 영업일"))


if __name__ == "__main__":
    unittest.main()
