# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleWarehouseRule(models.Model):
    _name = "sale.warehouse.rule"
    _inherit = "attribute.value.dependent.mixin"
    _description = "Sale Warehouse Rule"
    _order = "applied_on"

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    applied_on = fields.Selection(
        selection=[
            ("0_product", "Product"),
            ("1_attribute", "Attribute"),
            ("2_template", "Template"),
        ],
        string="Applied on",
        compute="_compute_applied_on",
        store=True,
    )

    @api.depends("product_id", "attribute_value_ids")
    def _compute_applied_on(self):
        for rule in self:
            if rule.product_id:
                rule.applied_on = "0_product"
            elif rule.attribute_value_ids:
                rule.applied_on = "1_attribute"
            else:
                rule.applied_on = "2_template"

    @api.constrains("product_id", "attribute_value_ids", "warehouse_id")
    def _check_warehouse_rule_uniqueness(self):
        for rule in self:
            base_domain = [
                ("id", "!=", rule.id),
                ("product_tmpl_id", "=", rule.product_tmpl_id.id),
                ("company_id", "=", rule.company_id.id),
                ("warehouse_id", "!=", rule.warehouse_id.id),
            ]
            if rule.attribute_value_ids:
                domain = base_domain + [
                    ("product_id", "=", False),
                    ("attribute_value_ids", "in", rule.attribute_value_ids.ids),
                ]
                if self.search_count(domain):
                    raise ValidationError(
                        self.env._("A rule with the same attributes already exists.")
                    )
            if rule.product_id:
                domain = base_domain + [
                    ("product_id", "=", rule.product_id.id),
                    ("attribute_value_ids", "=", False),
                ]
                if self.search_count(domain):
                    raise ValidationError(
                        self.env._("A rule with the same product already exists.")
                    )
            if not rule.product_id and not rule.attribute_value_ids:
                domain = base_domain + [
                    ("product_id", "=", False),
                    ("attribute_value_ids", "=", False),
                ]
                if self.search_count(domain):
                    raise ValidationError(
                        self.env._("Warehouse rules must be unique by template.")
                    )
