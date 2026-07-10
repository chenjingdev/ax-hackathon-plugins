"""CLI 오케스트레이션 — normalize → (에이전트 extraction) → classify → grounding → report.

에이전트 표면(Codex, SKILL.md)이 extraction.json을 만들고, 여기서 결정론 파이프라인을 돌린다.
extraction 미지정 시 에이전트가 무엇을 만들어야 하는지 안내한다.
순수 stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine.delta_engine import classify, counts
from engine.grounding import verify
from engine.normalize import load_docs
from engine.report import render_json, render_md

BASELINE_DIR = Path(__file__).resolve().parent.parent / "baseline"


def _read_baseline(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"[에러] 베이스라인 없음: {path}")
    # utf-8-sig: codex/에디터가 붙일 수 있는 UTF-8 BOM(EF BB BF)을 관대하게 흡수한다.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_baseline(domain: str) -> dict:
    return _read_baseline(BASELINE_DIR / f"{domain}.json")


def _docs_name(docs: str | list[str]) -> str:
    """회사명 폴백용 — 첫 문서 경로에서 이름을 뽑는다(파일이면 stem, 폴더면 name)."""
    first = docs[0] if isinstance(docs, list) else docs
    p = Path(first)
    return p.stem if p.suffix else p.name


def run(docs, domain: str, extraction_path: str, out_dir: str | None = None,
        baseline_path: str | None = None) -> dict:
    if baseline_path:
        baseline = _read_baseline(Path(baseline_path))
        baseline_label = f"첨부된 표준 CS 매뉴얼({Path(baseline_path).name})"
    else:
        baseline = load_baseline(domain)
        baseline_label = None  # render_*가 동봉 표준 라벨을 기본값으로 채운다
    units = load_docs(docs)
    # utf-8-sig: codex 출력이 BOM으로 오더라도 JSONDecodeError 없이 파싱한다.
    extraction = json.loads(Path(extraction_path).read_text(encoding="utf-8-sig"))
    deltas = classify(baseline["slots"], extraction)
    ok, violations = verify(deltas, units)
    company = extraction.get("company") or _docs_name(docs)
    md = render_md(ok, violations, company, baseline_label=baseline_label)
    js = render_json(ok, violations, company, baseline_label=baseline_label)
    if out_dir:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{company}.report.md").write_text(md, encoding="utf-8")
        (out / f"{company}.report.json").write_text(
            json.dumps(js, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"md": md, "json": js, "company": company}


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows cp949 콘솔 대응
        except Exception:
            pass
    p = argparse.ArgumentParser(description="CS 온보딩 차이점 도우미")
    p.add_argument("--docs", required=True, nargs="+",
                   help="고객사 문서 — 디렉토리 또는 파일(들). 시연 폴더에 표준 매뉴얼이 함께 있어도 고객사 문서만 지정할 수 있다")
    p.add_argument("--domain", default="ecommerce-cs")
    p.add_argument("--baseline", help="기준 baseline JSON 경로(미지정 시 동봉 baseline/<domain>.json). 첨부 표준 매뉴얼을 컴파일한 JSON을 넘길 수 있다")
    p.add_argument("--extraction", help="에이전트 추출 JSON(extraction.json)")
    p.add_argument("--out", default="out", help="리포트 출력 디렉토리")
    args = p.parse_args(argv)

    if not args.extraction:
        base = _read_baseline(Path(args.baseline)) if args.baseline else load_baseline(args.domain)
        print(
            "[안내] extraction.json이 필요합니다.\n"
            "  이 CLI는 결정론 파이프라인(분류·검증·리포트)만 실행합니다.\n"
            "  에이전트(Codex)가 SKILL.md 절차대로 문서를 읽어 각 표준 슬롯의 답을\n"
            "  추출한 extraction.json을 먼저 만든 뒤 --extraction 으로 넘기세요.\n"
            f"  기준 슬롯: {[s['slot_id'] for s in base['slots']]}",
            file=sys.stderr)
        return 2

    res = run(args.docs, args.domain, args.extraction, args.out, baseline_path=args.baseline)
    print(res["md"])
    c = res["json"]["summary"]
    print(f"\n[요약] {res['company']}: "
          f"SAME {c['SAME']} DIFFERENT {c['DIFFERENT']} MISSING {c['MISSING']} "
          f"CONFLICT {c['CONFLICT']} EXTRA {c['EXTRA']} "
          f"| 근거불명 {len(res['json']['grounding_violations'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
