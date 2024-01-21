# Copyright 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.mapped("order_id")._update_product_uom_qty()
        return res

    def write(self, vals):
        res = super().write(vals)
        loop_safe = self.env.context.get("product_uom_qty.loop_safe", True)
        if any(
            [
                "product_template_id" in vals,
                "product_uom_qty" in vals and loop_safe,
            ]
        ):
            self.mapped("order_id")._update_product_uom_qty()
        return res

    def unlink(self):
        self.mapped("order_id")._update_product_uom_qty()
        return super().unlink()
