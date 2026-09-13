# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    untaxed_amount_to_invoice = fields.Monetary(
        compute="_compute_untaxed_amount_to_invoice", store=True
    )

    @api.depends("order_line.untaxed_amount_to_invoice")
    def _compute_untaxed_amount_to_invoice(self):
        """Compute the total invoice amount for each sales order."""
        result = self.env["sale.order.line"]._read_group(
            [("order_id", "in", self.ids)],
            groupby=["order_id"],
            aggregates=["untaxed_amount_to_invoice:sum"],
        )
        amounts = {item[0].id: item[1] for item in result}
        for order in self:
            order.untaxed_amount_to_invoice = amounts.get(order.id, 0)
