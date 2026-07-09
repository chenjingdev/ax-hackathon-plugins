"""M2 게이트: A12(영상 modality_loss) + canonicalize/grounding(A17 토대). SPEC §5.1·§4.4."""
from scoring.normalize import normalize, canonicalize, is_grounded

PRODUCT = {"product": {"name": "레티놀 세럼", "category": "skincare", "key_attributes": ["레티놀"]}}

VIDEO = {
    "creator_id": "vid",
    "platform": "youtube",
    "contents": [{
        "type": "video",
        "caption": "레티놀 세럼 리뷰",
        "transcript": "여러분 이건 2주 직접 써보고 말씀드려요.",
        "hashtags": ["#레티놀"],
        "comments_sample": ["저도 샀어요"],
        "engagement": {"likes": 100, "comments": 10},
    }],
}


def test_normalize_video_modality_loss():
    """영상 입력(transcript+caption+comments) 병합 + modality_loss 비어있지 않음 (A12)."""
    norm = normalize(VIDEO, PRODUCT)
    assert norm["modality_loss"], "영상인데 modality_loss가 비어있음"
    assert norm["has_video"] is True


def test_normalize_merges_fields():
    norm = normalize(VIDEO, PRODUCT)
    m = norm["merged_text"]
    assert "레티놀 세럼 리뷰" in m          # caption
    assert "2주 직접 써보고" in m            # transcript
    assert "저도 샀어요" in m                # comments
    assert norm["fields"]["transcript"]      # per-field 보존(A17 grounding용)


def test_post_no_modality_loss():
    post = {"creator_id": "p", "platform": "instagram",
            "contents": [{"type": "post", "caption": "성분 설명", "transcript": None,
                          "hashtags": [], "comments_sample": [], "engagement": {}}]}
    assert normalize(post, PRODUCT)["modality_loss"] == []


def test_canonicalize_rules():
    """NFKC·소문자·구두점/이모지 제거·공백 collapse (편집거리/fuzzy 없음)."""
    assert canonicalize("HELLO,   World! 😀") == "hello world"
    assert canonicalize("레티놀  0.1%  세럼!!") == "레티놀 01 세럼"   # % 구두점 제거
    assert canonicalize(None) == ""


def test_is_grounded_substring_and_boundary():
    """정당 인용 PASS / 환각·경계횡단 인용 FAIL."""
    norm = normalize(VIDEO, PRODUCT)
    # 원문 transcript에 실재하는 인용 → grounded
    assert is_grounded("2주 직접 써보고", "transcript", norm) is True
    # ASR/구두점 차이도 canonicalize로 흡수
    assert is_grounded("2주 직접 써보고 말씀드려요.", "transcript", norm) is True
    # 원문에 없는 환각 인용 → not grounded
    assert is_grounded("매출 3억 달성", "transcript", norm) is False
    # caption에 없는 문구를 caption source_field로 주장 → not grounded
    assert is_grounded("저도 샀어요", "caption", norm) is False
    # 올바른 source_field(comments)면 grounded
    assert is_grounded("저도 샀어요", "comments", norm) is True
