Some customers can only be served in multiples of a given quantity of a product:
a full box, a layer or a pallet, or the way their own purchase system orders it.
This module adds a **Sale Multiple** to the customer info of the product
(`product.customerinfo`, the same record that holds the customer's product code)
and applies it to the sale order lines of that customer:

- **Round down**: 63 units with a multiple of 50 become 50. The customer
  is served the full multiples only, as many distributors do with
  logistic units.
- **Round up**: 63 units become 100.
- **Round to the nearest**: halves go up, so 74 units become 50 and 75
  become 100. It never goes below one multiple: 20 units become 50.
- **Only warn**: the quantity is kept and the line is highlighted.

The rounding is done in the sale order form, with a warning showing the ordered
and the adjusted quantity, and also on lines created or changed by code
(imports, EDI, portals), leaving a note on the order. The multiple is in the
unit of measure of the product; lines in another unit are converted.

Unlike `sale_restricted_qty`, which sets the restrictions on the product for every
customer, the multiple here belongs to one customer, so each customer can have
its own (or none).
