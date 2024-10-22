# Copyright 2024 Ecosoft (<https://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """Invoked when confirm order."""
        self.mapped("order_line").create_auto_spread()
        res = super().action_confirm()
        spreads = self.mapped("order_line.spread_id")
        spreads.compute_spread_board()
        return res

    def action_cancel(self):
        """Cancel the spread lines and their related moves when
        the sales is canceled."""
        spread_lines = self.mapped("order_line.spread_id.line_ids")
        moves = spread_lines.mapped("move_id")
        moves.line_ids.remove_move_reconcile()
        moves.filtered(lambda move: move.state == "posted").button_draft()
        moves.with_context(force_delete=True).unlink()
        spread_lines.unlink()
        res = super().action_cancel()
        return res
