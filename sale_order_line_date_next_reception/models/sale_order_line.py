# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_next_reception = fields.Date(
        compute="_compute_date_next_reception", compute_sudo=True
    )

    def _compute_date_next_reception(self):
        for line in self:
            line.date_next_reception = False
            qty_available = line.product_id.with_context(
                warehouse=line.order_id.warehouse_id.id
            ).qty_available
            if qty_available <= 0 and line.state not in ["done", "cancel"]:
                picking_model = self.env["stock.picking"]
                picking_id = picking_model.search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("picking_type_id.code", "=", "incoming"),
                        ("state", "in", ["ready", "waiting", "assigned"]),
                    ],
                    limit=1,
                )
                line.date_next_reception = picking_id.scheduled_date
