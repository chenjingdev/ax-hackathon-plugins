"""M2 게이트: A4·A8(피처 재현). SPEC §4.3·§5.2."""
from scoring.normalize import normalize
from scoring.features import extract_deterministic_features

DIMS = ["D1", "D2", "D3", "D4", "D5"]

PRODUCT = {"product": {"name": "레티놀 세럼", "category": "skincare",
                       "key_attributes": ["레티놀", "모공", "탄력"]}}

RICH = {
    "creator_id": "rich",
    "platform": "youtube",
    "surface_metrics": {"followers": 12000, "avg_likes": 800, "avg_comments": 90,
                        "post_cadence_days": 5, "ad_tag_ratio": 0.2},
    "contents": [{
        "type": "video",
        "caption": "레티놀 0.1% 세럼 2주 직접 써본 후기. 피부 장벽 자극 없이 모공·탄력 개선.",
        "transcript": "여러분 안녕하세요. 레티놀은 턴오버를 도와요. 아침저녁 순서로 발라보니 한 달 만에 좋아졌어요. 단점은 초반 자극될 수 있어요.",
        "hashtags": ["#성분리뷰", "#레티놀", "#사용법"],
        "comments_sample": ["저도 샀어요 공감!", "좋은 질문 감사합니다 답글 달았어요"],
        "engagement": {"likes": 800, "comments": 90},
    }],
}

POOR = {
    "creator_id": "poor",
    "platform": "instagram",
    "surface_metrics": {"followers": 500000, "avg_likes": 30000, "avg_comments": 50,
                        "post_cadence_days": 45, "ad_tag_ratio": 0.9},
    "contents": [{
        "type": "post",
        "caption": "오늘 날씨 좋아서 카페 왔어요 ☕ 행복한 하루!",
        "transcript": None,
        "hashtags": ["#daily", "#카페"],
        "comments_sample": ["예뻐요", "좋아요"],
        "engagement": {"likes": 30000, "comments": 50},
    }],
}


def test_features_reproducible(ontology):
    """같은 normalized 입력 → 동일 피처 벡터 N=10 (temp 무관)."""
    norm = normalize(RICH, PRODUCT)
    outs = [extract_deterministic_features(norm, ontology) for _ in range(10)]
    assert all(o == outs[0] for o in outs)


def test_features_in_unit_range(ontology):
    for cr in (RICH, POOR):
        f = extract_deterministic_features(normalize(cr, PRODUCT), ontology)
        for D in DIMS:
            assert 0.0 <= f[D] <= 1.0, (D, f[D])


def test_features_discriminate_rich_vs_poor(ontology):
    """구매유발 결이 풍부한 콘텐츠가 빈약 콘텐츠보다 핵심 차원 점수가 높다(변별)."""
    fr = extract_deterministic_features(normalize(RICH, PRODUCT), ontology)
    fp = extract_deterministic_features(normalize(POOR, PRODUCT), ontology)
    # D1(전문성)·D3(정보성)·D4(후기)에서 명확히 변별
    assert fr["D1"] > fp["D1"]
    assert fr["D3"] > fp["D3"]
    assert fr["D4"] > fp["D4"]
