#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compliance-kb — 로컬 컴플라이언스 지식베이스 MCP 서버 (오프라인·순수 stdlib).

무신사 표시정보 컴플라이언스 플러그인의 '법적 근거 검증층'.
- 전송: stdio + newline-delimited JSON-RPC 2.0 (MCP stdio transport)
- 데이터: src/kb/**/*.json (라이선스 정리된 법령·심사지침·공정위 의결례 등)
- 외부 네트워크·API 키 0  → 심사 샌드박스에서도 그대로 동작(런타임 키 불요).

노출 도구(룰 패밀리 매핑):
  search_legal_basis   GW·MX·OR  위반에 해당하는 조문·심사지침 인출(provenance 동반)
  get_ftc_precedent    GW·MX     유사 공정위 의결례 첨부(반려 사유서 설득력)
  verify_citation      전 출력    인용 조문이 KB에 실존하는지 오프라인 교차검증(환각 방지)
  check_test_lab       TC·MX     시험성적서 발급기관 진위(KOLAS — 데이터 라이선스 확정 후 연결)
  lookup_trademark     TS        상표 진위/택갈이 단서(KIPRIS — 데이터 라이선스 확정 후 연결)

이 파일은 스켈레톤이다. 검색은 lexical(키워드/본문 카운트)로 시작하며,
필요 시 로컬 임베딩으로 확장 가능(외부 임베딩 API는 쓰지 않는다 — A9).
"""
import sys
import os
import re
import json
import glob
import argparse
# cp949 등 비UTF-8 콘솔/파이프(Windows 기본)에서도 JSON-RPC(ensure_ascii=False)
# 한글 입출력이 UnicodeEncode/DecodeError로 죽지 않도록 stdio(3종) 인코딩만 UTF-8로
# 강제한다(프로토콜/판정 로직 불변). Py3.7+. stdin도 포함해야 한글 쿼리를 정상 수신.
try:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SERVER_NAME = "compliance-kb"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"


# ---------------------------------------------------------------- KB 로딩
def resolve_kb_dir(arg):
    """--kb 인자를 cwd / 스크립트 기준으로 차례로 해석(플러그인 루트 어디서 띄워도 동작)."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        arg,
        os.path.join(os.getcwd(), arg),
        os.path.join(here, "..", arg),   # mcp_server/.. → src/kb
        os.path.join(here, "..", "kb"),
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return os.path.abspath(c)
    return os.path.abspath(arg)


def load_kb(kb_dir):
    docs = []
    for path in glob.glob(os.path.join(kb_dir, "**", "*.json"), recursive=True):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            if not isinstance(d, dict) or "doc_id" not in d:
                continue
            d["_path"] = os.path.relpath(path, kb_dir)
            docs.append(d)
        except Exception as e:  # noqa: BLE001 — 스킵하고 계속(서버는 죽지 않음)
            sys.stderr.write("[compliance-kb] skip %s: %s\n" % (path, e))
    sys.stderr.write("[compliance-kb] loaded %d docs from %s\n" % (len(docs), kb_dir))
    return docs


# ---------------------------------------------------------------- 검색 유틸
def tokenize(s):
    return [t for t in re.split(r"[^0-9A-Za-z가-힣]+", (s or "").lower()) if t]


def haystack(doc):
    return " ".join([
        doc.get("title", ""),
        doc.get("body", ""),
        " ".join(doc.get("keywords", []) or []),
        " ".join(doc.get("rule_refs", []) or []),
    ]).lower()


def lex_score(doc, qtokens):
    hay = haystack(doc)
    return sum(hay.count(t) for t in qtokens)


def provenance(doc):
    """심사자가 출처를 즉시 확인할 수 있도록 출처·라이선스를 함께 반환."""
    return {
        "doc_id": doc.get("doc_id"),
        "type": doc.get("type"),
        "title": doc.get("title"),
        "source_org": doc.get("source_org"),
        "provenance_url": doc.get("provenance_url"),
        "license": doc.get("license"),
        "attribution_required": doc.get("attribution_required", False),
        "rule_refs": doc.get("rule_refs", []),
        "excerpt": (doc.get("body", "") or "")[:400],
    }


