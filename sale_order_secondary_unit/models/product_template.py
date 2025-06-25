<<<<<<< HEAD
# Copyright 2018-2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_secondary_uom_id = fields.Many2one(
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        comodel_name="product.secondary.unit",
        string="Default secondary unit for sales",
        compute="_compute_sale_secondary_uom_id",
        inverse="_inverse_sale_secondary_uom_id",
        help="In order to set a value, please first add at least one record"
        " in 'Secondary Unit of Measure'",
        domain="[('product_tmpl_id', '=', id), ('product_id', '=', False)]",
        store=True,
||||||| parent of 90d059d1c ([11.0][IMP] sale_secondary_unit: Set secondary uom quantity as 1.0 by default)
        comodel_name='product.secondary.unit',
        string='Default unit sale',
=======
        comodel_name='product.secondary.unit',
        string='Default secondary unit for sales',
>>>>>>> 90d059d1c ([11.0][IMP] sale_secondary_unit: Set secondary uom quantity as 1.0 by default)
||||||| parent of 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
        comodel_name='product.secondary.unit',
        string='Default secondary unit for sales',
=======
        comodel_name="product.secondary.unit", string="Default secondary unit for sales"
>>>>>>> 331900273 ([MIG] migrate sale_order_secondary_unit from 12.0 to 13.0)
||||||| parent of 2ddeab7d2 ([MIG] sale_order_secondary_unit: Migration to 14.0)
        comodel_name="product.secondary.unit", string="Default secondary unit for sales"
=======
        comodel_name="product.secondary.unit",
        string="Default secondary unit for sales",
        help="In order to set a value, please first add at least one record"
        " in 'Secondary Unit of Measure'",
>>>>>>> 2ddeab7d2 ([MIG] sale_order_secondary_unit: Migration to 14.0)
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
                    "title": self.env._("Warning"),
                    "message": self.env._(
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
        templates = super().create(vals_list)
        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list, strict=True):
            related_vals = {}
            if vals.get("sale_secondary_uom_id"):
                related_vals["sale_secondary_uom_id"] = vals["sale_secondary_uom_id"]
            if related_vals:
                template.write(related_vals)
        return templates
||||||| parent of e596a34a8 (code refactor update)
=======
# Copyright 2018-2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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
<<<<<<< HEAD
>>>>>>> e596a34a8 (code refactor update)
||||||| parent of c0e2baecd ([IMP] sale_order_secondary_unit: Compatibility with product variants)
=======

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
                    "title": self.env._("Warning"),
                    "message": self.env._(
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
        templates = super().create(vals_list)
        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list, strict=True):
            related_vals = {}
            if vals.get("sale_secondary_uom_id"):
                related_vals["sale_secondary_uom_id"] = vals["sale_secondary_uom_id"]
            if related_vals:
                template.write(related_vals)
        return templates
>>>>>>> c0e2baecd ([IMP] sale_order_secondary_unit: Compatibility with product variants)
