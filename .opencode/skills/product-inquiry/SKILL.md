---
name: product-inquiry
description: Answer questions about ordered products and store policy using only order records and the local knowledge base.
---
# Product inquiry

- Product facts (item name, price, status) come only from `python -m lab support lookup <order_id>`.
- Policy questions come only from `python -m lab search "<question>"`; name the source file.
- If neither source has the answer, say you don't have that information. Never invent
  specifications, stock levels or delivery dates.
