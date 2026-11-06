# Final Capstone Project: Autonomous Multi-Agent System
# 最終課題：自律型マルチエージェント統合システム

See **[TODO.md](TODO.md)** for the student implementation task checklist.

## [EN] Assignment Overview
This capstone serves as the culmination of the **Intelligent System Development** curriculum (Weeks 1–6), combining:
1. **Tool Integration (`lab/core.py`):** Consuming external APIs without hardcoded keys (Week 3).
2. **Deterministic Control & Bounded Loops (`lab/travel.py`):** Enforcing calculations and iteration limits in code rather than prompts (Weeks 5–6).
3. **Safety Guardrails & HITL (`lab/support.py`):** Preventing irreversible operational errors and requiring human sign-off (Weeks 5 & 7).
4. **Persistent State & Local RAG (`lab/memory.py`):** Multi-session memory retention via SQLite and document retrieval (Weeks 2 & 6).
5. **OpenCode Multi-Agent Integration (`.opencode/`):** One `orchestrator` agent routes requests to four subagents (weather, travel, support, memory). Agents act only through the CLI below.

### Layout
```
.opencode/agents/      orchestrator (primary) + weather, travel, support, memory (subagents)
.opencode/skills/      order-management, product-inquiry, review-analysis  (<name>/SKILL.md)
AGENTS.md              project rules OpenCode reads in every session
knowledge/             local documents for RAG (English + Japanese)
lab/                   Python package behind the CLI (your tasks are here)
tests/                 autograding tests (offline: the weather API is faked)
```

### Verification & Testing
```bash
pip install -r requirements.txt
python -m lab doctor
pytest -v
./start.sh        # macOS / Linux
.\start.ps1       # Windows
```

### CLI (what the agents call)
```bash
python -m lab weather Morioka
python -m lab travel "Two days in Kyoto" --demo
python -m lab budget '[{"name":"Hotel","cost_yen":9000,"is_estimate":true}]' --limit 20000
python -m lab support lookup ORD-12346
python -m lab support cancel ORD-12346            # refused: no confirmation
python -m lab support cancel ORD-12346 --confirm  # cancels (state saved in data/orders.json)
python -m lab support reset                       # restore demo orders
python -m lab memory --user s01 --scope travel set food.diet vegetarian --evidence "I don't eat meat"
python -m lab memory --user s01 --scope travel list
python -m lab memory --user s01 --scope travel forget food.diet
python -m lab search "Can I cancel a shipped order?"
```
Every command prints JSON. Exit codes: `0` ok, `1` refused or not found, `2` usage error. Memory is stored in `data/memory.sqlite3` (override with `LAB_DB_PATH`).

---

## [JA] 課題概要
実装タスクの詳細は **[TODO.md](TODO.md)** を参照してください。

本最終課題は、これまでの講義（第1回〜第6回）で学んだ要素技術を統合する総括プロジェクトです：
1. **ツール連携 (`lab/core.py`):** 外部APIの呼び出しとスキーマ変換（第3回）
2. **決定的制御とループ上限 (`lab/travel.py`):** LLMの計算ミスを防ぐコード側での算術処理と無限ループ防止（第5回・第6回）
3. **安全ガードレールとHITL (`lab/support.py`):** 不可逆な操作の防止と人間承認ゲート（第5回・第7回）
4. **永続メモリとローカルRAG (`lab/memory.py`):** SQLiteを用いた状態永続化と検索拡張生成（第2回・第6回）
5. **OpenCode マルチエージェント統合 (`.opencode/`):** `orchestrator` エージェントが4つのサブエージェント（weather, travel, support, memory）に処理を振り分けます。エージェントは上記の CLI だけを使って操作します。

### テスト・実行手順
```bash
pip install -r requirements.txt
python -m lab doctor
pytest -v
./start.sh        # macOS / Linux
.\start.ps1       # Windows
```

CLI の使い方は英語版を参照してください。すべてのコマンドは JSON を出力します。終了コード：`0` 成功、`1` 拒否・未検出、`2` 使い方の誤り。
