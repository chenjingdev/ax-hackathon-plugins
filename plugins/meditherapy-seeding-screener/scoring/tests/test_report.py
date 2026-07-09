"""M2 게이트: A7·A9·A13(리포트·JSON 로그). SPEC §7.1·§7.3."""
from scoring import report

RESULT = {
    "product": "레티놀 세럼",
    "ruleset_version": "v0.1",
    "guard": "purchase_intent_fit = 구매의도 적합 추정 · 매출귀인 아님 · 바이럴 아님",
    "mode": "pool",
    "candidates": [
        {
            "creator_id": "alpha",
            "purchase_intent_fit": 72,
            "dimensions": {"D1": 0.35, "D2": 0.40, "D3": 0.60, "D4": 0.81, "D5": 0.40},
            "evidence": [{"dimension": "D4", "content_quote": "2주 직접 써보고",
                          "source_field": "transcript", "grounded": True,
                          "paper": "박지혜(2017) 기능성화장품 후기신뢰"}],
            "suggestion": "성분/전문성 보강 시 부합도↑",
            "memo": "후기·정보성 강해 상위 추천",
            "confidence": {"D4": "high"},
            "modality_loss": ["video transcript: 비주얼 신호 일부 손실"],
        },
        {
            "creator_id": "beta",
            "purchase_intent_fit": 31,
            "dimensions": {"D1": 0.10, "D2": 0.20, "D3": 0.15, "D4": 0.10, "D5": 0.50},
            "evidence": [],
            "suggestion": "구매유발 결 빈약",
            "memo": "일상 콘텐츠 위주",
            "confidence": {},
            "modality_loss": [],
        },
    ],
}

REQUIRED_LOG_FIELDS = ["creator_id", "product", "purchase_intent_fit", "dimensions",
                       "evidence", "suggestion", "modality_loss", "ruleset_version",
                       "guard", "reviewed_by"]


def test_report_json_log_fields():
    """JSON 로그에 §7.3 전 필드 + reviewed_by='human-required' + guard 문자열 (A13)."""
    _, log = report.render(RESULT)
    assert isinstance(log, list) and len(log) == 2
    for entry in log:
        for k in REQUIRED_LOG_FIELDS:
            assert k in entry, f"§7.3 필드 누락: {k}"
        assert entry["reviewed_by"] == "human-required"
        assert "매출귀인 아님" in entry["guard"]
        assert set(entry["dimensions"].keys()) == {"D1", "D2", "D3", "D4", "D5"}


def test_report_evidence_schema():
    _, log = report.render(RESULT)
    ev = log[0]["evidence"][0]
    for k in ["dimension", "content_quote", "source_field", "grounded", "paper"]:
        assert k in ev


def test_report_markdown_sections():
    """§7.1 마크다운 골격(랭킹·dossier·보완·사유·가드) 존재 + 랭킹 내림차순."""
    md, _ = report.render(RESULT)
    for sec in ["후보 랭킹", "dossier", "보완 제안", "사유 메모", "가드"]:
        assert sec in md, f"§7.1 섹션 누락: {sec}"
    assert "reviewed_by" in md and "human-required" in md
    # 랭킹 내림차순: alpha(72)가 beta(31)보다 먼저
    assert md.index("alpha") < md.index("beta")


def test_report_rescan_delta():
    """재스캔 모드 score/rank delta 보고 (A14)."""
    rescan = dict(RESULT)
    rescan["mode"] = "rescan"
    rescan["rescan"] = {"from": "v0.1", "to": "v0.2",
                        "deltas": [{"creator_id": "alpha", "score_from": 60, "score_to": 72,
                                    "score_delta": 12, "rank_from": 2, "rank_to": 1, "rank_delta": -1}]}
    md, _ = report.render(rescan)
    assert "재스캔 변동분" in md
    assert "+12" in md
