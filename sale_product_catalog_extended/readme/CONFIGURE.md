## Default catalog origin

By default the catalog opens with no origin preselected. You can make it
open directly on a specific origin by setting a system parameter:

1. Go to *Settings > Technical > Parameters > System Parameters*.
2. Create a new parameter with:
   - **Key:** `sale_product_catalog_extended.catalog_default_origin`
   - **Value:** the technical value of the origin to preselect. This
     module provides `sale_order` (the **Last sales** option). Other
     modules may add further origins; use the corresponding selection
     value here.

When this parameter is set, opening the catalog from a sale order will
preselect the matching option in the *Origin* search panel automatically.
For example, set the value to `sale_order` to always open the catalog on
the **Last sales** origin. Leaving the parameter empty or removing it
restores the default behaviour (no origin preselected).

## Default catalog price mode

By default the catalog opens with no price mode preselected. You can make
it open directly on a specific price mode by setting a system parameter:

1. Go to *Settings > Technical > Parameters > System Parameters*.
2. Create a new parameter with:
   - **Key:** `sale_product_catalog_extended.catalog_default_price_mode`
   - **Value:** the technical value of the price mode to preselect. This
     module provides `last_price` (the **Last sale** option). Other
     modules may add further price modes; use the corresponding selection
     value here.

When this parameter is set, opening the catalog from a sale order will
preselect the matching option in the *Price* search panel automatically.
For example, set the value to `last_price` to always open the catalog on
the **Last sale** price mode. Leaving the parameter empty or removing it
restores the default behaviour (no price mode preselected).

## Catalog history partner

The **Last sales** origin and the **Last sale** price look at the customer
sale history. By default that history is matched against the order
**commercial partner** (including its child contacts), so all the orders of
the same customer are taken into account regardless of the delivery address.

You can match the history against the order **delivery address** instead
through *Default Values*, scoped per user and company (same mechanism as the
sale order product picker):

1. Go to *Settings > Technical > Default Values*.
2. Create a new default value for:
   - **Field:** `sale.order` → `use_delivery_address`
   - **Value:** `True` to match by delivery address. Leaving no default (or
     `False`) keeps the default behaviour (commercial partner).

This affects both the order of the cards under the **Last sales** origin
(products are sorted by how often and how much they were sold to the matched
partner) and the price shown by the **Last sale** price mode.
