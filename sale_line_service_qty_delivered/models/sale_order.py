# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order"

    def _get_invoice_status(self):
        super()._get_invoice_status()
        to_invoice_state = "to invoice"
        for order in self:
            if order.state not in ("sale", "done"):
                continue
            if order.invoice_status != "no":
                continue
            if any(
                line._is_delivered_method_delivery()
                and line.invoice_status == to_invoice_state
                for line in order.order_line
            ):
                order.invoice_status = to_invoice_state
