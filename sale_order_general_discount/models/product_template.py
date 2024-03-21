# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    not_general_discount_apply = fields.Boolean(
        string="Don't apply general discount",
        compute="_compute_not_general_discount_apply",
        inverse="_inverse_not_general_discount_apply",
        search="_search_not_general_discount_apply",
        help="If this checkbox is not ticked, it means changing general discount on "
        "sale order will impact sale order lines with this related product.",
    )

    def _search_not_general_discount_apply(self, operator, value):
        templates = self.with_context(active_test=False).search(
            [("product_variant_ids.not_general_discount_apply", operator, value)]
        )
        return [("id", "in", templates.ids)]

    @api.depends("product_variant_ids.not_general_discount_apply")
    def _compute_not_general_discount_apply(self):
        self.not_general_discount_apply = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.not_general_discount_apply = (
                    template.product_variant_ids.not_general_discount_apply
                )

    def _inverse_not_general_discount_apply(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.not_general_discount_apply = (
                self.not_general_discount_apply
            )
