# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        todo_moves = super()._action_done(cancel_backorder=cancel_backorder)
        # ensure container deposit qty are updated on related SOs
        if todo_moves:
            todo_moves.sale_line_id.order_id.update_order_container_deposit_quantity()
        return todo_moves
