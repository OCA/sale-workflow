# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleWarehouseRule(models.Model):
    _name = "sale.warehouse.rule"
    _inherit = "attribute.value.dependant.mixin"
    _description = "Sale Warehouse Rule"

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
