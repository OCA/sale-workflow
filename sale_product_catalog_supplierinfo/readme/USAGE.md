On a sale order, open the product catalog and pick the **Suppliers** origin
(`catalog_origin_data = "supplierinfo"`). Every sellable product with at
least one vendor is shown once per vendor: adding a card creates (or
updates) an order line carrying that vendor (`vendor_id`) and, when the
vendor has more than one concurrently valid price, the exact
`product.supplierinfo` row that card priced from (`supplierinfo_id`).

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
