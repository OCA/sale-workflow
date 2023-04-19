# Copyright 2018-2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Default secondary unit for sales",
        compute="_compute_sale_secondary_uom_id",
        inverse="_inverse_sale_secondary_uom_id",
        help="In order to set a value, please first add at least one record"
        " in 'Secondary Unit of Measure'",
        domain="[('product_tmpl_id', '=', id), ('product_id', '=', False)]",
        store=True,
    )

    @api.depends("product_variant_ids", "product_variant_ids.sale_secondary_uom_id")
    def _compute_sale_secondary_uom_id(self):
        unique_variants = self.filtered(lambda tmpl: tmpl.product_variant_count == 1)
        for template in unique_variants:
            template.sale_secondary_uom_id = (
                template.product_variant_ids.sale_secondary_uom_id
            )
        for template in self - unique_variants:
            if len(template.product_variant_ids.sale_secondary_uom_id) == 1:
                template.sale_secondary_uom_id = (
                    template.product_variant_ids.sale_secondary_uom_id
                )
            else:
                template.sale_secondary_uom_id = False

    def _inverse_sale_secondary_uom_id(self):
        for template in self:
            # if template.product_variant_count == 1:
            template.product_variant_ids.sale_secondary_uom_id = (
                template.sale_secondary_uom_id
            )

    @api.onchange("sale_secondary_uom_id")
    def onchange_sale_secondary_uom_id(self):
        if len(self.product_variant_ids.sale_secondary_uom_id) > 1:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "Product variants have distinct sale secondary uom:"
                        "\n{secondary_uom}\n"
                        "All variants will be written with new secondary uom"
                    ).format(
                        secondary_uom="\n".join(
                            self.product_variant_ids.mapped(
                                "sale_secondary_uom_id.name"
                            )
                        )
                    ),
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)
        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get("sale_secondary_uom_id"):
                related_vals["sale_secondary_uom_id"] = vals["sale_secondary_uom_id"]
            if related_vals:
                template.write(related_vals)
        return templates
