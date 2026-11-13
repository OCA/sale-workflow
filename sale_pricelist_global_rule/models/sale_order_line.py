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
            order = line.order_id
            if not order:
                # The line is not linked to an order (yet): there is nothing to
                # accumulate, fall back to the standard per-line computation.
                res = super(SaleOrderLine, line)._compute_pricelist_item_id()
                continue
            if order not in sale_data:
                sale_data[order] = order._get_cummulative_quantity()
            qty_data = sale_data[order]
            res = super(
                SaleOrderLine,
                line.with_context(pricelist_global_cummulative_quantity=qty_data),
            )._compute_pricelist_item_id()
        return res
