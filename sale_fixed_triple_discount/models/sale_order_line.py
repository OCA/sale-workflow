# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("discount_fixed", "price_unit")
    def _compute_discount(self):
        # sale_triple_discount recomputes the discount of every line from
        # discount1/2/3 after super(), whatever the module order is, so the
        # fixed discount is applied again last to take priority.
        res = super()._compute_discount()
        for line in self:
            if not line.discount_fixed:
                continue
            line.discount = line._get_discount_from_fixed_discount()
        return res

    def _compute_discount1(self):
        # sale_fixed_discount's _compute_discount derives the discount from
        # discount_fixed; that value must not be dragged into discount1
        res = super()._compute_discount1()
        for line in self:
            if line.discount_fixed:
                line.discount1 = 0.0
        return res

    def _drop_discount_if_fixed(self, vals):
        """The fixed discount takes priority over the percentage discount.

        When both are passed, ``discount`` is dropped so it is recomputed from
        ``discount_fixed``. Otherwise an explicit value would be kept on the
        stored computed field and fail ``_check_discounts`` when both don't match.

        :return: a new dict, the given one is left untouched.
        """
        if "discount" in vals and vals.get("discount_fixed"):
            return {key: value for key, value in vals.items() if key != "discount"}
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._drop_discount_if_fixed(v) for v in vals_list])

    def write(self, vals):
        return super().write(self._drop_discount_if_fixed(vals))
