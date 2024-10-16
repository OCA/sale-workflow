# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_cancel(self):
        sale_moves = self.filtered(
            lambda m: m.sale_line_id and m.state not in ("done", "cancel")
        )
        res = super()._action_cancel()
        sale_lines = sale_moves.filtered(lambda m: m.state == "cancel").sale_line_id
        sale_lines._update_qty_canceled()
        return res

    def _action_done(self, cancel_backorder=False):
        moves_todo = super()._action_done(cancel_backorder=cancel_backorder)
        if cancel_backorder and moves_todo:
            # _action_cancel is called before marking as done, so the hook on
            # _action_cancel will not be triggered. Call it now
            self.sale_line_id._update_qty_canceled()
        return moves_todo
