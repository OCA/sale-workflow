# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_next_reception = fields.Date(compute="_compute_date_next_reception")

    def _compute_date_next_reception(self):
        for line in self:
            line.date_next_reception = False
            qty_available = line.product_id.with_context(
                warehouse=line.order_id.warehouse_id.id
            ).qty_available
            if qty_available <= 0 and line.state not in ["done", "cancel"]:
                line.date_next_reception = line.product_id.date_next_reception
