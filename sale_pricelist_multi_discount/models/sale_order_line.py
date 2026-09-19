# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_pricelist_discount_distribution(self):
        """Copy the rule's own distribution onto the line.

        Falls back to the standard single-percent seeding
        when the matching rule does not carry an explicit
        ``discount_distribution``.
        """
        self.ensure_one()
        rule = self.pricelist_item_id
        if rule and rule.discount_distribution and rule._show_discount():
            return list(rule.discount_distribution)
        return super()._get_pricelist_discount_distribution()
