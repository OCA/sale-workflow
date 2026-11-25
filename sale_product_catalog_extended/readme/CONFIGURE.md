Go to *Sales > Configuration > Settings*. The **Product Catalog** block has
the options of the catalog opened from a sale order.

## Order catalog options

The options of the catalog search panel preselected when the catalog is
opened:

- **Origin**: the cards shown. Empty shows the products; other modules add
  further origins (e.g. **Suppliers** in `sale_product_catalog_supplierinfo`).
- **Last sales**: only show the products sold to the customer, most frequently
  sold first.
- **Price**: empty shows the pricelist price, **Last sale** the price of the
  last sale to the customer.
- **History**: the partner the sale history is matched against. Empty matches
  the customer (commercial partner, including its child contacts), **Delivery
  address** the order delivery address. Check **Show** to show this section in
  the catalog search panel, hidden by default; the partner chosen here applies
  either way.
- **Sort**: the order of the products. Empty keeps the order of the origin
  (favorites first, then by internal reference, or the most sold first for the
  last sales), **Name** sorts them by product name in the language of the user
  and **Category** by category and then by name. With the last sales, the
  most sold products are kept and then sorted. Check **Show** to show this
  section in the catalog search panel, hidden by default; the order chosen
  here applies either way.

They are saved as the global default value of the catalog fields of
`product.product` (`catalog_origin_data`, `catalog_last_sales`,
`catalog_price_mode`, `catalog_history_partner` and `catalog_sort`), so they
can also be set
per user or company in *Settings > Technical > User-defined Defaults*, as for
any other field.

## Order catalog last sales

- **Days**: days of sale history used by the **Last sales** option and the
  **Last sale** price, 180 by default.
- **Product limit**: maximum number of products shown by the **Last sales**
  option. `0` shows them all.

## Order catalog layout

- **Grid**: several product cards per row, as in the standard catalog.
- **Rows**: one card per row, with the image, the product data and the
  quantity buttons side by side. On wide screens the price and the quantity on
  hand go to a column of their own, so the cards are lower, and on extra wide
  screens the vendor of the supplier cards too. Every card keeps the same
  positions in every origin. Everything other modules add to the card is
  kept. Small screens and grouped views keep the grid cards.
