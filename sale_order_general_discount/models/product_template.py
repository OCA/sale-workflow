# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bypass_general_discount = fields.Boolean(
        string="Don't apply general discount",
        compute="_compute_bypass_general_discount",
        inverse="_inverse_bypass_general_discount",
        search="_search_bypass_general_discount",
        help="If this checkbox is not ticked, it means changing general discount on "
        "sale order will impact sale order lines with this related product.",
    )

    def _search_bypass_general_discount(self, operator, value):
        templates = self.with_context(active_test=False).search(
            [("product_variant_ids.bypass_general_discount", operator, value)]
        )
        return [("id", "in", templates.ids)]

    @api.depends("product_variant_ids.bypass_general_discount")
    def _compute_bypass_general_discount(self):
        self.bypass_general_discount = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.bypass_general_discount = (
                    template.product_variant_ids.bypass_general_discount
                )

    def _inverse_bypass_general_discount(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.bypass_general_discount = (
                self.bypass_general_discount
            )
