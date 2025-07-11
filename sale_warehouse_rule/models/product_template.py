# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    warehouse_rule_ids = fields.One2many(
        comodel_name="sale.warehouse.rule",
        inverse_name="product_tmpl_id",
        string="Warehouse Rules",
    )
