This module prevents users from applying manual discounts on sale order lines
when the applied pricelist rule uses a fixed price.

The discount field becomes readonly on those sale lines, and backend writes are
validated to block discounts created through imports, RPC calls, or custom code.

Protection also applies when the price comes from a protected fixed-price rule
through one or more intermediate pricelists. The applicable rules are selected
using the sale line product, quantity, unit of measure, and order date.

Formula adjustments are preserved. For protected prices, automatic percentage
discounts are included in the unit price, while additional manual discounts
remain blocked.