# ---------------------------------------------------------------- 도구 구현
def t_search_legal_basis(docs, args):
    q = args.get("query", "")
    limit = int(args.get("limit", 3))
    qt = tokenize(q)
    cand = [d for d in docs if d.get("type") in ("statute", "guideline")]
    ranked = sorted(((lex_score(d, qt), d) for d in cand), key=lambda x: -x[0])
    hits = [provenance(d) for s, d in ranked if s > 0][:limit]
    return {"query": q, "matches": hits, "count": len(hits),
            "note": "KB 내 법령·심사지침 lexical 검색. 빈 결과면 KB에 해당 근거 미수록."}


def t_get_ftc_precedent(docs, args):
    q = args.get("violation", "") or args.get("query", "")
    limit = int(args.get("limit", 3))
    qt = tokenize(q)
    cand = [d for d in docs if d.get("type") == "ftc_decision"]
    ranked = sorted(((lex_score(d, qt), d) for d in cand), key=lambda x: -x[0])
    hits = [provenance(d) for s, d in ranked if s > 0][:limit]
    return {"violation": q, "precedents": hits, "count": len(hits)}


def t_verify_citation(docs, args):
    """SKILL/출력이 인용한 조문이 KB에 실존하는지 오프라인 교차검증(korean-law-mcp verify_citations의 로컬판)."""
    text = args.get("text", "")
    # 법령명은 '법/법률'에 직접 붙은 토큰만 캡처(앞 단어 흡수 방지).
    refs = re.findall(r"[가-힣A-Za-z]+법(?:률)?(?:\s*시행령|\s*시행규칙)?\s*제\s*\d+\s*조(?:의\s*\d+)?", text)
    refs += re.findall(r"(?:환경성[^\n,。.]{0,12})?심사지침", text)
    results = []
    titles = [(d, haystack(d)) for d in docs]
    for ref in sorted(set(r.strip() for r in refs)):
        rt = tokenize(ref)
        found = None
        for d, hay in titles:
            if rt and all(tok in hay for tok in rt):
                found = d
                break
        results.append({
            "citation": ref,
            "status": "verified" if found else "NOT_FOUND",
            "doc_id": found.get("doc_id") if found else None,
            "provenance_url": found.get("provenance_url") if found else None,
        })
    bad = [r for r in results if r["status"] != "verified"]
    return {"citations": results, "all_verified": not bad,
            "flag": "[HALLUCINATION_RISK]" if bad else "OK"}


def t_check_test_lab(docs, args):
    issuer = (args.get("issuer", "") or "").strip()
    # (1) 드롭인: 라이선스 확보 후 kb/labs/ 에 동봉한 정식 KOLAS 레코드(type=test_lab)가 있으면
    #     그것으로 서빙한다 — 코드 변경 0. (BYO 라이선스 데이터 어댑터)
    for d in [x for x in docs if x.get("type") == "test_lab"]:
        names = [d.get("title", "")] + (d.get("keywords", []) or [])
        if issuer and any(issuer.lower() in (n or "").lower() for n in names):
            return {"issuer": issuer, "accredited": True, "status": "LICENSED_KB", "source": provenance(d)}
    # (2) 기본(미동봉): KOLAS 명부 DB는 동봉 불가(knab.go.kr 저작권·공공누리 없음 — 리서치 확정).
    #     인정기관 '명칭' 화이트리스트(공개 사실, 비저작권)로 1차 판별 + 공식 명부 인간검증 URL.
    whitelist = ["KOTITI", "FITI", "KATRI", "KCL", "KTR", "KTL"]
    known = bool(issuer) and issuer.upper() in whitelist
    return {
        "issuer": issuer,
        "in_curated_whitelist": known if issuer else None,
        "status": "CURATED_WHITELIST",
        "verify_url": "https://www.knab.go.kr/usr/inf/srh/InfoTestInsttSearchList.do",
        "byo_note": "라이선스 확보 시 kb/labs/ 에 type=test_lab 레코드를 넣으면 위 (1) 경로로 자동 서빙(코드 변경 0).",
        "source_note": "KOLAS 명부 데이터는 동봉 불가(공식 명부 저작권). 명칭 화이트리스트로 1차 판별, "
                       "최종 인정은 verify_url(KOLAS 공식 명부)에서 사람이 확인. 미등재≠비인정(보수적).",
    }


