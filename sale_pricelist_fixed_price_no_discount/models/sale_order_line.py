# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fixed_price_pricelist_rule = fields.Boolean(
        compute="_compute_fixed_price_pricelist_rule"
    )

    @api.depends("pricelist_item_id")
    def _compute_fixed_price_pricelist_rule(self):
        for line in self:
            line.fixed_price_pricelist_rule = line._has_fixed_price_pricelist_rule()

    def _has_fixed_price_pricelist_rule(self):
        self.ensure_one()
        return (
            self.pricelist_item_id.compute_price == "fixed"
            and self.pricelist_item_id.fixed_price_no_discount
        )

    @api.depends("pricelist_item_id")
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            if line._has_fixed_price_pricelist_rule():
                line.discount = 0.0
        return res

    @api.constrains("discount", "product_id", "product_uom", "product_uom_qty")
    def _check_no_discount_on_fixed_price_pricelist_rule(self):
        precision = self.env["decimal.precision"].precision_get("Discount")
        for line in self:
            if line.fixed_price_pricelist_rule and not float_is_zero(
                line.discount, precision_digits=precision
            ):
                raise ValidationError(
                    _(
                        "Discounts are not allowed when the applied pricelist rule "
                        "uses a fixed price."
                    )
                )
