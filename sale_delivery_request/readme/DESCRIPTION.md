This module implements a structured workflow to manage delivery date
consultations between Sales and Planning for Sales Orders.

It introduces a new model to request, confirm and track delivery dates
before generating stock pickings, supporting full order, line-level and
partial quantity confirmations.

The module allows Sales to request delivery dates from Planning before
confirming a Sales Order. Planning responds with confirmed delivery dates,
which are interpreted as relative lead times in business days.

Stock pickings are grouped automatically based on confirmed delivery dates,
supporting:

- Full order confirmation
- Line-level confirmation
- Partial quantity delivery splitting
- Expiration and re-confirmation logic

This module depends on `sale_delivery_split_date`.
