# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for order in self:
            if order.company_id.sale_auto_remove_zero_quantity_lines:
                zero_lines = order.order_line.filtered(
                    lambda line: line.product_id and line.product_uom_qty == 0
                )
                if zero_lines:
                    body = _(
                        "Some sale order lines with zero quantities were removed upon "
                        "confirmation."
                    )
                    order.message_post(body=body)
                    zero_lines.unlink()
        return super().action_confirm()
