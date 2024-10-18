# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleWarehouseRule(models.Model):
    _name = "sale.warehouse.rule"
    _inherit = "attribute.value.dependant.mixin"
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
            domain = [
                ("product_tmpl_id", "=", rule.product_tmpl_id.id),
                ("product_id", "=", rule.product_id.id),
                ("attribute_value_ids", "=", rule.attribute_value_ids.ids),
                ("warehouse_id", "!=", rule.warehouse_id.id),
                ("company_id", "=", rule.company_id.id),
            ]
            domain[1] = ("product_id", "=", False)
            if self.search_count(domain) and rule.attribute_value_ids:
                raise ValidationError(
                    _("A rule with the same attributes already exists.")
                )
            domain[1] = ("product_id", "=", rule.product_id.id)
            domain[2] = ("attribute_value_ids", "=", False)
            if self.search_count(domain) and rule.product_id:
                raise ValidationError(_("A rule with the same product already exists."))
            domain[1] = ("product_id", "=", False)
            if (
                self.search_count(domain)
                and not rule.product_id
                and not rule.attribute_value_ids
            ):
                raise ValidationError(_("Warehouse rules must be unique by template."))
