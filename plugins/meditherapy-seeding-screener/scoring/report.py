"""출력 렌더 (SPEC §7.1 마크다운 + §7.3 JSON 로그).

render(result) -> (markdown:str, json_log:list[dict])
핵심 산출 = '왜'의 원문 근거 인용(설명), 점수·랭킹은 부산물(SPEC §1.1·§5.5).
모든 산출에 guard 문자열 + reviewed_by="human-required"(A13).
"""

GUARD_DEFAULT = "purchase_intent_fit = 구매의도 적합 추정 · 매출귀인 아님 · 바이럴 아님 · 진위 확정판정 아님"
REVIEWED_BY = "human-required"
DIM_ORDER = ["D1", "D2", "D3", "D4", "D5"]
DIM_NAMES = {
    "D1": "전문성/더마권위", "D2": "준사회성/반복소통", "D3": "정보성/성분설명",
    "D4": "후기/eWOM", "D5": "진정성(보조)",
}


def _sorted_candidates(result):
    cands = list(result.get("candidates", []))
    return sorted(cands, key=lambda c: c.get("purchase_intent_fit", 0), reverse=True)


def render_json_log(result):
    """후보별 §7.3 JSON 로그 객체 리스트. 재스캔 모드면 entry에 rescan_delta 부착(A14)."""
    product = result.get("product", "")
    ruleset = result.get("ruleset_version", "v0.1")
    guard = result.get("guard", GUARD_DEFAULT)
    delta_by_cid = {d.get("creator_id", ""): d for d in (result.get("rescan", {}) or {}).get("deltas", [])}
    logs = []
    for c in result.get("candidates", []):
        cid = c.get("creator_id", "")
        entry = {
            "creator_id": cid,
            "product": product,
            "purchase_intent_fit": c.get("purchase_intent_fit", 0),
            "dimensions": {d: c.get("dimensions", {}).get(d, 0.0) for d in DIM_ORDER},
            "evidence": c.get("evidence", []),
            "suggestion": c.get("suggestion", ""),
            "modality_loss": c.get("modality_loss", []),
            "ruleset_version": ruleset,
            "guard": guard,
            "reviewed_by": REVIEWED_BY,
        }
        if cid in delta_by_cid:
            entry["rescan_delta"] = delta_by_cid[cid]
        logs.append(entry)
    return logs


def _fmt_dims(dims):
    return " · ".join(f"{d} {dims.get(d, 0.0):.2f}" for d in DIM_ORDER)


def render_markdown(result):
    product = result.get("product", "")
    guard = result.get("guard", GUARD_DEFAULT)
    mode = result.get("mode", "pool")
    ranked = _sorted_candidates(result)

    out = []
    out.append("## 인플루언서 시딩 콘텐츠 적합도 리포트")
    if product:
        out.append(f"> 제품 컨텍스트: **{product}** · ruleset {result.get('ruleset_version', 'v0.1')}")
    out.append("")

    # 1) 랭킹
    out.append("### 1) 후보 랭킹 (purchase_intent_fit)")
    out.append("")
    out.append("| 순위 | creator_id | purchase_intent_fit | 차원 점수 |")
    out.append("|---|---|---|---|")
    for i, c in enumerate(ranked, 1):
        out.append(f"| {i} | {c.get('creator_id','')} | **{c.get('purchase_intent_fit',0)}** | {_fmt_dims(c.get('dimensions',{}))} |")
    out.append("")

    # 재스캔 모드: delta 보고 (§3.4·A14)
    if mode == "rescan" and result.get("rescan"):
        rs = result["rescan"]
        out.append(f"### 1-b) 재스캔 변동분 (ruleset {rs.get('from','')} → {rs.get('to','')})")
        out.append("")
        out.append("| creator_id | score(이전→현재) Δ | rank(이전→현재) Δ |")
        out.append("|---|---|---|")
        for d in rs.get("deltas", []):
            out.append(f"| {d.get('creator_id','')} | {d.get('score_from','?')}→{d.get('score_to','?')} ({d.get('score_delta',0):+d}) | {d.get('rank_from','?')}→{d.get('rank_to','?')} ({d.get('rank_delta',0):+d}) |")
        out.append("")

    # 2) dossier
    out.append("### 2) 후보별 dossier — 차원 점수·근거 인용·confidence")
    out.append("")
    for c in ranked:
        out.append(f"#### {c.get('creator_id','')} — purchase_intent_fit {c.get('purchase_intent_fit',0)}")
        out.append("")
        out.append("| 차원 | 점수 | confidence | 근거 인용(원문 verbatim) | source_field | 논문 |")
        out.append("|---|---|---|---|---|---|")
        ev_by_dim = {}
        for ev in c.get("evidence", []):
            ev_by_dim.setdefault(ev.get("dimension", ""), []).append(ev)
        dims = c.get("dimensions", {})
        conf = c.get("confidence", {})
        for d in DIM_ORDER:
            evs = ev_by_dim.get(d, [])
            if evs:
                for ev in evs:
                    q = (ev.get("content_quote", "") or "").replace("\n", " ")
                    out.append(f"| {d} {DIM_NAMES[d]} | {dims.get(d,0.0):.2f} | {conf.get(d,'-')} | 「{q}」 | {ev.get('source_field','')} | {ev.get('paper','')} |")
            else:
                out.append(f"| {d} {DIM_NAMES[d]} | {dims.get(d,0.0):.2f} | {conf.get(d,'-')} | (근거 인용 없음 — 해당 차원 신호 약함) | - | - |")
        if c.get("modality_loss"):
            out.append("")
            out.append(f"- ⚠ modality_loss: {'; '.join(c['modality_loss'])}")
        out.append("")

    # 3) 보완 제안
    out.append("### 3) 보완 제안 (콘텐츠 디렉션)")
    out.append("")
    for c in ranked:
        if c.get("suggestion"):
            out.append(f"- **{c.get('creator_id','')}**: {c['suggestion']}")
    out.append("")

    # 4) 사유 메모
    out.append("### 4) 사유 메모 (사람 검토·확정)")
    out.append("")
    for c in ranked:
        if c.get("memo"):
            out.append(f"- **{c.get('creator_id','')}**: {c['memo']}")
    out.append("")

    # 5) 가드
    out.append("### 5) 가드")
    out.append("")
    out.append(f"- {guard}")
    out.append(f"- reviewed_by = **{REVIEWED_BY}** (자동 발송·확정 0)")
    out.append("")
    return "\n".join(out)


def render(result):
    return render_markdown(result), render_json_log(result)
