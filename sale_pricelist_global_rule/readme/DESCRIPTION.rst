This module allows configured pricelists to be applied to a sales order by considering cumulative quantities across all lines.

**Global by Product Template**

If a pricelist rule has a `min_quantity = 15`, and a sales order contains:

- Line 1: Variant 1, quantity = 8
- Line 2: Variant 2, quantity = 8

**Global by Product Category**

Similarly, if a pricelist rule has a `min_quantity = 20` for products within a category, and a sales order includes:

- Line 1: Product 1, quantity = 10
- Line 2: Product 2, quantity = 10

In standard Odoo, pricelist rules would not apply since no single line meets the minimum quantity. 
With this module, however, cumulative quantities across lines allow the pricelist rule to apply, 
as they meet the minimum threshold (16 in the product template example and 20 in the product category example).
