# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_no_effect_on_threshold_lines(self):
        """
        Returns the lines that have no effect on the minimum amount to reach
        """
        self.ensure_one()
        lines = self.order_line.filtered(lambda line: line.product_id.loyalty_exclude)
        return lines | super()._get_no_effect_on_threshold_lines()
