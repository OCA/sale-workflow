# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id")
    def _compute_name(self):
        if self.env.context.get("so_product_stock_inline"):
            self = self.with_context(so_product_stock_inline=False)
        return super(SaleOrderLine, self)._compute_name()
