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

They are saved as the global default value of the catalog fields of
`product.product` (`catalog_origin_data`, `catalog_last_sales`,
`catalog_price_mode` and `catalog_history_partner`), so they can also be set
per user or company in *Settings > Technical > User-defined Defaults*, as for
any other field.

## Order catalog last sales

- **Days**: days of sale history used by the **Last sales** option and the
  **Last sale** price, 180 by default.
- **Product limit**: maximum number of products shown by the **Last sales**
  option. `0` shows them all.
