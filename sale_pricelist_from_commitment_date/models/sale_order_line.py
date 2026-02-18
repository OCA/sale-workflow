# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "order_id.commitment_date",
    )
    def _compute_price_unit(self):
        return super()._compute_price_unit()

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "order_id.commitment_date",
    )
    def _compute_pricelist_item_id(self):
        return super()._compute_pricelist_item_id()

    def _get_order_date(self):
        if self.order_id.commitment_date:
            return self.order_id.commitment_date
        return super()._get_order_date()
