Two methods are meant to be extended by other modules:

- `sale.order._prepare_merge_key()` returns the values two quotations must have
  in common to be merged. Add an element to forbid merging quotations that
  differ on one more field.
- `sale.order.line._merge_line_key()` returns the values two lines must have in
  common to be consolidated. Add an element to keep lines apart on one more
  field, or `self.id` to keep them from ever being consolidated.

Two more hooks are available:

- `sale.order.line._move_to_order()` reassigns a line to the merged quotation.
- `sale.order._post_merge_from()` runs on the merged quotation once the lines
  and the references have been moved over.
