"""입력 문서 정규화 — 고객사 자료(.md/.csv)를 라인단위 Unit으로.

에이전트/그라운딩이 근거를 file:line 으로 추적할 수 있도록 1-indexed 라인 보존.
순수 stdlib.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

_PUNCT = re.compile(r"[,.·:;~\-–—()\[\]\"'`!?/]")
_WS = re.compile(r"\s+")


@dataclass(frozen=True)
class Unit:
    file: str
    line: int  # 1-indexed
    text: str


def normalize_text(s: str) -> str:
    """문장부호를 공백으로 치환하고 공백을 눌러 느슨한 비교에 쓰는 정규화."""
    s = _PUNCT.sub(" ", s.strip().lower())
    return _WS.sub(" ", s).strip()


def load_docs(directory: str | Path) -> list[Unit]:
    """디렉토리의 .md/.csv를 읽어 Unit 목록으로. .md=줄단위, .csv=행단위(셀 결합)."""
    directory = Path(directory)
    units: list[Unit] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() == ".md":
            for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                text = raw.strip()
                if text:
                    units.append(Unit(path.name, i, text))
        elif path.suffix.lower() == ".csv":
            with path.open(encoding="utf-8", newline="") as fh:
                for i, row in enumerate(csv.reader(fh), start=1):
                    cells = [c.strip() for c in row if c and c.strip()]
                    if cells:
                        units.append(Unit(path.name, i, " | ".join(cells)))
    return units
