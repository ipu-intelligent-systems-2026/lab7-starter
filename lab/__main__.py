"""
CLI entrypoint: python -m lab <command> ...
Every command prints JSON on stdout. Exit codes: 0 = ok, 1 = refused / not found, 2 = usage error.
すべてのコマンドは JSON を出力。終了コード：0=成功、1=拒否/未検出、2=使い方の誤り。
"""
import argparse
import json
import sqlite3
import sys

from lab.core import fetch_weather
from lab.memory import (PROJECT_ROOT, KNOWLEDGE_DIR, forget_preference,
                        get_preference_details, init_db, load_knowledge, search_knowledge,
                        set_preference)
from lab.support import cancel_order, load_orders, lookup_order, reset_orders, save_orders
from lab.travel import compute_budget_summary, run_bounded_review

ORDERS_STATE = str(PROJECT_ROOT / "data" / "orders.json")


def out(obj, code: int = 0) -> int:
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return code


# --------------------------------------------------------------------------- commands
def cmd_doctor(_args) -> int:
    checks = []
    ok_py = sys.version_info >= (3, 11)
    checks.append({"check": "python>=3.11", "ok": ok_py, "detail": sys.version.split()[0]})
    try:
        path = init_db()
        with sqlite3.connect(path) as conn:
            conn.execute("SELECT 1")
        checks.append({"check": "sqlite memory db writable", "ok": True, "detail": path})
    except Exception as e:
        checks.append({"check": "sqlite memory db writable", "ok": False, "detail": str(e)})
    n_chunks = len(load_knowledge()) if KNOWLEDGE_DIR.is_dir() else 0
    checks.append({"check": "knowledge/ has content", "ok": n_chunks > 0, "detail": f"{n_chunks} chunks"})
    skills = sorted(p.parent.name for p in (PROJECT_ROOT / ".opencode" / "skills").glob("*/SKILL.md"))
    checks.append({"check": ".opencode skills found", "ok": bool(skills), "detail": skills})
    all_ok = all(c["ok"] for c in checks)
    return out({"ok": all_ok, "checks": checks}, 0 if all_ok else 1)


def cmd_weather(args) -> int:
    try:
        res = fetch_weather(args.city)
    except ValueError as e:
        return out({"found": False, "error": str(e)}, 2)
    return out(res, 0 if res.get("found") else 1)


def cmd_travel(args) -> int:
    if not args.demo:
        return out({"error": "Live mode is handled by the travel agent (websearch/webfetch). "
                             "Use --demo for the offline example, or `travel budget` with your own items."}, 2)
    items = [
        {"name": "Round-trip Shinkansen", "cost_yen": 28000, "is_estimate": False},
        {"name": "Vegetarian Kaiseki Lunch", "cost_yen": 4500, "is_estimate": True},
        {"name": "Zen Temple Pass", "cost_yen": 1500, "is_estimate": False},
    ]
    summary = compute_budget_summary(items, budget_limit_yen=40000)
    review = run_bounded_review(["Initial draft", "Revised draft"], max_rounds=3)
    knowledge = search_knowledge(args.query, top_k=2)
    return out({"mode": "demo (offline)", "query": args.query, "budget": summary,
                "review": review, "knowledge": knowledge})


def cmd_budget(args) -> int:
    try:
        items = json.loads(args.items_json)
        if not isinstance(items, list):
            raise ValueError("items must be a JSON list")
        return out(compute_budget_summary(items, budget_limit_yen=args.limit))
    except (ValueError, TypeError, AttributeError) as e:
        return out({"error": f"Invalid budget input: {e}"}, 2)


def _with_orders(fn):
    load_orders(ORDERS_STATE)
    result = fn()
    save_orders(ORDERS_STATE)
    return result


def cmd_support_lookup(args) -> int:
    res = _with_orders(lambda: lookup_order(args.order_id))
    return out(res, 0 if res["found"] else 1)


def cmd_support_cancel(args) -> int:
    res = _with_orders(lambda: cancel_order(args.order_id, confirmed=args.confirm))
    return out(res, 0 if res["success"] else 1)


def cmd_support_reset(_args) -> int:
    reset_orders()
    save_orders(ORDERS_STATE)
    return out({"reset": True, "message": "Demo orders restored."})


def cmd_memory_set(args) -> int:
    try:
        set_preference(args.user, args.scope, args.key, args.value, evidence=args.evidence)
    except ValueError as e:
        return out({"stored": False, "error": str(e)}, 2)
    return out({"stored": True, "user": args.user, "scope": args.scope, "key": args.key, "value": args.value})


def cmd_memory_list(args) -> int:
    return out({"user": args.user, "scope": args.scope,
                "preferences": get_preference_details(args.user, args.scope)})


def cmd_memory_forget(args) -> int:
    deleted = forget_preference(args.user, args.scope, args.key)
    return out({"deleted": deleted, "key": args.key}, 0 if deleted else 1)


def cmd_search(args) -> int:
    return out({"query": args.query, "results": search_knowledge(args.query, top_k=args.top_k)})


# --------------------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m lab", description="OpenCode Lab CLI (all output is JSON)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check the environment").set_defaults(func=cmd_doctor)

    w = sub.add_parser("weather", help="Current weather for a city (Open-Meteo)")
    w.add_argument("city")
    w.set_defaults(func=cmd_weather)

    t = sub.add_parser("travel", help="Offline demo trip plan")
    t.add_argument("query")
    t.add_argument("--demo", action="store_true")
    t.set_defaults(func=cmd_travel)

    b = sub.add_parser("budget", help="Budget summary from a JSON list of items")
    b.add_argument("items_json", help='e.g. \'[{"name":"Hotel","cost_yen":9000,"is_estimate":true}]\'')
    b.add_argument("--limit", type=int, required=True, help="Budget limit in yen")
    b.set_defaults(func=cmd_budget)

    s = sub.add_parser("support", help="Order lookup and safe cancellation")
    ssub = s.add_subparsers(dest="action", required=True)
    sl = ssub.add_parser("lookup"); sl.add_argument("order_id"); sl.set_defaults(func=cmd_support_lookup)
    sc = ssub.add_parser("cancel"); sc.add_argument("order_id")
    sc.add_argument("--confirm", action="store_true", help="Only pass after the user explicitly said yes")
    sc.set_defaults(func=cmd_support_cancel)
    ssub.add_parser("reset", help="Restore demo orders").set_defaults(func=cmd_support_reset)

    m = sub.add_parser("memory", help="Scoped long-term preferences (SQLite)")
    m.add_argument("--user", default="demo")
    m.add_argument("--scope", default="general")
    msub = m.add_subparsers(dest="action", required=True)
    ms = msub.add_parser("set"); ms.add_argument("key"); ms.add_argument("value")
    ms.add_argument("--evidence", default="", help="What the user said that justifies storing this")
    ms.set_defaults(func=cmd_memory_set)
    msub.add_parser("list").set_defaults(func=cmd_memory_list)
    mf = msub.add_parser("forget"); mf.add_argument("key"); mf.set_defaults(func=cmd_memory_forget)

    q = sub.add_parser("search", help="Keyword search over knowledge/ (local RAG)")
    q.add_argument("query")
    q.add_argument("--top-k", type=int, default=2)
    q.set_defaults(func=cmd_search)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)  # argparse exits with code 2 on usage errors
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
