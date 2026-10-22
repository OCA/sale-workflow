Glue module between `sale_product_catalog_extended` and
`sale_order_secondary_unit`.

`sale_order_secondary_unit` makes the quantity typed in the sale catalog refer
to the product default sale secondary unit, and shows the secondary quantity of
the lines. This module applies the same rule to the quantities that
`sale_product_catalog_extended` sets on a specific order line, such as editing
one of several lines of the same product from its own catalog card, or adding
it from a vendor card of `sale_product_catalog_supplierinfo`, so the typed
quantity is always expressed in the unit the card shows.
