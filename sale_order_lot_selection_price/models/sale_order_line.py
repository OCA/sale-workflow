# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_product_price_context(self):
        ctx = super()._get_product_price_context()
        ctx.update(sol_lot=self.lot_id)
        return ctx

    @api.depends("lot_id")
    def _compute_price_unit(self):
        return super()._compute_price_unit()
