# Copyright 2018 Okia SPRL
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2020 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_moves_to_cancel(self):
        lines = self.filtered(
            lambda l: l.qty_delivered_method == "stock_move"
            and l.can_cancel_remaining_qty
        )
        return lines.move_ids.filtered(lambda m: m.state not in ("done", "cancel"))

    def _check_moves_to_cancel(self, moves):
        """Override this method to add checks before cancel"""

    def cancel_remaining_qty(self):
        moves_to_cancel = self._get_moves_to_cancel()
        moves_to_cancel.sale_line_id._check_moves_to_cancel(moves_to_cancel)
        if moves_to_cancel:
            moves_to_cancel.with_context(
                ignore_sale_order_line_cancel=True
            )._action_cancel()
        return super().cancel_remaining_qty()
