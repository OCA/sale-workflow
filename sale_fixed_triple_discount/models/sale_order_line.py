# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.float_utils import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("discount_fixed", "price_unit")
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            if not line.discount_fixed:
                continue
            line.discount = line._get_discount_from_fixed_discount()
        return res

    def _get_lines_to_compute_discount(self):
        lines = super()._get_lines_to_compute_discount()
        return lines.filtered(
            lambda line: float_is_zero(
                line.discount_fixed, precision_rounding=line.currency_id.rounding
            )
        )
