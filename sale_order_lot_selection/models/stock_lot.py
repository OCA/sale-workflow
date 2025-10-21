# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    document_count = fields.Integer(
        string="Documents Count", compute="_compute_document_count"
    )

    @api.depends("product_id")
    def _compute_document_count(self):
        for item in self:
            documents = item.product_id.product_document_ids.filtered(
                lambda x, lot=item: x.lot_id == lot
            )
            item.document_count = len(documents)

    def _get_product_document_domain(self):
        self.ensure_one()
        return [
            ("res_model", "=", self.product_id._name),
            ("res_id", "=", self.product_id.id),
            ("lot_id", "=", self.id),
        ]

    def action_open_documents(self):
        self.ensure_one()
        res = self.product_id.action_open_documents()
        res["domain"] = self._get_product_document_domain()
        res["context"].update(
            {
                "default_lot_id": self.id,
            }
        )
        return res
