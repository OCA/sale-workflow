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

## Last sale price

A *Price* filter panel is added to the catalog search panel with a
**Last sale** option. When active, products not yet in the order show
the unit price from the most recent confirmed delivery to the same shipping
address (last 6 months) instead of the pricelist price. When a new line is
added with this mode enabled, that last-sale price is automatically applied
as the unit price.

## Origin filter

An *Origin* filter panel is added to the catalog search panel with a
**Last sales** option. When active, the catalog displays only products
that were previously sold to the same shipping address (last 6 months),
ordered by frequency and delivered quantity. This origin can be
preselected automatically through a system parameter (see *Configuration*).

## Image zoom

Clicking on a product image in the catalog opens a full-size zoom dialog.
