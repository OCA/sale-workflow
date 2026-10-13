Configure locations as **put-to-order** zones to direct incoming goods
to bins that already hold products from the same order.

When a picking targets a PTO root location, the system examines child
bins for existing stock of the relevant products and proposes a
destination bin that passes storage-category validation.

**Key features:**

- Recursive `is_pto` boolean on `stock.location` — set on a parent and
  all children inherit the flag automatically.
- **Sale-order awareness** — when a picking is linked to a sale order,
  the resolution considers all products from the order (including lines
  not yet delivered) for more accurate bin selection on partial
  deliveries and backorders.
- Optional **auto-select** mode that automatically sets the destination
  on move lines during reservation (via `_apply_putaway_strategy`).
- Deterministic candidate ordering for reproducible bin selection.
- Extensible hook methods for custom validation rules
  (`_is_pto_location_valid`, `_get_pto_source_products`,
  `_prepare_pto_bin_group_vals`).
