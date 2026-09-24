# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _should_auto_remove_zero_quantity_lines(self):
        self.ensure_one()
        return self.company_id.sale_auto_remove_zero_quantity_lines

    def action_confirm(self):
        all_lines_to_unlink = self.env["sale.order.line"]
        for order in self:
            if order._should_auto_remove_zero_quantity_lines():
                zero_or_empty_lines = order.order_line.filtered(
                    lambda line: (line.product_id and line.product_uom_qty == 0)
                    or (line.display_type == "line_note" and not line.name.strip())
                )
                if zero_or_empty_lines:
                    body = self.env._(
                        "Some lines with zero quantities or empty notes were "
                        "removed upon confirmation."
                    )
                    order.message_post(body=body)
                    all_lines_to_unlink |= zero_or_empty_lines

        if all_lines_to_unlink:
            all_lines_to_unlink.unlink()

        return super().action_confirm()
