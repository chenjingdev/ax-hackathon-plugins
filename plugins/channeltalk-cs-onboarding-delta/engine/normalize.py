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


def _load_file(path: Path, units: list[Unit]) -> None:
    """단일 .md/.csv 파일을 Unit으로 적재. .md=줄단위, .csv=행단위(셀 결합)."""
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


def load_docs(docs: str | Path | list[str | Path]) -> list[Unit]:
    """고객사 문서를 Unit 목록으로 적재.

    `docs`는 (1)디렉토리 (2)단일 파일 (3)파일·디렉토리 경로의 리스트 중 무엇이든 된다.
    디렉토리면 그 안의 .md/.csv를 훑고, 파일이면 그 파일만 문서로 취급한다
    (시연 폴더에 표준 매뉴얼이 함께 있어도 고객사 문서만 지정할 수 있도록).
    """
    specs = [docs] if isinstance(docs, (str, Path)) else list(docs)
    units: list[Unit] = []
    for spec in specs:
        p = Path(spec)
        if p.is_dir():
            for path in sorted(p.iterdir()):
                _load_file(path, units)
        elif p.is_file():
            _load_file(p, units)
        else:
            raise SystemExit(f"[에러] 문서 경로 없음: {p}")
    return units
