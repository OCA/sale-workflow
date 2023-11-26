# Copyright 2018-2021 Acsone SA/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

line_restriction_amount_mapping = {
    "amount_total": "price_total",
    "amount_untaxed": "price_subtotal",
}


class SalePromotionRule(models.Model):

    _inherit = "sale.promotion.rule"

    filter_id = fields.Many2one(
        "ir.filters",
        "Filter",
        help="Export only products matching with the filter domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True, "default_is_assortment": 1},
    )

    def _get_promotion_rule_products(self):
        product_obj = self.env["product.product"]
        if self.filter_id:
            domain = self.filter_id._get_eval_domain()
            return product_obj.search(domain)
        return product_obj.search([])

    def _get_promotions_valid_order_lines(self, order=False, line=False):
        if order:
            order_lines = order.order_line
        elif line:
            order_lines = line
        if order_lines:
            if not self.filter_id:
                return order_lines
            promotion_product_ids = self._get_promotion_rule_products()
            order_line_ids = order_lines.filtered(
                lambda line, product_ids=promotion_product_ids: line.product_id.id
                in product_ids.ids
            )
            return order_line_ids
        else:
            return False

    @api.model
    def _get_restrictions(self):
        res = super()._get_restrictions()
        res.append("product_assortment")
        return res

    def _check_valid_product_assortment(self, order):
        if self.filter_id:
            order_lines = self._get_promotions_valid_order_lines(order=order)
            if not order_lines:
                return False

        return True

    def _is_promotion_valid_for_line(self, line):
        res = super()._is_promotion_valid_for_line(line)
        if self.filter_id:
            order_lines = self._get_promotions_valid_order_lines(line=line)
            if not order_lines:
                return False
        return res

    def _get_lines_excluded_from_total_amount(self, order):
        order_lines = self._get_promotions_valid_order_lines(order=order)
        return order.order_line - order_lines
