# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from .pricelist import COMPUTE_PRICE_TO_DISCOUNT_FIELD


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount2 = fields.Float(
        compute="_compute_discount",
        readonly=False,
        store=True,
        precompute=True,
        default=None,
    )
    discount3 = fields.Float(
        compute="_compute_discount",
        readonly=False,
        store=True,
        precompute=True,
        default=None,
    )

    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            discount = line.discount
            discount2 = discount3 = 0

            pricelist = line.order_id.pricelist_id
            if pricelist.discount_policy == "without_discount":
                price_rule = line.pricelist_item_id
                item_discount_field = COMPUTE_PRICE_TO_DISCOUNT_FIELD.get(
                    price_rule.compute_price
                )
                if item_discount_field is not None:
                    discount = price_rule[item_discount_field]
                    discount2 = price_rule.discount2
                    discount3 = price_rule.discount3

            line.discount = discount
            line.discount2 = discount2
            line.discount3 = discount3

        return res
