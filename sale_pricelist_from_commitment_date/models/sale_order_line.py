# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.depends(
        "product_id", "product_uom", "product_uom_qty", "order_id.commitment_date"
    )
    def _compute_price_unit(self):
        for line in self:
            date = self.env.context.get(
                "force_pricelist_date", line.order_id.commitment_date
            )
            line = line.with_context(force_pricelist_date=date)
            super(SaleOrderLine, line)._compute_price_unit()
        return True

    @api.depends(
        "product_id", "product_uom", "product_uom_qty", "order_id.commitment_date"
    )
    def _compute_pricelist_item_id(self):
        for line in self:
            date = self.env.context.get(
                "force_pricelist_date", line.order_id.commitment_date
            )
            line = line.with_context(force_pricelist_date=date)
            super(SaleOrderLine, line)._compute_pricelist_item_id()
        return True
