# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_margin(self):
        # Overload to consider the call-off order lines in the computation
        # For these lines the margin must be set to 0
        call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        other_lines = self - call_off_lines
        call_off_lines.margin = 0
        call_off_lines.margin_percent = 0
        return super(SaleOrderLine, other_lines)._compute_margin()
