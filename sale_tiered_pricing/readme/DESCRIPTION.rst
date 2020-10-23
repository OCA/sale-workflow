This module provides Tiered and Volume Pricing features.
To make it available, you need to go to settings and activate "pricelists: compute from formulas" (TODO check the other option).
It extends pricelists to use them for tiered pricing, e.g:

- starting from 0, sell for 10€
- starting from 100, sell for 8€
- starting from 200, sell for 7€

In tiered pricing, somebody buying 250 units would pay `100*10 + 200*8 + 50*7`.
In volume pricing, somebody buying 250 units would pay `250*7`.
In the first case the unit price is equivalent to the weighted average of tiers,
in the latter the highest reached tier's price is used.

Because this pricing is put on a pricelist item, other pricelist items can use
it as base to provide further discounts.
Formulas can also be used to defined the price of a given tier.
Whereas a tiered/volume pricelist cannot be recursive, i.e.
contain tiered/volume pricelist items.
A valid recursive tier pricing can always be flattened to an equivalent non-recursive tier pricing, so there is no loss of generality.

When defining a tiered pricing pricelist
(which can also be used as a volume pricing pricelist,
the application rule is defined at the pricelist item level)
some fields are not used, i.e. "applied on", etc.
This is because these fields will be put on the pricelist item
that will perform the application of the pricelist.
If set, these could conflict with the parent item own values.
For this reason, when saving these extraneous fields are removed.

TODO... (more about the pricelist view I guess).
TODO: check formatting
