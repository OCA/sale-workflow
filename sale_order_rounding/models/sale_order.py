# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import math

from odoo import models
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_apply_round_up(self):
        self.ensure_one()
        existing_rounding_lines = self.order_line.filtered("is_rounding_line")
        if existing_rounding_lines:
            existing_rounding_lines.unlink()
        difference = math.ceil(self.amount_total) - self.amount_total
        if self.currency_id.is_zero(difference):
            return False
        rounding_product = self.env.ref(
            "sale_order_rounding.product_product_rounding",
            raise_if_not_found=False,
        )
        if not rounding_product:
            return False
        next_sequence = max(self.order_line.mapped("sequence"), default=10) + 1
        self.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "product_id": rounding_product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": self.currency_id.round(difference),
                            "is_rounding_line": True,
                            "sequence": next_sequence,
                            "tax_ids": [Command.clear()],
                        }
                    )
                ]
            }
        )
        return True
