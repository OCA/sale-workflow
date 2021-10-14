# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import pycompat


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_classification = fields.Selection(
        selection=[
            ("a", "A"),
            ("b", "B"),
            ("c", "C"),
            ("d", "D"),
        ],
        compute="_compute_sale_classification",
        inverse="_inverse_sale_classification",
        search="_search_sale_classification",
        readonly=False,
    )
    seasonality_classification = fields.Selection(
        selection=[
            ("very high", "Very high"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        compute="_compute_seasonality_classification",
        inverse="_inverse_seasonality_classification",
        search="_search_seasonality_classification",
        readonly=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Set given values to first variant after creation"""
        templates = super().create(vals_list)
        for template, vals in pycompat.izip(templates, vals_list):
            related_vals = {}
            if vals.get("sale_classification"):
                related_vals["sale_classification"] = (
                    vals["sale_classification"])
            if vals.get("seasonality_classification"):
                related_vals["seasonality_classification"] = (
                    vals["seasonality_classification"])
            if related_vals:
                template.write(related_vals)
        return templates

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.sale_classification"
    )
    def _compute_sale_classification(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.sale_classification = (
                template.product_variant_ids.sale_classification
            )
        for template in (self - unique_variants):
            template.sale_classification = False

    def _inverse_sale_classification(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.sale_classification = (
                self.sale_classification
            )

    def _search_sale_classification(self, operator, value):
        products = self.env["product.product"].search(
            [
                ("sale_classification", operator, value)
            ],
            limit=None
        )
        return [("id", "in", products.mapped("product_tmpl_id").ids)]

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.seasonality_classification"
    )
    def _compute_seasonality_classification(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.seasonality_classification = (
                template.product_variant_ids.seasonality_classification
            )
        for template in (self - unique_variants):
            template.seasonality_classification = False

    def _inverse_seasonality_classification(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.seasonality_classification = (
                self.seasonality_classification
            )

    def _search_seasonality_classification(self, operator, value):
        products = self.env["product.product"].search(
            [
                ("seasonality_classification", operator, value)
            ],
            limit=None
        )
        return [("id", "in", products.mapped("product_tmpl_id").ids)]
