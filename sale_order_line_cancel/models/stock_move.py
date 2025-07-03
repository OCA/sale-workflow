# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_cancel(self):
        res = super()._action_cancel()
        sale_lines = self._get_sale_lines_to_update_qty_canceled()
        sale_lines._update_qty_canceled()
        return res

    def _action_done(self, cancel_backorder=False):
        moves_todo = super()._action_done(cancel_backorder=cancel_backorder)
        if cancel_backorder and moves_todo:
            # _action_cancel is called before marking as done, so the hook on
            # _action_cancel will not be triggered. Call it now
            self.sale_line_id._update_qty_canceled()
        return moves_todo

    def _get_sale_lines_to_update_qty_canceled(self):
        sale_lines = self.env["sale.order.line"]
        for move in self:
            if (
                move.sale_line_id
                and move._is_move_to_take_into_account_for_qty_canceled()
            ):
                sale_lines |= move.sale_line_id
        return sale_lines

    def _is_move_to_take_into_account_for_qty_canceled(self):
        self.ensure_one()
        return (
            self.state == "cancel"
            and self.sale_line_id
            and self.sale_line_id.state not in ["draft", "sent"]
            and self.picking_type_id.code == "outgoing"
        )
