"""델타 분류 — 결정론 바닥.

에이전트 추출(extraction)을 받아 각 베이스 슬롯을 5분류로 계산한다.
분류 판정은 여기(고정 로직)서만 하고, 에이전트는 추출·의미판단(matches_baseline)만 한다.
순수 stdlib.
"""
from __future__ import annotations

from dataclasses import dataclass, field

LABELS = ("SAME", "DIFFERENT", "MISSING", "CONFLICT", "EXTRA")


@dataclass(frozen=True)
class Cite:
    file: str
    line: int
    quote: str


@dataclass
class Delta:
    slot_id: str
    label: str
    category: str
    canonical_question: str
    baseline_answer: str
    company_answer: str | None
    citations: list[Cite] = field(default_factory=list)
    note: str = ""


def _cites(findings: list[dict]) -> list[Cite]:
    return [
        Cite(f.get("source_file", ""), int(f.get("source_line", 0) or 0), f.get("source_quote", ""))
        for f in findings
    ]


def classify(baseline_slots: list[dict], extraction: dict) -> list[Delta]:
    by_slot: dict[str, list[dict]] = {}
    for f in extraction.get("findings", []):
        if f.get("found"):
            by_slot.setdefault(f["slot_id"], []).append(f)

    deltas: list[Delta] = []
    for slot in baseline_slots:
        sid = slot["slot_id"]
        fs = by_slot.get(sid, [])
        common = dict(
            slot_id=sid,
            category=slot.get("category", ""),
            canonical_question=slot.get("canonical_question", ""),
            baseline_answer=slot.get("baseline_answer", ""),
        )
        if not fs:
            if slot.get("expectation") == "required":
                deltas.append(Delta(**common, label="MISSING", company_answer=None,
                                    note="required 슬롯인데 문서에서 근거 없음"))
            continue

        # 같은 슬롯의 finding들을 에이전트의 의미판단(matches_baseline)으로 분류한다.
        # matches_baseline = "이 답이 baseline과 실질적으로 같은 뜻인가"(에이전트가 판단).
        # CONFLICT는 문서 간 '문자열 distinctness'가 아니라 baseline 부합 여부의 '불일치'로 잡는다:
        #   - 부합/불부합이 섞이면(한 문서는 baseline과 같은 뜻, 다른 문서는 다른 뜻) → 회사 문서끼리
        #     실제로 상충 → CONFLICT. (표현만 다른 동일의미는 모두 부합이라 걸리지 않고, 서로 다른
        #     뜻을 같은 문구로 요약해도 부합 여부가 갈리면 잡힌다.)
        #   - 모두 부합 → SAME(표현이 달라도 같은 뜻이면 모순 아님).
        #   - 모두 불부합 → DIFFERENT(회사 고유 값, 문서끼리는 일치).
        matched = {bool(f.get("matches_baseline")) for f in fs}
        answer = fs[0].get("extracted_answer", "")
        if len(matched) >= 2:
            joined = " / ".join(f.get("extracted_answer", "") for f in fs)
            deltas.append(Delta(**common, label="CONFLICT", company_answer=joined,
                                citations=_cites(fs),
                                note="문서 간 상충(baseline 부합 여부 불일치) — 고객사 확인 필요"))
        elif True in matched:
            deltas.append(Delta(**common, label="SAME", company_answer=answer,
                                citations=_cites(fs)))
        else:
            deltas.append(Delta(**common, label="DIFFERENT", company_answer=answer,
                                citations=_cites(fs), note="이 회사 고유 값 — 반영"))

    for ex in extraction.get("extra_candidates", []):
        topic = ex.get("topic", "")
        deltas.append(Delta(slot_id=topic, label="EXTRA", category="(신규)",
                            canonical_question=topic, baseline_answer="", company_answer=topic,
                            citations=_cites([ex]), note="표준에 없는 신규 주제 — 슬롯 후보"))

    _assert_coverage(baseline_slots, deltas)
    return deltas


def _assert_coverage(baseline_slots: list[dict], deltas: list[Delta]) -> None:
    required = {s["slot_id"] for s in baseline_slots if s.get("expectation") == "required"}
    covered = {d.slot_id for d in deltas if d.label in ("SAME", "DIFFERENT", "MISSING", "CONFLICT")}
    gap = required - covered
    if gap:
        raise AssertionError(f"coverage gap (required 슬롯 누락): {sorted(gap)}")


def counts(deltas: list[Delta]) -> dict[str, int]:
    c = {label: 0 for label in LABELS}
    for d in deltas:
        c[d.label] = c.get(d.label, 0) + 1
    return c
