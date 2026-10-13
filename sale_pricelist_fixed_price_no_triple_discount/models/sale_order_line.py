# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        lambda self: self._get_multiple_discount_field_names()
        + ["fixed_price_pricelist_rule"]
    )
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            if line.fixed_price_pricelist_rule:
                line.discount1 = 0.0
                line.discount2 = 0.0
                line.discount3 = 0.0
                line.discount = 0.0
        return res
