# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _should_auto_remove_zero_quantity_lines(self):
        self.ensure_one()
        return self.company_id.sale_auto_remove_zero_quantity_lines

    def action_confirm(self):
        for order in self:
            if order._should_auto_remove_zero_quantity_lines():
                zero_or_empty_lines = order.order_line.filtered(
                    lambda line: (line.product_id and line.product_uom_qty == 0)
                    or (line.display_type == "line_note" and not line.name.strip())
                )
                if zero_or_empty_lines:
                    body = _(
                        "Some lines with zero quantities or empty notes were "
                        "removed upon confirmation."
                    )
                    order.message_post(body=body)
                    zero_or_empty_lines.unlink()
        return super().action_confirm()
