# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    general_discount_apply = fields.Boolean(
        string="Apply general discount",
        compute="_compute_general_discount_apply",
        inverse="_inverse_general_discount_apply",
        search="_search_general_discount_apply",
        help="If this checkbox is ticked, it means changing general discount on sale order "
        "will impact sale order lines with this related product.",
    )

    def _search_general_discount_apply(self, operator, value):
        templates = self.with_context(active_test=False).search(
            [("product_variant_ids.general_discount_apply", operator, value)]
        )
        return [("id", "in", templates.ids)]

    @api.depends("product_variant_ids.general_discount_apply")
    def _compute_general_discount_apply(self):
        self.general_discount_apply = True
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.general_discount_apply = (
                    template.product_variant_ids.general_discount_apply
                )

    def _inverse_general_discount_apply(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.general_discount_apply = (
                self.general_discount_apply
            )
