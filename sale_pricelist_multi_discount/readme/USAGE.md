To configure a multi-discount rule, edit the pricelist rule form and use
the *Discount Distribution* widget that appears for the *Percentage* and
*Formula* compute modes. Add the percentages one by one; they compose
multiplicatively.

When you then add the matching product to a sale order on this
pricelist, the line's `discount_distribution` is seeded with the same
list, so the end-customer-visible total reflects the full chain of
discounts rather than a single flattened percentage.

The native `percent_price` / `price_discount` fields on the rule are
kept in sync automatically: they always hold the multiplicative
aggregation of the distribution. Writing one of them directly (for
example through a single-value import) rewrites the distribution to that
single percentage, so the two representations never diverge.
