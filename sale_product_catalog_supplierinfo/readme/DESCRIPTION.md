This module extends
[sale_product_catalog_extended](https://github.com/OCA/sale-workflow/tree/18.0/sale_product_catalog_extended)
adding a new **Suppliers** origin to the sale order product catalog.

Each vendor card pins its supplierinfo on the sale order line, and the purchase
order line generated from it is priced from that row, also when later sales of
the same row are merged into it. To keep the rows of the same vendor in
different purchase order lines, install
[procurement_purchase_no_grouping_comment](https://github.com/OCA/stock-logistics-workflow/tree/18.0/procurement_purchase_no_grouping_comment),
which splits them by the vendor comment copied from each row.
