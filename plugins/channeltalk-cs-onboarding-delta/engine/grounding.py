"""그라운딩 — 인용 실재성 검증(환각0 하드게이트).

각 델타 인용문(source_quote)이 참조 파일의 실제 텍스트에 존재하는지 확인한다.
존재하지 않으면(에이전트가 지어낸 인용) 위반으로 분리해 리포트에서 '근거 불명'으로 강등한다.
순수 stdlib.
"""
from __future__ import annotations

from engine.delta_engine import Delta
from engine.normalize import Unit, normalize_text


def _file_texts(units: list[Unit]) -> dict[str, str]:
    acc: dict[str, list[str]] = {}
    for u in units:
        acc.setdefault(u.file, []).append(u.text)
    return {f: normalize_text(" ".join(t)) for f, t in acc.items()}


def verify(deltas: list[Delta], units: list[Unit]) -> tuple[list[Delta], list[dict]]:
    """(근거 검증 통과 델타, 위반 목록) 반환. 델타의 모든 인용이 파일에 실재하면 통과."""
    norm_file = _file_texts(units)
    ok: list[Delta] = []
    violations: list[dict] = []
    for d in deltas:
        bad = []
        for c in d.citations:
            q = normalize_text(c.quote)
            if q and q not in norm_file.get(c.file, ""):
                bad.append(c)
        if bad:
            violations.append({
                "slot_id": d.slot_id,
                "label": d.label,
                "bad": [{"file": c.file, "line": c.line, "quote": c.quote} for c in bad],
            })
        else:
            ok.append(d)
    return ok, violations
