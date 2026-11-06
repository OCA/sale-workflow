On a sale order, open the product catalog and pick the **Suppliers** origin.
Each sellable product with an applicable vendor row (`product.supplierinfo`) is
shown with one card per row: a row of a variant only for that variant, a row
without variant for every variant of the template. Adding a card creates (or
updates) an order line carrying that vendor (`vendor_id`), the exact row the
card priced from (`supplierinfo_id`) and its comment (`vendor_comment`).

Combined with the **Last sales** option, the catalog only shows the products
with vendors sold to the customer in the last days, most frequently sold first,
each one with all its vendor cards. With the **Last sale** price, each card
shows the last price of its row, or else of its vendor. The **Suppliers**
origin can be preselected in *Sales > Configuration > Settings > Product
Catalog*.

The vendor cards show **On order** instead of the vendor name, so the vendor
is not disclosed while showing the catalog. Check **Show the vendor on the
catalog cards** in the same settings block to show it.

## How the per-vendor price is resolved

With
[product_pricelist_supplierinfo](https://github.com/OCA/product-attribute/tree/18.0/product_pricelist_supplierinfo)
installed, a pricelist item can be based on the vendor's own price
(`base = "supplierinfo"`) instead of a fixed or cost-based one. This module
makes that price actually vary by the vendor picked on the catalog card or
on the order line's own **Vendor** field, in two places:

- **Which pricelist rule applies.** A category/product commonly has both a
  generic rule (e.g. `base = "standard_price"`) and a vendor-specific one
  (`base = "supplierinfo"`). Nothing about `product.pricelist.item`'s own
  ordering favors one over the other based on "a vendor was requested" — so
  this module reorders the candidates: the `supplierinfo` rule first when a
  vendor is forced (`force_filter_supplier_id`), last otherwise, falling
  back to the generic rule when there is none.
- **What price that rule computes.** Once a `supplierinfo` rule is chosen,
  its price still needs to know *which* vendor to price from — the line's
  `vendor_id`, forwarded as `force_filter_supplier_id`.

Both need to see the same vendor: this module makes sure the sale order
line's own pricelist-rule resolution (`pricelist_item_id`) is computed
against the vendor-annotated product, matching what the price computation
itself already used, so the two agree.

## Pinning an exact vendor row

A vendor can have more than one valid `product.supplierinfo` row at once
(e.g. a new price already active while the old one hasn't expired yet).
`_select_seller()` alone would just pick the cheapest one, which is not
necessarily the one shown/picked on a catalog card. Setting the line's
`supplierinfo_id` (as the catalog does) pins that exact row instead, for
both the price shown on the line and, if the sale generates a purchase
order (MTO/buy route), the resulting purchase order line.
