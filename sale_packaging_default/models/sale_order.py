# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import exceptions, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        if required_packaging_lines := self.mapped("order_line").filtered_domain(
            [("is_packaging_required", "=", True), ("product_packaging_id", "=", False)]
        ):
            raise exceptions.UserError(
                self.env._(
                    "Some packaging is required but not set "
                    "on the following lines:\n- %s",
                    "\n- ".join(required_packaging_lines.mapped("display_name")),
                )
            )
        return res
