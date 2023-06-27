# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_moves_sequence(self):
        for order in self:
            if any(
                [
                    ptype in ["product", "consu"]
                    for ptype in order.order_line.mapped("product_id.type")
                ]
            ):
                pickings = order.picking_ids.filtered(
                    lambda x: x.state not in ("done", "cancel")
                )
                if pickings:
                    picking = pickings[0]
                    order_lines = order.order_line.filtered(
                        lambda l: l.product_id.type in ["product", "consu"]
                    )
                    for move, line in zip(
                        sorted(picking.move_lines, key=lambda m: m.id), order_lines
                    ):
                        move.write({"sequence": line.sequence})

    def write(self, line_values):
        res = super(SaleOrder, self).write(line_values)
        if "order_line" in line_values:
            self._update_moves_sequence()
        return res
