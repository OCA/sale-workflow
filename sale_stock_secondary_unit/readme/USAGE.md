### Selling a product in a secondary unit

1. On the product's *General Information* tab, add a secondary unit of
   measure and its conversion factor (from `product_secondary_unit`), and
   pick one as the sale-facing default (`sale_secondary_uom_id`, from
   `sale_order_secondary_unit`).
2. Create a sale order for that product and set the secondary quantity on the
   order line (e.g. "40" pieces) instead of, or alongside, the primary one.
3. Confirm the order. Open the resulting delivery (or receipt, for a
   multi-step purchase route): its stock move already carries the same
   secondary unit and quantity, ready to be counted on the warehouse floor.

### Adding a product to an already-confirmed order from the catalog

Adding a new line (or raising an existing one's quantity) through the sale
order's product catalog after confirmation also carries the secondary unit
onto the newly created (or extended) stock move(s), the same as confirming
the order from scratch would - no separate step needed.

### Correcting a piece count after confirmation

If an operator or salesperson needs to correct the secondary quantity on an
already-confirmed line - typically because the real count differs from what
was ordered, and the primary quantity (e.g. weight) is not being touched at
the same time - just edit the line's secondary quantity field and save:

- The pending delivery (or receipt) move for that line is updated to the new
  count immediately, without needing to re-run any procurement action.
- If the secondary unit is a `secondary_priority` one (see
  `stock_secondary_unit`), the move's own primary quantity is recalculated
  from the new count too, since the weight is only ever an estimate derived
  from it.
- If the line has already been partially processed and has more than one
  pending move at once, the correction is spread across all of them in
  proportion to what each was already carrying - there is nothing extra to
  do, the split happens automatically.

### A multi-step "buy" route

No extra configuration is needed: when the purchase route procures an
intermediate move before the final delivery (e.g. *Receive in 2 steps*), the
secondary unit still ends up on every move in the chain, not just the last
one linked to the sale order line.
