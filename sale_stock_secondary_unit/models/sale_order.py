# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_is_zero, float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        values["secondary_uom_id"] = self.secondary_uom_id.id
        values["secondary_uom_qty"] = self.env.context.get(
            "procure_secondary_uom_qty", {}
        ).get(self.id, self.secondary_uom_qty)
        return values

    def write(self, vals):
        lines = self.env["sale.order.line"]
        if "secondary_uom_qty" in vals:
            lines = self.filtered(lambda r: r.state == "sale" and not r.is_expense)
            procure_secondary_uom_qty = {
                line.id: float_round(
                    vals["secondary_uom_qty"] - line.secondary_uom_qty,
                    precision_rounding=line.secondary_uom_id.uom_id.rounding or 0.01,
                )
                for line in lines
            }
            self = self.with_context(
                procure_secondary_uom_qty=procure_secondary_uom_qty
            )
        res = super().write(vals)
        if lines and "product_uom_qty" not in vals:
            # A pure secondary_uom_qty edit never changes product_uom_qty,
            # so _action_launch_stock_rule would be a no-op here: it only
            # ever creates a new move for a primary-quantity delta
            # (_get_qty_procurement() derives "already procured" from the
            # existing moves themselves, not from previous_product_uom_qty,
            # confirmed empirically), it never touches an existing move's
            # secondary_uom_qty. Propagate the correction directly onto
            # whichever move(s) are still pending instead - writing it
            # also recomputes each move's own product_uom_qty from the
            # new count (secondary_priority: weight is still estimated
            # from pieces).
            for line in lines:
                pending_moves = line.move_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                )
                if len(pending_moves) == 1:
                    pending_moves.secondary_uom_qty = line.secondary_uom_qty
                elif len(pending_moves) > 1:
                    # A line already partially processed can have several
                    # pending moves at once (e.g. a backorder pick still
                    # pending alongside an earlier push leg not yet
                    # processed) - distribute the corrected total
                    # proportionally to each move's current share of it,
                    # largest-remainder style: every move but the last
                    # gets its rounded share, the last absorbs whatever is
                    # left so the total always adds up exactly.
                    rounding = line.secondary_uom_id.uom_id.rounding or 0.01
                    previous_total = sum(pending_moves.mapped("secondary_uom_qty"))
                    remaining = line.secondary_uom_qty
                    *moves_to_share, last_move = pending_moves
                    for move in moves_to_share:
                        if float_is_zero(previous_total, precision_rounding=rounding):
                            # Nothing to base a proportion on (e.g. no
                            # count entered on any of them yet) - split
                            # evenly instead.
                            share = float_round(
                                line.secondary_uom_qty / len(pending_moves),
                                precision_rounding=rounding,
                            )
                        else:
                            share = float_round(
                                line.secondary_uom_qty
                                * move.secondary_uom_qty
                                / previous_total,
                                precision_rounding=rounding,
                            )
                        move.secondary_uom_qty = share
                        remaining -= share
                    last_move.secondary_uom_qty = remaining
        return res
