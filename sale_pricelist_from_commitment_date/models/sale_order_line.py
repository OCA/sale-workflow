# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import groupby


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "order_id.commitment_date",
        "order_id.pricelist_id",
    )
    def _compute_price_unit(self):
        for order, lines in groupby(self, key=lambda line: line.order_id):
            date = order._get_pricelist_date()
            lines_ = (
                self.browse().concat(*lines).with_context(force_pricelist_date=date)
            )
            super(SaleOrderLine, lines_)._compute_price_unit()
        return True

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "order_id.commitment_date",
        "order_id.pricelist_id",
    )
    def _compute_pricelist_item_id(self):
        for order, lines in groupby(self, key=lambda line: line.order_id):
            date = order._get_pricelist_date()
            lines_ = (
                self.browse().concat(*lines).with_context(force_pricelist_date=date)
            )
            super(SaleOrderLine, lines_)._compute_pricelist_item_id()
        return True
