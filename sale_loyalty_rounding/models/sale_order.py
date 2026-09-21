import math

from odoo import models
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_apply_round_up(self):
        self.ensure_one()

        existing_rounding_lines = self.order_line.filtered(lambda line: line.is_rounding_line)
        if existing_rounding_lines:
            existing_rounding_lines.unlink()
            self._compute_amounts()

        current_total = self.amount_total

        target_total = math.ceil(current_total)
        difference = target_total - current_total

        if difference > 0:
            rounding_product = self.env.ref("promovago.product_product_rounding", raise_if_not_found=False)

            if not rounding_product:
                return True

            rounding_price = self.currency_id.round(difference)

            next_sequence = max(self.order_line.mapped("sequence"), default=10) + 1

            self.write(
                {
                    "order_line": [
                        Command.create(
                            {
                                "product_id": rounding_product.id,
                                "product_uom_qty": 1.0,
                                "price_unit": rounding_price,
                                "is_rounding_line": True,
                                "sequence": next_sequence,
                                "tax_ids": [Command.clear()],
                            }
                        )
                    ]
                }
            )

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
