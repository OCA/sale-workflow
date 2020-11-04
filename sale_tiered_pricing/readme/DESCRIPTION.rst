This module provides Tiered Pricing features.
To make it available, you need to go to settings and activate "pricelists: compute from formulas" (TODO check the other option).
It extends pricelists to use them for tiered pricing, e.g:

- starting from 0, sell for 10€
- starting from 100, sell for 8€
- starting from 200, sell for 7€

In tiered pricing, somebody buying 250 units would pay `100*10 + 200*8 + 50*7`.
In other words the unit price is equivalent to the weighted average of tiers.

Because this pricing is put on a pricelist item, other pricelist items can use
it as base to provide further discounts.
Formulas can also be used to defined the price of a given tier.
Whereas a tiered pricelist cannot be recursive, i.e.
contain tiered pricelist items.
A valid recursive tier pricing can always be flattened to an equivalent non-recursive tier pricing, so there is no loss of generality.

When defining a tiered pricing pricelist some fields are not used,
i.e. "applied on", etc.
This is because these fields will be put on the pricelist item
that will perform the application of the pricelist.
If set, these could conflict with the parent item own values.
For this reason, when saving these extraneous fields are removed.

TODO...
