## 19.0.1.0.0 (2026-11-25)

- Migration to 19.0.
- `stock.package_level` no longer exists in 19.0: the Customer Ref. column on
  the package level form has been removed. The reference is still shown on
  moves, move lines and packages (`stock.package`).
- Behaviour change coming from Odoo 19.0 core: `sale_stock` now propagates
  `sale_line_id` to the chained pick/pack moves, and `sale_line_id` is a
  merge-distinct field. Chained moves of different sale order lines are
  therefore never merged anymore, even when they share the same customer
  reference (one pick/pack line per sale order line).
