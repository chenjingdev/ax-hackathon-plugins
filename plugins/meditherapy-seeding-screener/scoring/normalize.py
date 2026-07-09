"""입력 정규화 (SPEC §5.1) + canonicalize (SPEC §4.4).

영상은 caption+transcript+comments_sample을 하나의 텍스트로 병합하고,
영상 전용 신호(비주얼 비포애프터·톤) 손실을 modality_loss[]에 기록한다(A12).
제품 컨텍스트로 도메인 성분 사전을 바인딩한다.

canonicalize(): 인용↔원문 근거 실재성(A17) 매칭용 엄격 정규화.
  NFKC → 소문자 → 구두점/이모지 제거 → 연속 공백 1칸 collapse.
  (SPEC §4.4 의도: 소문자·구두점 제거·단일 공백. 구두점 제거가 만든 잔여 이중공백을
   막기 위해 collapse를 마지막에 적용 — 인용·원문 양쪽에 동일 변환이라 매칭은 일관.)
  편집거리·동의어·fuzzy 금지(환각 통과 차단).
"""

import re
import unicodedata

# 영상 모달리티: transcript/영상형 콘텐츠는 비주얼 신호가 텍스트로 일부 손실됨
_VIDEO_TYPES = {"reel", "short", "video"}

# 도메인(skincare) 기본 성분/관심 사전 — 제품 컨텍스트 key_attributes와 합집합으로 바인딩
BASE_SKINCARE_LEXICON = [
    "레티놀", "레티날", "바쿠치올", "나이아신아마이드", "나이아신", "히알루론산", "히알루론",
    "비타민c", "비타민 c", "아스코르빈산", "세라마이드", "펩타이드", "판테놀", "아데노신",
    "콜라겐", "마데카소사이드", "시카", "센텔라", "병풀", "티트리", "녹차", "어성초",
    "aha", "bha", "pha", "살리실산", "글리콜산", "락토바이오닉", "글리세린", "스쿠알란",
    "알란토인", "프로폴리스", "세린", "엘라스틴", "트라넥삼산", "아줄렌", "징크",
    "선크림", "토너", "세럼", "앰플", "에센스", "크림", "클렌저", "필링",
]


def canonicalize(text):
    """SPEC §4.4 엄격 정규화 (근거 실재성 매칭 전용)."""
    if text is None:
        return ""
    t = unicodedata.normalize("NFKC", str(text))
    t = t.lower()
    # 구두점/이모지 제거 (\w = 한글·영숫자·_ 보존, 공백 보존)
    t = re.sub(r"[^\w\s]", "", t, flags=re.UNICODE)
    # 연속 공백 1칸 collapse (구두점 제거 후 — 잔여 이중공백 차단)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def normalize(creator, product_ctx=None):
    """후보 크리에이터/콘텐츠 객체(§3.2)를 스코어링용 정규화 표현으로 변환.

    반환: {creator_id, platform, surface_metrics, merged_text,
           fields{caption,transcript,comments}, per_content[], hashtags[],
           modality_loss[], domain{...}}
    근거 실재성(A17)은 per_content의 개별 source_field에 대조하므로 원문 보존.
    """
    product_ctx = product_ctx or {}
    contents = creator.get("contents", []) or []

    caption_parts, transcript_parts, comment_parts, hashtags = [], [], [], []
    per_content = []
    modality_loss = []
    has_video = False

    for c in contents:
        ctype = (c.get("type") or "").lower()
        cap = c.get("caption") or ""
        tr = c.get("transcript")
        comments = _as_list(c.get("comments_sample"))
        tags = _as_list(c.get("hashtags"))

        if cap:
            caption_parts.append(cap)
        if tr:
            transcript_parts.append(tr)
        comment_parts.extend([cm for cm in comments if cm])
        hashtags.extend(tags)

        if ctype in _VIDEO_TYPES:
            has_video = True
            if tr:
                modality_loss.append(
                    f"{ctype} '{(cap[:18] or c.get('type'))}...': transcript 사용 — "
                    "비주얼 비포애프터·톤·발화 강세 등 영상 전용 신호 일부 손실 (ASR 인용은 §4.4 canonicalize로 A17 검증)"
                )
            else:
                modality_loss.append(
                    f"{ctype} '{(cap[:18] or c.get('type'))}...': transcript 없음 — 영상 의미 신호 손실(캡션·댓글로만 평가)"
                )

        per_content.append({
            "type": ctype,
            "caption": cap,
            "transcript": tr or "",
            "comments_sample": comments,
            "hashtags": tags,
            "engagement": c.get("engagement", {}) or {},
        })

    fields = {
        "caption": "\n".join(caption_parts),
        "transcript": "\n".join(transcript_parts),
        "comments": "\n".join(comment_parts),
    }
    merged_text = "\n".join(
        [fields["caption"], fields["transcript"], fields["comments"], " ".join(hashtags)]
    ).strip()

    product = product_ctx.get("product", {}) or {}
    key_attrs = [str(a).lower() for a in _as_list(product.get("key_attributes"))]
    ingredients = sorted(set(BASE_SKINCARE_LEXICON) | set(key_attrs))

    domain = {
        "product_name": product.get("name", ""),
        "category": product.get("category", "skincare"),
        "key_attributes": key_attrs,
        "ingredients": ingredients,
        "target_need": product_ctx.get("target_need", ""),
        "brand_tone": product_ctx.get("brand_tone", ""),
    }

    return {
        "creator_id": creator.get("creator_id", ""),
        "platform": creator.get("platform", ""),
        "surface_metrics": creator.get("surface_metrics", {}) or {},
        "merged_text": merged_text,
        "fields": fields,
        "per_content": per_content,
        "hashtags": hashtags,
        "modality_loss": modality_loss,
        "has_video": has_video,
        "domain": domain,
    }


def is_grounded(quote, source_field, normalized):
    """근거 실재성(A17): 인용이 선언된 source_field의 *개별* 원문에 canonicalize 후
    substring으로 실재하는가. 병합 텍스트가 아닌 개별 콘텐츠 필드에 대조(경계-횡단 차단, §4.4).
    cli와 eval/grounding.py가 공유하는 단일 진실원천."""
    if not quote:
        return False
    cq = canonicalize(quote)
    if not cq:
        return False
    fkey = {"caption": "caption", "transcript": "transcript",
            "comments": "comments", "comments_sample": "comments"}.get(source_field)
    for pc in normalized.get("per_content", []):
        if fkey == "comments":
            texts = pc.get("comments_sample", []) or []
        elif fkey:
            texts = [pc.get(fkey, "")]
        else:  # source_field 미지정/불명 → 모든 필드 허용
            texts = [pc.get("caption", ""), pc.get("transcript", "")] + (pc.get("comments_sample", []) or [])
        for t in texts:
            if cq in canonicalize(t):
                return True
    return False
