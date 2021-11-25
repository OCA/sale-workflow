# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_qty_recursively(self, quantity):
        if self.move_orig_ids.filtered(lambda m: m.state not in ("cancel", "done")):
            self.move_orig_ids._update_qty_recursively(quantity)
        moves_done = self.filtered(lambda m: m.state == "done")
        for move in moves_done:
            quantity = quantity - move.product_uom_qty
            if quantity < 0:
                quantity = 0
                break
        self.filtered(lambda m: m.state not in ("cancel", "done")).write(
            {"product_uom_qty": quantity}
        )
