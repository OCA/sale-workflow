# Copyright 2019-2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SalePromotionRule(models.Model):

    _inherit = "sale.promotion.rule"

    def _get_lines_excluded_from_total_amount(self, order):
        lines = super()._get_lines_excluded_from_total_amount(order)
        lines |= order.order_line.filtered("is_delivery")
        return lines

    def _is_promotion_valid_for_line(self, line):
        self.ensure_one()
        if line.is_delivery:
            return False
        return super()._is_promotion_valid_for_line(line)