def t_lookup_trademark(docs, args):
    brand = (args.get("brand", "") or "").strip()
    # (1) 드롭인: 라이선스 확보 후 kb/trademarks/ 에 동봉한 정식 레코드(type=trademark)가 있으면 서빙.
    if brand:
        bl = brand.lower()
        for d in [x for x in docs if x.get("type") == "trademark"]:
            if bl in haystack(d):
                return {"brand": brand, "found": True, "status": "LICENSED_KB", "source": provenance(d)}
    # (2) 기본(미동봉): KIPRIS 상표는 재배포·가공·DB화 금지(KIPRIS Plus 약관 §17·§19 — 리서치 확정).
    #     데이터 동봉/자동조회 없이 MD가 직접 확인할 공식 검색 URL만 제공(인간 검증 포인터).
    return {
        "brand": brand,
        "status": "HUMAN_VERIFY_ONLY",
        "verify_url": "https://www.kipris.or.kr/khome/search/searchResult.do",
        "search_term": brand,
        "byo_note": "라이선스 확보 시 kb/trademarks/ 에 type=trademark 레코드를 넣으면 위 (1) 경로로 자동 서빙(코드 변경 0).",
        "source_note": "KIPRIS 상표는 재배포·DB화 불가(KIPRIS Plus 약관 §17·§19). 택갈이 1차 신호는 ruleset TS-02로 대체.",
    }


DISPATCH = {
    "search_legal_basis": t_search_legal_basis,
    "get_ftc_precedent": t_get_ftc_precedent,
    "verify_citation": t_verify_citation,
    "check_test_lab": t_check_test_lab,
    "lookup_trademark": t_lookup_trademark,
}

TOOLS = [
    {
        "name": "search_legal_basis",
        "description": "표시광고법·환경성 표시광고 심사지침 등 KB 내 법령·지침에서 위반 근거 조문을 출처와 함께 검색(GW·MX·OR).",
        "inputSchema": {"type": "object", "properties": {
            "query": {"type": "string", "description": "위반 내용·키워드(예: '인조가죽 친환경 표현 에코레더')"},
            "limit": {"type": "integer", "default": 3}}, "required": ["query"]},
    },
    {
        "name": "get_ftc_precedent",
        "description": "유사 공정거래위원회 의결례/결정문을 KB에서 검색해 반려 사유서 근거로 첨부(GW·MX).",
        "inputSchema": {"type": "object", "properties": {
            "violation": {"type": "string", "description": "위반 유형·키워드(예: '그린워싱 인조가죽')"},
            "limit": {"type": "integer", "default": 3}}, "required": ["violation"]},
    },
    {
        "name": "verify_citation",
        "description": "텍스트 내 법령·지침 인용이 KB에 실존하는지 오프라인 교차검증(환각 방지). 전 출력 검증용.",
        "inputSchema": {"type": "object", "properties": {
            "text": {"type": "string", "description": "조문 인용이 포함된 텍스트(반려 사유서 등)"}}, "required": ["text"]},
    },
    {
        "name": "check_test_lab",
        "description": "시험성적서 발급기관이 인정 시험기관인지 진위 확인(TC·MX). KOLAS 데이터 라이선스 확정 후 정식 연결.",
        "inputSchema": {"type": "object", "properties": {
            "issuer": {"type": "string", "description": "발급기관명(예: KOTITI)"}}, "required": ["issuer"]},
    },
    {
        "name": "lookup_trademark",
        "description": "상표 진위/택갈이 단서 조회(TS). KIPRIS 데이터 라이선스 확정 후 연결.",
        "inputSchema": {"type": "object", "properties": {
            "brand": {"type": "string"}}, "required": ["brand"]},
    },
]


# ---------------------------------------------------------------- JSON-RPC
def _result(rid, payload):
    return {"jsonrpc": "2.0", "id": rid, "result": payload}


def _error(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def handle(req, docs):
    method = req.get("method")
    rid = req.get("id")
    if method == "initialize":
        return _result(rid, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
    if method == "tools/list":
        return _result(rid, {"tools": TOOLS})
    if method == "tools/call":
        params = req.get("params", {}) or {}
        name = params.get("name")
        args = params.get("arguments", {}) or {}
        fn = DISPATCH.get(name)
        if not fn:
            return _error(rid, -32602, "unknown tool: %s" % name)
        try:
            data = fn(docs, args)
        except Exception as e:  # noqa: BLE001
            return _result(rid, {"content": [{"type": "text", "text": "tool error: %s" % e}],
                                 "isError": True})
        return _result(rid, {"content": [
            {"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]})
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None  # 알림엔 응답하지 않음
    if method == "ping":
        return _result(rid, {})
    return _error(rid, -32601, "method not found: %s" % method)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", default="kb")
    a = ap.parse_args()
    docs = load_kb(resolve_kb_dir(a.kb))

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req, docs)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
