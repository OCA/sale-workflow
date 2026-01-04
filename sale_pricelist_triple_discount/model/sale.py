# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright 2023 Simone Rubino - Aion Tech
# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from .pricelist import COMPUTE_PRICE_TO_DISCOUNT_FIELD


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _recompute_prices(self):
        res = super()._recompute_prices()
        lines_to_recompute = self._get_update_prices_lines()
        lines_to_recompute._compute_discounts()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom_id", "product_uom_qty", "pricelist_item_id")
    def _compute_discounts(self):
        res = super()._compute_discounts()
        for line in self:
            price_rule = line.pricelist_item_id
            item_discount_field = COMPUTE_PRICE_TO_DISCOUNT_FIELD.get(
                price_rule.compute_price
            )
            if item_discount_field is not None:
                line.discount1 = price_rule.percent_price
                line.discount2 = price_rule.discount2
                line.discount3 = price_rule.discount3
        return res
