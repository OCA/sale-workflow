Glue module between `sale_order_line_final_price` and `sale_multi_discount`.

With `sale_multi_discount` installed the line `discount` is a read-only
aggregate of `discount_distribution`, computed by its own method. The
dependency on *Final Price* that `sale_order_line_final_price` declares on the
standard discount compute never reaches that field, so typing a final price
would leave the discount untouched.

This module resolves the final price into the discount distribution instead,
through an inverse when the line is written and through an onchange while it is
edited in the form. The unit price coming from the pricelist stays on the line,
as in `sale_order_line_final_price`, and the lock of the unit price applies to
the discount distribution widget as well.
