"""고정 공식 합산 (SPEC §5.4).

dimension_score[D] = combine(deterministic_features[D], agentic_fit[D])   # 차원별
purchase_intent_fit = round( Σ_D dimension_score[D] × weight[D] × 100 )   ∈ [0,100]

핵심 불변식(A6): 에이전트가 넘긴 어떤 total/전체 점수도 무시한다 — 총점은 오직 이 모듈이
rubric 동결 가중치로 차원별 값에서 산출한다. 에이전트는 차원별 0~1 부합도만 매긴다.
블렌드비·가중치·D1 direct_weight는 rubric.json 동결값(루프 패치 금지·가중치 backdoor 차단).
"""


def _clamp01(x):
    return max(0.0, min(1.0, float(x)))


def _fit_value(x):
    """에이전트 부합도 입력 정규화. dict면 'fit' 키만, 숫자면 그 값, 그 외 0.0.
    (위조 'total' 등 어떤 비-차원 필드도 여기서 닿지 않는다 — 호출부가 차원 id로만 조회.)"""
    if isinstance(x, dict):
        return _clamp01(x.get("fit", 0.0))
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return _clamp01(x)
    return 0.0


def combine_dimensions(det_features, agentic_fits, rubric):
    """차원별 dimension_score = blend(det, agentic). D1은 direct_weight 감쇠(매개 재배분)."""
    blend = rubric["blend"]
    dw = float(blend["deterministic_weight"])
    aw = float(blend["agentic_weight"])
    out = {}
    for dim in rubric["dimensions"]:
        D = dim["id"]
        det = _clamp01(det_features.get(D, 0.0))
        agt = _fit_value(agentic_fits.get(D, 0.0))   # 차원 id로만 조회 → 'total' 무시(A6)
        base = dw * det + aw * agt
        if "direct_weight" in dim:        # D1: 직접효과 비유의 → 직접계수만 보수 반영(매개는 D2/D5에 재배분)
            base = base * float(dim["direct_weight"])
        out[D] = _clamp01(base)
    return out


def purchase_intent_fit(dimension_scores, rubric):
    """고정 공식 합산 → 0~100 정수. rubric 차원만 순회(에이전트 total 무시)."""
    s = 0.0
    for dim in rubric["dimensions"]:
        D = dim["id"]
        s += _clamp01(dimension_scores.get(D, 0.0)) * float(dim["weight"])
    return int(round(s * 100))


def compute(det_features, agentic_fits, rubric):
    """normalize→features 이후 한 후보의 차원 점수 + 총점 산출."""
    dims = combine_dimensions(det_features, agentic_fits, rubric)
    return {
        "dimensions": dims,
        "purchase_intent_fit": purchase_intent_fit(dims, rubric),
    }
