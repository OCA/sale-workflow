from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_pricelist_global_cumulative_quantity(self):
        sale_data = {}
        for line in self:
            if line.order_id not in sale_data:
                sale_data[line.order_id] = line.order_id._get_cummulative_quantity()
        return sale_data

    def _compute_pricelist_item_id(self):
        # Compute the cumulative quantity of products in the sale order
        # for each line to ensure quantities are not mixed between different orders.
        # Store the data in a dictionary to avoid redundant computations
        # for the same order multiple times.
        sale_data = self._prepare_pricelist_global_cumulative_quantity()
        for line in self:
            qty_data = sale_data[line.order_id]
            res = super(
                SaleOrderLine,
                line.with_context(pricelist_global_cummulative_quantity=qty_data),
            )._compute_pricelist_item_id()
        return res

    def _compute_price_unit(self):
        # As the price computation is done in 2 steps, first with the pricelist item,
        # and then this price, if the pricelists are set in several levels, the first
        # step only computes the direct rule, but if the global rule is at another
        # pricelist, then here the cumulative quantities are not set in the context, so
        # we need to perform the same operation
        sale_data = self._prepare_pricelist_global_cumulative_quantity()
        for line in self:
            qty_data = sale_data[line.order_id]
            res = super(
                SaleOrderLine,
                line.with_context(pricelist_global_cummulative_quantity=qty_data),
            )._compute_price_unit()
        return res

    def _compute_discount(self):
        # Same case as _compute_price_unit
        sale_data = self._prepare_pricelist_global_cumulative_quantity()
        for line in self:
            qty_data = sale_data[line.order_id]
            res = super(
                SaleOrderLine,
                line.with_context(pricelist_global_cummulative_quantity=qty_data),
            )._compute_discount()
        return res
