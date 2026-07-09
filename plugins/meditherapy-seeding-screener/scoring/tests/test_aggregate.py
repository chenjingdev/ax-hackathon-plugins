"""M2 게이트: A4·A6·A8(합산 코어). SPEC §5.4."""
from scoring.aggregate import combine_dimensions, purchase_intent_fit, compute

DIMS = ["D1", "D2", "D3", "D4", "D5"]


def test_aggregate_fixed_formula(rubric):
    """고정 {D:dimension_score}+rubric 가중치 → round(Σ score×weight×100) 정확 일치."""
    dims = {"D1": 0.30, "D2": 0.60, "D3": 0.45, "D4": 0.81, "D5": 0.40}
    w = {d["id"]: d["weight"] for d in rubric["dimensions"]}
    expected = int(round(sum(dims[D] * w[D] for D in DIMS) * 100))
    assert purchase_intent_fit(dims, rubric) == expected


def test_aggregate_ignores_agent_total(rubric):
    """위조 'total'/비-차원 필드를 섞어도 결과 불변 (A6 코드 보장)."""
    det = {D: 0.5 for D in DIMS}
    clean = {D: 0.7 for D in DIMS}
    forged = dict(clean)
    forged["total"] = 999            # 에이전트가 매긴 위조 총점
    forged["purchase_intent_fit"] = 100
    forged["score"] = 88

    ds_clean = combine_dimensions(det, clean, rubric)
    ds_forged = combine_dimensions(det, forged, rubric)
    assert ds_clean == ds_forged
    assert purchase_intent_fit(ds_clean, rubric) == purchase_intent_fit(ds_forged, rubric)


def test_aggregate_determinism(rubric):
    """같은 입력 N=10회 → 동일 출력 (stability=1.0, A8)."""
    det = {"D1": 0.4, "D2": 0.7, "D3": 0.55, "D4": 0.6, "D5": 0.33}
    agt = {"D1": 0.8, "D2": 0.5, "D3": 0.9, "D4": 0.7, "D5": 0.2}
    out = [compute(det, agt, rubric) for _ in range(10)]
    first = out[0]
    assert all(o == first for o in out)


def test_combine_d1_direct_attenuation(rubric):
    """D1은 direct_weight(0.4) 감쇠, 나머지 차원은 무감쇠 (매개 재배분·SPEC §5.4)."""
    det = {D: 1.0 for D in DIMS}
    agt = {D: 1.0 for D in DIMS}
    ds = combine_dimensions(det, agt, rubric)
    d1 = next(d for d in rubric["dimensions"] if d["id"] == "D1")
    assert abs(ds["D1"] - d1["direct_weight"]) < 1e-9   # 1.0 × 0.4
    assert abs(ds["D2"] - 1.0) < 1e-9                    # 무감쇠


def test_fit_value_accepts_dict_and_number(rubric):
    """에이전트 부합도가 dict{fit}이든 숫자든 동일 처리, 'total' 키는 차원이 아니라 안 닿음."""
    det = {D: 0.0 for D in DIMS}
    agt_dict = {D: {"fit": 0.5, "quote": "x", "confidence": "high"} for D in DIMS}
    agt_num = {D: 0.5 for D in DIMS}
    assert combine_dimensions(det, agt_dict, rubric) == combine_dimensions(det, agt_num, rubric)


def test_score_range_0_100(rubric):
    """purchase_intent_fit ∈ [0,100]."""
    for v in (0.0, 0.5, 1.0):
        ds = combine_dimensions({D: v for D in DIMS}, {D: v for D in DIMS}, rubric)
        pi = purchase_intent_fit(ds, rubric)
        assert 0 <= pi <= 100
