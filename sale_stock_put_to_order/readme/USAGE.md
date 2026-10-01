**Manual resolution**

Call
`picking._find_pto_dest_location_and_quants(excluded_locations=source)`
to iterate over candidate bins. The generator yields
`(location, quants)` pairs for locations with positive stock that pass
storage-category validation.

Use `picking._get_pto_bin_groups()` to obtain a mapping of
`{product_id: {"name": bin_name}}` for all products that already have
stock in a valid PTO bin.

**Automatic destination assignment**

When the *Auto-select PTO destination* setting is enabled, the module
overrides `_apply_putaway_strategy()` on `stock.move.line`. During
reservation (`action_assign`), each move line whose picking targets a
PTO zone is automatically redirected to the first valid bin. Lines
without a PTO match fall back to the standard putaway strategy.

**Extending the resolution logic:**

- Override `_get_pto_source_products()` to widen or narrow the product
  scope (e.g. include all products from a linked sale order).
- Override `_is_pto_location_valid()` to add custom checks (lot
  compatibility, weight limit, expiry date).
- Override `_prepare_pto_bin_group_vals()` to enrich the bin group
  payload with additional data.
