# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Entrepôt par défaut",
        compute="_compute_variant_warehouse_id",
    )

    @api.depends(
        "warehouse_rule_ids",
        "warehouse_rule_ids.product_id",
        "warehouse_rule_ids.attribute_value_ids",
        "warehouse_rule_ids.warehouse_id",
    )
    @api.depends_context("allowed_company_ids", "force_company_id")
    def _compute_variant_warehouse_id(self):
        for product in self:
            company_id = self.env.context.get("force_company_id") or self.env.company.id
            variant_warehouse_id = False
            for rule in product.warehouse_rule_ids:
                if rule.company_id.id == company_id and rule.is_matching_product(
                    product
                ):
                    variant_warehouse_id = rule.warehouse_id
                    break
            product.variant_warehouse_id = variant_warehouse_id
