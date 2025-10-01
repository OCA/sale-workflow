# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    display_in_report = fields.Boolean(
        default=True,
        help="Disable it to hide it in the invoice reports that customer sees",
    )

    def _compute_totals(self):
        res = super()._compute_totals()
        # Avoid hiding lines with any amount
        self.filtered(
            lambda line: line.price_total and not line.display_in_report
        ).display_in_report = True
        return res
