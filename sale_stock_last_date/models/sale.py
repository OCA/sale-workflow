# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    last_delivery_date = fields.Datetime(
        string="Last delivery date", compute="_compute_last_delivery_date", store=True
    )

    @api.depends("move_ids.state", "move_ids.date")
    def _compute_last_delivery_date(self):
        for line in self:
            stock_moves = line.move_ids.filtered(
                lambda m: (
                    m.picking_code == "outgoing"
                    and m.state == "done"
                    and not m.scrapped
                )
            )
            line.last_delivery_date = stock_moves.sorted("date", reverse=True)[:1].date
