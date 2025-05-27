# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    display_in_report = fields.Boolean(
        default=True,
        help="Disable it to hide it in the quotations/sale orders that customer sees",
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res["display_in_report"] = self.display_in_report
        return res

    def _compute_amount(self):
        res = super()._compute_amount()
        # Avoid hiding lines with any amount
        self.filtered(
            lambda line: line.price_total and not line.display_in_report
        ).display_in_report = True
        return res
