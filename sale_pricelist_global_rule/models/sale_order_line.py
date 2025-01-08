from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_pricelist_item_id(self):
        # Compute the cumulative quantity of products in the sale order
        # for each line to ensure quantities are not mixed between different orders.
        # Store the data in a dictionary to avoid redundant computations
        # for the same order multiple times.
        sale_data = {}
        res = None
        for line in self:
            if line.order_id not in sale_data:
                sale_data[line.order_id] = line.order_id._get_cummulative_quantity()
            qty_data = sale_data[line.order_id]
            res = super(
                SaleOrderLine,
                line.with_context(pricelist_global_cummulative_quantity=qty_data),
            )._compute_pricelist_item_id()
        return res
