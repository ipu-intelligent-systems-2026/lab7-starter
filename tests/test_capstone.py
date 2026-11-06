"""
Lab 7 capstone tests (offline: the Open-Meteo API is mocked).
第7週 最終課題テスト（Open-Meteo API はモック化、ネットワーク不要）
"""
import json
from pathlib import Path

import pytest

import lab.core as core
from lab.__main__ import main
from lab.core import describe_weather_code, fetch_weather
from lab.memory import (forget_preference, get_preference_details, get_preferences, load_knowledge,
                        search_knowledge, set_preference, simple_keyword_rag)
from lab.support import cancel_order, lookup_order, reset_orders
from lab.travel import compute_budget_summary, run_bounded_review

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Fresh orders and a temporary memory DB for every test."""
    reset_orders()
    monkeypatch.setenv("LAB_DB_PATH", str(tmp_path / "mem.sqlite3"))
    monkeypatch.setattr("lab.__main__.ORDERS_STATE", str(tmp_path / "orders.json"))
    yield
    reset_orders()


# ===========================================================================
# Chapter 1: Weather
# ===========================================================================
GEO_OK = {"results": [{"name": "Tokyo", "country": "Japan", "latitude": 35.69, "longitude": 139.69}]}
WX_OK = {"current": {"time": "2026-11-05T17:00", "temperature_2m": 14.2,
                     "relative_humidity_2m": 61, "weather_code": 3}}


def fake_api(*responses):
    calls = []
    queue = list(responses)

    def _get_json(url):
        calls.append(url)
        r = queue.pop(0)
        if isinstance(r, Exception):
            raise r
        return r
    return _get_json, calls


class TestWeather:
    @pytest.mark.parametrize("city", ["", "   ", None])
    def test_empty_city(self, city):
        with pytest.raises(ValueError):
            fetch_weather(city)

    def test_success(self, monkeypatch):
        fn, calls = fake_api(GEO_OK, WX_OK)
        monkeypatch.setattr(core, "_get_json", fn)
        res = fetch_weather("  Tokyo ")
        assert res["found"] is True
        assert res["city"] == "Tokyo" and res["temperature_c"] == 14.2
        assert res["humidity_pct"] == 61 and res["conditions"] == "Overcast"
        assert "Open-Meteo" in res["attribution"]
        assert "name=Tokyo" in calls[0]  # input was stripped and URL-encoded

    def test_city_not_found(self, monkeypatch):
        monkeypatch.setattr(core, "_get_json", fake_api({"results": []})[0])
        res = fetch_weather("Atlantis")
        assert res["found"] is False and "not found" in res["error"]

    def test_network_error_does_not_raise(self, monkeypatch):
        monkeypatch.setattr(core, "_get_json", fake_api(OSError("timed out"))[0])
        res = fetch_weather("Tokyo")
        assert res["found"] is False and "failed" in res["error"]

    def test_malformed_weather_response(self, monkeypatch):
        monkeypatch.setattr(core, "_get_json", fake_api(GEO_OK, {"current": {}})[0])
        assert fetch_weather("Tokyo")["found"] is False

    def test_weather_code_descriptions(self):
        assert describe_weather_code(0) == "Clear sky"
        assert describe_weather_code(95) == "Thunderstorm"
        assert describe_weather_code(1234) == "Unknown"
        assert describe_weather_code(None) == "Unknown"


# ===========================================================================
# Chapter 2: Budget & bounded review
# ===========================================================================
class TestBudget:
    ITEMS = [
        {"name": "Bullet Train Ticket", "cost_yen": 14000, "is_estimate": False},
        {"name": "Zen Garden Admission", "cost_yen": 1000, "is_estimate": False},
        {"name": "Shojin Ryori Lunch", "cost_yen": 3500, "is_estimate": True},
    ]

    def test_known_and_estimated_are_separate(self):
        s = compute_budget_summary(self.ITEMS, budget_limit_yen=20000)
        assert s["known_total_yen"] == 15000
        assert s["estimated_total_yen"] == 3500
        assert s["projected_total_yen"] == 18500
        assert s["remaining_yen"] == 1500
        assert s["is_within_budget"] is True and s["has_estimates"] is True

    def test_over_budget_because_of_estimates(self):
        s = compute_budget_summary(self.ITEMS, budget_limit_yen=16000)
        assert s["known_total_yen"] <= 16000
        assert s["is_within_budget"] is False and s["remaining_yen"] == -2500

    def test_exactly_on_budget(self):
        assert compute_budget_summary(self.ITEMS, 18500)["is_within_budget"] is True

    def test_empty_items(self):
        s = compute_budget_summary([], 1000)
        assert s["projected_total_yen"] == 0 and s["remaining_yen"] == 1000

    @pytest.mark.parametrize("cost", [-1, "abc", None, 12.5, True])
    def test_invalid_costs_rejected(self, cost):
        with pytest.raises(ValueError):
            compute_budget_summary([{"name": "x", "cost_yen": cost}], 1000)

    @pytest.mark.parametrize("limit", [-1, "1000", 10.5])
    def test_invalid_limit_rejected(self, limit):
        with pytest.raises(ValueError):
            compute_budget_summary([], limit)


class TestBoundedReview:
    def test_ceiling_reached(self):
        r = run_bounded_review(["D1", "D2", "D3", "D4"], max_rounds=3)
        assert r["rounds_executed"] == 3 and r["status"] == "needs_attention"
        assert r["final_draft"] == "D3"

    def test_completes_within_limit(self):
        r = run_bounded_review(["D1", "D2"], max_rounds=3)
        assert r["status"] == "completed" and r["rounds_executed"] == 2 and r["final_draft"] == "D2"

    def test_custom_reviewer_approves_early(self):
        r = run_bounded_review(["bad", "good", "unused"], max_rounds=3,
                               review_fn=lambda d, _rnd: d == "good")
        assert r["status"] == "completed" and r["rounds_executed"] == 2

    def test_reviewer_never_called_beyond_ceiling(self):
        seen = []
        run_bounded_review([f"D{i}" for i in range(10)], max_rounds=3,
                           review_fn=lambda d, rnd: seen.append(rnd) or False)
        assert seen == [1, 2, 3]

    def test_no_drafts_is_not_success(self):
        r = run_bounded_review([], max_rounds=3)
        assert r["status"] == "needs_attention" and r["rounds_executed"] == 0

    @pytest.mark.parametrize("bad", [0, -1])
    def test_invalid_max_rounds(self, bad):
        with pytest.raises(ValueError):
            run_bounded_review(["D1"], max_rounds=bad)


# ===========================================================================
# Chapter 3: Support guardrails
# ===========================================================================
class TestSupport:
    def test_cannot_cancel_shipped(self):
        res = cancel_order("ORD-12345", confirmed=True)
        assert res["success"] is False and "already shipped" in res["message"]
        assert lookup_order("ORD-12345")["status"] == "shipped"

    def test_requires_confirmation(self):
        res = cancel_order("ORD-12346", confirmed=False)
        assert res["success"] is False and "confirmation required" in res["message"]
        assert lookup_order("ORD-12346")["status"] == "preparing"

    @pytest.mark.parametrize("fake_yes", ["yes", 1, "True"])
    def test_only_real_true_counts_as_confirmation(self, fake_yes):
        assert cancel_order("ORD-12346", confirmed=fake_yes)["success"] is False

    def test_confirmed_cancel_succeeds_once(self):
        assert cancel_order("ORD-12346", confirmed=True)["success"] is True
        assert lookup_order("ORD-12346")["status"] == "cancelled"
        again = cancel_order("ORD-12346", confirmed=True)
        assert again["success"] is False and "already cancelled" in again["message"]

    def test_unknown_order(self):
        assert cancel_order("ORD-00000", confirmed=True)["success"] is False
        assert lookup_order("ORD-00000")["found"] is False

    def test_order_ids_case_insensitive(self):
        assert lookup_order("  ord-12345 ")["found"] is True

    def test_tests_do_not_leak_state(self):
        # Runs after a cancelling test in the same session: the fixture must have reset it.
        assert lookup_order("ORD-12346")["status"] == "preparing"


# ===========================================================================
# Chapter 4: Memory & RAG
# ===========================================================================
class TestMemory:
    def test_roundtrip_with_evidence(self):
        set_preference("student_01", "travel", "food.diet", "vegetarian", "I do not eat meat")
        assert get_preferences("student_01", "travel") == {"food.diet": "vegetarian"}
        assert get_preference_details("student_01", "travel")[0]["evidence"] == "I do not eat meat"

    def test_update_overwrites(self):
        set_preference("u", "travel", "pace", "fast")
        set_preference("u", "travel", "pace", "slow")
        assert get_preferences("u", "travel") == {"pace": "slow"}

    def test_scopes_and_users_are_isolated(self):
        set_preference("alice", "travel", "food.diet", "vegetarian")
        set_preference("alice", "support", "contact.language", "ja")
        set_preference("bob", "travel", "food.diet", "none")
        assert get_preferences("alice", "travel") == {"food.diet": "vegetarian"}
        assert get_preferences("alice", "support") == {"contact.language": "ja"}
        assert get_preferences("bob", "travel") == {"food.diet": "none"}

    def test_forget(self):
        set_preference("u", "travel", "food.diet", "vegetarian")
        set_preference("u", "travel", "pace", "slow")
        assert forget_preference("u", "travel", "food.diet") is True
        assert get_preferences("u", "travel") == {"pace": "slow"}
        assert forget_preference("u", "travel", "food.diet") is False

    def test_bare_filename_db_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        set_preference("u", "s", "k", "v", db_path="flat.sqlite3")
        assert get_preferences("u", "s", db_path="flat.sqlite3") == {"k": "v"}

    def test_persists_across_connections(self, tmp_path):
        db = str(tmp_path / "persist.sqlite3")
        set_preference("u", "s", "k", "v", db_path=db)
        assert get_preferences("u", "s", db_path=db) == {"k": "v"}

    @pytest.mark.parametrize("args", [("", "s", "k", "v"), ("u", "", "k", "v"),
                                      ("u", "s", " ", "v"), ("u", "s", "k", "")])
    def test_empty_fields_rejected(self, args):
        with pytest.raises(ValueError):
            set_preference(*args)


class TestRag:
    DOCS = [
        "Quiet gardens in Kyoto include Daitoku-ji and Ryoan-ji zen rocks.",
        "Tokyo metropolitan subway fare calculation and IC card recharge rules.",
        "Vegetarian restaurants and tofu cuisine around Arashiyama bamboo grove.",
    ]

    def test_keyword_rag(self):
        res = simple_keyword_rag("Find quiet gardens and zen temple in Kyoto", self.DOCS, top_k=1)
        assert len(res) == 1 and "Daitoku-ji" in res[0]

    def test_stopwords_do_not_score(self):
        docs = ["the the the and in of in of", "Daitoku-ji zen temple"]
        assert simple_keyword_rag("the zen temple in Kyoto", docs, top_k=1) == ["Daitoku-ji zen temple"]
        assert simple_keyword_rag("the and in of", docs) == []

    def test_repeated_words_do_not_inflate_score(self):
        docs = ["kyoto kyoto kyoto kyoto", "kyoto zen garden"]
        assert simple_keyword_rag("kyoto zen garden", docs, top_k=1) == ["kyoto zen garden"]

    def test_japanese_partial_match(self):
        docs = ["京都の静かな庭園なら大徳寺がおすすめ", "東京の地下鉄の運賃について"]
        assert simple_keyword_rag("京都にある庭園", docs, top_k=1) == [docs[0]]

    def test_knowledge_folder_is_loaded(self):
        chunks = load_knowledge()
        assert {c["source"] for c in chunks} >= {"return_policy.md", "travel_guidelines.md"}

    @pytest.mark.parametrize("query,source,snippet", [
        ("Can I cancel a shipped order?", "return_policy.md", "Shipped"),
        ("vegetarian food in Arashiyama", "travel_guidelines.md", "Shojin"),
        ("出荷済みの注文はキャンセルできますか", "return_policy.md", "出荷済み"),
    ])
    def test_search_knowledge(self, query, source, snippet):
        top = search_knowledge(query, top_k=1)[0]
        assert top["source"] == source and snippet in top["text"]


# ===========================================================================
# CLI (what the OpenCode agents actually call)
# ===========================================================================
def run_cli(capsys, *argv):
    code = main(list(argv))
    return code, json.loads(capsys.readouterr().out)


class TestCli:
    def test_cancel_flow_persists_between_commands(self, capsys):
        code, res = run_cli(capsys, "support", "cancel", "ORD-12346")
        assert code == 1 and res["success"] is False
        code, res = run_cli(capsys, "support", "cancel", "ORD-12346", "--confirm")
        assert code == 0 and res["success"] is True
        reset_orders()  # simulate a new process: state must come from the saved file
        code, res = run_cli(capsys, "support", "lookup", "ORD-12346")
        assert res["status"] == "cancelled"

    def test_memory_commands(self, capsys):
        run_cli(capsys, "memory", "--user", "s1", "--scope", "travel", "set", "food.diet", "vegetarian",
                "--evidence", "I do not eat meat")
        _, res = run_cli(capsys, "memory", "--user", "s1", "--scope", "travel", "list")
        assert res["preferences"][0]["value"] == "vegetarian"
        code, res = run_cli(capsys, "memory", "--user", "s1", "--scope", "travel", "forget", "food.diet")
        assert code == 0 and res["deleted"] is True

    def test_usage_error_exits_2(self, capsys):
        with pytest.raises(SystemExit) as e:
            main(["memory", "set", "only_key"])
        assert e.value.code == 2

    def test_budget_command(self, capsys):
        items = json.dumps(TestBudget.ITEMS)
        code, res = run_cli(capsys, "budget", items, "--limit", "20000")
        assert code == 0 and res["projected_total_yen"] == 18500
        code, res = run_cli(capsys, "budget", "not json", "--limit", "1")
        assert code == 2 and "error" in res

    def test_doctor_passes(self, capsys):
        code, res = run_cli(capsys, "doctor")
        assert code == 0 and res["ok"] is True


# ===========================================================================
# OpenCode configuration
# ===========================================================================
def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} must start with YAML frontmatter"
    block = text.split("---\n", 2)[1]
    return {line.split(":", 1)[0]: line.split(":", 1)[1].strip()
            for line in block.splitlines() if line and not line.startswith(" ") and ":" in line}


class TestOpenCodeConfig:
    def test_skills_follow_opencode_format(self):
        skills = list((ROOT / ".opencode" / "skills").glob("*/SKILL.md"))
        assert len(skills) >= 2
        for path in skills:
            fm = frontmatter(path)
            assert fm.get("name") == path.parent.name
            assert 1 <= len(fm.get("description", "")) <= 1024

    def test_one_primary_agent_and_subagents(self):
        modes = {p.stem: frontmatter(p).get("mode") for p in (ROOT / ".opencode" / "agents").glob("*.md")}
        assert list(modes.values()).count("primary") == 1
        assert list(modes.values()).count("subagent") >= 3

    def test_cancel_requires_approval_in_support_agent(self):
        text = (ROOT / ".opencode" / "agents" / "support.md").read_text(encoding="utf-8")
        assert '"python -m lab support cancel *": ask' in text
