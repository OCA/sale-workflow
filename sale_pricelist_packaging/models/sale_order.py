# Copyright 2025 Akretion (https://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        self.with_context(packaging=self.product_packaging).product_uom_change()
        return super()._onchange_product_packaging()

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        res = super().product_uom_change()
        if self.product_packaging and "packaging" not in self.env.context:
            self = self.with_context(packaging=self.product_packaging)
        print("### product_uom_change TRIGGERED", self.env.context)
        return res
