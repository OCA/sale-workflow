# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright 2023 Simone Rubino - Aion Tech
# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _recompute_prices(self):
        res = super()._recompute_prices()
        lines_to_recompute = self._get_update_prices_lines()
        lines_to_recompute._compute_discount1()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount2 = fields.Float(
        compute="_compute_discount1",
        readonly=False,
        store=True,
        compute_sudo=True,
        precompute=True,
    )
    discount3 = fields.Float(
        compute="_compute_discount1",
        readonly=False,
        store=True,
        compute_sudo=True,
        precompute=True,
    )

    def _compute_discount1(self):
        # super() sets in discount1 the whole discount of the pricelist rule,
        # that is the combination of the three discounts of the rule:
        # split it back in the three discounts.
        res = super()._compute_discount1()
        for line in self:
            price_rule = line.pricelist_item_id
            if (
                line.discount1
                and not line.combo_item_id
                and price_rule._show_discount()
            ):
                total = line.discount1
                extra = (1 - price_rule.discount2 / 100) * (
                    1 - price_rule.discount3 / 100
                )
                if extra:
                    line.discount1 = 100 * (1 - (1 - total / 100) / extra)
                line.discount2 = price_rule.discount2
                line.discount3 = price_rule.discount3
            else:
                line.discount2 = 0
                line.discount3 = 0
        return res
