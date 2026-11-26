# Copyright 2026 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.price_total")
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for order in self.filtered(lambda x: x.invoice_status == "to invoice"):
            lines_to_invoice = order.order_line.filtered(
                lambda x: x.invoice_status == "to invoice"
                and not x.is_downpayment
                and not x.display_type
            )
            if lines_to_invoice and all(
                order.currency_id.is_zero(line.price_total) for line in lines_to_invoice
            ):
                order.invoice_status = "no"
        return res
