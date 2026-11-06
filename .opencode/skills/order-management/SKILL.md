---
name: order-management
description: Look up order status and handle cancellation requests safely (shipped orders cannot be cancelled; explicit confirmation required).
---
# Order management

1. Look up: `python -m lab support lookup <order_id>` (IDs are case-insensitive).
2. Decide from `status`:
   - `preparing`: can be cancelled, but only after explicit user confirmation.
   - `shipped`: cannot be cancelled. Explain the return-after-receipt process
     (`python -m lab search "return shipped order"`).
   - `cancelled`: already cancelled; take no action.
3. To cancel, show the order details, ask "Do you want to cancel this order? (yes/no)",
   and only after a clear yes run `python -m lab support cancel <order_id> --confirm`.
4. Report the `message` from the command output. Never say an order was cancelled unless `success` is true.
