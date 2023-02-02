# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_cancel(self):
        sale_moves = self.filtered(
            lambda m: m.sale_line_id and m.state not in ("done", "cancel")
        )
        res = super()._action_cancel()
        for rec in sale_moves:
            if rec.state != "cancel":
                continue
            rec.sale_line_id.product_qty_canceled = rec.product_uom_qty
        return res
