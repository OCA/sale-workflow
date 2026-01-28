# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order"

    def _get_invoice_status(self):
        super()._get_invoice_status()
        to_invoice_status = "to invoice"
        no_invoice_status = "no"
        for order in self:
            if (
                order.state not in ("sale", "done")
                or order.invoice_status != no_invoice_status
            ):
                continue

            invoice_status = no_invoice_status
            for line in order.order_line:
                if not line._is_delivered_method_delivery():
                    continue
                if line.invoice_status == to_invoice_status:
                    invoice_status = to_invoice_status
                    break

            if invoice_status == to_invoice_status:
                order.invoice_status = to_invoice_status
