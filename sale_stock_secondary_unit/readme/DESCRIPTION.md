This module bridges `sale_order_secondary_unit` (the secondary unit demanded on
a sale order line) and `stock_secondary_unit` (the secondary unit carried on a
stock move), so a product ordered in a secondary unit (e.g. "40 pieces" of a
product sold by weight) keeps that unit and quantity all the way through the
delivery/procurement chain, not just on the sale order line itself.

## Confirming an order

When a sale order is confirmed, the secondary unit and quantity of each line
are copied onto the stock move(s) it procures
(`sale.order.line._prepare_procurement_values()`), and `stock.rule` is told to
actually carry those two keys onto the created move
(`_get_custom_move_fields()`) - without this, a procurement only ever carries
core's own fields (product, quantity, dates...), never anything
module-specific.

## Multi-step "buy" routes

A multi-step purchase route (e.g. Receive in 2 steps) procures an
*intermediate* move first (the vendor receipt), which has no `sale_line_id` of
its own - only the eventual delivery move, further down the same chain, is
linked back to the sale order line. Without walking that chain,
`_prepare_procurement_values()` on the intermediate move would have no sale
line to read the secondary unit from and silently drop it (or worse, wipe out
whatever `stock_secondary_unit`'s own generic value already put there for a
pure-internal chain). `stock.move._prepare_procurement_values()` here falls
back to `sale_stock`'s own `_get_sale_order_lines()` (which walks the chain in
both directions) to find the real originating sale line, and only overrides
the secondary unit/quantity when one is actually found.

## Correcting a count on an already-confirmed order

A line's secondary quantity (e.g. a piece count) is sometimes corrected
*after* the order is confirmed and the delivery is already scheduled - a
weight-based product ordered as "40 pieces" turns out to need 42. Simply
writing the new count on the line does two things:

- Relaunches the sale order's own procurement rule *only if* the primary
  quantity (e.g. the weight) was written in the same call - a pure count
  correction never touches the primary quantity, and relaunching the stock
  rule for an unchanged primary quantity is a no-op (it only ever creates a
  new move for a primary-quantity delta; it never reads back into an existing
  move's secondary quantity).
- So, when only the count changes, the correction is instead written directly
  onto whichever stock move for that line is still pending (not `done` or
  `cancel`). For a `secondary_priority` secondary unit, writing it also
  recomputes that move's own primary quantity, since the weight is still
  estimated from the corrected count.
- If the line already has **more than one** pending move at once (e.g. a
  backorder pick still pending alongside an earlier leg not yet processed),
  the corrected total is distributed across all of them proportionally to
  each move's current secondary-quantity share, so none of them is left with
  a stale count and the sum still adds up exactly.
