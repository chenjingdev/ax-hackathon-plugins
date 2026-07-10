"""리포트 렌더 — 차이점(Delta)을 사람용 마크다운 + 기계용 JSON으로.

글래스박스: 모든 항목에 출처(file:line + 인용문). 자동 반영 없음(reviewed_by).
순수 stdlib.
"""
from __future__ import annotations

from engine.delta_engine import Delta, counts

_ORDER = ["CONFLICT", "DIFFERENT", "MISSING", "EXTRA"]
_TITLE = {
    "CONFLICT": "⚠ 안내가 서로 어긋남 (CONFLICT) — 먼저 확인",
    "DIFFERENT": "✎ 이 회사만 다른 정책 (DIFFERENT) — 검수 후 반영",
    "MISSING": "▢ 문서에 없는 항목 (MISSING) — 고객사에 질문",
    "EXTRA": "＋ 표준에 없는 신규 주제 (EXTRA) — 슬롯 후보",
}


def _cite_lines(d: Delta) -> list[str]:
    return [f'    · {c.file}:{c.line}  "{c.quote}"' for c in d.citations]


def render_md(deltas: list[Delta], violations: list[dict] | None = None, company: str = "") -> str:
    violations = violations or []
    c = counts(deltas)
    out: list[str] = []
    out.append(f"## 온보딩 차이점 리포트 — {company or '고객사'} (도메인: 이커머스 CS)")
    out.append(
        f"요약: 표준과 동일(SAME) {c['SAME']} · 이 회사만 다름(DIFFERENT) {c['DIFFERENT']} · "
        f"문서에 없음(MISSING) {c['MISSING']} · 서로 어긋남(CONFLICT) {c['CONFLICT']} · "
        f"신규 주제(EXTRA) {c['EXTRA']}"
    )
    out.append("")
    for label in _ORDER:
        group = [d for d in deltas if d.label == label]
        if not group:
            continue
        out.append(f"### {_TITLE[label]} — {len(group)}")
        for d in group:
            head = f"- [{d.slot_id}] {d.canonical_question}"
            out.append(head)
            if label == "DIFFERENT":
                out.append(f"    · 표준: {d.baseline_answer}")
                out.append(f"    · 이 회사: {d.company_answer}")
            elif label == "CONFLICT":
                out.append(f"    · 상충 값: {d.company_answer}")
            elif label == "MISSING":
                out.append("    · 문서에 근거 없음 → 고객사 확인 필요")
            elif label == "EXTRA":
                out.append(f"    · 신규 주제: {d.company_answer}")
            out.extend(_cite_lines(d))
        out.append("")
    same = [d.slot_id for d in deltas if d.label == "SAME"]
    if same:
        out.append(f"### ✓ 표준과 동일 (SAME) — 재작성 불필요 — {len(same)}")
        out.append("    " + ", ".join(same))
        out.append("")
    if violations:
        out.append(f"### ✗ 근거 불명 (인용이 문서에 없어 제외됨) — {len(violations)}")
        for v in violations:
            for b in v["bad"]:
                out.append(f'    · [{v["slot_id"]}] {b["file"]}:{b["line"]} "{b["quote"]}" ← 문서에 없음')
        out.append("")
    out.append("---")
    out.append("_모든 항목은 사람 검수 필요(reviewed_by: human-required). 자동 반영·발송 없음._")
    return "\n".join(out)


def _delta_json(d: Delta) -> dict:
    return {
        "slot_id": d.slot_id,
        "label": d.label,
        "category": d.category,
        "canonical_question": d.canonical_question,
        "baseline_answer": d.baseline_answer,
        "company_answer": d.company_answer,
        "citations": [{"file": c.file, "line": c.line, "quote": c.quote} for c in d.citations],
        "note": d.note,
    }


def render_json(deltas: list[Delta], violations: list[dict] | None = None, company: str = "") -> dict:
    return {
        "company": company,
        "domain": "ecommerce-cs",
        "summary": counts(deltas),
        "deltas": [_delta_json(d) for d in deltas],
        "grounding_violations": violations or [],
        "reviewed_by": "human-required",
    }
