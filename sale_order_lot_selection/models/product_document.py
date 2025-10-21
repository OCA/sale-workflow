# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductDocument(models.Model):
    _inherit = "product.document"

    domain_lot_id = fields.Binary(compute="_compute_domain_lot_id")
    lot_id = fields.Many2one(
        comodel_name="stock.lot", string="Lot", domain="domain_lot_id"
    )

    @api.depends("res_model", "res_id")
    def _compute_domain_lot_id(self):
        for item in self:
            if item.res_id and item.res_model in (
                "product.product",
                "product.template",
            ):
                record = self.env[item.res_model].browse(item.res_id)
                if item.res_model == "product.product":
                    domain = [("product_id", "=", record.id)]
                else:
                    domain = [("product_id.product_tmpl_id", "=", record.id)]
                item.domain_lot_id = domain
            else:
                item.domain_lot_id = []
