"""
Lab 7 Module 2: Deterministic Budget Arithmetic & Bounded Iteration
モジュール 2：確定的予算計算と反復上限制御
"""
from typing import Any, Callable, Dict, List, Optional


def compute_budget_summary(items: List[Dict[str, Any]], budget_limit_yen: int) -> Dict[str, Any]:
    """
    TODO [Task 2.1]: Deterministic Budget Arithmetic (Week 5 Concept)
    Compute the budget in Python (never by the LLM), keeping confirmed and estimated costs apart.
    確定費用と見積費用を分けて、Pythonで予算を計算する。

    - budget_limit_yen must be a non-negative int, otherwise raise ValueError.
    - Each cost_yen must be a whole, non-negative number (not bool, not str), otherwise ValueError.
    - known_total_yen:     sum of items with is_estimate = False
    - estimated_total_yen: sum of items with is_estimate = True
    - projected_total_yen: known + estimated (the budget check uses this figure)
    - remaining_yen = budget_limit_yen - projected_total_yen
    - is_within_budget = projected_total_yen <= budget_limit_yen
    - has_estimates, item_count, items (name, cost_yen, is_estimate for each item)
    """
    # --- STUDENT IMPLEMENTATION START ---
    raise NotImplementedError("TODO: implement this block")
    # --- STUDENT IMPLEMENTATION END ---


ReviewFn = Callable[[str, int], bool]


def run_bounded_review(drafts: List[str], max_rounds: int = 3,
                       review_fn: Optional[ReviewFn] = None) -> Dict[str, Any]:
    """
    TODO [Task 2.2]: Bounded Review Iteration Ceiling (Week 6 StateGraph Concept)
    Run a draft -> review loop with a hard ceiling of `max_rounds`.
    レビューは最大 max_rounds 回まで。上限に達したら 'needs_attention'（偽の成功を報告しない）。

    drafts:    successive drafts (draft i is what the writer produces in round i)
    review_fn: review_fn(draft, round_number) -> True if approved.
               Default (None): only the last supplied draft is approved.

    - max_rounds < 1 (or not an int) -> raise ValueError
    - Call review_fn at most max_rounds times, stop at the first approval.
    - Approved     -> status "completed", rounds_executed = that round, final_draft = that draft
    - Not approved -> status "needs_attention", final_draft = last reviewed draft ("" if none), add "reason"
    - Always return rounds_executed, max_rounds, status, final_draft and
      history = [{"round": n, "approved": bool}, ...]
    """
    # --- STUDENT IMPLEMENTATION START ---
    raise NotImplementedError("TODO: implement this block")
    # --- STUDENT IMPLEMENTATION END ---
