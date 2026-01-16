# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_moves_sequence(self):
        for order in self:
            if any(
                ptype in ["product", "consu"]
                for ptype in order.order_line.mapped("product_id.type")
            ):
                for move in order.mapped("picking_ids.move_ids"):
                    move.sequence = move.sale_line_id.visible_sequence

    def action_confirm(self):
        res = super().action_confirm()
        self._update_moves_sequence()
        return res

    def write(self, line_values):
        res = super().write(line_values)
        if "order_line" in line_values:
            self._update_moves_sequence()
        return res
