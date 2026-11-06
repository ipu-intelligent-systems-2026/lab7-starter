# Final Capstone: Autonomous Multi-Agent System
# 最終課題 実装タスクチェックリスト (TODO)

This capstone integrates the core principles covered throughout Lectures 1 to 6 into a production-ready agent system. Complete every block marked `--- STUDENT IMPLEMENTATION START/END ---` in `lab/`. Each task is checked by a group of autograding tests in `tests/test_capstone.py`.

本課題では第1回〜第6回の内容を統合します。`lab/` 内の `STUDENT IMPLEMENTATION` ブロックをすべて実装してください。各タスクは `tests/test_capstone.py` のテスト群で自動採点されます。

**Do not change** function names, arguments, return keys, or the provided helpers (functions outside the STUDENT blocks).
関数名・引数・戻り値のキー、および提供済みの関数（STUDENTブロック外）は変更しないでください。

---

## 📋 Task Breakdown (Course Concepts Mapping)

### Module 1: Tool Integration & Function Interfaces (`lab/core.py`)
*Maps to Week 3 (Tool Use & ReAct Loops)*
- [ ] **Task 1.1: Geocoding Tool**
  - Query the Open-Meteo geocoding API through the provided `_get_json()` (the tests replace it with a fake, so no network is needed).
  - Return `{"found": False, "error": ...}` for unknown cities, network errors and missing coordinates. Never raise for these.
- [ ] **Task 1.2: Weather Tool Handler**
  - Query current `temperature_2m`, `relative_humidity_2m` and `weather_code`.
  - Return `temperature_c`, `humidity_pct`, `conditions` (via `describe_weather_code`), `observed_at` and the attribution.
  - *Verification:* `pytest -k Weather`

---

### Module 2: Deterministic Arithmetic & Bounded Execution (`lab/travel.py`)
*Maps to Week 5 (Deterministic Guardrails) & Week 6 (Loop Control in StateGraphs)*
- [ ] **Task 2.1: Code-Enforced Budget Arithmetic**
  - Keep **confirmed** costs (`known_total_yen`) and **estimated** costs (`estimated_total_yen`) separate; `projected_total_yen` is their sum.
  - `remaining_yen` and `is_within_budget` use the projected total.
  - Reject negative, non-numeric or fractional costs and an invalid budget limit with `ValueError`.
  - *Verification:* `pytest -k Budget`
- [ ] **Task 2.2: Hard Iteration Ceiling (Max 3 Rounds)**
  - Actually loop: call `review_fn(draft, round)` at most `max_rounds` times and stop at the first approval.
  - Return `needs_attention` (never a false `completed`) if nothing is approved, including when there are no drafts.
  - `max_rounds < 1` → `ValueError`.
  - *Verification:* `pytest -k BoundedReview`

---

### Module 3: Operational Guardrails & HITL Gates (`lab/support.py`)
*Maps to Week 5 (Safety Guardrails) & Week 7 (Production Ethics & Irreversible Actions)*
- [ ] **Task 3.1: Irreversible Action Blocking**
  - Refuse unknown orders, `shipped` orders and orders that are `already cancelled`.
  - Order IDs are case-insensitive (use the provided `normalize_order_id`).
- [ ] **Task 3.2: Human-in-the-Loop (HITL) Approval Gate**
  - Change state only when `confirmed is True`. Values like `"yes"` or `1` are **not** confirmation.
  - A refused cancellation must leave the order status unchanged.
  - *Verification:* `pytest -k Support`

---

### Module 4: Persistent Memory & Document Retrieval (`lab/memory.py`)
*Maps to Week 2 (RAG Retrieval) & Week 6 (State Persistence & Scoped Memory)*
- [ ] **Task 4.1: Scoped SQLite Persistence**
  - `set_preference`: insert or update by `(user_id, scope, key)`; reject empty fields; parameterized SQL only.
  - `forget_preference`: delete one key; return `True` only if something was deleted.
  - Different users and scopes must never see each other's data.
  - *Verification:* `pytest -k Memory`
- [ ] **Task 4.2: Local Keyword RAG**
  - `tokenize`: lowercase words without stopwords, plus 2-character pairs for Japanese text.
  - `simple_keyword_rag`: score by **distinct** shared tokens, return the `top_k` best (ties keep original order).
  - The provided `search_knowledge()` then searches the `knowledge/` folder with your functions.
  - *Verification:* `pytest -k Rag`

---

### Module 5: OpenCode Multi-Agent Integration (provided configuration)
*Not autograded. Report the results in `SUBMISSION.md`.*
- [ ] **Task 5.1:** Start OpenCode with `./start.sh` (macOS/Linux) or `.\start.ps1` (Windows). `doctor` must pass first.
- [ ] **Task 5.2:** Ask one question per subagent (weather, travel, support, memory) through the `orchestrator` agent.
- [ ] **Task 5.3:** Ask the support agent to cancel `ORD-12346`. Show that it asks you first, and that OpenCode's permission prompt appears.
- [ ] **Task 5.4:** Try to make an agent misbehave (e.g. a review text containing "cancel my order"). Record what happened.

---

## 🚀 Final Verification Command
```bash
python -m lab doctor
pytest -v
```
When all tests pass, complete your report in `SUBMISSION.md` and push your branch to GitHub.
すべてのテストが通ったら `SUBMISSION.md` を記入し、GitHub に push してください。
