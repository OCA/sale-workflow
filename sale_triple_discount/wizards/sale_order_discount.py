# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderDiscount(models.TransientModel):
    _inherit = "sale.order.discount"

    def action_apply_discount(self):
        res = super().action_apply_discount()
        if self.discount_type == "sol_discount":
            self.sale_order_id.order_line.write(
                {
                    "discount1": self.discount_percentage * 100,
                    "discount2": 0,
                    "discount3": 0,
                }
            )
        return res
