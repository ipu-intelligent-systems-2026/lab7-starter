"""
Lab 7 Module 3: Operational Guardrails & Human-in-the-Loop (HITL)
モジュール 3：運用ガードレールと人間承認ゲート
"""
import copy
import json
import os
from typing import Any, Dict

_SEED_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-12345": {"status": "shipped", "item": "Wireless Noise-Cancelling Headphones", "price_yen": 24000},
    "ORD-12346": {"status": "preparing", "item": "Mechanical Ergonomic Keyboard", "price_yen": 18000},
    "ORD-12347": {"status": "cancelled", "item": "USB-C Docking Station", "price_yen": 12000},
}

# In-memory demo store (the CLI saves it to data/orders.json between commands).
ORDERS_DB: Dict[str, Dict[str, Any]] = copy.deepcopy(_SEED_ORDERS)

CANCELLABLE_STATUSES = {"preparing"}


# ----------------------------------------------------------------- provided helpers
def reset_orders() -> None:
    """Restore the demo data (used by tests so they don't leak state into each other)."""
    ORDERS_DB.clear()
    ORDERS_DB.update(copy.deepcopy(_SEED_ORDERS))


def load_orders(path: str) -> None:
    """Load order state saved by the CLI so a cancellation persists between commands."""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            ORDERS_DB.clear()
            ORDERS_DB.update(json.load(f))


def save_orders(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ORDERS_DB, f, ensure_ascii=False, indent=2)


def normalize_order_id(order_id: str) -> str:
    return (order_id or "").strip().upper()


def lookup_order(order_id: str) -> Dict[str, Any]:
    """Query order status from the local catalog (IDs are case-insensitive)."""
    oid = normalize_order_id(order_id)
    if oid not in ORDERS_DB:
        return {"found": False, "message": f"Order '{order_id}' was not found in the records."}
    return {"found": True, "order_id": oid, **ORDERS_DB[oid]}


# ----------------------------------------------------------------- student task
def cancel_order(order_id: str, confirmed: bool = False) -> Dict[str, Any]:
    """
    TODO [Task 3.1 / 3.2]: Irreversible Action Guardrails & HITL Confirmation (Week 5 & 7)
    Normalize the ID with normalize_order_id(), then:
    - Rule 1: Unknown order                     -> success False, message contains "not found"
    - Rule 2: status "shipped"                  -> success False, message contains "already shipped"
    - Rule 3: status "cancelled"                -> success False, message contains "already cancelled"
    - Rule 4: any other non-cancellable status  -> success False
    - Rule 5: confirmed is not exactly True ("yes", 1, "True" do NOT count)
                                                -> success False, message contains "confirmation required",
                                                   status unchanged
    - Rule 6: otherwise set status to "cancelled" -> success True
    Every result includes "success", "message" and (for known orders) "status".
    """
    # --- STUDENT IMPLEMENTATION START ---
    raise NotImplementedError("TODO: implement this block")
    # --- STUDENT IMPLEMENTATION END ---
