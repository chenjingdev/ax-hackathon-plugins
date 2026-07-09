"""결정론 바닥 피처 추출 (SPEC §4.3·§5.2).

extract_deterministic_features(normalized, rubric) -> {D1..D5: float in [0,1]}
같은 normalized 입력 → 항상 동일 출력(temp 무관·100% 재현, A8).

여기 상수(키워드 사전·포화 임계)는 *측정 휴리스틱*이며 루프가 튜닝 가능(SPEC §12.5).
가중치·블렌드비·D1 배분(동결값)은 여기에 없다 — rubric.json 소관.
"""

import re
import unicodedata

# --- 측정 휴리스틱 상수 (루프 튜닝 대상, 가중치 아님) ---
MECHANISM_KW = [
    "장벽", "진피", "각질", "턴오버", "피지", "모공", "탄력", "보습", "진정", "흡수",
    "자극", "재생", "트러블", "홍조", "각질층", "피부결", "당김", "유수분", "콜라겐 생성",
]
DERMA_KW = ["피부과", "전문의", "더마", "임상", "약사", "성분 전문", "테스트 완료", "피부과 전문"]
ADDRESS_KW = ["여러분", "구독자", "구독자님", "우리", "댓글", "답글", "님들", "여러분들", "구독", "알림"]
REPLY_KW = ["답글", "감사합니다", "감사해요", "맞아요", "좋은 질문", "@", "댓글 남겨", "공감", "동의"]
USAGE_KW = ["아침", "저녁", "순서", "바른다", "발라", "사용법", "단계", "토너 후", "세럼 후", "다음", "마지막", "두드려", "흡수시켜"]
REVIEW_KW = ["써봤", "사용해", "사용한", "발라보", "직접", "후기", "리뷰", "사봤", "써본", "경험", "테스트해"]
CONCORD_KW = ["저도", "샀어요", "구매", "따라샀", "공감", "같은 경험", "사야겠", "주문", "재구매", "득템"]
BALANCE_KW = ["단점", "아쉬", "안 맞", "맞지 않", "자극될", "주의", "비추", "별로", "호불호", "단, ", "다만", "단점은"]
HYPE_KW = ["대박", "인생템", "무조건", "강추", "최고", "완전 좋", "역대급", "씹", "갓", "찐"]
INFO_HASHTAG_KW = ["성분", "정보", "리뷰", "사용법", "꿀팁", "추천", "비교", "분석"]

_PCT_RE = re.compile(r"\d+(?:\.\d+)?\s*%")
_DURATION_RE = re.compile(r"(\d+\s*(?:주|개월|달|일|주일|년)|꾸준히|한\s*달|두\s*달|매일|매주|몇\s*주)")


def _norm(text):
    return unicodedata.normalize("NFKC", str(text or "")).lower()


def _count_distinct(text, terms):
    return sum(1 for t in terms if t in text)


def _count_total(text, terms):
    return sum(text.count(t) for t in terms)


def _sat(x, cap):
    """0..1 포화: min(x/cap, 1)."""
    if cap <= 0:
        return 0.0
    return min(x / cap, 1.0)


def _clamp01(x):
    return max(0.0, min(1.0, float(x)))


def extract_deterministic_features(normalized, rubric):
    text = _norm(normalized.get("merged_text", ""))
    fields = normalized.get("fields", {})
    cap_tr = _norm(fields.get("caption", "") + " " + fields.get("transcript", ""))
    comments = _norm(fields.get("comments", ""))
    sm = normalized.get("surface_metrics", {}) or {}
    ingredients = [i.lower() for i in normalized.get("domain", {}).get("ingredients", [])]
    hashtags = [_norm(h) for h in normalized.get("hashtags", [])]

    total_tokens = max(len(text.split()), 1)

    # --- D1 전문성/더마권위 ---
    ingredient_n = _count_distinct(text, ingredients)
    pct = 1.0 if _PCT_RE.search(text) else 0.0
    mech_n = _count_distinct(text, MECHANISM_KW)
    derma = 1.0 if _count_distinct(text, DERMA_KW) > 0 else 0.0
    d1 = (_sat(ingredient_n, 3) * 0.35 + pct * 0.20 + _sat(mech_n, 3) * 0.25 + derma * 0.20)

    # --- D2 준사회성/반복소통 ---
    address_n = _count_total(cap_tr, ADDRESS_KW)
    cadence_days = sm.get("post_cadence_days")
    if cadence_days is None or cadence_days == 0:
        cadence = 0.2
    elif cadence_days <= 7:
        cadence = 1.0
    elif cadence_days <= 14:
        cadence = 0.7
    elif cadence_days <= 30:
        cadence = 0.4
    else:
        cadence = 0.2
    avg_likes = sm.get("avg_likes") or 0
    avg_comments = sm.get("avg_comments") or 0
    clr = _sat((avg_comments / avg_likes) if avg_likes else 0.0, 0.1)
    reply_n = _count_total(comments, REPLY_KW)
    d2 = (_sat(address_n, 3) * 0.30 + cadence * 0.30 + clr * 0.20 + _sat(reply_n, 2) * 0.20)

    # --- D3 정보성/성분설명 ---
    info_tokens = ingredient_n + _count_total(cap_tr, USAGE_KW)
    info_density = _sat(info_tokens / total_tokens, 0.12)
    usage_n = _count_distinct(cap_tr, USAGE_KW)
    info_tags = sum(1 for h in hashtags if any(k in h for k in INFO_HASHTAG_KW))
    tag_ratio = (info_tags / len(hashtags)) if hashtags else 0.0
    d3 = (info_density * 0.40 + _sat(usage_n, 3) * 0.40 + tag_ratio * 0.20)

    # --- D4 후기/eWOM·커뮤니티신뢰 ---
    review_n = _count_distinct(cap_tr, REVIEW_KW)
    duration = 1.0 if _DURATION_RE.search(cap_tr) else 0.0
    concord_n = _count_total(comments, CONCORD_KW)
    d4 = (_sat(review_n, 3) * 0.40 + duration * 0.30 + _sat(concord_n, 2) * 0.30)

    # --- D5 진정성 (보조) ---
    balance_n = _count_distinct(text, BALANCE_KW)
    ad_ratio = sm.get("ad_tag_ratio")
    non_commercial = (1.0 - min(float(ad_ratio), 1.0)) if ad_ratio is not None else 0.5
    hype_n = _count_total(text, HYPE_KW)
    d5 = (_sat(balance_n, 2) * 0.50 + non_commercial * 0.30 + (1.0 - _sat(hype_n, 3)) * 0.20)

    return {
        "D1": _clamp01(d1),
        "D2": _clamp01(d2),
        "D3": _clamp01(d3),
        "D4": _clamp01(d4),
        "D5": _clamp01(d5),
    }
