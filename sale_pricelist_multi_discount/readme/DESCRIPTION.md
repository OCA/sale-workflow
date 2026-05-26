This module configures multiple multiplicative discounts on pricelist
rules and propagates them to sale order lines.

It adds the `discount_distribution` JSON field on
`product.pricelist.item` and exposes it through the Discount
Distribution widget in the *Percentage* and *Formula* compute modes.
The distribution is aggregated multiplicatively and stored back into the
native `percent_price` (Percentage mode) and `price_discount` (Formula
mode) fields, so the standard price computation runs unchanged. The sale
order line then copies the same list into its own
`discount_distribution` field so the full chain of discounts is visible.
