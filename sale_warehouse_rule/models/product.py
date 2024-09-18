# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        compute="_compute_variant_warehouse_id",
        store=True,
        string="Product Warehouse",
    )

    @api.depends(
        "product_tmpl_id.warehouse_rule_ids",
        "product_tmpl_id.warehouse_rule_ids.product_id",
        "product_tmpl_id.warehouse_rule_ids.attribute_value_ids",
        "product_tmpl_id.warehouse_rule_ids.warehouse_id",
    )
    def _compute_variant_warehouse_id(self):
        for product in self:
            tmpl_warehouse_rule = product.product_tmpl_id.warehouse_rule_ids.filtered(
                lambda r: not r.product_id and not r.attribute_value_ids
            )
            if tmpl_warehouse_rule:
                product.variant_warehouse_id = tmpl_warehouse_rule.warehouse_id
            else:
                variant_warehouse_id = False
                product_ptav_ids = product.product_template_attribute_value_ids
                for rule in product.product_tmpl_id.warehouse_rule_ids:
                    if (rule.product_id and rule.product_id == product) or (
                        rule.attribute_value_ids
                        and product_ptav_ids.product_attribute_value_id
                        in rule.attribute_value_ids
                    ):
                        variant_warehouse_id = rule.warehouse_id
                product.variant_warehouse_id = variant_warehouse_id
