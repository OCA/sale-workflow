# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    has_packaging_available = fields.Boolean(
        compute="_compute_has_packaging_available",
    )

    @api.depends("product_id.packaging_ids")
    def _compute_has_packaging_available(self):
        for record in self:
            record.has_packaging_available = bool(record.product_id.packaging_ids)
