This module introduces a new apply-on option **`3_global`** in the field
`display_applied_on`.

When this option is selected, the module displays a new field
`global_applied_on`, allowing the user to choose how the global
pricelist rule should be applied:

- **Global – Product Template**
- **Global – Product Category**
- **Global – Ancestor Product Category**

This expands Odoo’s standard behavior by allowing pricelist rules to be
computed based on cumulative quantities across templates, categories, or
ancestor category trees.

---

## Cumulative Quantities in Pricelists

This module allows configured pricelists to be applied to a sales order
by considering cumulative quantities across all lines.

**Global by Product Template**

If a pricelist rule has a min_quantity = 15, and a sales order contains:

- Line 1: Variant 1, quantity = 8
- Line 2: Variant 2, quantity = 8

**Global by Product Category**

Similarly, if a pricelist rule has a min_quantity = 20 for products
within a category, and a sales order includes:

- Line 1: Product 1, quantity = 10
- Line 2: Product 2, quantity = 10

In standard Odoo, pricelist rules would not apply since no single line
meets the minimum quantity. With this module, however, cumulative
quantities across lines allow the pricelist rule to apply, as they meet
the minimum threshold (16 in the product template example and 20 in the
product category example).

**Global by Ancestor Product Category**

This option allows defining a rule on an *ancestor category*, and it will
apply to all products that belong to this category or any of its descendants.
The minimum quantity check is performed on the **total ordered quantity**
across all descendant categories.

For example, suppose we have the following category tree:

- Cat A
  - Cat B
  - Cat C
    - Cat D

And a pricelist rule is configured on *Cat C* with a minimum quantity = 5
and a 20% discount.
If a sales order contains:

- Line 1: Product in Cat C, quantity = 4
- Line 2: Product in Cat D, quantity = 2

Then the total for Cat C’s branch = 6 (4 + 2), which meets the minimum
threshold of 5. As a result, the 20% discount rule applies to both lines.
