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

    @api.depends("product_id", "product_uom_id", "product_uom_qty")
    def _compute_discount1(self):
        # discount1 copies the discount computed by super(), which is the
        # percentage of the fixed discount on lines having one: keep it empty
        # there, as account_invoice_fixed_triple_discount does on invoices.
        lines_with_discount_fixed = self.filtered("discount_fixed")
        lines_with_discount_fixed.discount1 = 0.0
        return super(
            SaleOrderLine, self - lines_with_discount_fixed
        )._compute_discount1()

    @api.model_create_multi
    def create(self, vals_list):
        # As on invoice lines (account_invoice_fixed_triple_discount), a fixed
        # discount is not copied to discount1: drop the percentage given with it
        # so the discount is computed from the fixed amount.
        vals_list = [
            {key: value for key, value in vals.items() if key != "discount"}
            if vals.get("discount_fixed")
            else vals
            for vals in vals_list
        ]
        return super().create(vals_list)
