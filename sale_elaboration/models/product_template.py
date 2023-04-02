# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_elaboration = fields.Boolean()
    elaboration_profile_id = fields.Many2one(
        comodel_name="product.elaboration.profile",
        compute="_compute_elaboration_profile_id",
        inverse="_inverse_elaboration_profile_id",
        store=True,
    )

    @api.depends("product_variant_ids", "product_variant_ids.elaboration_profile_id")
    def _compute_elaboration_profile_id(self):
        unique_variants = self.filtered(lambda tmpl: tmpl.product_variant_count == 1)
        for template in unique_variants:
            template.elaboration_profile_id = (
                template.product_variant_ids.elaboration_profile_id
            )
        for template in self - unique_variants:
            template.elaboration_profile_id = False

    def _inverse_elaboration_profile_id(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.elaboration_profile_id = (
                    template.elaboration_profile_id
                )

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)
        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            if vals.get("elaboration_profile_id"):
                template.write(
                    {"elaboration_profile_id": vals["elaboration_profile_id"]}
                )
        return templates
