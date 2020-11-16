To make it available, you need to go to settings and activate pricelists.
When this module is installed, activating any pricelist option activates all
features (formulas and the option to see pricelists from product).

Note also that since the price unit is computed as a weighted average,
it is important to set a high decimal precision to avoid rounding issues.

Because this pricing is put on a pricelist item, other pricelist items can use
it as base to provide further discounts.
Formulas can also be used to defined the price of a given tier.
Whereas a tiered pricelist cannot be recursive, i.e. contain tiered pricelist items.
A valid recursive tier pricing can always be flattened to an equivalent
non-recursive tier pricing, so there is no loss of generality.

When defining a tiered pricing pricelist some fields are not used,
i.e. "applied on", etc.
This is because these fields will be put on the pricelist item
that will perform the application of the pricelist.
If set, these could conflict with the parent item own values.
For this reason, when saving these extraneous fields are removed.
