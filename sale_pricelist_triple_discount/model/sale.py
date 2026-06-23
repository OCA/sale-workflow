# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright 2023 Simone Rubino - Aion Tech
# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from .pricelist import COMPUTE_PRICE_TO_DISCOUNT_FIELD


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
        default=None,
    )
    discount3 = fields.Float(
        compute="_compute_discount1",
        readonly=False,
        store=True,
        compute_sudo=True,
        precompute=True,
        default=None,
    )

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount1(self):
        res = super()._compute_discount1()
        for line in self:
            pricelist = line.order_id.pricelist_id
            if pricelist.discount_policy == "without_discount":
                price_rule = line.pricelist_item_id
                item_discount_field = COMPUTE_PRICE_TO_DISCOUNT_FIELD.get(
                    price_rule.compute_price
                )
                if item_discount_field is not None:
                    line.discount1 = price_rule[item_discount_field]
                    line.discount2 = price_rule.discount2
                    line.discount3 = price_rule.discount3
        return res
