This module extends the standard Odoo product catalog available from sale
orders with the following additions:

## Multi-line product cards

When a product has more than one order line in the current sale order, the
catalog renders one card per line instead of a single aggregated card. Each
card shows the individual quantity and unit price for that specific line,
allowing independent editing without opening the order form.

## Per-line actions

Each in-order card exposes three inline actions:

- **New line** – adds a new order line for the same product.
- **Edit** – opens the specific order line form directly from the catalog.
- **Remove** – removes that individual line from the order.

## Search panel options

The catalog search panel gets these sections, combinable with each other and
with the standard ones:

- **Origin**: the cards shown, the products or the ones other modules add
  (e.g. one card per vendor row with `sale_product_catalog_supplierinfo`). It
  is only shown when such a module is installed.
- **Last sales**: restricts the cards of the chosen origin to the products
  previously sold to the customer (last 180 days by default), most frequently
  sold first, then by delivered quantity.
- **Price**: **Last sale** shows the unit price of the most recent delivered
  sale to the customer instead of the pricelist price, for the products that
  have one, and applies it to the lines added from the catalog.
- **History**: the partner the sale history is matched against, the customer
  (commercial partner, including its child contacts) or the order delivery
  address. It is only shown when enabled in the settings and while the *Last
  sales* option or the *Last sale* price is active, as it has no effect
  otherwise.

The options preselected when the catalog is opened, the period and the product
limit of the last sales are set in the Sales settings (see *Configuration*).

## Exclude from last sales

The card dropdown menu adds an **Exclude from last sales** entry. It stores the
product and the catalog history partner in a dedicated model, so that product is
no longer offered by the *Last sales* option for any order of that partner. The
*Last sale* price is not affected.

The entry is only shown while the *Last sales* option is active. On the vendor
cards of `sale_product_catalog_supplierinfo` it excludes the product, not the
vendor row.

The exclusion is dropped as soon as an order containing that product is
confirmed for the same partner, so the product goes back to the *Last sales*
option without any manual clean up. Adding the product to an already confirmed
order has the same effect.

The exclusions can be checked and deleted in *Sales > Configuration > Catalog
Last Sales Exclusions*, to offer an excluded product again without selling it.

## Image zoom

Clicking on a product image in the catalog opens a full-size zoom dialog.
