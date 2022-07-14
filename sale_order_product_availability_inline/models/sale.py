# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        so_line = self
        if self.env.context.get("so_product_stock_inline"):
            so_line = self.with_context(
                so_product_stock_inline=False, warehouse=self.warehouse_id.id
            )
        return super(SaleOrderLine, so_line).product_id_change()
