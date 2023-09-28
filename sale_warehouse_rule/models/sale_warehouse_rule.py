# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleWarehouseRule(models.Model):
    _name = "sale.warehouse.rule"
    _inherit = "attribute.value.dependant.mixin"
    _description = "Sale Warehouse Rule"

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    product_id = fields.Many2one(domain="[('id', 'in', available_product_ids)]")
    available_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Available Products",
        compute="_compute_available_product_ids",
    )

    @api.depends("product_tmpl_id")
    def _compute_available_product_ids(self):
        for rec in self:
            rec.available_product_ids = self.env["product.product"].search(
                [("product_tmpl_id", "=", self.product_tmpl_id._origin.id)]
            )
