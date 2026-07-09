"""M2 게이트: 자기완결 — src/scoring 네트워크 import 0 (SPEC §10.3) + cli 스모크."""
import ast
import glob
import json
import os
import subprocess
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SCORING = os.path.join(_SRC, "scoring")

FORBIDDEN = {"socket", "ssl", "urllib", "http", "ftplib", "telnetlib", "asyncio",
             "requests", "httpx", "aiohttp", "urllib3", "smtplib"}


def _imported_modules(path):
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods


def test_no_network_imports():
    for py in glob.glob(os.path.join(_SCORING, "*.py")):
        mods = _imported_modules(py)
        bad = mods & FORBIDDEN
        assert not bad, f"{os.path.basename(py)} 금지 import: {bad}"


def test_cli_smoke_deterministic_only(tmp_path):
    """cli가 결정론 바닥만으로도 §7.3 JSON 로그를 emit (네트워크 0)."""
    inp = {
        "mode": "pool",
        "product": {"name": "레티놀 세럼", "category": "skincare", "key_attributes": ["레티놀"]},
        "candidates": [{
            "creator_id": "smoke",
            "platform": "youtube",
            "surface_metrics": {"avg_likes": 100, "avg_comments": 10, "post_cadence_days": 7},
            "contents": [{"type": "video", "caption": "레티놀 성분 설명",
                          "transcript": "2주 써본 후기예요", "hashtags": ["#성분"],
                          "comments_sample": ["저도 샀어요"], "engagement": {}}],
        }],
    }
    ip = tmp_path / "in.json"
    op = tmp_path / "out.json"
    ip.write_text(json.dumps(inp, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "scoring.cli", "score", "--input", str(ip),
         "--deterministic-only", "--out-json", str(op)],
        cwd=_SRC, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    log = json.loads(op.read_text(encoding="utf-8"))
    assert log and log[0]["reviewed_by"] == "human-required"
    assert log[0]["modality_loss"], "영상인데 modality_loss 비어있음"
