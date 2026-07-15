A lot of businesses don't set different prices according to the quantity of
the product to sell, and they find it very annoying to set a manual discount
after the negotiation with the customer, only to see it changed when they
vary the demanded quantity.

Since Odoo 18.0, the unit price is natively protected from recomputation when
modified manually (via the ``technical_price_unit`` field). However, the
``discount`` and ``pricelist_item_id`` fields are still recomputed when the
quantity or unit of measure changes.

This module prevents this by avoiding the recomputation of the discount and
pricelist item fields if only the quantity or unit of measure has been changed
in the sales order line.
