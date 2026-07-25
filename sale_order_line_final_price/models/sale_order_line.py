# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import config, float_compare, float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_final = fields.Float(
        string="Final Price",
        compute="_compute_price_final",
        store=True,
        readonly=False,
        precompute=True,
        min_display_digits="Product Price",
        help="Unit price once the discount is applied. Set here the price agreed "
        "with the customer and the discount will be computed accordingly, keeping "
        "the unit price given by the pricelist.",
    )
    price_edit_allowed = fields.Boolean(
        compute="_compute_price_edit_allowed",
        help="Technical field to know whether the current user is allowed to edit "
        "the unit price and the discount of the line.",
    )

    @api.depends("product_id")
    @api.depends_context("uid")
    def _compute_price_edit_allowed(self):
        if config["test_enable"] and not self.env.context.get(
            "test_sale_order_line_final_price"
        ):
            self.price_edit_allowed = True
        else:
            self.price_edit_allowed = self.env.user.has_group(
                "sales_team.group_sale_manager"
            )

    @api.depends("price_unit", "discount")
    def _compute_price_final(self):
        for line in self:
            line.price_final = line._get_discounted_price()

    @api.depends("price_final")
    def _compute_price_unit(self):
        dp = self.env["decimal.precision"].precision_get("Product Price")
        handled = self.browse()
        for line in self:
            # Distinguish if the final price has been changed
            if float_compare(
                line.price_final, line._get_discounted_price(), precision_digits=dp
            ):
                handled += line
                if not line.technical_price_unit:
                    # If not initial price, we need to set it to the final price, as no
                    # discount variation can be set for getting the desired one
                    line.price_unit = line.price_final
        self -= handled
        return super()._compute_price_unit()

    @api.depends("price_final")
    def _compute_discount(self):
        dp = self.env["decimal.precision"].precision_get("Product Price")
        dpd = self.env["decimal.precision"].precision_get("Discount")
        handled = self.browse()
        for line in self:
            # Distinguish if the final price has been changed
            if float_compare(
                line.price_final, line._get_discounted_price(), precision_digits=dp
            ):
                handled += line
                if not line.technical_price_unit:
                    line.discount = 0
                else:
                    line.discount = float_round(
                        (1 - line.price_final / line.price_unit) * 100,
                        precision_digits=dpd,
                    )
        self -= handled
        return super()._compute_discount()

    def _add_precomputed_values(self, vals_list):
        # To be removed if odoo/odoo#278444 is merged
        for vals in vals_list:
            if "price_unit" in vals and "technical_price_unit" not in vals:
                # Absurd value to not match any of the possible creation values
                vals["technical_price_unit"] = -9999999999
        return super()._add_precomputed_values(vals_list)
