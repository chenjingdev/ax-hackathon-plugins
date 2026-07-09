"""결정론 오케스트레이션 진입점 (SKILL이 shell로 호출 — SPEC §5·§7).

흐름: 입력(§3.2/§3.4) + rubric + 에이전트 부합도(JSON) →
      normalize → features → combine → aggregate(고정공식) → report(§7.1 md + §7.3 json).

A6 보장: 총점은 이 파이프라인의 aggregate가 산출. 에이전트 입력은 차원별 0~1 부합도·인용만.
에이전트 입력(--agentic) 미제공 시 결정론 바닥만으로 스모크(점수=바닥, 인용 없음).

사용:
  python3 -m scoring.cli score --input sample/input.kr.json \
      --rubric rules/rubric.json --agentic agentic.json \
      --out-md logs/report.md --out-json logs/log.json
"""

import argparse
import json
import os
import sys

# 패키지로 실행되지 않을 때(스크립트 직접 실행)도 import 되도록 src 경로 보강
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from scoring.normalize import normalize, is_grounded            # noqa: E402
from scoring.features import extract_deterministic_features      # noqa: E402
from scoring.aggregate import compute                            # noqa: E402
from scoring import report                                       # noqa: E402

DIMS = ["D1", "D2", "D3", "D4", "D5"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _product_ctx(data):
    return {
        "product": data.get("product", {}) or {},
        "target_need": data.get("target_need", ""),
        "brand_tone": data.get("brand_tone", ""),
    }


def _score_candidate(creator, product_ctx, rubric, agentic_for_cid, deterministic_only):
    norm = normalize(creator, product_ctx)
    det = extract_deterministic_features(norm, rubric)
    cid = norm["creator_id"]

    evidence, confidence, suggestion, memo = [], {}, "", ""
    af = agentic_for_cid or {}

    if deterministic_only or not af:
        agentic_fits = {D: det[D] for D in DIMS}     # 바닥만(스모크) — 인용 없음
    else:
        agentic_fits = {}
        for D in DIMS:
            e = af.get(D)
            if isinstance(e, dict):
                agentic_fits[D] = e.get("fit", 0.0)
                confidence[D] = e.get("confidence", "-")
                q = e.get("quote") or e.get("content_quote")
                if q:
                    sf = e.get("source_field", "caption")
                    evidence.append({
                        "dimension": D,
                        "content_quote": q,
                        "source_field": sf,
                        "grounded": is_grounded(q, sf, norm),
                        "paper": e.get("paper", ""),
                    })
            elif isinstance(e, (int, float)):
                agentic_fits[D] = float(e)
        suggestion = af.get("suggestion", "")
        memo = af.get("memo", "")

    res = compute(det, agentic_fits, rubric)
    return {
        "creator_id": cid,
        "purchase_intent_fit": res["purchase_intent_fit"],
        "dimensions": res["dimensions"],
        "evidence": evidence,
        "confidence": confidence,
        "suggestion": suggestion,
        "memo": memo,
        "modality_loss": norm["modality_loss"],
        "_det": det,
    }


def run_score(input_path, rubric_path, agentic_path, deterministic_only):
    data = load_json(input_path)
    rubric = load_json(rubric_path)
    agentic = load_json(agentic_path) if agentic_path else {}
    product_ctx = _product_ctx(data)
    mode = data.get("mode", "pool")

    scored = [
        _score_candidate(cr, product_ctx, rubric, agentic.get(cr.get("creator_id", "")), deterministic_only)
        for cr in data.get("candidates", [])
    ]

    result = {
        "product": product_ctx["product"].get("name", ""),
        "ruleset_version": rubric.get("ruleset_version", "v0.1"),
        "guard": rubric.get("guard"),
        "mode": mode,
        "candidates": scored,
    }

    # 재스캔(§3.4·A14): 현재(to) 재평가 + 후보별 baseline(from) 대비 score/rank delta
    if mode == "rescan":
        cur_rank = {c["creator_id"]: i + 1 for i, c in enumerate(
            sorted(scored, key=lambda c: c["purchase_intent_fit"], reverse=True))}
        deltas = []
        for cr in data.get("candidates", []):
            cid = cr.get("creator_id", "")
            base = cr.get("baseline", {}) or {}
            cur = next((c for c in scored if c["creator_id"] == cid), None)
            if cur is None:
                continue
            sf = base.get("purchase_intent_fit")
            rf = base.get("rank")
            deltas.append({
                "creator_id": cid,
                "score_from": sf, "score_to": cur["purchase_intent_fit"],
                "score_delta": (cur["purchase_intent_fit"] - sf) if isinstance(sf, int) else 0,
                "rank_from": rf, "rank_to": cur_rank.get(cid),
                "rank_delta": (cur_rank.get(cid) - rf) if isinstance(rf, int) else 0,
            })
        result["rescan"] = {
            "from": data.get("ruleset_version_from", ""),
            "to": data.get("ruleset_version_to", rubric.get("ruleset_version", "")),
            "deltas": deltas,
        }
    return result


def main(argv=None):
    p = argparse.ArgumentParser(prog="scoring.cli")
    sub = p.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("score", help="픽스처 채점 → md + json 로그")
    sc.add_argument("--input", required=True)
    sc.add_argument("--rubric", default=os.path.join(_SRC, "rules", "rubric.json"))
    sc.add_argument("--agentic", default=None, help="에이전트 부합도 JSON(없으면 결정론 바닥만)")
    sc.add_argument("--out-md", default=None)
    sc.add_argument("--out-json", default=None)
    sc.add_argument("--deterministic-only", action="store_true")
    args = p.parse_args(argv)

    if args.cmd == "score":
        result = run_score(args.input, args.rubric, args.agentic, args.deterministic_only)
        md, log = report.render(result)
        if args.out_md:
            os.makedirs(os.path.dirname(os.path.abspath(args.out_md)), exist_ok=True)
            with open(args.out_md, "w", encoding="utf-8") as f:
                f.write(md)
        if args.out_json:
            os.makedirs(os.path.dirname(os.path.abspath(args.out_json)), exist_ok=True)
            with open(args.out_json, "w", encoding="utf-8") as f:
                json.dump(log, f, ensure_ascii=False, indent=2)
        if not args.out_json:
            print(json.dumps(log, ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
